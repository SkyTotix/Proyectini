"""
Modelo de datos para libros
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class Book:
    """Modelo de datos para un libro"""
    
    # Campos obligatorios
    title: str
    author: str
    purchase_price: float
    sale_price: float
    stock_quantity: int
    
    # Campos opcionales
    id: Optional[int] = None
    isbn: Optional[str] = None
    genre: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    min_stock: int = 5
    condition: str = "Nuevo"
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validaciones después de la inicialización"""
        if self.purchase_price < 0:
            raise ValueError("El precio de compra no puede ser negativo")
        if self.sale_price < 0:
            raise ValueError("El precio de venta no puede ser negativo")
        if self.stock_quantity < 0:
            raise ValueError("La cantidad en stock no puede ser negativa")
        if self.min_stock < 0:
            raise ValueError("El stock mínimo no puede ser negativo")
    
    @property
    def profit_margin(self) -> float:
        """Calcula el margen de ganancia"""
        if self.purchase_price == 0:
            return 0
        return ((self.sale_price - self.purchase_price) / self.purchase_price) * 100
    
    @property
    def total_value(self) -> float:
        """Calcula el valor total del stock"""
        return self.sale_price * self.stock_quantity
    
    @property
    def is_low_stock(self) -> bool:
        """Verifica si el stock está bajo"""
        return self.stock_quantity <= self.min_stock
    
    @property
    def is_out_of_stock(self) -> bool:
        """Verifica si no hay stock"""
        return self.stock_quantity == 0
    
    def to_dict(self) -> dict:
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'genre': self.genre,
            'publisher': self.publisher,
            'publication_year': self.publication_year,
            'purchase_price': self.purchase_price,
            'sale_price': self.sale_price,
            'stock_quantity': self.stock_quantity,
            'min_stock': self.min_stock,
            'condition': self.condition,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Book':
        """Crea un objeto Book desde un diccionario"""
        return cls(
            id=data.get('id'),
            title=data['title'],
            author=data['author'],
            isbn=data.get('isbn'),
            genre=data.get('genre'),
            publisher=data.get('publisher'),
            publication_year=data.get('publication_year'),
            purchase_price=data['purchase_price'],
            sale_price=data['sale_price'],
            stock_quantity=data['stock_quantity'],
            min_stock=data.get('min_stock', 5),
            condition=data.get('condition', 'Nuevo'),
            description=data.get('description'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def __str__(self) -> str:
        """Representación string del libro"""
        return f"{self.title} - {self.author} (Stock: {self.stock_quantity})"
    
    def __repr__(self) -> str:
        """Representación para debugging"""
        return f"Book(id={self.id}, title='{self.title}', author='{self.author}')"
