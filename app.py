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

# CSS minimalista y elegante
st.markdown("""
<style>
    /* Variables de colores minimalistas */
    :root {
        --primary: #2c3e50;
        --secondary: #3498db;
        --accent: #e74c3c;
        --light: #f8f9fa;
        --gray: #6c757d;
        --success: #27ae60;
        --warning: #f39c12;
        --border: #e9ecef;
    }

    /* Header principal minimalista */
    .main-header {
        font-size: 2.2rem;
        color: var(--primary);
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 300;
        letter-spacing: 2px;
    }

    /* Sidebar limpio */
    .sidebar-header {
        font-size: 1.1rem;
        font-weight: 500;
        color: var(--primary);
        margin-bottom: 1.5rem;
        padding: 0.75rem 0;
        border-bottom: 1px solid var(--border);
    }

    /* Métricas minimalistas */
    .metric-card {
        background: white;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.75rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }

    /* Botones elegantes */
    .stButton > button {
        background: white;
        border: 1px solid var(--border);
        border-radius: 8px;
        color: var(--primary);
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        min-height: 3rem;
    }

    .stButton > button:hover {
        background: var(--light);
        border-color: var(--secondary);
        color: var(--secondary);
        box-shadow: 0 2px 8px rgba(52, 152, 219, 0.2);
    }

    /* Selectbox limpio */
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 1px solid var(--border);
    }

    /* Ocultar elementos innecesarios para look más limpio */
    .stDeployButton { display: none; }
    #MainMenu { visibility: hidden; }
    .stDecoration { display: none; }
    footer { visibility: hidden; }

    /* Espaciado optimizado */
    .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }

    /* Cards informativos */
    .info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.25rem;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    .success-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        border-radius: 12px;
        padding: 1.25rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 12px rgba(17, 153, 142, 0.3);
    }

    /* Divisores más sutiles */
    hr {
        border: none;
        height: 1px;
        background: var(--border);
        margin: 2rem 0;
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

    # Inicializar página en session_state si no existe
    if 'page' not in st.session_state:
        st.session_state.page = "dashboard"

    # Obtener la página actual del session_state
    current_page = st.session_state.page
    
    # Encontrar el nombre de la página actual para el selectbox
    current_page_name = None
    for name, key in pages.items():
        if key == current_page:
            current_page_name = name
            break
    
    # Selectbox sincronizado con session_state
    selected_page = st.sidebar.selectbox(
        "Selecciona una página:", 
        list(pages.keys()),
        index=list(pages.keys()).index(current_page_name) if current_page_name else 0
    )
    
    # Actualizar session_state si cambió la selección
    if pages[selected_page] != st.session_state.page:
        st.session_state.page = pages[selected_page]
        st.rerun()

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
        from ui.pages.reports import show_reports_page
        show_reports_page()
    
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
