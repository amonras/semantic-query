import hashlib
import os
from io import BytesIO

from PyPDF2 import PdfFileReader, PdfFileWriter
from starlette.websockets import WebSocket

from semantic_pdf.paths import uploads
from semantic_pdf.server.dto.websocket import FileUploaded


class Connection:
    """
    A class to handle the connection between the server and the client.
    """
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.message_count = 0
        self.last_message = None
        self.uploaded_files = {}

    async def send_message(self, message: dict):
        await self.websocket.send_json(message)
        self.message_count += 1

    async def receive_message(self):
        message = await self.websocket.receive_json()
        self.message_count += 1
        self.last_message = message
        return message

    def get_state_hash(self):
        return hashlib.sha256(str(self.__dict__).encode()).hexdigest()

    async def upload(self, file):
        """
        Save file to the server and update the uploaded_files attribute.
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