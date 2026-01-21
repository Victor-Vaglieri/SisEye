from onvif import ONVIFCamera
import re
import sys

# ==========================
# CONFIGURAÇÕES
# ==========================
USUARIO = "admin"
SENHA = "admin"  # Verifique se a senha é essa mesmo
ARQ_ENTRADA = "cameras_onvif.txt"
ARQ_SAIDA = "rtsp_urls_detalhado.txt"

# Lista de portas comuns para tentar automaticamente
PORTAS_ONVIF = [80, 8080, 8899, 5000, 2020]

# ==========================
# Extrair IPs
# ==========================
def extrair_ips(arquivo):
    ips = []
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            for linha in f:
                # Pega IP e ignora linhas de comentário
                m = re.search(r"IP:\s*([\d\.]+)", linha)
                if m:
                    ips.append(m.group(1))
    except FileNotFoundError:
        print(f"❌ Crie o arquivo '{ARQ_ENTRADA}' com os IPs (ex: IP: 192.168.1.10)")
        sys.exit()
    return ips

# ==========================
# Tenta conectar em várias portas
# ==========================
def conectar_camera(ip):
    for porta in PORTAS_ONVIF:
        print(f"   ⏳ Tentando conectar em {ip}:{porta}...")
        try:
            cam = ONVIFCamera(ip, porta, USUARIO, SENHA)
            # Tenta pegar a data só para ver se comunicou
            cam.devicemgmt.GetSystemDateAndTime()
            print(f"   ✅ Sucesso na porta {porta}!")
            return cam
        except Exception as e:
            # Erros comuns de conexão ignorados para tentar a próxima porta
            continue
    
    print(f"   ❌ Falha: Não foi possível conectar em {ip} em nenhuma porta comum.")
    return None

# ==========================
# MAIN
# ==========================
def main():
    ips = extrair_ips(ARQ_ENTRADA)
    if not ips:
        print("❌ Nenhum IP encontrado.")
        return

    resultados = []

    for ip in ips:
        print(f"\n==========================================")
        print(f"📷 ANALISANDO CÂMERA: {ip}")
        print(f"==========================================")

        cam = conectar_camera(ip)
        
        if cam:
            try:
                media = cam.create_media_service()
                profiles = media.GetProfiles()

                print(f"   🔎 Encontrados {len(profiles)} perfis de vídeo:\n")

                for p in profiles:
                    # Tenta pegar a URL RTSP deste perfil
                    try:
                        setup = {"Stream": "RTP-Unicast", "Transport": {"Protocol": "RTSP"}}
                        uri_obj = media.GetStreamUri({"StreamSetup": setup, "ProfileToken": p.token})
                        url_rtsp = uri_obj.Uri

                        # Limpa o IP local (algumas câmeras devolvem IP interno errado)
                        url_rtsp = url_rtsp.replace("127.0.0.1", ip)

                        # Nome do perfil ajuda a saber o que é (Main = Alta qualidade, Sub = Baixa)
                        info = f"Perfil: {p.Name} (Token: {p.token})"
                        print(f"   📺 {info}")
                        print(f"      URL: {url_rtsp}")
                        
                        resultados.append(f"# Câmera {ip} - {info}\n{url_rtsp}")

                    except Exception as e:
                        print(f"      ⚠️ Erro ao pegar URL do perfil {p.Name}: {e}")

            except Exception as e:
                print(f"   ⚠️ Erro ao listar perfis: {e}")

    # Salva no arquivo
    if resultados:
        with open(ARQ_SAIDA, "w", encoding="utf-8") as f:
            f.write("\n".join(resultados))
        print(f"\n\n✔ Relatório salvo em: {ARQ_SAIDA}")
        print("Copie as URLs 'MainStream' (ou similar) para o seu rtsp_urls.txt")
    else:
        print("\n❌ Nenhuma URL válida foi extraída.")

if __name__ == "__main__":
    main()