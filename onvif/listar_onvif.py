from wsdiscovery import WSDiscovery
from wsdiscovery.scope import Scope
import socket
from datetime import datetime

ARQUIVO_SAIDA = "cameras_onvif.txt"

def descobrir_cameras():
    wsd = WSDiscovery()
    wsd.start()

    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    linhas = []
    linhas.append("========================================")
    linhas.append("DESCOBERTA DE CAMERAS ONVIF")
    linhas.append(f"Data/Hora: {agora}")
    linhas.append("========================================\n")

    services = wsd.searchServices(
        scopes=[Scope("onvif://www.onvif.org/type/video_encoder")]
    )

    if not services:
        linhas.append("Nenhuma camera ONVIF encontrada.\n")
    else:
        for i, service in enumerate(services, 1):
            linhas.append(f"CAMERA {i}")

            xaddrs = service.getXAddrs()
            if xaddrs:
                linhas.append(f"Endpoint ONVIF: {xaddrs[0]}")

                try:
                    host = xaddrs[0].split("/")[2].split(":")[0]
                    ip = socket.gethostbyname(host)
                    linhas.append(f"IP: {ip}")
                except:
                    linhas.append("IP: nao identificado")

            linhas.append(f"Tipos: {service.getTypes()}")
            linhas.append("-" * 40)

    wsd.stop()

    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        for l in linhas:
            f.write(l + "\n")

    print(f"✔ Resultado salvo em {ARQUIVO_SAIDA}")

if __name__ == "__main__":
    descobrir_cameras()
