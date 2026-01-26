import sys
import os
import re
from onvif import ONVIFCamera

# ==========================
# CONFIGURAÇÕES DE ACESSO
# ==========================
# Como o arquivo de texto geralmente só tem o IP, 
# precisamos definir o usuário e senha padrão aqui:
USUARIO = "admin"
SENHA = "admin"
PORTA_PADRAO = 8899

ARQUIVO_ALVO = "cameras_onvif.txt"

# ==========================
# FUNÇÕES
# ==========================
def ler_arquivo_cameras(arquivo):
    """Lê o arquivo e retorna uma lista de tuplas (ip, porta)"""
    alvos = []
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo '{arquivo}' não encontrado.")
        return []

    print(f"📂 Lendo arquivo: {arquivo}...")
    with open(arquivo, "r", encoding="utf-8") as f:
        for linha in f:
            # Procura por IP e opcionalmente a porta (Ex: 192.168.1.5 ou 192.168.1.5:8080)
            # Regex: Procura "IP:", espaços, (números e pontos), opcionalmente (: e números)
            match = re.search(r"IP:\s*([\d\.]+)(?::(\d+))?", linha)
            if match:
                ip = match.group(1)
                # Se tiver porta no arquivo usa ela, senão usa a padrão
                porta = int(match.group(2)) if match.group(2) else PORTA_PADRAO
                alvos.append((ip, porta))
    
    return alvos

def listar_comandos(ip, porta, user, senha):
    print("\n" + "="*60)
    print(f"🔌 CONECTANDO EM: {ip}:{porta}")
    print("="*60)
    
    try:
        # 1. Conexão
        cam = ONVIFCamera(ip, porta, user, senha)
        
        # 2. Info do Dispositivo
        resp = cam.devicemgmt.GetDeviceInformation()
        print(f"✅ SUCESSO! Hardware identificado:")
        print(f"   ► Fabricante: {resp.Manufacturer}")
        print(f"   ► Modelo:     {resp.Model}")
        print(f"   ► Firmware:   {resp.FirmwareVersion}")

        # 3. Mapeamento de Serviços
        servicos = [
            ("PTZ (Movimento)", cam.create_ptz_service()),
            ("IMAGING (Imagem)", cam.create_imaging_service()),
            ("MEDIA (Vídeo)", cam.create_media_service()),
            ("EVENTS (Eventos)", cam.create_events_service()),
            ("DEVICE (Sistema)", cam.devicemgmt)
        ]

        print("\n📜 MENU DE COMANDOS DISPONÍVEIS:")

        for nome_servico, objeto_servico in servicos:
            print(f"\n   📁 [{nome_servico}]")
            try:
                # Tenta listar as operações disponíveis no WSDL desse serviço
                if hasattr(objeto_servico, 'zeep_client'):
                    ops = list(objeto_servico.zeep_client.service._operations.keys())
                    ops.sort()
                    
                    if ops:
                        # Formata a saída em colunas simples
                        linha_atual = ""
                        for i, op in enumerate(ops):
                            print(f"      🔹 {op}")
                    else:
                        print("      (Nenhum comando público encontrado)")
                else:
                    print("      ⚠️ Erro de leitura WSDL.")
            except Exception:
                print("      ❌ Serviço não suportado nesta câmera.")

    except Exception as e:
        print(f"❌ FALHA AO CONECTAR EM {ip}:")
        print(f"   Erro: {e}")
        print("   (Verifique se o usuário/senha no script estão corretos)")

# ==========================
# MAIN
# ==========================
def main():
    print("--- INSPETOR DE COMANDOS ONVIF (EM LOTE) ---")
    print(f"Usando credenciais padrão: {USUARIO} / {SENHA}")
    
    lista_cameras = ler_arquivo_cameras(ARQUIVO_ALVO)

    if not lista_cameras:
        print("Nenhuma câmera encontrada no arquivo.")
        return

    print(f"Encontrados {len(lista_cameras)} dispositivos para análise.\n")

    for ip, porta in lista_cameras:
        listar_comandos(ip, porta, USUARIO, SENHA)

    print("\n" + "="*60)
    print("Fim do relatório.")
    input("Pressione ENTER para sair...")

if __name__ == "__main__":
    main()