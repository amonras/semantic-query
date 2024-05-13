from fastapi import FastAPI, WebSocket
from typing import List
import hashlib

from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect

from semantic import paths


class Connection:
    """
    A class to handle the connection between the server and the client.
    """
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.message_count = 0
        self.last_message = None

    async def send_message(self, message: str):
        await self.websocket.send_text(message)
        self.message_count += 1

    async def receive_message(self):
        message = await self.websocket.receive_text()
        self.message_count += 1
        self.last_message = message
        return message

    def get_state_hash(self):
        return hashlib.sha256(str(self.__dict__).encode()).hexdigest()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[Connection] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        connection = Connection(websocket)
        self.active_connections.append(connection)
        return connection

    def disconnect(self, connection: Connection):
        self.active_connections.remove(connection)


app = FastAPI()
app.mount("/static", StaticFiles(directory=paths.static), name="static")
app.mount("/templates", StaticFiles(directory=paths.templates), name="templates")

manager = ConnectionManager()


@app.get("/")
async def home():
    return HTMLResponse(content=open(paths.templates / "websocket_test.html", "r").read())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    connection = await manager.connect(websocket)
    try:
        while True:
            try:
                await connection.receive_message()
                await connection.send_message(f"Message count: {connection.message_count}")
                await connection.send_message(f"Last message: {connection.last_message}")
                await connection.send_message(f"State hash: {connection.get_state_hash()}")
            except WebSocketDisconnect:
                manager.disconnect(connection)
                break
    except Exception as e:
        manager.disconnect(connection)
        raise e
