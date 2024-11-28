import logging

from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect
from semantic_pdf.custom_logger import WebSocketHandler
import asyncio

from semantic_pdf.server.websocket import ConnectionManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = FastAPI()

manager = ConnectionManager()


@app.on_event("startup")
async def startup_event():
    # Create a new WebSocket connection
    websocket = WebSocket()
    await manager.connect(websocket)

    # Initialize the WebSocketHandler with the WebSocket connection
    loop = asyncio.get_running_loop()
    ws_handler = WebSocketHandler(websocket, loop)
    logger.addHandler(ws_handler)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # process data
    except WebSocketDisconnect:
        await manager.disconnect(websocket)

import logging
import os
import json
import asyncio
import threading
from pathlib import Path

from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from werkzeug.utils import secure_filename

from semantic_pdf import paths
from semantic_pdf.custom_logger import WebSocketHandler
from semantic_pdf.consultant import Consultant
from semantic_pdf.splitters.article_splitter import ArticleSplitter


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

UPLOAD_FOLDER = '/Users/amonras/Projects/semantic_query/docs'
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

app = FastAPI()
app.mount("/static", StaticFiles(directory=paths.static), name="static")

consultant = Consultant(splitter=ArticleSplitter(title_pattern=r"Art\. \d+ - .*"))


def run_function(args, logger, result_container):
    """
    Run the function in a separate thread to avoid blocking the main thread.
    :param args: Arguments to pass to the function
    :param logger: Logger object to log messages and send them to the client
    :param result_container: Dictionary to store the result of the function
    """
    result_container["result"] = web_runner(args, custom_logger=logger)


def web_runner(kwargs, custom_logger: logging.Handler = None):
    """
    Wrapper to run the tool in a web server. Use custom_logger to capture logs
    :kwargs: args to pass to the scraper
    :param custom_logger:
    :return:
    """
    logger.addHandler(custom_logger)

    if kwargs["query"] == "":
        kwargs["query"] = None

    query = kwargs["query"]
    logger.info("Running query: %s", query)
    docs = consultant.query(query)

    return docs


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(content=open(paths.static / "index.html", "r").read())


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Invalid file type")
    if file.filename == '':
        raise HTTPException(status_code=400, detail="No selected file")
    filename = secure_filename(file.filename)
    file_location = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    consultant.upload_file(Path(file_location))
    return {"detail": "File uploaded successfully"}
