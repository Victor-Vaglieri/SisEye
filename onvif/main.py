#!/usr/bin/env python3
# Script principal que gerencia a execucao dos outros scripts do sistema SisEye.

import os
import subprocess
import sys
import platform
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def limpar_tela():
    sistema = platform.system()
    if sistema == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def listar_scripts():
    scripts_dir = "scripts"
    if not os.path.exists(scripts_dir):
        return []
    
    arquivos = [os.path.join(scripts_dir, f) for f in os.listdir(scripts_dir) if f.endswith(".py")]
    return sorted(arquivos)

def executar(script_path, pausa=True):
    limpar_tela()
    print(f"Executando {os.path.basename(script_path)}...\n")
    print("-" * 40)
    
    try:
        subprocess.run([sys.executable, script_path])
    except KeyboardInterrupt:
        print("\n\nExecucao interrompida pelo usuario.")
    except Exception as e:
        logger.error(f"Erro ao executar script: {e}")

    print("-" * 40)
    if pausa:
        input("\nPressione ENTER para continuar...")

def menu():
    while True:
        scripts = listar_scripts()
        limpar_tela()
        print("==== SIS EYE: PAINEL DE CONTROLE ====\n")

        for i, s in enumerate(scripts, 1):
            nome = os.path.basename(s).replace(".py", "").replace("_", " ").title()
            print(f"{i}) {nome}")

        print("\n9) Inspetor de Comandos (Utils)")
        print("0) Sair")

        escolha = input("\nEscolha uma opcao: ").strip()

        if escolha == "0":
            print("Saindo...")
            break
        elif escolha == "9":
            executar(os.path.join("scripts", "utils", "inspector.py"))
            continue

        if not escolha.isdigit():
            continue

        idx = int(escolha) - 1
        if 0 <= idx < len(scripts):
            executar(scripts[idx])

if __name__ == "__main__":
    menu()
