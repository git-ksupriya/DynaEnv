import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

connected_clients: list[WebSocket] = []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)

    try:
        while True:
            message = await websocket.receive_text()

            for client in connected_clients:
                await client.send_text(message)

    except WebSocketDisconnect:
        connected_clients.remove(websocket)