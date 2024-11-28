from fastapi import FastAPI, WebSocket, Request
from typing import Dict
import hashlib
from fastapi import UploadFile, File

from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect

from semantic_pdf import paths
from semantic_pdf.server.connection import Connection
from semantic_pdf.server.dto.websocket import ConnectionId


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Connection] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        # generate a unique id for the connection
        connection_id = hashlib.sha256(str(websocket).encode()).hexdigest()
        connection = Connection(websocket)
        self.active_connections[connection_id] = connection
        await self.active_connections[connection_id].send_message(ConnectionId(connection_id=connection_id).to_dict())
        return connection

    def disconnect(self, connection: Connection):
        # remove the connection from the active connections
        for connection_id, con in self.active_connections.items():
            if connection == con:
                del self.active_connections[connection_id]
                break


app = FastAPI()
app.mount("/static", StaticFiles(directory=paths.static), name="static")
app.mount("/templates", StaticFiles(directory=paths.templates), name="templates")

manager = ConnectionManager()


@app.get("/")
async def home():
    return HTMLResponse(content=open(paths.templates / "index.html", "r").read())


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


@app.post("/upload")
async def upload(request: Request, file: UploadFile = File(...)):
    print(request.headers)
    print(file)
    # get the connection id from the header
    connection_id = request.headers["Connection-ID"]
    connection = manager.active_connections[connection_id]
    file_path = await connection.upload(file)

    return {"message": f"File uploaded successfully to {file_path}"}


def main():
    import uvicorn
    uvicorn.run(app)


if __name__ == "__main__":
    main()