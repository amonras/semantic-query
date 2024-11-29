import hashlib
import os
from io import BytesIO

from PyPDF2 import PdfFileReader
from starlette.websockets import WebSocket

from frontend.paths import uploads
from ragagent import RAGAgent
from frontend.server.dto.websocket import WebSocketMessage, ChatQueryMessage, FileUploaded, ChatResponseMessage, \
    UnfoldNodes


#
# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: List[WebSocket] = []
#
#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections.append(websocket)
#
#     async def disconnect(self, websocket: WebSocket):
#         self.active_connections.remove(websocket)
#
#     async def send_message(self, message: str, websocket: WebSocket):
#         await websocket.send_text(message)


class Connection:
    """
    A class to handle the connection between the frontend and the client.

    The Connection class is responsible for handling the communication between the frontend and the client. It provides
    an interface to send and receive messages, upload files, and serve files to the client.

    Messages are passed as WebSocketMessage objects. The Connection handles the serialization and deserialization of
    those messages
    """

    def __init__(self, conn_id: str, websocket: WebSocket, rag_agent: RAGAgent):
        self.id = conn_id
        self.rag_agent = rag_agent
        self.websocket = websocket
        self.message_count = 0
        self.last_message = None
        self.uploaded_files = {}

    async def send_message(self, message: dict):
        print(message)
        await self.websocket.send_json(message)
        self.message_count += 1

    async def receive_message(self):
        message = await self.websocket.receive_json()
        self.message_count += 1
        self.last_message = message
        await self.handle_message(WebSocketMessage.from_dict(message))
        return message

    async def handle_message(self, msg: WebSocketMessage):
        if isinstance(msg, ChatQueryMessage):
            print(msg.message)
            response = self.rag_agent.query(msg.message)
            nodes_uuids = [n['data-uuid'] for metadata in response['metadatas'] for n in metadata]
            print("Sending response to websocket client")
            await self.send_message(
                UnfoldNodes(node_uuids=nodes_uuids).to_dict()
            )
            print("Response sent")
        else:
            pass

    def get_state_hash(self):
        return hashlib.sha256(str(self.__dict__).encode()).hexdigest()

    async def upload(self, file):
        """
        Save file to the frontend and update the uploaded_files attribute.
        :param file:
        :return:
        """
        file_path = os.path.join(uploads, file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        self.uploaded_files[file.filename] = file_path
        await self.send_message(FileUploaded(filename=file.filename).to_dict())
        return file_path

    def serve_file(self, filename, format="pdf"):
        """
        Serve a file to the client.
        :param file_path:
        :param format: bytes, pdf or html
        :return:
        """
        with open(os.path.join(uploads, filename), "rb") as f:
            file_bytes = f.read()
            if format == "bytes":
                return file_bytes
            elif format == "pdf":
                pdf = PdfFileReader(BytesIO(file_bytes))
                return pdf
            elif format == "html":
                return f"<html><body><pre>{file_bytes.decode()}</pre></body></html>"
