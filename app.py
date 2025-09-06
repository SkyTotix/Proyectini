"""
Aplicación principal del Sistema POS - Librería Callejera
Archivo principal para despliegue en Streamlit Community Cloud
"""

import streamlit as st
import sys
from pathlib import Path

# Agregar el directorio src al path para importar módulos
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Importar configuración
from config import get_app_config, STREAMLIT_CONFIG

# Configurar Streamlit al inicio (debe ser lo primero)
st.set_page_config(**STREAMLIT_CONFIG)

def main():
    """Función principal de la aplicación"""

    # Configuración de la aplicación
    config = get_app_config()

    # Header principal
    st.title("📚 Sistema POS - Librería Callejera")
    st.markdown("---")

    # Información del sistema
    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(f"📦 **Versión:** {config['app']['version']}")

    with col2:
        st.info("💻 **Estado:** En desarrollo")

    with col3:
        st.info("🏪 **Tipo:** Comercio Informal")

    st.markdown("---")

    # Mensaje de bienvenida
    st.success("🎉 ¡Bienvenido al Sistema POS para tu librería callejera!")
    st.info("📋 El sistema está en desarrollo. Próximamente tendrás acceso completo a:")
    st.markdown("""
    - 📚 Gestión de inventario
    - 💰 Procesamiento de ventas
    - 📊 Reportes y estadísticas
    - 🗄️ Base de datos local
    """)

    # Espacio para futuras funcionalidades
    st.markdown("### 🚀 Próximas Funcionalidades")
    st.markdown("""
    Mantente atento a las actualizaciones. El sistema se irá completando paso a paso.
    """)

    # Footer
    st.markdown("---")
    st.markdown(f"<center><small>{config['app']['author']}</small></center>",
                unsafe_allow_html=True)

if __name__ == "__main__":
    main()
