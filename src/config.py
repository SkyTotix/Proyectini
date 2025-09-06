"""
Configuración del Sistema POS - Librería Callejera
"""

import os
from pathlib import Path

# Configuración de rutas
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "bookstore.db"

# Configuración de la aplicación
APP_NAME = "Sistema POS - Librería Callejera"
APP_VERSION = "1.0.0"
AUTHOR = "Desarrollado para comercio informal"

# Configuración de Streamlit
STREAMLIT_CONFIG = {
    "page_title": APP_NAME,
    "page_icon": "📚",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Configuración de base de datos
DATABASE_CONFIG = {
    "path": DATABASE_PATH,
    "timeout": 30.0,
    "check_same_thread": False
}

# Configuración de negocio
BUSINESS_CONFIG = {
    "currency": "MXN",
    "currency_symbol": "$",
    "tax_rate": 0.16,  # IVA México
    "min_stock_alert": 5,
    "max_items_per_sale": 50
}

# Configuración de UI
UI_CONFIG = {
    "theme": "light",
    "primary_color": "#2E8B57",  # Verde para libros
    "secondary_color": "#F0F8FF",
    "success_color": "#28a745",
    "warning_color": "#ffc107",
    "danger_color": "#dc3545"
}

def ensure_data_directory():
    """Asegura que el directorio de datos existe"""
    DATA_DIR.mkdir(exist_ok=True)

def get_database_path():
    """Retorna la ruta completa de la base de datos"""
    ensure_data_directory()
    return DATABASE_PATH

def get_app_config():
    """Retorna la configuración completa de la aplicación"""
    return {
        "app": {
            "name": APP_NAME,
            "version": APP_VERSION,
            "author": AUTHOR
        },
        "database": DATABASE_CONFIG,
        "business": BUSINESS_CONFIG,
        "ui": UI_CONFIG,
        "streamlit": STREAMLIT_CONFIG
    }
