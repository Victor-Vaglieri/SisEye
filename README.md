# SisEye (ONVIF)

Este repositório contém a documentação e o código-fonte de um conjunto de ferramentas desenvolvidas em Python para descoberta, gerenciamento e visualização de câmeras de segurança compatíveis com o protocolo ONVIF, com foco em aprendizado técnico, automação e construção de um painel de vigilância customizado.

## Visão Geral

O projeto foi concebido como um laboratório para estudo de protocolos de vídeo, redes e controle de dispositivos, aliado à construção incremental de uma solução de monitoramento.

A abordagem prioriza modularidade e a evolução, permitindo que cada componente seja utilizado de forma independente ou integrada ao ecossistema completo.

### Objetivos do Projeto

1. Descoberta Automática de Câmeras: Identificar dispositivos ONVIF na rede local e coletar informações para integração.
2. Centralização de Streams RTSP: Extrair e padronizar URLs RTSP para consumo por painéis, gravadores ou outras aplicações.
3. Painel de Visualização (CFTV): Desenvolver uma interface gráfica própria para exibição simultânea de câmeras em grid.
4. Controle Centralizado: Preparar a base para comandos globais, como controle de PTZ, iluminação IR e modos de visão noturna.
5. Aprimoramento Técnico: Servir como estudo de caso para redes, protocolos ONVIF/RTSP, OpenCV, Pygame e arquitetura de sistemas de monitoramento.

## Ciclo de Desenvolvimento

O desenvolvimento segue uma abordagem incremental, organizada nas seguintes etapas:

1. Descoberta e Inventário: Implementação de scripts para localização de câmeras ONVIF na rede.
2. Extração de Streams: Obtenção e padronização das URLs RTSP.
3. Visualização: Construção de um painel para exibição simultânea das câmeras.
4. Interação e Comandos: Implementação de controles globais e por câmera (PTZ, IR, modos).
5. Refinamento: Otimizações de performance, estabilidade e organização da interface.

## Execução

Todos os scripts podem ser executados individualmente ou por meio de um launcher em terminal, que lista automaticamente as ferramentas disponíveis no diretório.

```
python3 launcher.py
```

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

Python 3
+ ONVIF (onvif-zeep)
+ RTSP
+ OpenCV
+ Pygame
+ WS-Discovery
+ Linux (ambiente principal de execução)

## Estrutura do Projeto
onvif/
├── launcher.py
├── descobrir_onvif.py
├── gerar_rtsp.py
├── painel.py
├── cameras_onvif.txt
└── rtsp_urls.txt


Automação de dispositivos de rede

Desenvolvimento de soluções customizadas de vigilância
