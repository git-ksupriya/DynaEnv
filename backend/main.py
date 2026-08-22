import json
import time

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

connected_clients: list[WebSocket] = []

MESSAGE_TTL = 10


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)

    try:
        while True:
            raw_message = await websocket.receive_text()

            message = json.loads(raw_message)

            message["created_at"] = time.time()
            message["expires_at"] = (
                message["created_at"] + MESSAGE_TTL
            )

            payload = json.dumps(message)

            for client in connected_clients:
                await client.send_text(payload)

    except WebSocketDisconnect:
        if websocket in connected_clients:
            connected_clients.remove(websocket)