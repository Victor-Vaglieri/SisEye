# Arquivo de configuracao central do sistema SisEye, contendo credenciais, caminhos de arquivos e constantes de rede.

import os
from dotenv import load_dotenv

load_dotenv()

# Credenciais e configuracoes de rede extraidas do ambiente (.env)
ONVIF_USER = os.getenv("ONVIF_USER")
ONVIF_PASS = os.getenv("ONVIF_PASS")
ONVIF_PORT = int(os.getenv("ONVIF_PORT", 8899))
IP_TESTE = os.getenv("IP_TESTE", "127.0.0.1")
WEB_PORT = int(os.getenv("WEB_PORT", 8000))

# Nomes de arquivos de saida e fallback
CAMERAS_FILE = "cameras_onvif.txt"
RTSP_FILE = "rtsp_urls_detalhado.txt"
FALLBACK_VIDEO = "loading.mp4"

# Portas comuns para descoberta manual e conexao
PORTAS_ONVIF = [80, 8080, 8899, 5000, 2020]

# Configuracoes visuais (Dashboard Desktop)
LARGURA_TELA = 1920
ALTURA_TELA = 1080
COR_BG = (20, 20, 20)
COR_TEXTO = (0, 220, 0)
COR_OFFLINE = (50, 0, 0)
