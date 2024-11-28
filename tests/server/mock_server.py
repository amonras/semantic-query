from fastapi import FastAPI, WebSocket
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles

from semantic_pdf import paths

app = FastAPI()
app.mount("/static", StaticFiles(directory=paths.static), name="static")


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(content=open(paths.static / "index.html", "r").read())


@app.websocket("/ws")
async def websocket_connection(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")