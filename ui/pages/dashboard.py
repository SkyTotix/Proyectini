"""
Página del dashboard principal
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from database.db_manager import db_manager

def show_dashboard():
    """Muestra el dashboard principal minimalista"""
    
    # Header simple y elegante
    st.markdown('<h2 style="text-align: center; color: #2c3e50; font-weight: 300; margin-bottom: 2rem;">Dashboard</h2>', unsafe_allow_html=True)
    
    # Obtener datos para métricas
    all_books = db_manager.execute_query("SELECT * FROM books")
    total_books = len(all_books)
    total_stock = sum(book['stock_quantity'] for book in all_books)
    low_stock_books = [book for book in all_books if book['stock_quantity'] <= book['min_stock']]
    
    # Ventas del día
    today = date.today().strftime('%Y-%m-%d')
    today_sales = db_manager.execute_query('''
        SELECT * FROM sales 
        WHERE DATE(sale_date) = ?
    ''', (today,))
    today_revenue = sum(sale['total_amount'] for sale in today_sales)
    
    # Métricas principales en cards minimalistas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e9ecef; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
            <h3 style="color: #3498db; margin: 0; font-size: 2rem; font-weight: 300;">{total_books}</h3>
            <p style="color: #6c757d; margin: 0.5rem 0 0 0; font-size: 0.9rem;">Total Libros</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e9ecef; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
            <h3 style="color: #27ae60; margin: 0; font-size: 2rem; font-weight: 300;">{total_stock}</h3>
            <p style="color: #6c757d; margin: 0.5rem 0 0 0; font-size: 0.9rem;">Stock Total</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        color = "#e74c3c" if len(low_stock_books) > 0 else "#27ae60"
        st.markdown(f"""
        <div style="background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e9ecef; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
            <h3 style="color: {color}; margin: 0; font-size: 2rem; font-weight: 300;">{len(low_stock_books)}</h3>
            <p style="color: #6c757d; margin: 0.5rem 0 0 0; font-size: 0.9rem;">Stock Bajo</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e9ecef; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
            <h3 style="color: #f39c12; margin: 0; font-size: 2rem; font-weight: 300;">${today_revenue:,.0f}</h3>
            <p style="color: #6c757d; margin: 0.5rem 0 0 0; font-size: 0.9rem;">Ventas Hoy</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Acciones rápidas minimalistas
    st.markdown('<h3 style="color: #2c3e50; font-weight: 400; margin-bottom: 1.5rem;">Acciones Rápidas</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Agregar Libro", use_container_width=True):
            st.session_state.page = "inventory"
            st.rerun()
    
    with col2:
        if st.button("🛒 Nueva Venta", use_container_width=True):
            st.session_state.page = "sales"
            st.rerun()
    
    with col3:
        if st.button("📊 Ver Reportes", use_container_width=True):
            st.session_state.page = "reports"
            st.rerun()
    
    st.divider()
    
    # Alertas de stock bajo
    if low_stock_books:
        st.warning(f"⚠️ **Alerta de Stock Bajo** - {len(low_stock_books)} libros necesitan reposición")
        
        with st.expander("Ver libros con stock bajo"):
            for book in low_stock_books:
                st.write(f"• **{book['title']}** por {book['author']} - Stock: {book['stock_quantity']} (Mín: {book['min_stock']})")
    
    # Resumen de libros recientes
    st.subheader("📖 Libros Agregados Recientemente")
    if all_books:
        recent_books = sorted(all_books, key=lambda x: x['created_at'], reverse=True)[:5]
        df_recent = pd.DataFrame(recent_books)
        st.dataframe(
            df_recent[['title', 'author', 'sale_price', 'stock_quantity']].rename(columns={
                'title': 'Título',
                'author': 'Autor', 
                'sale_price': 'Precio',
                'stock_quantity': 'Stock'
            }),
            use_container_width=True
        )
    else:
        st.info("No hay libros en el inventario. ¡Comienza agregando algunos!")
    
    # Gráficos de resumen
    st.subheader("📊 Resumen Visual")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribución por género
        if all_books:
            genre_counts = {}
            for book in all_books:
                genre = book['genre'] or 'Sin género'
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
            
            if genre_counts:
                st.markdown("#### 📚 Libros por Género")
                genre_df = pd.DataFrame(list(genre_counts.items()), columns=['Género', 'Cantidad'])
                st.bar_chart(genre_df.set_index('Género'))
    
    with col2:
        # Ventas de la última semana
        week_ago = (date.today() - pd.Timedelta(days=7)).strftime('%Y-%m-%d')
        week_sales = db_manager.execute_query('''
            SELECT DATE(sale_date) as sale_date, 
                   COUNT(*) as sales_count,
                   SUM(total_amount) as daily_revenue
            FROM sales 
            WHERE DATE(sale_date) >= ?
            GROUP BY DATE(sale_date)
            ORDER BY sale_date
        ''', (week_ago,))
        
        if week_sales:
            st.markdown("#### 📈 Ventas de la Última Semana")
            df_week = pd.DataFrame(week_sales)
            df_week['sale_date'] = pd.to_datetime(df_week['sale_date'])
            st.line_chart(df_week.set_index('sale_date')['daily_revenue'])
        else:
            st.info("No hay ventas en la última semana")
    
    # Información del sistema
    st.subheader("ℹ️ Información del Sistema")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"📦 **Versión:** 1.0.0")
    
    with col2:
        st.info("💻 **Estado:** Funcionando")
    
    with col3:
        st.info("🏪 **Tipo:** Comercio Informal")
