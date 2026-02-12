import cv2
import time
import os
import threading
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from onvif import ONVIFCamera
from dotenv import load_dotenv


load_dotenv()
app = FastAPI()


if not os.path.exists("templates"):
    os.makedirs("templates")
    print("⚠️ Pasta 'templates' criada. Certifique-se de que o index.html está lá.")

templates = Jinja2Templates(directory="templates")

ONVIF_USER = os.getenv("ONVIF_USER", "admin")
ONVIF_PASS = os.getenv("ONVIF_PASS", "admin")
ONVIF_PORT = 8899
ARQUIVO_FALLBACK = "loading.mp4" 


RTSP_URLS = []
if os.path.exists("rtsp_urls_detalhado.txt"):
    with open("rtsp_urls_detalhado.txt", "r", encoding="utf-8") as f:
        
        RTSP_URLS = [line.strip() for line in f if line.strip().startswith("rtsp://")]
else:
    print("❌ ERRO: Arquivo de URLs não encontrado.")

print(f"✅ URLs Carregadas: {len(RTSP_URLS)}")


class SmartCamera:
    def __init__(self, id, rtsp_url, is_crop=False):
        self.id = id
        self.url = rtsp_url
        self.is_crop = is_crop
        self.frame = None
        self.lock = threading.Lock()
        
        
        self.online = False
        self.trying_reconnect = False
        self.new_cap_available = None
        
        
        if os.path.exists(ARQUIVO_FALLBACK):
            self.cap_fallback = cv2.VideoCapture(ARQUIVO_FALLBACK)
        else:
            self.cap_fallback = None
            print(f"⚠️ Aviso: '{ARQUIVO_FALLBACK}' não encontrado. A tela ficará preta se cair.")

        
        threading.Thread(target=self.update_loop, daemon=True).start()

    def update_loop(self):
        print(f"📷 Iniciando Câmera {self.id}...")
        cap = cv2.VideoCapture(self.url)
        
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'H264'))
        
        while True:
            if cap.isOpened():
                success, img = cap.read()
                if success:
                    self.online = True
                    
                    if self.is_crop:
                        h, w, _ = img.shape
                        img = img[0:int(h/2), 0:w]
                    
                    with self.lock:
                        self.frame = img
                else:
                    self.online = False
                    cap.release()
            else:
                self.online = False
                self.handle_offline()
                
                if self.new_cap_available:
                    cap = self.new_cap_available
                    self.new_cap_available = None

    def handle_offline(self):
        
        if self.cap_fallback is None:
            time.sleep(1)
            return

        success, img = self.cap_fallback.read()
        if not success:
            self.cap_fallback.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, img = self.cap_fallback.read()
            
        if success:
            
            cv2.putText(img, "CONEXAO PERDIDA...", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            if self.is_crop:
                img = cv2.resize(img, (640, 180))
            else:
                img = cv2.resize(img, (640, 360))

            with self.lock:
                self.frame = img
        
        
        if not self.trying_reconnect:
            self.trying_reconnect = True
            threading.Thread(target=self.reconnect_worker, daemon=True).start()
        
        time.sleep(0.03)

    def reconnect_worker(self):
        time.sleep(5) 
        try:
            
            temp_cap = cv2.VideoCapture(self.url)
            if temp_cap.isOpened():
                ret, _ = temp_cap.read()
                if ret:
                    self.new_cap_available = temp_cap
                    print(f"✅ Câmera {self.id} RECONECTADA!")
                else:
                    temp_cap.release()
        except:
            pass
        self.trying_reconnect = False


cameras = []
if RTSP_URLS:
    cameras.append(SmartCamera(0, RTSP_URLS[0], is_crop=False))
    
    url_cam2 = RTSP_URLS[1] if len(RTSP_URLS) > 1 else RTSP_URLS[0]
    cameras.append(SmartCamera(1, url_cam2, is_crop=True))
else:
    print("⚠️ Nenhuma câmera iniciada (Lista vazia).")


ptz_service = None
ptz_token = None

def setup_ptz():
    global ptz_service, ptz_token
    if not RTSP_URLS: return
    
    url = RTSP_URLS[0]
    print(f"🔧 Configurando PTZ usando URL: {url[:25]}...") 
    
    try:
        
        if "@" in url:
            ip = url.split("@")[1].split(":")[0]
        else:
            ip = url.split("//")[-1].split(":")[0]
            if "/" in ip: ip = ip.split("/")[0]

        print(f"🌍 IP Detectado para PTZ: {ip}")
        cam = ONVIFCamera(ip, ONVIF_PORT, ONVIF_USER, ONVIF_PASS)
        media = cam.create_media_service()
        ptz_service = cam.create_ptz_service()
        ptz_token = media.GetProfiles()[0].token
        print("✅ Serviço PTZ Ativo!")
    except Exception as e:
        print(f"❌ Erro ao iniciar PTZ: {e}")

threading.Thread(target=setup_ptz).start()


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def gen_stream(cam_id):
    my_cam = next((c for c in cameras if c.id == cam_id), None)
    if not my_cam: return

    while True:
        with my_cam.lock:
            if my_cam.frame is None:
                time.sleep(0.1)
                continue
            img = my_cam.frame.copy()
        
        img = cv2.resize(img, (640, 360))
        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.04) 

@app.get("/video_feed/{id}")
def video_feed(id: int):
    return StreamingResponse(gen_stream(id), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/api/ptz/{command}")
def ptz_control(command: str):
    global ptz_service
    if not ptz_service: return {"status": "error", "msg": "PTZ Off"}
    try:
        req = ptz_service.create_type('ContinuousMove')
        req.ProfileToken = ptz_token
        velo = 0.5
        if command == "stop": ptz_service.Stop({'ProfileToken': ptz_token, 'PanTilt': True, 'Zoom': True})
        else:
            if command == "up": req.Velocity = {'PanTilt': {'x': 0, 'y': velo}}
            elif command == "down": req.Velocity = {'PanTilt': {'x': 0, 'y': -velo}}
            elif command == "left": req.Velocity = {'PanTilt': {'x': -velo, 'y': 0}}
            elif command == "right": req.Velocity = {'PanTilt': {'x': velo, 'y': 0}}
            ptz_service.ContinuousMove(req)
        return {"status": "success"}
    except Exception as e: return {"status": "error", "msg": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)