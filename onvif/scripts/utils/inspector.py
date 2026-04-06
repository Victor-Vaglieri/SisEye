# Utilitario para inspecionar os comandos disponiveis e informacoes de hardware das cameras ONVIF.

import sys
import os
import re
from onvif import ONVIFCamera
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import CAMERAS_FILE, ONVIF_USER, ONVIF_PASS, ONVIF_PORT

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ler_arquivo_cameras(arquivo):
    alvos = []
    if not os.path.exists(arquivo):
        logger.error(f"Arquivo '{arquivo}' nao encontrado.")
        return []

    with open(arquivo, "r", encoding="utf-8") as f:
        for linha in f:
            match = re.search(r"IP:\s*([\d\.]+)(?::(\d+))?", linha)
            if match:
                ip = match.group(1)
                porta = int(match.group(2)) if match.group(2) else ONVIF_PORT
                alvos.append((ip, porta))
    return alvos

def listar_comandos(ip, porta, user, senha):
    print("\n" + "="*60)
    print(f"CONECTANDO EM: {ip}:{porta}")
    print("="*60)
    
    try:
        cam = ONVIFCamera(ip, porta, user, senha)
        resp = cam.devicemgmt.GetDeviceInformation()
        print(f"SUCESSO! Hardware identificado:")
        print(f"   Fabricante: {resp.Manufacturer}")
        print(f"   Modelo:     {resp.Model}")
        print(f"   Firmware:   {resp.FirmwareVersion}")

        servicos = [
            ("PTZ", cam.create_ptz_service()),
            ("IMAGING", cam.create_imaging_service()),
            ("MEDIA", cam.create_media_service()),
            ("DEVICE", cam.devicemgmt)
        ]

        for nome, obj in servicos:
            print(f"\n   [{nome}]")
            try:
                if hasattr(obj, 'zeep_client'):
                    ops = sorted(list(obj.zeep_client.service._operations.keys()))
                    for op in ops:
                        print(f"      {op}")
            except Exception:
                print("      Servico nao suportado.")
    except Exception as e:
        logger.error(f"Falha ao conectar em {ip}: {e}")

def main():
    print("--- SIS EYE: INSPETOR DE COMANDOS ---")
    lista = ler_arquivo_cameras(CAMERAS_FILE)
    if not lista: return

    for ip, porta in lista:
        listar_comandos(ip, porta, ONVIF_USER, ONVIF_PASS)

if __name__ == "__main__":
    main()
