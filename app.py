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

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E8B57;
        font-size: 2.5rem;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #2E8B57;
        margin: 0.5rem 0;
    }
    .sidebar-header {
        color: #2E8B57;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem 1rem;
        border-radius: 0.375rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Función principal de la aplicación"""

    # Configuración de la aplicación
    config = get_app_config()

    # Header principal
    st.markdown('<h1 class="main-header">📚 Sistema POS - Librería Callejera</h1>', unsafe_allow_html=True)

    # Sidebar para navegación
    st.sidebar.markdown('<div class="sidebar-header">🧭 Navegación</div>', unsafe_allow_html=True)

    pages = {
        "🏠 Dashboard": "dashboard",
        "📚 Inventario": "inventory", 
        "💰 Ventas": "sales",
        "📊 Reportes": "reports",
        "⚙️ Configuración": "settings"
    }

    selected_page = st.sidebar.selectbox("Selecciona una página:", list(pages.keys()))
    current_page = pages[selected_page]

    # Inicializar página en session_state si no existe
    if 'page' not in st.session_state:
        st.session_state.page = current_page

    # Navegación entre páginas
    if current_page != st.session_state.page:
        st.session_state.page = current_page

    # Mostrar la página seleccionada
    if st.session_state.page == "dashboard":
        from ui.pages.dashboard import show_dashboard
        show_dashboard()
    
    elif st.session_state.page == "inventory":
        from ui.pages.inventory import show_inventory_page
        show_inventory_page()
    
    elif st.session_state.page == "sales":
        from ui.pages.sales import show_sales_page
        show_sales_page()
    
    elif st.session_state.page == "reports":
        st.header("📊 Reportes y Estadísticas")
        st.info("🚧 Esta sección está en desarrollo. Próximamente tendrás acceso a reportes detallados.")
    
    elif st.session_state.page == "settings":
        st.header("⚙️ Configuración del Sistema")
        st.info("🚧 Esta sección está en desarrollo. Próximamente podrás configurar el sistema.")

    # Footer
    st.divider()
    st.markdown(
        '<div style="text-align: center; color: #666; padding: 1rem;">📚 Sistema POS Librería - Desarrollado con ❤️ para el comercio informal</div>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
