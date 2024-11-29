import logging

from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

from frontend import paths
from ragagent import RAGAgent
from frontend.server.server import ConnectionManager

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
import asyncio

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from starlette.staticfiles import StaticFiles

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = FastAPI()
app.mount("/static", StaticFiles(directory=paths.static), name="static")

consultant = RAGAgent()


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
    Wrapper to run the tool in a web frontend. Use custom_logger to capture logs
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


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(content=open(paths.static / "index.html", "r").read())

