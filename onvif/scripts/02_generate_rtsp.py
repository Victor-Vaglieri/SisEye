# Script responsavel por conectar as cameras descobertas e gerar as URLs de streaming RTSP.

import re
import sys
import os
import logging
from onvif import ONVIFCamera

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import CAMERAS_FILE, RTSP_FILE, PORTAS_ONVIF, ONVIF_USER, ONVIF_PASS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_ips(file_path):
    ips = []
    if not os.path.exists(file_path):
        logger.error(f"Arquivo '{file_path}' nao encontrado. Execute o script de descoberta primeiro.")
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            match = re.search(r"IP:\s*([\d\.]+)", line)
            if match:
                ips.append(match.group(1))
    return ips

def connect_camera(ip):
    for port in PORTAS_ONVIF:
        logger.info(f"Tentando conectar em {ip}:{port}...")
        try:
            cam = ONVIFCamera(ip, port, ONVIF_USER, ONVIF_PASS)
            cam.devicemgmt.GetSystemDateAndTime()
            logger.info(f"Sucesso na porta {port}!")
            return cam
        except Exception:
            continue
    logger.warning(f"Falha ao conectar em {ip} em nenhuma porta comum.")
    return None

def main():
    ips = extract_ips(CAMERAS_FILE)
    if not ips:
        return

    results = []
    for ip in ips:
        print(f"\n" + "="*40)
        print(f"ANALISANDO CAMERA: {ip}")
        print("="*40)

        cam = connect_camera(ip)
        if cam:
            try:
                media = cam.create_media_service()
                profiles = media.GetProfiles()
                logger.info(f"Encontrados {len(profiles)} perfis de video.")

                for p in profiles:
                    try:
                        setup = {"Stream": "RTP-Unicast", "Transport": {"Protocol": "RTSP"}}
                        uri_obj = media.GetStreamUri({"StreamSetup": setup, "ProfileToken": p.token})
                        url_rtsp = uri_obj.Uri.replace("127.0.0.1", ip)

                        info = f"Perfil: {p.Name} (Token: {p.token})"
                        print(f"   {info}")
                        print(f"      URL: {url_rtsp}")
                        results.append(f"# Camera {ip} - {info}\n{url_rtsp}")
                    except Exception as e:
                        logger.error(f"Erro ao obter URL do perfil {p.Name}: {e}")
            except Exception as e:
                logger.error(f"Erro ao listar perfis: {e}")

    if results:
        with open(RTSP_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(results))
        logger.info(f"Relatorio salvo em: {RTSP_FILE}")
    else:
        logger.error("Nenhuma URL valida foi extraida.")

if __name__ == "__main__":
    main()
