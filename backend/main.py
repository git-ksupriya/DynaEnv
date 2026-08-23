import asyncio
import time
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from backend.spatial import (
    get_message_size,
    get_dynamic_position,
    is_position_valid,
)
from backend.embeddings import (
    get_embedding,
    get_most_similar_and_dissimilar,
)

connected_clients: list[WebSocket] = []
active_messages: list[dict] = []
pending_messages: list[dict] = []


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

        # Something may have opened up.
        if expired and pending_messages:
            await process_queue()

        await asyncio.sleep(0.5)

async def broadcast_queue_status():

    payload = json.dumps({
        "type": "queue_status",
        "count": len(pending_messages),
    })

    dead_clients = []

    for client in connected_clients:
        try:
            await client.send_text(payload)
        except Exception:
            dead_clients.append(client)

    for client in dead_clients:
        if client in connected_clients:
            connected_clients.remove(client)

async def broadcast_message(payload: str):

    dead_clients = []

    for client in connected_clients:
        try:
            await client.send_text(payload)
        except Exception:
            dead_clients.append(client)

    for client in dead_clients:
        if client in connected_clients:
            connected_clients.remove(client)

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

async def try_place_message(message: dict) -> bool:

    # TTL starts NOW because we're attempting to display it.
    message["created_at"] = time.time()

    ttl = calculate_ttl(
        message["text"]
    )

    message["ttl"] = ttl

    message["expires_at"] = (
        message["created_at"] + ttl
    )

    # Generate semantic embedding.
    if "embedding" not in message:
        message["embedding"] = get_embedding(
            message["text"]
        )

    similar_message, dissimilar_message = (
        get_most_similar_and_dissimilar(
            message["embedding"],
            active_messages,
        )
    )

    size = get_message_size(
        message["text"]
    )

    message["size"] = size

    preferred_position = get_dynamic_position(
        similar_message,
        dissimilar_message,
        active_messages,
        size,
    )

    if preferred_position is None:
        return False

    message["position"] = preferred_position

    active_messages.append(message)

    broadcast_payload = {
        key: value
        for key, value in message.items()
        if key != "embedding"
    }

    payload = json.dumps(
        broadcast_payload
    )

    await broadcast_message(payload)

    return True

async def process_queue():

    while pending_messages:

        message = pending_messages[0]

        placed = await try_place_message(message)

        if not placed:
            # Board is still full.
            break

        pending_messages.pop(0)

        await broadcast_queue_status()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)

    await websocket.send_text(
        json.dumps({
            "type": "queue_status",
            "count": len(pending_messages),
        })
    )

    try:
        while True:
            raw_message = await websocket.receive_text()

            message = json.loads(raw_message)

            if message.get("type") == "geometry":

                message_id = message["message_id"]

                for active_message in active_messages:

                    if active_message["id"] == message_id:

                        new_size = {
                            "width": message["width"],
                            "height": message["height"],
                        }

                        active_message["size"] = new_size

                        other_messages = [
                            other
                            for other in active_messages
                            if other["id"] != message_id
                        ]

                        if not is_position_valid(
                            active_message["position"],
                            new_size,
                            other_messages,
                        ):

                            most_similar, most_dissimilar = (
                                get_most_similar_and_dissimilar(
                                    active_message["embedding"],
                                    other_messages,
                                )
                            )

                            new_position = get_dynamic_position(
                                most_similar,
                                most_dissimilar,
                                other_messages,
                                new_size,
                            )

                            if new_position is not None:
                                active_message["position"] = new_position
                        break

                continue
            # If something is already waiting,
            # preserve FIFO order.
            if pending_messages:
                pending_messages.append(message)

                await broadcast_queue_status()

                continue

            # Try to display immediately.
            placed = await try_place_message(
                message
            )

            if not placed:
                pending_messages.append(message)

                await broadcast_queue_status()
            """
            #message["created_at"] = time.time()

            #ttl = calculate_ttl(message["text"])

            #message["ttl"] = ttl

            #message["expires_at"] = (
                #message["created_at"] + ttl
            #)

            # Generate semantic embedding.
            #embedding = get_embedding(
                message["text"]
            #)

            #message["embedding"] = embedding


            # Find the strongest semantic attraction
            # and repulsion targets.
            #most_similar, most_dissimilar = (
                #get_most_similar_and_dissimilar(
                   # embedding,
                   # active_messages, ))

            #size = get_message_size(
                message["text"]
            #)

            #message["size"] = size

            #position = get_dynamic_position(
                most_similar,
                most_dissimilar,
                active_messages,
                size,
            #)

            #if position is None:
                # Temporary behavior.
                # Queueing comes next.
                continue

            #message["position"] = position
            #message["size"] = size

            #active_messages.append(message)

            #broadcast_message = {
                #key: value
                #for key, value in message.items()
                #if key != "embedding"
            #}

            #payload = json.dumps(broadcast_message)

            #for client in connected_clients:
             #   await client.send_text(payload)
             """

    except WebSocketDisconnect:
        if websocket in connected_clients:
            connected_clients.remove(websocket)