"""
Página de reportes y análisis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from database.db_manager import db_manager

def show_reports_page():
    """Muestra la página de reportes y análisis"""
    
    st.header("📊 Dashboard de Reportes")
    st.markdown("---")
    
    # Tabs para diferentes tipos de reportes
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Resumen General", 
        "💰 Análisis de Ventas", 
        "📚 Inventario",
        "🎯 Rendimiento"
    ])
    
    with tab1:
        show_general_summary()
    
    with tab2:
        show_sales_analysis()
    
    with tab3:
        show_inventory_analysis()
    
    with tab4:
        show_performance_analysis()

def show_general_summary():
    """Muestra el resumen general del negocio"""
    st.subheader("📈 Resumen General del Negocio")
    
    # Filtros de fecha
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Fecha de Inicio", value=date.today().replace(day=1), key="general_start")
    with col2:
        end_date = st.date_input("Fecha de Fin", value=date.today(), key="general_end")
    
    if start_date <= end_date:
        # Obtener métricas principales
        sales_data = db_manager.execute_query('''
            SELECT COUNT(*) as total_sales, 
                   COALESCE(SUM(total_amount), 0) as total_revenue,
                   COALESCE(SUM(discount), 0) as total_discounts,
                   COALESCE(AVG(total_amount), 0) as avg_sale
            FROM sales 
            WHERE DATE(sale_date) BETWEEN ? AND ?
        ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        
        # Obtener datos de inventario
        inventory_data = db_manager.execute_query('''
            SELECT COUNT(*) as total_books,
                   COALESCE(SUM(stock_quantity), 0) as total_stock,
                   COALESCE(SUM(sale_price * stock_quantity), 0) as inventory_value,
                   COUNT(CASE WHEN stock_quantity <= min_stock THEN 1 END) as low_stock_items
            FROM books
        ''')
        
        if sales_data and inventory_data:
            sales_metrics = sales_data[0]
            inventory_metrics = inventory_data[0]
            
            # Mostrar métricas principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "💰 Ingresos Totales", 
                    f"${sales_metrics['total_revenue']:,.2f}",
                    help="Ingresos totales en el período seleccionado"
                )
            
            with col2:
                st.metric(
                    "🛒 Total de Ventas", 
                    sales_metrics['total_sales'],
                    help="Número total de transacciones"
                )
            
            with col3:
                st.metric(
                    "📊 Venta Promedio", 
                    f"${sales_metrics['avg_sale']:,.2f}",
                    help="Valor promedio por venta"
                )
            
            with col4:
                st.metric(
                    "🎁 Descuentos Dados", 
                    f"${sales_metrics['total_discounts']:,.2f}",
                    help="Total de descuentos aplicados"
                )
            
            st.markdown("---")
            
            # Segunda fila de métricas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "📚 Total de Libros", 
                    inventory_metrics['total_books'],
                    help="Títulos diferentes en inventario"
                )
            
            with col2:
                st.metric(
                    "📦 Stock Total", 
                    inventory_metrics['total_stock'],
                    help="Unidades totales en stock"
                )
            
            with col3:
                st.metric(
                    "💎 Valor Inventario", 
                    f"${inventory_metrics['inventory_value']:,.2f}",
                    help="Valor total del inventario"
                )
            
            with col4:
                st.metric(
                    "⚠️ Stock Bajo", 
                    inventory_metrics['low_stock_items'],
                    help="Libros con stock bajo"
                )
            
            # Gráfico de ventas por día
            daily_sales = db_manager.execute_query('''
                SELECT DATE(sale_date) as date, 
                       COUNT(*) as sales_count,
                       SUM(total_amount) as daily_revenue
                FROM sales 
                WHERE DATE(sale_date) BETWEEN ? AND ?
                GROUP BY DATE(sale_date)
                ORDER BY date
            ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            
            if daily_sales:
                st.markdown("### 📈 Tendencia de Ventas Diarias")
                df_daily = pd.DataFrame(daily_sales)
                df_daily['date'] = pd.to_datetime(df_daily['date'])
                
                fig = px.line(df_daily, x='date', y='daily_revenue', 
                             title='Ingresos por Día',
                             labels={'daily_revenue': 'Ingresos ($)', 'date': 'Fecha'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.error("La fecha de inicio debe ser anterior a la fecha de fin")

def show_sales_analysis():
    """Muestra análisis detallado de ventas"""
    st.subheader("💰 Análisis de Ventas")
    
    # Filtros de fecha
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Fecha de Inicio", value=date.today().replace(day=1), key="sales_start")
    with col2:
        end_date = st.date_input("Fecha de Fin", value=date.today(), key="sales_end")
    
    if start_date <= end_date:
        # Libros más vendidos
        top_books = db_manager.execute_query('''
            SELECT b.title, b.author, b.sale_price,
                   SUM(si.quantity) as total_sold,
                   SUM(si.subtotal) as total_revenue,
                   COUNT(DISTINCT s.id) as num_sales
            FROM sale_items si
            JOIN books b ON si.book_id = b.id
            JOIN sales s ON si.sale_id = s.id
            WHERE DATE(s.sale_date) BETWEEN ? AND ?
            GROUP BY b.id
            ORDER BY total_sold DESC
            LIMIT 10
        ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        
        if top_books:
            st.markdown("### 🏆 Libros Más Vendidos")
            
            df_top = pd.DataFrame(top_books)
            df_top.columns = ['Título', 'Autor', 'Precio', 'Cantidad Vendida', 'Ingresos', 'Num. Ventas']
            df_top['Precio'] = df_top['Precio'].apply(lambda x: f"${x:.2f}")
            df_top['Ingresos'] = df_top['Ingresos'].apply(lambda x: f"${x:.2f}")
            
            st.dataframe(df_top, use_container_width=True)
            
            # Gráfico de barras
            fig = px.bar(df_top.head(5), x='Título', y='Cantidad Vendida',
                        title='Top 5 Libros Más Vendidos',
                        labels={'Cantidad Vendida': 'Unidades Vendidas'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Análisis por método de pago
        payment_analysis = db_manager.execute_query('''
            SELECT payment_method, 
                   COUNT(*) as num_sales,
                   SUM(total_amount) as total_revenue
            FROM sales 
            WHERE DATE(sale_date) BETWEEN ? AND ?
            GROUP BY payment_method
            ORDER BY total_revenue DESC
        ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        
        if payment_analysis:
            st.markdown("### 💳 Análisis por Método de Pago")
            
            df_payment = pd.DataFrame(payment_analysis)
            df_payment.columns = ['Método de Pago', 'Número de Ventas', 'Ingresos Totales']
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de pastel
                fig_pie = px.pie(df_payment, values='Ingresos Totales', names='Método de Pago',
                                title='Distribución de Ingresos por Método de Pago')
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.dataframe(df_payment, use_container_width=True)
    
    else:
        st.error("La fecha de inicio debe ser anterior a la fecha de fin")

def show_inventory_analysis():
    """Muestra análisis del inventario"""
    st.subheader("📚 Análisis de Inventario")
    
    # Libros con stock bajo
    low_stock = db_manager.execute_query('''
        SELECT title, author, stock_quantity, min_stock, sale_price
        FROM books 
        WHERE stock_quantity <= min_stock
        ORDER BY stock_quantity ASC
    ''')
    
    if low_stock:
        st.markdown("### ⚠️ Libros con Stock Bajo")
        df_low = pd.DataFrame(low_stock)
        df_low.columns = ['Título', 'Autor', 'Stock Actual', 'Stock Mínimo', 'Precio']
        df_low['Precio'] = df_low['Precio'].apply(lambda x: f"${x:.2f}")
        
        st.dataframe(df_low, use_container_width=True)
        
        if len(df_low) > 0:
            st.warning(f"⚠️ Tienes {len(df_low)} libro(s) con stock bajo. ¡Considera reabastecerlos!")
    else:
        st.success("✅ Todos los libros tienen stock suficiente")
    
    # Distribución por género
    genre_distribution = db_manager.execute_query('''
        SELECT genre, 
               COUNT(*) as num_books,
               SUM(stock_quantity) as total_stock,
               SUM(sale_price * stock_quantity) as total_value
        FROM books 
        GROUP BY genre
        ORDER BY total_value DESC
    ''')
    
    if genre_distribution:
        st.markdown("### 📖 Distribución por Género")
        
        df_genre = pd.DataFrame(genre_distribution)
        df_genre.columns = ['Género', 'Número de Títulos', 'Stock Total', 'Valor Total']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de barras
            fig_genre = px.bar(df_genre, x='Género', y='Valor Total',
                              title='Valor del Inventario por Género')
            fig_genre.update_layout(height=400)
            st.plotly_chart(fig_genre, use_container_width=True)
        
        with col2:
            df_genre['Valor Total'] = df_genre['Valor Total'].apply(lambda x: f"${x:.2f}")
            st.dataframe(df_genre, use_container_width=True)
    
    # Libros más valiosos
    valuable_books = db_manager.execute_query('''
        SELECT title, author, sale_price, stock_quantity,
               (sale_price * stock_quantity) as total_value
        FROM books 
        ORDER BY total_value DESC
        LIMIT 10
    ''')
    
    if valuable_books:
        st.markdown("### 💎 Libros Más Valiosos (por valor total en stock)")
        
        df_valuable = pd.DataFrame(valuable_books)
        df_valuable.columns = ['Título', 'Autor', 'Precio Unit.', 'Stock', 'Valor Total']
        df_valuable['Precio Unit.'] = df_valuable['Precio Unit.'].apply(lambda x: f"${x:.2f}")
        df_valuable['Valor Total'] = df_valuable['Valor Total'].apply(lambda x: f"${x:.2f}")
        
        st.dataframe(df_valuable, use_container_width=True)

def show_performance_analysis():
    """Muestra análisis de rendimiento"""
    st.subheader("🎯 Análisis de Rendimiento")
    
    # Filtros de fecha
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Fecha de Inicio", value=date.today().replace(day=1), key="perf_start")
    with col2:
        end_date = st.date_input("Fecha de Fin", value=date.today(), key="perf_end")
    
    if start_date <= end_date:
        # Análisis de ganancias (solo para libros con precio de compra)
        profit_analysis = db_manager.execute_query('''
            SELECT b.title, b.author, b.purchase_price, b.sale_price,
                   (b.sale_price - b.purchase_price) as profit_per_unit,
                   SUM(si.quantity) as units_sold,
                   SUM(si.quantity * (b.sale_price - b.purchase_price)) as total_profit
            FROM sale_items si
            JOIN books b ON si.book_id = b.id
            JOIN sales s ON si.sale_id = s.id
            WHERE DATE(s.sale_date) BETWEEN ? AND ?
              AND b.purchase_price > 0
            GROUP BY b.id
            ORDER BY total_profit DESC
            LIMIT 10
        ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        
        if profit_analysis:
            st.markdown("### 💰 Libros Más Rentables")
            st.info("💡 Solo se muestran libros con precio de compra registrado")
            
            df_profit = pd.DataFrame(profit_analysis)
            df_profit.columns = ['Título', 'Autor', 'Precio Compra', 'Precio Venta', 
                               'Ganancia/Unidad', 'Unidades Vendidas', 'Ganancia Total']
            
            # Formatear precios
            for col in ['Precio Compra', 'Precio Venta', 'Ganancia/Unidad', 'Ganancia Total']:
                df_profit[col] = df_profit[col].apply(lambda x: f"${x:.2f}")
            
            st.dataframe(df_profit, use_container_width=True)
            
            # Calcular ganancia total del período
            total_profit = sum([float(row['total_profit']) for row in profit_analysis])
            st.metric("🎯 Ganancia Total del Período", f"${total_profit:.2f}")
        
        else:
            st.warning("⚠️ No hay datos de ganancias disponibles. Asegúrate de registrar el precio de compra de los libros.")
        
        # Comparación con período anterior
        days_diff = (end_date - start_date).days
        previous_start = start_date - timedelta(days=days_diff + 1)
        previous_end = start_date - timedelta(days=1)
        
        current_period = db_manager.execute_query('''
            SELECT COUNT(*) as sales, SUM(total_amount) as revenue
            FROM sales 
            WHERE DATE(sale_date) BETWEEN ? AND ?
        ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        
        previous_period = db_manager.execute_query('''
            SELECT COUNT(*) as sales, SUM(total_amount) as revenue
            FROM sales 
            WHERE DATE(sale_date) BETWEEN ? AND ?
        ''', (previous_start.strftime('%Y-%m-%d'), previous_end.strftime('%Y-%m-%d')))
        
        if current_period and previous_period:
            current = current_period[0]
            previous = previous_period[0]
            
            st.markdown("### 📊 Comparación con Período Anterior")
            
            col1, col2 = st.columns(2)
            
            with col1:
                sales_change = current['sales'] - previous['sales'] if previous['sales'] else current['sales']
                sales_pct = (sales_change / previous['sales'] * 100) if previous['sales'] > 0 else 0
                
                st.metric(
                    "Ventas vs Período Anterior",
                    current['sales'],
                    delta=f"{sales_change} ({sales_pct:+.1f}%)"
                )
            
            with col2:
                revenue_change = (current['revenue'] or 0) - (previous['revenue'] or 0)
                revenue_pct = (revenue_change / previous['revenue'] * 100) if previous['revenue'] and previous['revenue'] > 0 else 0
                
                st.metric(
                    "Ingresos vs Período Anterior",
                    f"${current['revenue'] or 0:.2f}",
                    delta=f"${revenue_change:.2f} ({revenue_pct:+.1f}%)"
                )
    
    else:
        st.error("La fecha de inicio debe ser anterior a la fecha de fin")
