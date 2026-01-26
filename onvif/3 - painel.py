import cv2
import numpy as np
import threading
import time
import os
import sys
import re
from onvif import ONVIFCamera
from dotenv import load_dotenv


try:
    import keyboard
except ImportError:
    print("ERRO: Biblioteca 'keyboard' faltando. Rode: pip install keyboard")
    sys.exit()


AUDIO_RECV_AVAILABLE = False
try:
    from ffpyplayer.player import MediaPlayer
    AUDIO_RECV_AVAILABLE = True
except ImportError:
    print("[AVISO] 'ffpyplayer' ausente. Áudio desativado.")




os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
ARQ_RTSP = "rtsp_urls_detalhado.txt"
LARGURA_TELA = 1920
ALTURA_TELA = 1080

ONVIF_USER = os.getenv("ONVIF_USER") or "admin"
ONVIF_PASS = os.getenv("ONVIF_PASS") or "admin"
ONVIF_PORT = os.getenv("ONVIF_PORT") or 8899

COR_BG = (20, 20, 20)
COR_TEXTO = (0, 220, 0)
COR_OFFLINE = (50, 0, 0) 




class CameraStream:
    def __init__(self, url, id_cam):
        self.url = url
        self.id = id_cam
        self.cap = None
        self.frame = None
        self.running = True
        self.connected = False
        self.lock = threading.Lock()
        
        
        self.thread = threading.Thread(target=self.update, args=(), daemon=True)
        self.thread.start()

    def update(self):
        while self.running:
            
            if self.cap is None or not self.cap.isOpened():
                try:
                    
                    self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
                    
                    if not self.cap.isOpened():
                        
                        time.sleep(3)
                        continue
                        
                    
                except:
                    time.sleep(3)
                    continue

            
            ret, frame = self.cap.read()
            
            if ret:
                self.connected = True
                with self.lock: self.frame = frame
            else:
                
                self.connected = False
                if self.cap: self.cap.release()
                self.cap = None
                
                time.sleep(1)

    def get_frame(self):
        with self.lock: return self.frame, self.connected




class AudioPlayer:
    def __init__(self, rtsp_url):
        self.player = None
        self.is_muted = False
        self.url = rtsp_url
        self.restart_needed = False
        
        if AUDIO_RECV_AVAILABLE:
            self._start_player()

    def _start_player(self):
        ff_opts = {'rtsp_transport': 'tcp', 'allowed_media_types': 'audio', 'analyzeduration': '50000'}
        try:
            self.player = MediaPlayer(self.url, ff_opts=ff_opts)
            self.player.set_volume(1.0 if not self.is_muted else 0.0)
        except: pass

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        if self.player:
            try: self.player.set_volume(0.0 if self.is_muted else 1.0)
            except: pass
        return self.is_muted

    def update(self):
        if self.player:
            try: 
                _, val = self.player.get_frame()
                if val == 'eof': self.restart_needed = True 
            except: pass
        
        if self.restart_needed:
            self.stop()
            self._start_player()
            self.restart_needed = False

    def stop(self):
        if self.player: 
            try: self.player.close_player()
            except: pass
            self.player = None




class CameraController:
    def __init__(self, rtsp_url):
        self.connected = False
        self.ptz = None
        self.request_ptz = None
        self.is_moving = False
        self.last_move_cmd = (0, 0)
        
        match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", rtsp_url)
        if match:
            self.ip = match.group(1)
            self.user = ONVIF_USER
            self.password = ONVIF_PASS
            threading.Thread(target=self._conectar, daemon=True).start()

    def _conectar(self):
        try:
            cam = ONVIFCamera(self.ip, ONVIF_PORT, self.user, self.password)
            media = cam.create_media_service()
            self.ptz = cam.create_ptz_service()
            profile = media.GetProfiles()[0]
            self.token = profile.token
            self.request_ptz = self.ptz.create_type('ContinuousMove')
            self.request_ptz.ProfileToken = self.token
            self.request_ptz.Velocity = self.ptz.GetStatus({'ProfileToken': self.token}).Position
            self.connected = True
            print(f"[ONVIF] PTZ Pronto!")
        except Exception as e: print(f"[ERRO PTZ] {e}")

    def iniciar_movimento(self, x, y):
        if not self.connected: return
        if self.is_moving and self.last_move_cmd == (x, y): return
        def _envia():
            try:
                self.request_ptz.Velocity.PanTilt.x = x
                self.request_ptz.Velocity.PanTilt.y = y
                self.ptz.ContinuousMove(self.request_ptz)
            except: pass
        self.is_moving = True
        self.last_move_cmd = (x, y)
        threading.Thread(target=_envia, daemon=True).start()

    def parar_movimento(self):
        if not self.connected or not self.is_moving: return
        def _envia_stop():
            try: self.ptz.Stop({'ProfileToken': self.token, 'PanTilt': True, 'Zoom': True})
            except: pass
        self.is_moving = False
        self.last_move_cmd = (0, 0)
        threading.Thread(target=_envia_stop, daemon=True).start()

def aplicar_zoom_digital(frame, zoom_factor):
    if zoom_factor <= 1.0: return frame
    h, w = frame.shape[:2]
    new_w = int(w / zoom_factor)
    new_h = int(h / zoom_factor)
    x1 = (w - new_w) // 2
    y1 = (h - new_h) // 2
    cropped = frame[y1:y1+new_h, x1:x1+new_w]
    return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)




