# Modulo responsavel pela descoberta de dispositivos ONVIF na rede local.

import socket
import logging
from datetime import datetime
from wsdiscovery import WSDiscovery
from wsdiscovery.scope import Scope
from .config import CAMERAS_FILE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ONVIFDiscoverer:
    @staticmethod
    def discover_cameras(save_to_file: bool = True):
        """Descobre cameras ONVIF na rede e opcionalmente salva em um arquivo."""
        wsd = WSDiscovery()
        wsd.start()

        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            "========================================",
            "DESCOBERTA DE CAMERAS ONVIF",
            f"Data/Hora: {agora}",
            "========================================\n"
        ]

        logger.info("Iniciando descoberta de cameras ONVIF...")
        services = wsd.searchServices(
            scopes=[Scope("onvif://www.onvif.org/type/video_encoder")]
        )

        if not services:
            logger.warning("Nenhuma camera ONVIF encontrada.")
            lines.append("Nenhuma camera ONVIF encontrada.\n")
        else:
            logger.info(f"Encontradas {len(services)} cameras.")
            for i, service in enumerate(services, 1):
                lines.append(f"CAMERA {i}")
                xaddrs = service.getXAddrs()
                if xaddrs:
                    endpoint = xaddrs[0]
                    lines.append(f"Endpoint ONVIF: {endpoint}")
                    try:
                        host = endpoint.split("/")[2].split(":")[0]
                        ip = socket.gethostbyname(host)
                        lines.append(f"IP: {ip}")
                        logger.info(f"Camera {i}: IP {ip}")
                    except Exception as e:
                        logger.error(f"Erro ao identificar IP da camera {i}: {e}")
                        lines.append("IP: nao identificado")

                lines.append(f"Tipos: {service.getTypes()}")
                lines.append("-" * 40)

        wsd.stop()

        if save_to_file:
            with open(CAMERAS_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            logger.info(f"Resultado salvo em {CAMERAS_FILE}")
        
        return services

if __name__ == "__main__":
    ONVIFDiscoverer.discover_cameras()
