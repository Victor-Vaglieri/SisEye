# SisEye (ONVIF)

Este repositório contém a documentação e o código-fonte de um conjunto de ferramentas desenvolvidas em Python para descoberta, gerenciamento e visualização de câmeras de segurança compatíveis com o protocolo ONVIF, com foco em aprendizado técnico, automação e construção de um painel de vigilância customizado.

## Visão Geral

O projeto foi concebido como um laboratório para estudo de protocolos de vídeo e redes, evoluindo para uma solução prática de monitoramento. Diferente de VMS tradicionais, o SisEye é leve e roda via linha de comando ou interface gráfica minimalista baseada em OpenCV.

### Objetivos do Projeto

1. Descoberta Automática: Identificação de dispositivos ONVIF na rede local (Port Scanning e Handshake SOAP).
2. Extração de Streams: Coleta automática de URLs RTSP, com suporte a diferenciação de perfis (MainStream/SubStream).
3. Painel de Vigilância (SisEye Player): Interface gráfica com Layout em Grid (1 câmera principal + 1 secundária).
4. Controle Integrado: Terminal de comandos embutido na interface visual (controle de Luz/IR).
5. Estabilidade de Rede: Implementação de captura assíncrona (Threading) e transporte via TCP para evitar corrupção de pacotes em Wi-Fi.



## Ciclo de Desenvolvimento

O desenvolvimento segue uma abordagem incremental, organizada nas seguintes etapas:

1. Descoberta e Inventário: Implementação de scripts para localização de câmeras ONVIF na rede.
2. Extração de Streams: Obtenção e padronização das URLs RTSP.
3. Visualização: Construção de um painel para exibição simultânea das câmeras.
4. Interação e Comandos: Implementação de controles globais e por câmera (PTZ, IR, modos).
5. Refinamento: Otimizações de performance, estabilidade e organização da interface.



## Principais Ferramentas
### Descoberta ONVIF

+ Localiza câmeras compatíveis com ONVIF na rede local
+ Gera um arquivo de inventário com IPs e informações básicas

### Extração de URLs RTSP

+ Conecta às câmeras via ONVIF
+ Obtém os perfis de mídia disponíveis
+ Gera uma lista padronizada de URLs RTSP

### Painel de Monitoramento (CFTV)

+ Exibição simultânea das câmeras em grid quadrado
+ Slot dedicado para comandos e interações
+ Estrutura preparada para controle PTZ e modos de operação

### Launcher de Ferramentas

+ Interface em terminal
+ Listagem automática de scripts disponíveis
+ Execução isolada e organizada de cada módulo


## Tecnologias Utilizadas

+ Python 3.11
+ Visão Computacional & UI: OpenCV (cv2)
+ Protocolos: ONVIF (onvif-zeep), RTSP, TCP/IP
+ Concorrência: Python threading e subprocess



## Estrutura do Projeto

```
onvif/
├── main.py
├── 1 - listar_onvif.py
├── 2 - gerar_rtsp.py
├── 3 - painel.py
├── cameras_onvif.txt
└── rtsp_urls_detalhado.txt
```



## Execução

Todos os scripts podem ser executados individualmente ou por meio de um launcher em terminal, que lista automaticamente as ferramentas disponíveis no diretório.

### dependencias

Antes de iniciar, instale as bibliotecas essenciais para processamento de imagem (OpenCV), comunicação com câmeras (ONVIF) e descoberta de rede:

```
pip install opencv-python onvif-zeep numpy wsdiscovery
```

### Launcher de controle

Inicia o menu interativo no terminal, permitindo selecionar e executar qualquer ferramenta do kit de forma centralizada e organizada.

```
python3 main.py
```

### Localizador de cameras ONVIF

Realiza uma varredura na rede local (scan) para identificar dispositivos ativos compatíveis com ONVIF e cria o inventário inicial de IPs.

```
python3 listar_onvif.py
```

### Coletador de URLs RTSP

Lê o arquivo de IPs, conecta-se a cada câmera para identificar os perfis de vídeo (Main/Sub Stream) e gera a lista detalhada de links de reprodução.

```
python3 gerar_rtsp.py
```

> [!NOTE]
> Para Executar é necessario do arquivo _**cameras_onvif.txt**_

###  Painel  com Grid

Abre a interface gráfica de monitoramento baseada em OpenCV, com suporte a multithreading para exibição fluida e terminal de comandos integrado.

```
python3 painel.py
```

> [!NOTE]
> Para Executar é necessario do arquivo _**rtsp_urls_detalhado.txt**_

