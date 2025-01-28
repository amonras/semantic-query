from textwrap import dedent

from fastapi import FastAPI, WebSocket, Request
from typing import Dict
import hashlib
from fastapi import UploadFile, File

from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect

from verdictnet.config import get_config
from verdictnet.etl import get_files
from verdictnet.frontend import paths
from verdictnet.ragagent import RAGAgent
from verdictnet.frontend.server.websocket import Connection
from verdictnet.frontend.server.dto.websocket import ConnectionId, DisplayDocuments
from verdictnet.render.html import HTMLRenderer
from verdictnet.storage.hybrid_storage import HybridStorage

conf = get_config()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Connection] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        # generate a unique id for the connection
        connection_id = hashlib.sha256(str(websocket).encode()).hexdigest()

        # Create a new RAG agent and pass it to the connection
        connection = Connection(
            conn_id=connection_id,
            websocket=websocket,
            rag_agent=RAGAgent(conf)
        )
        self.active_connections[connection_id] = connection
        await self.active_connections[connection_id].send_message(ConnectionId(connection_id=connection_id).to_dict())
        return connection

    def disconnect(self, connection: Connection):
        # remove the connection from the active connections
        del self.active_connections[connection.id]


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

    # Send DisplayDocuments message once the connection is established
    documents = [open(filename, 'r').read() for filename in get_files(conf['storage']['html'], extension='html')]

    storage = HybridStorage.get_hybrid_storage(conf)
    documents = storage.graph_storage.retrieve_by(level='dataset')
    doc_repr = [
        HTMLRenderer.render(
            doc,
            preamble=dedent("""<html lang="es"><head><meta charset="utf-8" /></head>""")
        )
        for doc in documents
    ]
    await connection.send_message(DisplayDocuments(documents=doc_repr).to_dict())

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
