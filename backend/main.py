import json
import time

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from backend.spatial import get_position

app = FastAPI()

connected_clients: list[WebSocket] = []


def calculate_ttl(text: str) -> int:
    length = len(text.strip())

    if length <= 5:
        return 5

    if length <= 30:
        return 10

    return 15


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
            message["position"] = get_position(
                message["text"]
            )

            payload = json.dumps(message)

            for client in connected_clients:
                await client.send_text(payload)

    except WebSocketDisconnect:
        if websocket in connected_clients:
            connected_clients.remove(websocket)