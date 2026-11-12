from pathlib import Path

import cv2
import numpy as np

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from gesture_engine import GestureEngine


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"


app = FastAPI()


# Makes CSS, JavaScript and audio available to the browser
app.mount(
    "/static",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="static"
)


@app.get("/")
def home():
    return FileResponse(
        str(FRONTEND_DIR / "index.html")
    )


@app.get("/health")
def health():
    return {"status": "alive"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    engine = GestureEngine()

    print("Browser connected")

    try:

        while True:

            image_bytes = await websocket.receive_bytes()

            image_array = np.frombuffer(
                image_bytes,
                dtype=np.uint8
            )

            frame = cv2.imdecode(
                image_array,
                cv2.IMREAD_COLOR
            )

            if frame is None:
                await websocket.send_text("decode_failed")
                continue

            gesture = engine.process(frame)
            await websocket.send_text(gesture)

    except WebSocketDisconnect:
        print("Browser disconnected")
        