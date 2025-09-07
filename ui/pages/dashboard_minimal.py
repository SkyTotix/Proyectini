"""
Dashboard principal minimalista
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
    
    # Header elegante y simple
    st.markdown('<h2 style="text-align: center; color: #2c3e50; font-weight: 300; margin-bottom: 3rem; letter-spacing: 1px;">Dashboard</h2>', unsafe_allow_html=True)
    
    # Obtener datos esenciales
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
        <div style="background: white; padding: 2rem; border-radius: 16px; border: 1px solid #e9ecef; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.08); transition: all 0.3s ease;">
            <h2 style="color: #3498db; margin: 0; font-size: 2.5rem; font-weight: 200;">{total_books}</h2>
            <p style="color: #6c757d; margin: 1rem 0 0 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Libros</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: white; padding: 2rem; border-radius: 16px; border: 1px solid #e9ecef; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.08); transition: all 0.3s ease;">
            <h2 style="color: #27ae60; margin: 0; font-size: 2.5rem; font-weight: 200;">{total_stock}</h2>
            <p style="color: #6c757d; margin: 1rem 0 0 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Stock</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        color = "#e74c3c" if len(low_stock_books) > 0 else "#27ae60"
        st.markdown(f"""
        <div style="background: white; padding: 2rem; border-radius: 16px; border: 1px solid #e9ecef; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.08); transition: all 0.3s ease;">
            <h2 style="color: {color}; margin: 0; font-size: 2.5rem; font-weight: 200;">{len(low_stock_books)}</h2>
            <p style="color: #6c757d; margin: 1rem 0 0 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Alertas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: white; padding: 2rem; border-radius: 16px; border: 1px solid #e9ecef; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.08); transition: all 0.3s ease;">
            <h2 style="color: #f39c12; margin: 0; font-size: 2.5rem; font-weight: 200;">${today_revenue:,.0f}</h2>
            <p style="color: #6c757d; margin: 1rem 0 0 0; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Hoy</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Espaciado elegante
    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)
    
    # Acciones rápidas con diseño minimalista
    st.markdown('<h3 style="text-align: center; color: #2c3e50; font-weight: 300; margin-bottom: 2rem; letter-spacing: 1px;">Acciones Rápidas</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Agregar Libro", use_container_width=True, key="add_book"):
            st.session_state.page = "inventory"
            st.rerun()
    
    with col2:
        if st.button("Nueva Venta", use_container_width=True, key="new_sale"):
            st.session_state.page = "sales"
            st.rerun()
    
    with col3:
        if st.button("Ver Reportes", use_container_width=True, key="view_reports"):
            st.session_state.page = "reports"
            st.rerun()
    
    # Alertas importantes (solo si las hay)
    if low_stock_books:
        st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #fff3cd, #ffeaa7); border-radius: 12px; padding: 1.5rem; text-align: center; border: 1px solid #f39c12;">
            <h4 style="color: #856404; margin: 0; font-weight: 400;">⚠️ {len(low_stock_books)} libro(s) necesitan reposición</h4>
        </div>
        """, unsafe_allow_html=True)
    
    # Resumen de actividad (solo si hay ventas hoy)
    if today_sales:
        st.markdown("<div style='margin: 3rem 0 2rem 0;'></div>", unsafe_allow_html=True)
        st.markdown('<h3 style="text-align: center; color: #2c3e50; font-weight: 300; margin-bottom: 1.5rem; letter-spacing: 1px;">Actividad de Hoy</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #11998e, #38ef7d); border-radius: 12px; padding: 2rem; text-align: center; color: white; box-shadow: 0 4px 12px rgba(17, 153, 142, 0.3);">
                <h3 style="margin: 0; font-weight: 300; font-size: 2rem;">{len(today_sales)}</h3>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">Ventas Realizadas</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_sale = today_revenue / len(today_sales) if today_sales else 0
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 12px; padding: 2rem; text-align: center; color: white; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);">
                <h3 style="margin: 0; font-weight: 300; font-size: 2rem;">${avg_sale:.0f}</h3>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">Venta Promedio</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Espaciado final
    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)
