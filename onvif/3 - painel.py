import cv2
import numpy as np
import threading
import time
import os
import sys  # Necessário para o encerramento forçado

# ==========================
# CONFIGURAÇÕES DE REDE (TCP)
# ==========================
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

# ==========================
# CONFIGURAÇÕES VISUAIS
# ==========================
ARQ_RTSP = "rtsp_urls_detalhado.txt"
LARGURA_TELA = 1920
ALTURA_TELA = 1080

# Cores
COR_BG = (20, 20, 20)
COR_BORDA = (60, 60, 60)
COR_TEXTO = (0, 220, 0)
COR_OFFLINE = (50, 0, 0) 

# ==========================
# CLASSE DE CAPTURA
# ==========================
class CameraStream:
    def __init__(self, url, id_cam):
        self.url = url
        self.id = id_cam
        self.cap = None
        self.frame = None
        self.running = True
        self.lock = threading.Lock()
        self.connected = False
        
        # Daemon = True significa: "Se o programa principal fechar, mate essa thread também"
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True 
        self.thread.start()

    def update(self):
        print(f"[CAM {self.id}] Thread iniciada.")
        while self.running:
            if self.cap is None or not self.cap.isOpened():
                try:
                    self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
                    if not self.cap.isOpened():
                        time.sleep(2)
                        continue
                except:
                    time.sleep(2)
                    continue

            ret, frame = self.cap.read()
            if ret:
                self.connected = True
                with self.lock:
                    self.frame = frame
            else:
                self.connected = False
                if self.cap: self.cap.release()
                self.cap = None
                time.sleep(1)

    def get_frame(self):
        with self.lock:
            return self.frame, self.connected

    # Removemos o método STOP com join() que travava tudo.
    # Agora deixamos o sistema operacional matar as threads.

# ==========================
# MAIN
# ==========================
def main():
    print("--- INICIANDO SISEYE (Fechamento Rápido) ---")
    
    urls = []
    if os.path.exists(ARQ_RTSP):
        with open(ARQ_RTSP) as f:
            urls = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    
    cams = [CameraStream(u, i+1) for i, u in enumerate(urls)]
    
    texto_cmd = ""
    luz_on = False
    noite_on = False

    # Layout
    areas = [
        (0, 0, LARGURA_TELA // 2, ALTURA_TELA),
        (LARGURA_TELA // 2, 0, LARGURA_TELA // 2, ALTURA_TELA // 2),
        (LARGURA_TELA // 2, ALTURA_TELA // 2, LARGURA_TELA // 2, ALTURA_TELA // 2)
    ]

    cv2.namedWindow("SisEye", cv2.WINDOW_NORMAL)
    # cv2.setWindowProperty("SisEye", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:
        # Verifica se clicou no X da janela
        try:
            if cv2.getWindowProperty("SisEye", cv2.WND_PROP_VISIBLE) < 1:
                print("Fechando pelo X...")
                break
        except:
            pass

        canvas = np.zeros((ALTURA_TELA, LARGURA_TELA, 3), dtype=np.uint8)
        canvas[:] = COR_BG

        # Desenho (Mesma lógica)
        num_slots_cam = len(areas) - 1 
        for i in range(num_slots_cam):
            x, y, w, h = areas[i]
            if i < len(cams):
                cam = cams[i]
                frame, online = cam.get_frame()
                if online and frame is not None:
                    try:
                        frame_res = cv2.resize(frame, (w, h))
                        canvas[y:y+h, x:x+w] = frame_res
                        cv2.rectangle(canvas, (x, y), (x+w, y+h), (0, 100, 0), 2)
                        cv2.putText(canvas, f"CAM {i+1}", (x+10, y+30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
                    except: pass
                else:
                    cv2.rectangle(canvas, (x, y), (x+w, y+h), COR_OFFLINE, -1)
                    cv2.putText(canvas, f"CAM {i+1}...", (x+10, y+40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (150,150,150), 2)
            else:
                cv2.rectangle(canvas, (x, y), (x+w, y+h), (10, 10, 10), -1)

        # Controle
        cx, cy, cw, ch = areas[-1]
        cv2.rectangle(canvas, (cx, cy), (cx+cw, cy+ch), (15, 15, 15), -1)
        cv2.rectangle(canvas, (cx, cy), (cx+cw, cy+ch), (0, 200, 0), 2)
        
        margem_x, margem_y = cx + 20, cy + 40
        cv2.putText(canvas, "SISEYE CONTROL", (margem_x, margem_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, COR_TEXTO, 2)
        cv2.putText(canvas, f"> {texto_cmd}_", (margem_x, margem_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
        cv2.putText(canvas, f"[1] LUZ:   {'ON' if luz_on else 'OFF'}", (margem_x, margem_y + 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COR_TEXTO, 2)
        cv2.putText(canvas, f"[2] IR:    {'ON' if noite_on else 'OFF'}", (margem_x, margem_y + 140), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COR_TEXTO, 2)

        cv2.imshow("SisEye", canvas)

        # Inputs
        key = cv2.waitKey(20) & 0xFF
        
        if key == 27: # ESC
            print("ESC pressionado. Matando processo...")
            # FECHAMENTO FORÇADO
            cv2.destroyAllWindows()
            os._exit(0) # <--- O SEGREDO ESTÁ AQUI
            
        elif key == 13: # Enter
            cmd = texto_cmd.lower().strip()
            if cmd == "luz": luz_on = not luz_on
            elif cmd == "noite": noite_on = not noite_on
            texto_cmd = ""
        elif key == 8: # Backspace
            texto_cmd = texto_cmd[:-1]
        elif 32 <= key <= 126:
            if len(texto_cmd) < 30: texto_cmd += chr(key)

    # Se saiu pelo X da janela ou break
    cv2.destroyAllWindows()
    os._exit(0)

if __name__ == "__main__":
    main()