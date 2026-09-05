"""Configuracion de pytest para el paquete bibtex_ris"""

import os
import sys
from pathlib import Path

# Agrega src al path por si el paquete no esta instalado
SRC_DIR = Path(__file__).resolve().parent.parent / 'src'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Los procesos hijos de los tests de CLI importan el paquete
os.environ['PYTHONPATH'] = str(SRC_DIR)