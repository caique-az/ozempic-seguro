#!/usr/bin/env python
"""
Script de inicialização do Ozempic Seguro.
Execute este arquivo para iniciar a aplicação.
"""

import sys
import os

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Importa e executa o main
from ozempic_seguro.main import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Encerramento silencioso via Ctrl+C
        sys.exit(0)
    except Exception:
        sys.exit(1)
