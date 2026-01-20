from onvif import ONVIFCamera
import re

# ==========================
# CONFIGURAÇÕES PADRÃO
# ==========================
USUARIO = "admin"
SENHA = "admin123"
PORTA_ONVIF = 80

ARQ_ENTRADA = "cameras_onvif.txt"
ARQ_SAIDA = "rtsp_urls.txt"

# ==========================
# Extrair IPs do arquivo
# ==========================
def extrair_ips(arquivo):
    ips = []
    with open(arquivo, "r", encoding="utf-8") as f:
        for linha in f:
            m = re.search(r"IP:\s*([\d\.]+)", linha)
            if m:
                ips.append(m.group(1))
    return ips

# ==========================
# Obter URLs RTSP via ONVIF
# ==========================
def obter_rtsp(ip):
    cam = ONVIFCamera(ip, PORTA_ONVIF, USUARIO, SENHA)
    media = cam.create_media_service()

    profiles = media.GetProfiles()
    urls = []

    for p in profiles:
        setup = {
            "Stream": "RTP-Unicast",
            "Transport": {"Protocol": "RTSP"}
        }

        uri = media.GetStreamUri({
            "StreamSetup": setup,
            "ProfileToken": p.token
        })

        urls.append(uri.Uri)

    return urls

# ==========================
# PROGRAMA PRINCIPAL
# ==========================
def main():
    ips = extrair_ips(ARQ_ENTRADA)

    if not ips:
        print("❌ Nenhum IP encontrado no arquivo.")
        return

    saida = []

    for ip in ips:
        print(f"\n📷 Processando câmera {ip}")

        try:
            urls = obter_rtsp(ip)

            for u in urls:
                print("RTSP:", u)
                saida.append(u)

        except Exception as e:
            print("⚠️ Falha ao acessar câmera:", e)

    if not saida:
        print("\n❌ Nenhuma URL RTSP obtida.")
        return

    with open(ARQ_SAIDA, "w", encoding="utf-8") as f:
        for u in saida:
            f.write(u + "\n")

    print(f"\n✔ URLs RTSP salvas em: {ARQ_SAIDA}")

if __name__ == "__main__":
    main()