def main():
    print("--- SISEYE (ROBUSTO) ---")
    
    urls = []
    if os.path.exists(ARQ_RTSP):
        with open(ARQ_RTSP) as f:
            urls = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    if not urls: return

    
    cams = [CameraStream(u, i+1) for i, u in enumerate(urls)]
    
    
    control = CameraController(urls[0]) 
    audio_player = AudioPlayer(urls[0])
    
    zoom_level = 1.0
    VELOCIDADE_PTZ = 0.5
    
    
    areas = [
        (0, 0, LARGURA_TELA // 2, ALTURA_TELA),
        (LARGURA_TELA // 2, 0, LARGURA_TELA // 2, ALTURA_TELA // 2),
        (LARGURA_TELA // 2, ALTURA_TELA // 2, LARGURA_TELA // 2, ALTURA_TELA // 2)
    ]

    cv2.namedWindow("SisEye", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("SisEye", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    running = True
    try:
        while running:
            try:
                if cv2.getWindowProperty("SisEye", cv2.WND_PROP_VISIBLE) < 1: running = False; break
            except: pass
            
            
            moveu_ptz = False
            if keyboard.is_pressed('up'): control.iniciar_movimento(0, VELOCIDADE_PTZ); moveu_ptz = True
            elif keyboard.is_pressed('down'): control.iniciar_movimento(0, -VELOCIDADE_PTZ); moveu_ptz = True
            elif keyboard.is_pressed('left'): control.iniciar_movimento(-VELOCIDADE_PTZ, 0); moveu_ptz = True
            elif keyboard.is_pressed('right'): control.iniciar_movimento(VELOCIDADE_PTZ, 0); moveu_ptz = True
            
            if not moveu_ptz: control.parar_movimento()

            if keyboard.is_pressed('esc'): running = False; break

            
            if audio_player: audio_player.update()
            
            canvas = np.zeros((ALTURA_TELA, LARGURA_TELA, 3), dtype=np.uint8)
            canvas[:] = COR_BG

            for i in range(len(areas)-1):
                x, y, w, h = areas[i]
                if i < len(cams):
                    cam = cams[i]
                    frame, online = cam.get_frame()
                    
                    if online and frame is not None:
                        try:
                            
                            if i == 0:
                                if zoom_level > 1.0: frame = aplicar_zoom_digital(frame, zoom_level)
                                frame_res = cv2.resize(frame, (w, h))
                                
                            
                            elif i == 1:
                                h_src, w_src = frame.shape[:2]
                                frame_cropped = frame[0 : h_src // 2, 0 : w_src] 
                                frame_res = cv2.resize(frame_cropped, (w, h))
                                
                            
                            else:
                                frame_res = cv2.resize(frame, (w, h))

                            canvas[y:y+h, x:x+w] = frame_res
                            cv2.rectangle(canvas, (x, y), (x+w, y+h), (0, 100, 0), 2)
                            
                            label = f"CAM {i+1}"
                            if i == 1: label += " (CROP)"
                            cv2.putText(canvas, label, (x+10, y+30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
                        except: pass
                    else:
                        
                        cv2.rectangle(canvas, (x, y), (x+w, y+h), COR_OFFLINE, -1)
                        cv2.putText(canvas, f"CAM {i+1} CONECTANDO...", (x+w//2 - 150, y+h//2), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)
                else:
                    cv2.rectangle(canvas, (x, y), (x+w, y+h), (10, 10, 10), -1)

            
            cx, cy, cw, ch = areas[-1]
            cv2.rectangle(canvas, (cx, cy), (cx+cw, cy+ch), (15, 15, 15), -1)
            cv2.rectangle(canvas, (cx, cy), (cx+cw, cy+ch), (0, 200, 0), 2)
            
            mx, my = cx + 20, cy + 40
            cv2.putText(canvas, "SISEYE CONTROL", (mx, my), cv2.FONT_HERSHEY_SIMPLEX, 0.8, COR_TEXTO, 2)
            cv2.putText(canvas, "PTZ: Setas | ZOOM: < >", (mx, my + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            status_audio = "OFF"
            cor_audio = (50, 50, 50)
            if AUDIO_RECV_AVAILABLE:
                status_audio = "MUDO (F1)" if audio_player.is_muted else "OUVINDO (F1)"
                cor_audio = (0, 0, 255) if audio_player.is_muted else (0, 255, 0)
            cv2.putText(canvas, f"AUDIO CAM 1: {status_audio}", (mx, my + 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor_audio, 2)

            cv2.imshow("SisEye", canvas)
            
            full_key = cv2.waitKeyEx(1)
            key_char = full_key & 0xFF 
            if full_key != -1:
                if full_key == 7340032: audio_player.toggle_mute()
                elif key_char == 62 or key_char == 46: zoom_level = min(5.0, zoom_level + 0.1)
                elif key_char == 60 or key_char == 44: zoom_level = max(1.0, zoom_level - 0.1)

    except Exception as e:
        print(f"\n[CRASH] {e}")

    finally:
        print("\n--- Encerrando... ---")
        if control: control.parar_movimento()
        if audio_player: audio_player.stop()
        cv2.destroyAllWindows()
        os._exit(0)

if __name__ == "__main__":
    main()