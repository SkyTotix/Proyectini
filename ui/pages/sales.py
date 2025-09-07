"""
Página de gestión de ventas
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from database.db_manager import db_manager
from src.models import Sale, SaleItem

def show_sales_page():
    """Muestra la página de gestión de ventas"""
    
    st.header("💰 Gestión de Ventas")
    st.markdown("---")
    
    # Inicializar carrito en session_state
    if 'cart' not in st.session_state:
        st.session_state.cart = []
    
    # Tabs para diferentes acciones
    tab1, tab2, tab3 = st.tabs([
        "🛒 Nueva Venta", 
        "📋 Historial de Ventas", 
        "📊 Estadísticas de Ventas"
    ])
    
    with tab1:
        show_new_sale()
    
    with tab2:
        show_sales_history()
    
    with tab3:
        show_sales_stats()

def show_new_sale():
    """Muestra la interfaz para crear una nueva venta"""
    st.subheader("🛒 Nueva Venta")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 🔍 Buscar Productos")
        
        # Buscar productos para agregar
        search_product = st.text_input("Buscar libro para agregar:", placeholder="Título, autor o ISBN")
        
        if search_product:
            search_results = db_manager.execute_query('''
                SELECT * FROM books 
                WHERE (title LIKE ? OR author LIKE ? OR isbn LIKE ?) 
                AND stock_quantity > 0
                ORDER BY title
            ''', (f"%{search_product}%", f"%{search_product}%", f"%{search_product}%"))
            
            if search_results:
                for book in search_results:
                    col_book, col_qty, col_btn = st.columns([3, 1, 1])
                    
                    with col_book:
                        st.write(f"**{book['title']}** - {book['author']}")
                        st.write(f"Precio: ${book['sale_price']:.2f} | Stock: {book['stock_quantity']}")
                    
                    with col_qty:
                        qty_key = f"qty_{book['id']}"
                        quantity = st.number_input("Cant.", min_value=1, max_value=book['stock_quantity'], 
                                                 key=qty_key, value=1)
                    
                    with col_btn:
                        if st.button(f"➕", key=f"add_{book['id']}"):
                            # Verificar si el libro ya está en el carrito
                            existing_item = next((item for item in st.session_state.cart 
                                                if item['book_id'] == book['id']), None)
                            
                            if existing_item:
                                existing_item['quantity'] += quantity
                                existing_item['subtotal'] = existing_item['quantity'] * existing_item['unit_price']
                            else:
                                st.session_state.cart.append({
                                    'book_id': book['id'],
                                    'title': book['title'],
                                    'author': book['author'],
                                    'unit_price': book['sale_price'],
                                    'quantity': quantity,
                                    'subtotal': book['sale_price'] * quantity
                                })
                            
                            st.success(f"✅ {book['title']} agregado al carrito")
                            st.rerun()
            else:
                st.warning("No se encontraron libros disponibles")
        
        # Mostrar carrito
        st.markdown("#### 🛒 Carrito de Compras")
        
        if st.session_state.cart:
            total_cart = 0
            items_to_remove = []
            
            for i, item in enumerate(st.session_state.cart):
                col_item, col_qty, col_price, col_remove = st.columns([3, 1, 1, 1])
                
                with col_item:
                    st.write(f"**{item['title']}**")
                    st.write(f"por {item['author']}")
                
                with col_qty:
                    new_qty = st.number_input("Cantidad", min_value=1, value=item['quantity'], key=f"cart_qty_{i}")
                    if new_qty != item['quantity']:
                        item['quantity'] = new_qty
                        item['subtotal'] = item['unit_price'] * new_qty
                
                with col_price:
                    st.write(f"${item['unit_price']:.2f}")
                    st.write(f"**${item['subtotal']:.2f}**")
                
                with col_remove:
                    if st.button("🗑️", key=f"remove_{i}"):
                        items_to_remove.append(i)
                
                total_cart += item['subtotal']
            
            # Remover items marcados
            for i in reversed(items_to_remove):
                st.session_state.cart.pop(i)
                st.rerun()
            
            st.markdown("---")
            st.markdown(f"#### 💰 Total: ${total_cart:.2f}")
            
        else:
            st.info("El carrito está vacío. Busca y agrega libros para vender.")
    
    with col2:
        st.markdown("#### 💳 Finalizar Venta")
        
        if st.session_state.cart:
            with st.form("complete_sale"):
                customer_name = st.text_input("Nombre del Cliente (opcional)")
                customer_phone = st.text_input("Teléfono del Cliente (opcional)")
                
                payment_method = st.selectbox("Método de Pago", 
                    ["Efectivo", "Tarjeta", "Transferencia", "Otro"])
                
                st.markdown("#### 💰 Ajustes de Precio")
                
                # Opción de descuento flexible
                discount_type = st.radio(
                    "Tipo de descuento:",
                    ["Porcentaje (%)", "Cantidad fija ($)"],
                    horizontal=True,
                    key="discount_type_radio"
                )
                
                # Inicializar variables
                discount = 0.0
                fixed_discount = 0.0
                
                if discount_type == "Porcentaje (%)":
                    discount = st.number_input("Descuento (%)", min_value=0.0, max_value=100.0, value=0.0, key="percent_discount")
                else:
                    fixed_discount = st.number_input("Descuento en pesos ($)", min_value=0.0, value=0.0, key="fixed_discount")
                
                # Opción de precio real de venta
                st.markdown("#### 🎯 Precio Real de Venta")
                use_real_price = st.checkbox("Usar precio real de venta (para descuentos informales)")
                
                if use_real_price:
                    st.info("💡 Puedes ajustar el precio final considerando descuentos informales")
                    real_total = st.number_input(
                        "Precio real a cobrar ($)", 
                        min_value=0.0, 
                        value=sum(item['subtotal'] for item in st.session_state.cart),
                        help="Precio final que realmente vas a cobrar al cliente"
                    )
                else:
                    real_total = sum(item['subtotal'] for item in st.session_state.cart)
                
                tax = st.number_input("Impuesto (%)", min_value=0.0, max_value=100.0, value=0.0)
                
                notes = st.text_area("Notas adicionales")
                
                # Calcular totales
                subtotal = sum(item['subtotal'] for item in st.session_state.cart)
                
                # Debug: mostrar valores
                st.info(f"🔍 **Debug:** Tipo: '{discount_type}' | Descuento: {discount}% | Fijo: ${fixed_discount}")
                
                if use_real_price:
                    # Usar precio real de venta
                    total_amount = real_total
                    discount_amount = subtotal - real_total if real_total < subtotal else 0
                    tax_amount = 0  # No aplicar impuestos adicionales si usamos precio real
                else:
                    # Cálculo normal con descuentos
                    if discount_type == "Porcentaje (%)":
                        discount_amount = subtotal * (discount / 100)
                    else:
                        discount_amount = fixed_discount  # Descuento fijo en pesos
                    
                    tax_amount = (subtotal - discount_amount) * (tax / 100)
                    total_amount = subtotal - discount_amount + tax_amount
                
                # Debug adicional para ver los cálculos
                st.warning(f"🔍 **Cálculos:** Subtotal: ${subtotal:.2f} | Descuento aplicado: ${discount_amount:.2f} | Total final: ${total_amount:.2f}")
                
                st.markdown("#### 📋 Resumen:")
                st.write(f"Subtotal: ${subtotal:.2f}")
                
                if use_real_price:
                    if real_total < subtotal:
                        st.write(f"Descuento informal: -${discount_amount:.2f}")
                    st.write(f"**Precio real a cobrar: ${total_amount:.2f}**")
                else:
                    if discount_type == "Porcentaje (%)" and discount > 0:
                        st.write(f"Descuento ({discount}%): -${discount_amount:.2f}")
                    elif discount_type == "Cantidad fija ($)" and fixed_discount > 0:
                        st.write(f"Descuento: -${discount_amount:.2f}")
                    if tax > 0:
                        st.write(f"Impuesto ({tax}%): +${tax_amount:.2f}")
                    st.write(f"**Total: ${total_amount:.2f}**")
                
                if st.form_submit_button("🎯 Completar Venta", use_container_width=True):
                    try:
                        # Crear la venta en la base de datos
                        sale_notes = notes if notes else ""
                        if use_real_price and real_total < subtotal:
                            sale_notes += f" | Precio real: ${real_total:.2f} (Descuento informal: ${discount_amount:.2f})"
                        
                        sale_id = db_manager.execute_update('''
                            INSERT INTO sales (total_amount, payment_method, customer_name,
                                             customer_phone, discount, tax, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            total_amount, payment_method, customer_name if customer_name else None,
                            customer_phone if customer_phone else None, discount_amount, tax_amount,
                            sale_notes
                        ))
                        
                        # Agregar items de la venta
                        for item in st.session_state.cart:
                            db_manager.execute_update('''
                                INSERT INTO sale_items (sale_id, book_id, quantity, unit_price, subtotal)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (sale_id, item['book_id'], item['quantity'], 
                                  item['unit_price'], item['subtotal']))
                            
                            # Actualizar stock del libro
                            db_manager.execute_update('''
                                UPDATE books SET stock_quantity = stock_quantity - ?
                                WHERE id = ?
                            ''', (item['quantity'], item['book_id']))
                            
                            # Registrar movimiento de inventario
                            db_manager.execute_update('''
                                INSERT INTO inventory_movements 
                                (book_id, movement_type, quantity, reason, reference_id)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (item['book_id'], 'OUT', item['quantity'], 
                                  f'Venta #{sale_id}', sale_id))
                        
                        st.success(f"🎉 ¡Venta completada exitosamente! ID: {sale_id}")
                        st.balloons()
                        
                        # Limpiar carrito
                        st.session_state.cart = []
                        
                        # Mostrar resumen de la venta
                        st.markdown("#### 📋 Resumen de la Venta:")
                        st.write(f"**ID de Venta:** {sale_id}")
                        st.write(f"**Total:** ${total_amount:.2f}")
                        st.write(f"**Método de Pago:** {payment_method}")
                        if customer_name:
                            st.write(f"**Cliente:** {customer_name}")
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error al procesar la venta: {str(e)}")
        else:
            st.info("Agrega productos al carrito para completar una venta")

def show_sales_history():
    """Muestra el historial de ventas"""
    st.subheader("📋 Historial de Ventas")
    
    # Filtros de fecha
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Fecha de Inicio", value=date.today().replace(day=1))
    with col2:
        end_date = st.date_input("Fecha de Fin", value=date.today())
    
    if start_date <= end_date:
        # Obtener ventas del período
        sales = db_manager.execute_query('''
            SELECT s.*, COUNT(si.id) as total_items
            FROM sales s
            LEFT JOIN sale_items si ON s.id = si.sale_id
            WHERE DATE(s.sale_date) BETWEEN ? AND ?
            GROUP BY s.id
            ORDER BY s.sale_date DESC
        ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        
        if sales:
            # Mostrar métricas
            col1, col2, col3, col4 = st.columns(4)
            
            total_sales = len(sales)
            total_revenue = sum(sale['total_amount'] for sale in sales)
            avg_sale = total_revenue / total_sales if total_sales > 0 else 0
            total_items = sum(sale['total_items'] for sale in sales)
            
            with col1:
                st.metric("🛒 Total Ventas", total_sales)
            
            with col2:
                st.metric("💰 Ingresos", f"${total_revenue:,.2f}")
            
            with col3:
                st.metric("📊 Venta Promedio", f"${avg_sale:.2f}")
            
            with col4:
                st.metric("📦 Total Items", total_items)
            
            st.markdown("---")
            
            # Tabla de ventas
            df = pd.DataFrame(sales)
            display_columns = ['id', 'sale_date', 'total_amount', 'payment_method', 'customer_name', 'total_items']
            display_df = df[display_columns].copy()
            display_df.columns = ['ID', 'Fecha', 'Total', 'Método de Pago', 'Cliente', 'Items']
            display_df['Fecha'] = pd.to_datetime(display_df['Fecha']).dt.strftime('%Y-%m-%d %H:%M')
            display_df = display_df.fillna('-')
            
            st.dataframe(display_df, use_container_width=True)
            
            # Botón para ver detalles
            selected_sale = st.selectbox("Seleccionar venta para ver detalles:", 
                                       [f"Venta #{sale['id']} - ${sale['total_amount']:.2f}" for sale in sales])
            
            if selected_sale:
                sale_id = int(selected_sale.split('#')[1].split(' ')[0])
                
                # Obtener detalles de la venta
                sale_details = db_manager.execute_query('''
                    SELECT si.*, b.title, b.author
                    FROM sale_items si
                    JOIN books b ON si.book_id = b.id
                    WHERE si.sale_id = ?
                ''', (sale_id,))
                
                if sale_details:
                    st.markdown("#### 📋 Detalles de la Venta")
                    details_df = pd.DataFrame(sale_details)
                    display_details = details_df[['title', 'author', 'quantity', 'unit_price', 'subtotal']].copy()
                    display_details.columns = ['Título', 'Autor', 'Cantidad', 'Precio Unit.', 'Subtotal']
                    
                    st.dataframe(display_details, use_container_width=True)
        
        else:
            st.info("No hay ventas en el período seleccionado")
    else:
        st.error("La fecha de inicio debe ser anterior a la fecha de fin")

def show_sales_stats():
    """Muestra estadísticas de ventas"""
    st.subheader("📊 Estadísticas de Ventas")
    
    # Filtros de fecha
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Fecha de Inicio", value=date.today().replace(day=1), key="stats_start")
    with col2:
        end_date = st.date_input("Fecha de Fin", value=date.today(), key="stats_end")
    
    if start_date <= end_date:
        # Obtener resumen de ventas
        summary = db_manager.execute_query('''
            SELECT COUNT(*) as total_sales, 
                   COALESCE(SUM(total_amount), 0) as total_revenue,
                   COALESCE(AVG(total_amount), 0) as avg_sale
            FROM sales 
            WHERE DATE(sale_date) BETWEEN ? AND ?
        ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        
        if summary:
            summary_data = summary[0]
            
            # Métricas principales
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("💰 Ingresos Totales", f"${summary_data['total_revenue']:,.2f}")
            
            with col2:
                st.metric("🛒 Total de Ventas", summary_data['total_sales'])
            
            with col3:
                st.metric("📊 Venta Promedio", f"${summary_data['avg_sale']:,.2f}")
            
            # Libros más vendidos
            top_books = db_manager.execute_query('''
                SELECT b.title, b.author, SUM(si.quantity) as total_sold
                FROM sale_items si
                JOIN books b ON si.book_id = b.id
                JOIN sales s ON si.sale_id = s.id
                WHERE DATE(s.sale_date) BETWEEN ? AND ?
                GROUP BY b.id
                ORDER BY total_sold DESC
                LIMIT 10
            ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            
            if top_books:
                st.markdown("#### 📚 Libros Más Vendidos")
                
                df_top_books = pd.DataFrame(top_books)
                df_top_books.columns = ['Título', 'Autor', 'Cantidad Vendida']
                
                st.dataframe(df_top_books, use_container_width=True)
                
                # Gráfico de barras
                st.bar_chart(df_top_books.set_index('Título')['Cantidad Vendida'])
            
            # Ventas por día
            daily_sales = db_manager.execute_query('''
                SELECT DATE(sale_date) as sale_date, 
                       COUNT(*) as sales_count,
                       SUM(total_amount) as daily_revenue
                FROM sales 
                WHERE DATE(sale_date) BETWEEN ? AND ?
                GROUP BY DATE(sale_date)
                ORDER BY sale_date
            ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            
            if daily_sales:
                st.markdown("#### 📈 Ventas por Día")
                
                df_daily = pd.DataFrame(daily_sales)
                df_daily['sale_date'] = pd.to_datetime(df_daily['sale_date'])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.line_chart(df_daily.set_index('sale_date')['daily_revenue'])
                
                with col2:
                    st.line_chart(df_daily.set_index('sale_date')['sales_count'])
        
        else:
            st.info("No hay datos de ventas en el período seleccionado")
    else:
        st.error("La fecha de inicio debe ser anterior a la fecha de fin")
