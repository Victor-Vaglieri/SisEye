# SisEye (ONVIF)

Este repositório contém o código-fonte de um conjunto de ferramentas profissionais desenvolvidas em Python para descoberta, gerenciamento e visualização de câmeras de segurança compatíveis com o protocolo ONVIF. O foco do projeto é automação, segurança e a construção de um painel de vigilância customizado e eficiente.

## Hardware Compatível

Este software foi otimizado e validado para hardware OEM genérico, mas segue os padrões universais do protocolo ONVIF.

* **Fabricante Sugerido:** H264 (OEM Genérico / ICSee / XMeye)
* **Protocolo:** ONVIF 2.0+
* **Codecs Suportados:** H.264 / H.265 (HEVC)

## Visão Geral

O SisEye é uma solução leve e modular de monitoramento. Ele separa a lógica de conexão, descoberta e interface para garantir manutenibilidade e performance. Diferente de VMS pesados, o SisEye foca na agilidade e no controle direto via código ou interfaces minimalistas.

### Diferenciais do Projeto

1.  **Arquitetura Modular:** Lógica centralizada na pasta `core/` para fácil reaproveitamento.
2.  **Segurança Avançada:** Uso rigoroso de variáveis de ambiente (`.env`) para proteger credenciais.
3.  **Interface Híbrida:** Opções de monitoramento via Desktop (OpenCV) ou Web (FastAPI).
4.  **Recorte Inteligente:** Suporte a visualizações customizadas (Crop) para focar em áreas de interesse.
5.  **Robustez:** Sistema de reconexão automática e tratamento de quedas de stream.

## Estrutura do Projeto

```text
onvif/
├── core/                 # Lógica central (Config, Descoberta, Stream)
├── scripts/              # Scripts de execução (01 a 04)
│   └── utils/            # Utilitários de inspeção e teste
├── static/               # Arquivos estáticos (CSS, JS) para o Painel Web
├── templates/            # Templates HTML (Jinja2)
├── main.py               # Launcher central do sistema
├── .env.example          # Modelo de configuração de ambiente
└── requirements.txt      # Dependências do projeto
```

## Configuração e Instalação

### 1. Requisitos
Certifique-se de ter o Python 3.8+ instalado. Instale as dependências utilizando o arquivo `requirements.txt`:

```bash
pip install -r onvif/requirements.txt
```

### 2. Variáveis de Ambiente
O projeto utiliza um arquivo `.env` para gerenciar credenciais com segurança. 
Copie o modelo de exemplo e preencha com seus dados:

```bash
cp onvif/.env.example onvif/.env
```

Edite o arquivo `onvif/.env` com as informações da sua rede:
```env
ONVIF_USER=admin
ONVIF_PASS=sua_senha
ONVIF_PORT=8899
IP_TESTE=192.168.1.100
```

## Como Usar

### Launcher Central
A maneira mais fácil de utilizar o sistema é através do script principal na raiz da pasta `onvif`:

```bash
python onvif/main.py
```

### Fluxo de Operação
Para configurar o sistema pela primeira vez, siga esta ordem:

1.  **01_discovery.py**: Localiza as câmeras ONVIF na sua rede local.
2.  **02_generate_rtsp.py**: Conecta nas câmeras encontradas e extrai as URLs de streaming.
3.  **03_web_panel.py**: Inicia o servidor para visualização via navegador (FastAPI).
4.  **04_desktop_panel.py**: Inicia a interface desktop de alta performance (OpenCV).

## Tecnologias Utilizadas

* **Linguagem:** Python 3
* **Streaming:** OpenCV, FFmpeg
* **Web:** FastAPI, Uvicorn, Jinja2
* **ONVIF:** onvif-zeep, wsdiscovery
* **Interface:** Vanilla CSS & JS, Keyboard (Desktop)

---
*Desenvolvido para entusiastas de CFTV e automação residencial.*
