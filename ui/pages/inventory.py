"""
Página de gestión de inventario
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from database.db_manager import db_manager
from src.models import Book

def show_inventory_page():
    """Muestra la página de gestión de inventario"""
    
    st.header("📚 Gestión de Inventario")
    st.markdown("---")
    
    # Tabs para diferentes acciones
    tab1, tab2, tab3, tab4 = st.tabs([
        "➕ Agregar Libro", 
        "📋 Lista de Libros", 
        "🔍 Buscar Libros",
        "📊 Estadísticas"
    ])
    
    with tab1:
        show_add_book_form()
    
    with tab2:
        show_books_list()
    
    with tab3:
        show_search_books()
    
    with tab4:
        show_inventory_stats()

def show_add_book_form():
    """Muestra el formulario para agregar un libro"""
    st.subheader("➕ Agregar Nuevo Libro")
    
    with st.form("add_book_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Título *", placeholder="Ej: Cien años de soledad")
            author = st.text_input("Autor *", placeholder="Ej: Gabriel García Márquez")
            isbn = st.text_input("ISBN", placeholder="Ej: 978-84-376-0494-7")
            genre = st.selectbox("Género", [
                "", "Ficción", "No Ficción", "Romance", "Misterio", "Ciencia Ficción",
                "Fantasía", "Historia", "Biografía", "Autoayuda", "Técnico", "Infantil",
                "Juvenil", "Poesía", "Teatro", "Ensayo", "Otro"
            ])
            publisher = st.text_input("Editorial", placeholder="Ej: Editorial Sudamericana")
        
        with col2:
            publication_year = st.number_input("Año de Publicación", min_value=1000, max_value=2024, value=2020)
            purchase_price = st.number_input("Precio de Compra *", min_value=0.0, format="%.2f")
            sale_price = st.number_input("Precio de Venta *", min_value=0.0, format="%.2f")
            stock_quantity = st.number_input("Cantidad en Stock *", min_value=0, value=1)
            min_stock = st.number_input("Stock Mínimo", min_value=0, value=5)
            condition = st.selectbox("Condición", [
                "Nuevo", "Usado - Como Nuevo", "Usado - Bueno", "Usado - Regular"
            ])
        
        description = st.text_area("Descripción", placeholder="Descripción opcional del libro...")
        
        # Mostrar cálculos automáticos
        if purchase_price > 0 and sale_price > 0:
            profit = sale_price - purchase_price
            margin = (profit / purchase_price) * 100 if purchase_price > 0 else 0
            total_value = sale_price * stock_quantity
            
            col_calc1, col_calc2, col_calc3 = st.columns(3)
            with col_calc1:
                st.metric("💰 Ganancia por unidad", f"${profit:.2f}")
            with col_calc2:
                st.metric("📈 Margen de ganancia", f"{margin:.1f}%")
            with col_calc3:
                st.metric("💎 Valor total stock", f"${total_value:.2f}")
        
        submitted = st.form_submit_button("➕ Agregar Libro", use_container_width=True)
        
        if submitted:
            if title and author and purchase_price > 0 and sale_price > 0:
                try:
                    # Crear objeto Book
                    book = Book(
                        title=title,
                        author=author,
                        isbn=isbn if isbn else None,
                        genre=genre if genre else None,
                        publisher=publisher if publisher else None,
                        publication_year=publication_year,
                        purchase_price=purchase_price,
                        sale_price=sale_price,
                        stock_quantity=stock_quantity,
                        min_stock=min_stock,
                        condition=condition,
                        description=description if description else None
                    )
                    
                    # Insertar en la base de datos
                    book_id = db_manager.execute_update('''
                        INSERT INTO books (title, author, isbn, genre, publisher, 
                                         publication_year, purchase_price, sale_price, 
                                         stock_quantity, min_stock, condition, description)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        book.title, book.author, book.isbn, book.genre, book.publisher,
                        book.publication_year, book.purchase_price, book.sale_price,
                        book.stock_quantity, book.min_stock, book.condition, book.description
                    ))
                    
                    # Registrar movimiento de inventario si hay stock
                    if book.stock_quantity > 0:
                        db_manager.execute_update('''
                            INSERT INTO inventory_movements 
                            (book_id, movement_type, quantity, reason)
                            VALUES (?, ?, ?, ?)
                        ''', (book_id, 'IN', book.stock_quantity, 'Stock inicial'))
                    
                    st.success(f"✅ Libro agregado exitosamente con ID: {book_id}")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Error al agregar libro: {str(e)}")
            else:
                st.error("❌ Por favor completa todos los campos obligatorios (marcados con *)")

def show_books_list():
    """Muestra la lista de libros con filtros"""
    st.subheader("📋 Lista de Libros en Inventario")
    
    # Obtener todos los libros
    books = db_manager.execute_query("SELECT * FROM books ORDER BY title")
    
    if books:
        # Filtros
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            filter_genre = st.selectbox("Filtrar por Género", 
                ["Todos"] + list(set([book['genre'] for book in books if book['genre']])))
        
        with col2:
            filter_condition = st.selectbox("Filtrar por Condición",
                ["Todos"] + list(set([book['condition'] for book in books if book['condition']])))
        
        with col3:
            sort_by = st.selectbox("Ordenar por", 
                ["Título", "Autor", "Precio", "Stock", "Fecha"])
        
        with col4:
            show_low_stock = st.checkbox("Solo stock bajo", value=False)
        
        # Aplicar filtros
        filtered_books = books.copy()
        
        if filter_genre != "Todos":
            filtered_books = [book for book in filtered_books if book['genre'] == filter_genre]
        
        if filter_condition != "Todos":
            filtered_books = [book for book in filtered_books if book['condition'] == filter_condition]
        
        if show_low_stock:
            filtered_books = [book for book in filtered_books if book['stock_quantity'] <= book['min_stock']]
        
        # Ordenar
        if sort_by == "Título":
            filtered_books.sort(key=lambda x: x['title'])
        elif sort_by == "Autor":
            filtered_books.sort(key=lambda x: x['author'])
        elif sort_by == "Precio":
            filtered_books.sort(key=lambda x: x['sale_price'], reverse=True)
        elif sort_by == "Stock":
            filtered_books.sort(key=lambda x: x['stock_quantity'])
        elif sort_by == "Fecha":
            filtered_books.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Mostrar tabla
        if filtered_books:
            df = pd.DataFrame(filtered_books)
            
            # Seleccionar y renombrar columnas para mostrar
            display_columns = ['title', 'author', 'genre', 'sale_price', 'stock_quantity', 'condition']
            display_df = df[display_columns].copy()
            display_df.columns = ['Título', 'Autor', 'Género', 'Precio', 'Stock', 'Condición']
            
            # Agregar columna de estado de stock
            def get_stock_status(row):
                if row['Stock'] == 0:
                    return "❌ Sin stock"
                elif row['Stock'] <= 5:  # Asumiendo min_stock de 5
                    return "⚠️ Stock bajo"
                else:
                    return "✅ En stock"
            
            display_df['Estado'] = display_df.apply(get_stock_status, axis=1)
            
            st.dataframe(display_df, use_container_width=True)
            
            # Botones de acción
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 Ver Estadísticas", use_container_width=True):
                    st.session_state.show_stats = True
            
            with col2:
                if st.button("📤 Exportar CSV", use_container_width=True):
                    csv = display_df.to_csv(index=False)
                    st.download_button(
                        label="💾 Descargar CSV",
                        data=csv,
                        file_name=f"inventario_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            with col3:
                if st.button("🔄 Actualizar", use_container_width=True):
                    st.rerun()
        
        else:
            st.info("No hay libros que coincidan con los filtros seleccionados.")
    
    else:
        st.info("No hay libros en el inventario. ¡Comienza agregando algunos!")

def show_search_books():
    """Muestra la funcionalidad de búsqueda de libros"""
    st.subheader("🔍 Buscar Libros")
    
    # Barra de búsqueda
    search_query = st.text_input("🔍 Buscar por título, autor o ISBN:", placeholder="Escribe aquí...")
    
    if search_query:
        # Realizar búsqueda
        search_results = db_manager.execute_query('''
            SELECT * FROM books 
            WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?
            ORDER BY title
        ''', (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
        
        if search_results:
            st.success(f"Se encontraron {len(search_results)} resultado(s)")
            
            for book in search_results:
                with st.expander(f"📖 {book['title']} - {book['author']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Género:** {book['genre'] or 'No especificado'}")
                        st.write(f"**Editorial:** {book['publisher'] or 'No especificado'}")
                        st.write(f"**Año:** {book['publication_year'] or 'No especificado'}")
                        st.write(f"**ISBN:** {book['isbn'] or 'No especificado'}")
                        st.write(f"**Condición:** {book['condition']}")
                    
                    with col2:
                        st.write(f"**Precio de compra:** ${book['purchase_price']:.2f}")
                        st.write(f"**Precio de venta:** ${book['sale_price']:.2f}")
                        st.write(f"**Stock actual:** {book['stock_quantity']}")
                        st.write(f"**Stock mínimo:** {book['min_stock']}")
                        
                        # Indicador de stock
                        if book['stock_quantity'] <= book['min_stock']:
                            st.warning("⚠️ Stock bajo")
                        elif book['stock_quantity'] == 0:
                            st.error("❌ Sin stock")
                        else:
                            st.success("✅ En stock")
                    
                    if book['description']:
                        st.write(f"**Descripción:** {book['description']}")
                    
                    # Botones de acción
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    
                    with col_btn1:
                        if st.button(f"✏️ Editar", key=f"edit_{book['id']}"):
                            st.session_state.edit_book_id = book['id']
                    
                    with col_btn2:
                        if st.button(f"📦 Ajustar Stock", key=f"stock_{book['id']}"):
                            st.session_state.adjust_stock_id = book['id']
                    
                    with col_btn3:
                        if st.button(f"🗑️ Eliminar", key=f"delete_{book['id']}"):
                            st.session_state.delete_book_id = book['id']
        
        else:
            st.warning("No se encontraron libros que coincidan con la búsqueda")
    
    else:
        st.info("Escribe algo en el campo de búsqueda para encontrar libros")

def show_inventory_stats():
    """Muestra estadísticas del inventario"""
    st.subheader("📊 Estadísticas del Inventario")
    
    # Obtener datos
    books = db_manager.execute_query("SELECT * FROM books")
    
    if books:
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        total_books = len(books)
        total_stock = sum(book['stock_quantity'] for book in books)
        total_value = sum(book['sale_price'] * book['stock_quantity'] for book in books)
        low_stock_count = len([book for book in books if book['stock_quantity'] <= book['min_stock']])
        
        with col1:
            st.metric("📚 Total Libros", total_books)
        
        with col2:
            st.metric("📦 Stock Total", total_stock)
        
        with col3:
            st.metric("💰 Valor Total", f"${total_value:,.2f}")
        
        with col4:
            st.metric("⚠️ Stock Bajo", low_stock_count)
        
        st.markdown("---")
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribución por género
            genre_counts = {}
            for book in books:
                genre = book['genre'] or 'Sin género'
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
            
            if genre_counts:
                st.subheader("📊 Libros por Género")
                genre_df = pd.DataFrame(list(genre_counts.items()), columns=['Género', 'Cantidad'])
                st.bar_chart(genre_df.set_index('Género'))
        
        with col2:
            # Distribución por condición
            condition_counts = {}
            for book in books:
                condition = book['condition'] or 'Sin condición'
                condition_counts[condition] = condition_counts.get(condition, 0) + 1
            
            if condition_counts:
                st.subheader("📊 Libros por Condición")
                condition_df = pd.DataFrame(list(condition_counts.items()), columns=['Condición', 'Cantidad'])
                st.bar_chart(condition_df.set_index('Condición'))
        
        # Tabla de libros con stock bajo
        if low_stock_count > 0:
            st.subheader("⚠️ Libros con Stock Bajo")
            low_stock_books = [book for book in books if book['stock_quantity'] <= book['min_stock']]
            
            low_stock_df = pd.DataFrame(low_stock_books)
            display_columns = ['title', 'author', 'stock_quantity', 'min_stock', 'sale_price']
            display_df = low_stock_df[display_columns].copy()
            display_df.columns = ['Título', 'Autor', 'Stock Actual', 'Stock Mínimo', 'Precio']
            
            st.dataframe(display_df, use_container_width=True)
        
        # Top 5 libros más valiosos
        st.subheader("💎 Top 5 Libros Más Valiosos")
        books_with_value = [(book, book['sale_price'] * book['stock_quantity']) for book in books]
        books_with_value.sort(key=lambda x: x[1], reverse=True)
        
        top_books = books_with_value[:5]
        for i, (book, value) in enumerate(top_books, 1):
            st.write(f"{i}. **{book['title']}** - ${value:,.2f} (Stock: {book['stock_quantity']})")
    
    else:
        st.info("No hay libros en el inventario para mostrar estadísticas.")
