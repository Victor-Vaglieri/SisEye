import pygame
import cv2
import numpy as np
import math

# ==========================
# CONFIGURAÇÕES
# ==========================
ARQ_RTSP = "rtsp_urls.txt"
LARGURA = 1280
ALTURA = 800
FPS = 30

BG_COR = (20, 20, 20)
BORDA_COR = (60, 60, 60)
TXT_COR = (0, 220, 0)

# ==========================
# LÊ STREAMS
# ==========================
with open(ARQ_RTSP) as f:
    urls = [l.strip() for l in f if l.strip()]

# Último slot é comandos
num_slots = len(urls) + 1
grid_n = math.ceil(math.sqrt(num_slots))

# ==========================
# ABRE CAMERAS
# ==========================
caps = [cv2.VideoCapture(u) for u in urls]

# ==========================
# PYGAME INIT
# ==========================
pygame.init()
screen = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Painel de Vigilância")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 18)

# ==========================
# ESTADOS
# ==========================
texto_cmd = ""
luz_on = False
noite_on = False

pan = 0
tilt = 0
cam_movel = 0  # índice da câmera móvel

# ==========================
# FUNÇÕES
# ==========================
def draw_text(txt, x, y):
    img = font.render(txt, True, TXT_COR)
    screen.blit(img, (x, y))

def frame_para_surface(frame, w, h):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (w, h))
    return pygame.surfarray.make_surface(frame.swapaxes(0, 1))

# ==========================
# LOOP PRINCIPAL
# ==========================
running = True
while running:
    clock.tick(FPS)
    screen.fill(BG_COR)

    slot_w = LARGURA // grid_n
    slot_h = ALTURA // grid_n

    # ======================
    # DESENHA CAMERAS
    # ======================
    for i, cap in enumerate(caps):
        r, frame = cap.read()
        if not r:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            r, frame = cap.read()
            if not r:
                continue

        x = (i % grid_n) * slot_w
        y = (i // grid_n) * slot_h

        surf = frame_para_surface(frame, slot_w, slot_h)
        screen.blit(surf, (x, y))
        pygame.draw.rect(screen, BORDA_COR, (x, y, slot_w, slot_h), 1)

        draw_text(f"CAM {i+1}", x + 5, y + 5)

    # ======================
    # SLOT DE COMANDOS
    # ======================
    cmd_idx = num_slots - 1
    x = (cmd_idx % grid_n) * slot_w
    y = (cmd_idx // grid_n) * slot_h

    pygame.draw.rect(screen, (10, 10, 10), (x, y, slot_w, slot_h))
    pygame.draw.rect(screen, (0, 180, 0), (x, y, slot_w, slot_h), 2)

    draw_text("COMANDOS", x + 10, y + 10)
    draw_text(f"> {texto_cmd}", x + 10, y + 40)

    draw_text("Comandos disponíveis:", x + 10, y + 80)
    draw_text("luz   - liga/desliga luzes", x + 10, y + 110)
    draw_text("noite - liga/desliga IR", x + 10, y + 140)
    draw_text("Setas: mover câmera", x + 10, y + 170)

    draw_text(f"Luz: {'ON' if luz_on else 'OFF'}", x + 10, y + 210)
    draw_text(f"Noite: {'ON' if noite_on else 'OFF'}", x + 10, y + 240)

    # ======================
    # EVENTOS
    # ======================
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                running = False

            elif e.key == pygame.K_RETURN:
                cmd = texto_cmd.lower().strip()

                if cmd == "luz":
                    luz_on = not luz_on
                    print("Luz:", luz_on)

                elif cmd == "noite":
                    noite_on = not noite_on
                    print("Visão noturna:", noite_on)

                texto_cmd = ""

            elif e.key == pygame.K_BACKSPACE:
                texto_cmd = texto_cmd[:-1]

            elif e.key in (pygame.K_UP, pygame.K_DOWN,
                           pygame.K_LEFT, pygame.K_RIGHT):
                if e.key == pygame.K_LEFT:
                    pan -= 1
                elif e.key == pygame.K_RIGHT:
                    pan += 1
                elif e.key == pygame.K_UP:
                    tilt += 1
                elif e.key == pygame.K_DOWN:
                    tilt -= 1

                print(f"PTZ -> Pan:{pan} Tilt:{tilt}")

            else:
                if e.unicode.isprintable():
                    texto_cmd += e.unicode

    pygame.display.flip()

# ==========================
# FINALIZA
# ==========================
for c in caps:
    c.release()
pygame.quit()
