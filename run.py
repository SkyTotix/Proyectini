#!/usr/bin/env python3
"""
Script de inicio para el Sistema POS - Librería Callejera
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path para importar módulos
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    try:
        import streamlit
        import pandas
        import plotly
        return True
    except ImportError as missing:
        print(f"❌ Dependencia faltante: {missing}")
        print("Ejecuta: pip install -r requirements.txt")
        return False

def main():
    """Función principal de inicio"""
    print("📚 Sistema POS - Librería Callejera")
    print("=" * 40)

    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)

    # Ejecutar Streamlit directamente
    try:
        print("✅ Iniciando aplicación...")
        import subprocess
        subprocess.run([sys.executable, "-m", "streamlit", "run", "src/app.py"])
    except Exception as e:
        print(f"❌ Error al ejecutar la aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
