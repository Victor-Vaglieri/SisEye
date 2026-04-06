# Script para descoberta automatica de dispositivos ONVIF na rede.

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import ONVIFDiscoverer

def main():
    print("--- SIS EYE: DESCOBERTA DE DISPOSITIVOS ---")
    ONVIFDiscoverer.discover_cameras()
    print("Concluido.")

if __name__ == "__main__":
    main()
