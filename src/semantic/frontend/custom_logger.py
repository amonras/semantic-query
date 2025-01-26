import logging
import asyncio


async def send_message(websocket, message):
    await websocket.send_json({"type": "log", "payload": message})


class WebSocketHandler(logging.Handler):
    """
    This component is a logging handler that sends log messages to a websocket.
    """
    def __init__(self, websocket, loop):
        super().__init__()
        self.websocket = websocket
        self.loop = loop

    def emit(self, record):
        try:
            log_entry = self.format(record)
            message = {"type": "log", "payload": log_entry}
            # print(f"Sending message: {message}")
            future = asyncio.run_coroutine_threadsafe(self.websocket.send_json(message), self.loop)
            # Wait for the future to complete and raise any exceptions
            future.result()
        except Exception as e:
            print(f"Error in WebSocketHandler.emit: {e}")