#!/usr/bin/env python3
import os
import subprocess
import sys
import platform

# ==========================
# CONFIG
# ==========================
EXTENSAO = ".py"

# ==========================
# UTILITÁRIOS
# ==========================
def limpar_tela():
    sistema = platform.system()
    if sistema == "Windows":
        os.system("cls")
    else:
        os.system("clear")

# ==========================
# LISTAR PROGRAMAS
# ==========================
def listar_programas():
    arquivos = []
    # Lista arquivos do diretório atual
    for f in os.listdir("."):
        # Filtra por extensão e ignora o próprio script
        if f.endswith(EXTENSAO) and f != os.path.basename(__file__):
            arquivos.append(f)
    return sorted(arquivos)

# ==========================
# MENU
# ==========================
def menu(programas):
    limpar_tela()
    print("==== PAINEL DE FERRAMENTAS ====\n")

    for i, p in enumerate(programas, 1):
        print(f"{i}) {p}")

    print("\n0) Sair")

# ==========================
# EXECUTAR
# ==========================
def executar(programa, pausa=True):
    limpar_tela()
    print(f"▶ Executando {programa}...\n")
    print("-" * 40)
    
    try:
        # Chama o python atual para rodar o script
        subprocess.run([sys.executable, programa])
    except KeyboardInterrupt:
        print("\n\n⏹ Execução interrompida pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro ao tentar executar: {e}")

    print("-" * 40)
    
    if pausa:
        input("\nPressione ENTER para continuar...")

# ==========================
# MAIN
# ==========================
def main():
    # 1. Carrega a lista inicial
    programas = listar_programas()

    if not programas:
        print("❌ Nenhum programa encontrado no diretório.")
        input("Pressione ENTER para sair...")
        return

    # =========================================
    # 🚀 AUTO-EXECUÇÃO DOS 3 PRIMEIROS
    # =========================================
    # Pega os 3 primeiros da lista (ou menos, se tiver menos de 3)
    fila_automatica = programas[:3] 
    
    if fila_automatica:
        print(f"🔄 Iniciando execução automática de {len(fila_automatica)} scripts...")
        import time
        time.sleep(1.5) # Pequena pausa para ler a mensagem

        for prog in fila_automatica:
            executar(prog, pausa=True) # 'pausa=True' para você ver o resultado antes do próximo

    # =========================================
    # 🖥 ENTRA NO MENU INTERATIVO
    # =========================================
    while True:
        # Recarrega a lista (caso algum arquivo tenha sido criado/deletado)
        programas = listar_programas()
        
        menu(programas)

        escolha = input("\nEscolha uma opção: ").strip()

        if escolha == "0":
            limpar_tela()
            print("Saindo...")
            break

        if not escolha.isdigit():
            continue

        idx = int(escolha) - 1
        if 0 <= idx < len(programas):
            executar(programas[idx])

if __name__ == "__main__":
    main()