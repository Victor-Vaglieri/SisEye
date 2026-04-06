# Servidor FastAPI que fornece uma interface web para monitoramento das cameras e controle PTZ.

import os
import sys
import time
import logging
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import cv2

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import CameraStream, PTZController, RTSP_FILE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

if not os.path.exists("static"):
    os.makedirs("static/css", exist_ok=True)
    os.makedirs("static/js", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

RTSP_URLS = []
if os.path.exists(RTSP_FILE):
    with open(RTSP_FILE, "r", encoding="utf-8") as f:
        RTSP_URLS = [line.strip() for line in f if line.strip().startswith("rtsp://")]
else:
    logger.error(f"Arquivo de URLs {RTSP_FILE} nao encontrado.")

logger.info(f"URLs Carregadas: {len(RTSP_URLS)}")

cameras = []
ptz_controller = None

if RTSP_URLS:
    cameras.append(CameraStream(0, RTSP_URLS[0], is_crop=False))
    url_cam2 = RTSP_URLS[1] if len(RTSP_URLS) > 1 else RTSP_URLS[0]
    cameras.append(CameraStream(1, url_cam2, is_crop=True))
    ptz_controller = PTZController(RTSP_URLS[0])
else:
    logger.warning("Nenhuma camera disponivel.")

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def gen_stream(cam_id: int):
    my_cam = next((c for c in cameras if c.id == cam_id), None)
    if not my_cam: return

    while True:
        frame = my_cam.get_frame()
        if frame is None:
            time.sleep(0.1)
            continue
        
        frame = cv2.resize(frame, (640, 360))
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
            
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.04)

@app.get("/video_feed/{id}")
def video_feed(id: int):
    return StreamingResponse(gen_stream(id), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/api/ptz/{command}")
def ptz_control(command: str):
    if not ptz_controller or not ptz_controller.connected:
        return {"status": "error", "msg": "PTZ Off"}
    
    velo = 0.5
    if command == "stop":
        ptz_controller.stop()
    elif command == "up":
        ptz_controller.move(0, velo)
    elif command == "down":
        ptz_controller.move(0, -velo)
    elif command == "left":
        ptz_controller.move(-velo, 0)
    elif command == "right":
        ptz_controller.move(velo, 0)
    
    return {"status": "success"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
