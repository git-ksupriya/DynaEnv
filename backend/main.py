import asyncio
import time
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from backend.spatial import (
    get_semantic_position,
    get_message_size,
    find_free_position,
)


connected_clients: list[WebSocket] = []
active_messages: list[dict] = []


def calculate_ttl(text: str) -> int:
    length = len(text.strip())

    if length <= 5:
        return 5

    if length <= 30:
        return 10

    return 15


async def cleanup_expired_messages():
    while True:
        now = time.time()

        expired = [
            message
            for message in active_messages
            if message["expires_at"] <= now
        ]

        for message in expired:
            active_messages.remove(message)

        await asyncio.sleep(0.5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    cleanup_task = asyncio.create_task(
        cleanup_expired_messages()
    )

    yield

    cleanup_task.cancel()

    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)

    try:
        while True:
            raw_message = await websocket.receive_text()

            message = json.loads(raw_message)

            message["created_at"] = time.time()

            ttl = calculate_ttl(message["text"])

            message["ttl"] = ttl

            message["expires_at"] = (
                message["created_at"] + ttl
            )

            preferred_position = get_semantic_position(
                message["text"]
            )

            size = get_message_size(
                message["text"]
            )

            message["size"] = size

            position = find_free_position(
                preferred_position,
                size,
                active_messages,
            )

            if position is None:
                # Temporary behavior.
                # Queueing comes next.
                continue

            message["position"] = position
            message["size"] = size

            active_messages.append(message)

            payload = json.dumps(message)

            for client in connected_clients:
                await client.send_text(payload)

    except WebSocketDisconnect:
        if websocket in connected_clients:
            connected_clients.remove(websocket)