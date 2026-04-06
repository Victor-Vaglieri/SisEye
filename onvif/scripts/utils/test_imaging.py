# Utilitario para testar as configuracoes de imagem das cameras, como o filtro IR (Day/Night).

import sys
import os
import time
from onvif import ONVIFCamera
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import ONVIF_USER, ONVIF_PASS, ONVIF_PORT, IP_TESTE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def conectar(ip, port, user, password):
    logger.info(f"Conectando em {ip}...")
    try:
        cam = ONVIFCamera(ip, port, user, password)
        imaging = cam.create_imaging_service()
        media = cam.create_media_service()
        token = media.GetVideoSources()[0].token
        return imaging, token
    except Exception as e:
        logger.error(f"Erro ao conectar: {e}")
        return None, None

def ler_estado(imaging, token):
    try:
        settings = imaging.GetImagingSettings({'VideoSourceToken': token})
        print("\n--- ESTADO ATUAL ---")
        if hasattr(settings, 'IrCutFilter'):
            print(f"Modo Day/Night (IrCutFilter): [{settings.IrCutFilter}]")
        if hasattr(settings, 'Exposure'):
            print(f"Exposicao (Mode): [{settings.Exposure.Mode}]")
        print("-----------------------")
        return settings
    except Exception as e:
        logger.error(f"Erro ao ler configuracoes: {e}")
        return None

def mudar_modo(imaging, token, modo):
    logger.info(f"Tentando mudar IrCutFilter para: {modo}...")
    try:
        request = imaging.create_type('SetImagingSettings')
        request.VideoSourceToken = token
        current = imaging.GetImagingSettings({'VideoSourceToken': token})
        request.ImagingSettings = current
        request.ImagingSettings.IrCutFilter = modo
        imaging.SetImagingSettings(request)
        print("Comando enviado.")
        time.sleep(1)
        ler_estado(imaging, token)
    except Exception as e:
        logger.error(f"Camera rejeitou o comando: {e}")

def main():
    imaging, token = conectar(IP_TESTE, ONVIF_PORT, ONVIF_USER, ONVIF_PASS)
    if not imaging: return

    while True:
        ler_estado(imaging, token)
        print("\nESCOLHA O MODO:")
        print("1 - MODO NOITE (ON)")
        print("2 - MODO DIA (OFF)")
        print("3 - AUTOMATICO (AUTO)")
        print("0 - Sair")
        
        opt = input("Opcao: ")
        if opt == '1': mudar_modo(imaging, token, 'ON')
        elif opt == '2': mudar_modo(imaging, token, 'OFF')
        elif opt == '3': mudar_modo(imaging, token, 'AUTO')
        elif opt == '0': break

if __name__ == "__main__":
    main()
