# Modulo contendo as classes CameraStream para streaming RTSP e PTZController para controle de movimento.

import cv2
import threading
import time
import logging
import re
from onvif import ONVIFCamera
from .config import ONVIF_USER, ONVIF_PASS, ONVIF_PORT, FALLBACK_VIDEO

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CameraStream:
    def __init__(self, camera_id: int, rtsp_url: str, is_crop: bool = False):
        self.id = camera_id
        self.url = rtsp_url
        self.is_crop = is_crop
        self.frame = None
        self.lock = threading.Lock()
        self.online = False
        self.running = True
        
        self.cap = None
        self.fallback_cap = None
        if FALLBACK_VIDEO and hasattr(cv2, 'VideoCapture'):
            self.fallback_cap = cv2.VideoCapture(FALLBACK_VIDEO)

        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()

    def _update_loop(self):
        logger.info(f"Iniciando Camera {self.id} (RTSP: {self.url[:30]}...)")
        self.cap = cv2.VideoCapture(self.url)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'H264'))

        while self.running:
            if self.cap and self.cap.isOpened():
                success, img = self.cap.read()
                if success:
                    self.online = True
                    if self.is_crop:
                        h, w, _ = img.shape
                        img = img[0:int(h/2), 0:w]
                    
                    with self.lock:
                        self.frame = img
                else:
                    self.online = False
                    self.cap.release()
                    self._handle_reconnect()
            else:
                self.online = False
                self._handle_offline_display()
                time.sleep(1)
                self.cap = cv2.VideoCapture(self.url)

    def _handle_reconnect(self):
        logger.warning(f"Camera {self.id} desconectada. Tentando reconectar...")
        time.sleep(5)
        self.cap = cv2.VideoCapture(self.url)

    def _handle_offline_display(self):
        if self.fallback_cap and self.fallback_cap.isOpened():
            success, img = self.fallback_cap.read()
            if not success:
                self.fallback_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                success, img = self.fallback_cap.read()
            
            if success:
                cv2.putText(img, "CONEXAO PERDIDA...", (50, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                if self.is_crop:
                    img = cv2.resize(img, (640, 180))
                else:
                    img = cv2.resize(img, (640, 360))
                with self.lock:
                    self.frame = img

    def get_frame(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        if self.fallback_cap:
            self.fallback_cap.release()

class PTZController:
    def __init__(self, rtsp_url: str):
        self.connected = False
        self.ptz = None
        self.token = None
        self.request = None
        self.ip = self._extract_ip(rtsp_url)
        
        if self.ip:
            threading.Thread(target=self._setup_ptz, daemon=True).start()

    def _extract_ip(self, url):
        match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", url)
        if match:
            return match.group(1)
        return None

    def _setup_ptz(self):
        try:
            logger.info(f"Configurando PTZ para IP: {self.ip}")
            cam = ONVIFCamera(self.ip, ONVIF_PORT, ONVIF_USER, ONVIF_PASS)
            media = cam.create_media_service()
            self.ptz = cam.create_ptz_service()
            profile = media.GetProfiles()[0]
            self.token = profile.token
            self.request = self.ptz.create_type('ContinuousMove')
            self.request.ProfileToken = self.token
            self.connected = True
            logger.info(f"PTZ pronto para {self.ip}")
        except Exception as e:
            logger.error(f"Erro ao configurar PTZ: {e}")

    def move(self, x: float, y: float, zoom: float = 0):
        if not self.connected: return
        try:
            self.request.Velocity = {'PanTilt': {'x': x, 'y': y}, 'Zoom': {'x': zoom}}
            self.ptz.ContinuousMove(self.request)
        except Exception as e:
            logger.error(f"Erro no comando PTZ: {e}")

    def stop(self):
        if not self.connected: return
        try:
            self.ptz.Stop({'ProfileToken': self.token, 'PanTilt': True, 'Zoom': True})
        except Exception as e:
            logger.error(f"Erro ao parar PTZ: {e}")
