from onvif import ONVIFCamera
import time

# --- CONFIGURAÇÕES ---
IP = "192.168.15.27"
PORT = 8899
USER = "Victor"
PASS = "OsOs0505!"

def conectar():
    print(f"🔌 Conectando em {IP}...")
    try:
        cam = ONVIFCamera(IP, PORT, USER, PASS)
        imaging = cam.create_imaging_service()
        media = cam.create_media_service()
        token = media.GetVideoSources()[0].token
        return imaging, token
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None, None

def ler_estado(imaging, token):
    try:
        settings = imaging.GetImagingSettings({'VideoSourceToken': token})
        print("\n--- 📊 ESTADO ATUAL ---")
        
        # O filtro IR é o verdadeiro "Day/Night Switch" do ONVIF
        if hasattr(settings, 'IrCutFilter'):
            print(f"🔹 Modo Day/Night (IrCutFilter): [{settings.IrCutFilter}]")
        else:
            print("🔸 Câmera não reportou IrCutFilter.")

        if hasattr(settings, 'Exposure'):
            print(f"🔹 Exposição (Mode): [{settings.Exposure.Mode}]")
        
        if hasattr(settings, 'BacklightCompensation'):
            print(f"🔹 BLC (Mode): [{settings.BacklightCompensation.Mode}]")
            
        print("-----------------------")
        return settings
    except Exception as e:
        print(f"❌ Erro ao ler: {e}")
        return None

def mudar_modo(imaging, token, modo):
    # Modos Padrão ONVIF: 'ON', 'OFF', 'AUTO'
    # ON   = Modo Noite (Infravermelho ligado, Preto e Branco)
    # OFF  = Modo Dia (Colorido, IR desligado)
    # AUTO = A câmera decide (Geralmente causa o problema da luz branca)
    
    print(f"\n⚙️ Tentando mudar para: {modo}...")
    
    try:
        request = imaging.create_type('SetImagingSettings')
        request.VideoSourceToken = token
        
        # Pega config atual para não quebrar o resto
        current = imaging.GetImagingSettings({'VideoSourceToken': token})
        request.ImagingSettings = current
        
        # Aplica a mudança
        request.ImagingSettings.IrCutFilter = modo
        
        imaging.SetImagingSettings(request)
        print("✅ Comando enviado com sucesso!")
        
        # Lê de novo para confirmar
        time.sleep(1)
        ler_estado(imaging, token)
        
    except Exception as e:
        print(f"❌ A câmera rejeitou o comando: {e}")

def menu():
    imaging, token = conectar()
    if not imaging: return

    while True:
        current = ler_estado(imaging, token)
        
        print("\nESCOLHA O MODO:")
        print("1 - MODO NOITE (Forçar Preto e Branco/IR) [ON]")
        print("2 - MODO DIA (Forçar Colorido) [OFF]")
        print("3 - AUTOMÁTICO (Padrão da Câmera) [AUTO]")
        print("0 - Sair")
        
        opt = input("Opção: ")
        
        if opt == '1': mudar_modo(imaging, token, 'ON')
        elif opt == '2': mudar_modo(imaging, token, 'OFF')
        elif opt == '3': mudar_modo(imaging, token, 'AUTO')
        elif opt == '0': break
        else: print("Opção inválida.")

if __name__ == "__main__":
    menu()