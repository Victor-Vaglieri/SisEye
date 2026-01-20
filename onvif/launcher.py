#!/usr/bin/env python3
import os
import subprocess
import sys

# ==========================
# CONFIG
# ==========================
EXTENSAO = ".py"

# ==========================
# LISTAR PROGRAMAS
# ==========================
def listar_programas():
    arquivos = []
    for f in os.listdir("."):
        if f.endswith(EXTENSAO) and f != os.path.basename(__file__):
            arquivos.append(f)
    return sorted(arquivos)

# ==========================
# MENU
# ==========================
def menu(programas):
    os.system("clear")
    print("==== PAINEL DE FERRAMENTAS ====\n")

    for i, p in enumerate(programas, 1):
        print(f"{i}) {p}")

    print("\n0) Sair")

# ==========================
# EXECUTAR
# ==========================
def executar(programa):
    os.system("clear")   # 👈 LIMPA ANTES DE EXECUTAR
    print(f"▶ Executando {programa}\n")
    try:
        subprocess.run([sys.executable, programa])
    except KeyboardInterrupt:
        pass

    input("\nPressione ENTER para voltar ao menu...")

# ==========================
# MAIN
# ==========================
def main():
    while True:
        programas = listar_programas()

        if not programas:
            print("❌ Nenhum programa encontrado.")
            return

        menu(programas)

        escolha = input("\nEscolha: ").strip()

        if escolha == "0":
            os.system("clear")
            print("Saindo...")
            break

        if not escolha.isdigit():
            continue

        idx = int(escolha) - 1
        if 0 <= idx < len(programas):
            executar(programas[idx])

if __name__ == "__main__":
    main()
