# Aplicativo desktop para monitoramento de cameras em tempo real com suporte a zoom digital e controle PTZ.

import os
import sys
import threading
import time
import numpy as np
import cv2
import logging

try:
    import keyboard
except ImportError:
    print("ERRO: Biblioteca 'keyboard' faltando. Rode: pip install keyboard")
    sys.exit()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import CameraStream, PTZController, RTSP_FILE, LARGURA_TELA, ALTURA_TELA, COR_BG, COR_TEXTO, COR_OFFLINE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def aplicar_zoom_digital(frame, zoom_factor):
    if zoom_factor <= 1.0: return frame
    h, w = frame.shape[:2]
    new_w, new_h = int(w / zoom_factor), int(h / zoom_factor)
    x1, y1 = (w - new_w) // 2, (h - new_h) // 2
    cropped = frame[y1:y1+new_h, x1:x1+new_w]
    return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)

def main():
    print("--- SIS EYE: MONITOR DESKTOP ---")
    
    urls = []
    if os.path.exists(RTSP_FILE):
        with open(RTSP_FILE) as f:
            urls = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    
    if not urls:
        logger.error("Nenhuma URL RTSP encontrada. Execute o gerador de RTSP primeiro.")
        return

    cams = [CameraStream(i, url) for i, url in enumerate(urls)]
    ptz = PTZController(urls[0])
    
    zoom_level = 1.0
    VEL_PTZ = 0.5
    
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
            if cv2.getWindowProperty("SisEye", cv2.WND_PROP_VISIBLE) < 1:
                break
            
            moving = False
            if ptz.connected:
                if keyboard.is_pressed('up'): ptz.move(0, VEL_PTZ); moving = True
                elif keyboard.is_pressed('down'): ptz.move(0, -VEL_PTZ); moving = True
                elif keyboard.is_pressed('left'): ptz.move(-VEL_PTZ, 0); moving = True
                elif keyboard.is_pressed('right'): ptz.move(VEL_PTZ, 0); moving = True
                
                if not moving:
                    ptz.stop()

            if keyboard.is_pressed('esc'):
                break

            canvas = np.zeros((ALTURA_TELA, LARGURA_TELA, 3), dtype=np.uint8)
            canvas[:] = COR_BG

            for i, (x, y, w, h) in enumerate(areas):
                if i < len(cams):
                    cam = cams[i]
                    frame = cam.get_frame()
                    
                    if cam.online and frame is not None:
                        try:
                            if i == 0 and zoom_level > 1.0:
                                frame = aplicar_zoom_digital(frame, zoom_level)
                            
                            frame_res = cv2.resize(frame, (w, h))
                            canvas[y:y+h, x:x+w] = frame_res
                            
                            cv2.rectangle(canvas, (x, y), (x+w, y+h), (0, 100, 0), 2)
                            cv2.putText(canvas, f"CAM {i+1}", (x+10, y+30), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        except Exception as e:
                            logger.error(f"Erro ao processar frame da Cam {i+1}: {e}")
                    else:
                        cv2.rectangle(canvas, (x, y), (x+w, y+h), COR_OFFLINE, -1)
                        cv2.putText(canvas, f"CAM {i+1} DESCONECTADA", (x+50, y+h//2), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)
                else:
                    cv2.rectangle(canvas, (x, y), (x+w, y+h), (10, 10, 10), -1)

            cx, cy, cw, ch = areas[-1]
            cv2.rectangle(canvas, (cx, cy), (cx+cw, cy+ch), (0, 200, 0), 2)
            cv2.putText(canvas, "SISEYE DASHBOARD", (cx+20, cy+40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, COR_TEXTO, 2)
            cv2.putText(canvas, "PTZ: Setas | ZOOM: + -", (cx+20, cy+100), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.imshow("SisEye", canvas)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('+'): zoom_level = min(5.0, zoom_level + 0.1)
            elif key == ord('-'): zoom_level = max(1.0, zoom_level - 0.1)

    finally:
        logger.info("Encerrando monitor...")
        for cam in cams:
            cam.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
