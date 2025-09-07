"""
Gestor de Base de Datos SQLite para el Sistema POS
Maneja la creación, conexión y operaciones de la base de datos
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor principal de la base de datos SQLite"""
    
    def __init__(self, db_path: str = "data/bookstore.db"):
        """
        Inicializa el gestor de base de datos
        
        Args:
            db_path (str): Ruta donde se guardará la base de datos
        """
        self.db_path = db_path
        self.ensure_data_directory()
        self.init_database()
        logger.info(f"Base de datos inicializada en: {self.db_path}")
    
    def ensure_data_directory(self):
        """Asegura que el directorio de datos existe"""
        data_dir = Path(self.db_path).parent
        data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directorio de datos creado: {data_dir}")
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Obtiene una conexión a la base de datos
        
        Returns:
            sqlite3.Connection: Conexión a la base de datos
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
        return conn
    
    def init_database(self):
        """Inicializa las tablas de la base de datos"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabla de libros
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    isbn TEXT UNIQUE,
                    genre TEXT,
                    publisher TEXT,
                    publication_year INTEGER,
                    purchase_price REAL NOT NULL,
                    sale_price REAL NOT NULL,
                    stock_quantity INTEGER NOT NULL DEFAULT 0,
                    min_stock INTEGER DEFAULT 5,
                    condition TEXT DEFAULT 'Nuevo',
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de ventas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_amount REAL NOT NULL,
                    payment_method TEXT DEFAULT 'Efectivo',
                    customer_name TEXT,
                    customer_phone TEXT,
                    discount REAL DEFAULT 0,
                    tax REAL DEFAULT 0,
                    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            ''')
            
            # Tabla de items de venta
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sale_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id INTEGER NOT NULL,
                    book_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY (sale_id) REFERENCES sales (id) ON DELETE CASCADE,
                    FOREIGN KEY (book_id) REFERENCES books (id)
                )
            ''')
            
            # Tabla de movimientos de inventario
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory_movements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL,
                    movement_type TEXT NOT NULL, -- 'IN', 'OUT', 'ADJUSTMENT'
                    quantity INTEGER NOT NULL,
                    reason TEXT,
                    reference_id INTEGER, -- ID de venta si aplica
                    movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (book_id) REFERENCES books (id)
                )
            ''')
            
            # Tabla de configuración del sistema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    description TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insertar configuración inicial
            cursor.execute('''
                INSERT OR IGNORE INTO system_config (key, value, description) VALUES
                ('app_name', 'Sistema POS - Librería Callejera', 'Nombre de la aplicación'),
                ('version', '1.0.0', 'Versión actual del sistema'),
                ('currency', 'MXN', 'Moneda del sistema'),
                ('tax_rate', '0.16', 'Tasa de impuestos (IVA)'),
                ('min_stock_alert', '5', 'Stock mínimo para alertas')
            ''')
            
            conn.commit()
            logger.info("Esquema de base de datos creado exitosamente")
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict]:
        """
        Ejecuta una consulta SELECT y retorna los resultados
        
        Args:
            query (str): Consulta SQL
            params (Tuple): Parámetros para la consulta
            
        Returns:
            List[Dict]: Lista de diccionarios con los resultados
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error ejecutando consulta: {e}")
            return []
    
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """
        Ejecuta una consulta de actualización (INSERT, UPDATE, DELETE)
        
        Args:
            query (str): Consulta SQL
            params (Tuple): Parámetros para la consulta
            
        Returns:
            int: ID del último registro insertado o número de filas afectadas
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
        except Exception as e:
            logger.error(f"Error ejecutando actualización: {e}")
            return 0
    
    def get_system_config(self, key: str) -> Optional[str]:
        """
        Obtiene un valor de configuración del sistema
        
        Args:
            key (str): Clave de configuración
            
        Returns:
            Optional[str]: Valor de la configuración o None si no existe
        """
        result = self.execute_query(
            "SELECT value FROM system_config WHERE key = ?", 
            (key,)
        )
        return result[0]['value'] if result else None
    
    def set_system_config(self, key: str, value: str, description: str = None):
        """
        Establece un valor de configuración del sistema
        
        Args:
            key (str): Clave de configuración
            value (str): Valor a establecer
            description (str): Descripción opcional
        """
        self.execute_update(
            """INSERT OR REPLACE INTO system_config (key, value, description, updated_at) 
               VALUES (?, ?, ?, CURRENT_TIMESTAMP)""",
            (key, value, description)
        )
    
    def backup_database(self, backup_path: str = None) -> str:
        """
        Crea una copia de seguridad de la base de datos
        
        Args:
            backup_path (str): Ruta donde guardar el backup
            
        Returns:
            str: Ruta del archivo de backup creado
        """
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backups/bookstore_backup_{timestamp}.db"
        
        # Crear directorio de backups si no existe
        Path(backup_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Copiar la base de datos
        import shutil
        shutil.copy2(self.db_path, backup_path)
        
        logger.info(f"Backup creado en: {backup_path}")
        return backup_path
    
    def get_database_info(self) -> Dict:
        """
        Obtiene información sobre la base de datos
        
        Returns:
            Dict: Información de la base de datos
        """
        info = {
            'path': self.db_path,
            'size': os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0,
            'exists': os.path.exists(self.db_path)
        }
        
        if info['exists']:
            # Contar registros en cada tabla
            tables = ['books', 'sales', 'sale_items', 'inventory_movements']
            for table in tables:
                result = self.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                info[f'{table}_count'] = result[0]['count'] if result else 0
        
        return info

# Instancia global del gestor de base de datos
db_manager = DatabaseManager()
