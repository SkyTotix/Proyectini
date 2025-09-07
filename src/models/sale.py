"""
Modelo de datos para ventas
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime

@dataclass
class SaleItem:
    """Modelo de datos para un item de venta"""
    
    book_id: int
    quantity: int
    unit_price: float
    
    # Campos calculados
    subtotal: float = field(init=False)
    
    def __post_init__(self):
        """Calcula el subtotal después de la inicialización"""
        self.subtotal = self.quantity * self.unit_price
    
    def to_dict(self) -> dict:
        """Convierte el objeto a diccionario"""
        return {
            'book_id': self.book_id,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'subtotal': self.subtotal
        }

@dataclass
class Sale:
    """Modelo de datos para una venta"""
    
    # Campos obligatorios
    total_amount: float
    items: List[SaleItem]
    
    # Campos opcionales
    id: Optional[int] = None
    payment_method: str = "Efectivo"
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    discount: float = 0.0
    tax: float = 0.0
    sale_date: Optional[datetime] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Validaciones después de la inicialización"""
        if self.total_amount < 0:
            raise ValueError("El monto total no puede ser negativo")
        if self.discount < 0:
            raise ValueError("El descuento no puede ser negativo")
        if self.tax < 0:
            raise ValueError("El impuesto no puede ser negativo")
        if not self.items:
            raise ValueError("La venta debe tener al menos un item")
    
    @property
    def subtotal(self) -> float:
        """Calcula el subtotal de todos los items"""
        return sum(item.subtotal for item in self.items)
    
    @property
    def discount_amount(self) -> float:
        """Calcula el monto del descuento"""
        return self.subtotal * (self.discount / 100)
    
    @property
    def tax_amount(self) -> float:
        """Calcula el monto del impuesto"""
        return (self.subtotal - self.discount_amount) * (self.tax / 100)
    
    @property
    def final_total(self) -> float:
        """Calcula el total final"""
        return self.subtotal - self.discount_amount + self.tax_amount
    
    @property
    def total_items(self) -> int:
        """Calcula el total de items vendidos"""
        return sum(item.quantity for item in self.items)
    
    def add_item(self, book_id: int, quantity: int, unit_price: float):
        """Agrega un item a la venta"""
        item = SaleItem(book_id=book_id, quantity=quantity, unit_price=unit_price)
        self.items.append(item)
        # Recalcular total
        self.total_amount = self.final_total
    
    def remove_item(self, book_id: int):
        """Remueve un item de la venta"""
        self.items = [item for item in self.items if item.book_id != book_id]
        # Recalcular total
        self.total_amount = self.final_total
    
    def update_item_quantity(self, book_id: int, new_quantity: int):
        """Actualiza la cantidad de un item"""
        for item in self.items:
            if item.book_id == book_id:
                item.quantity = new_quantity
                item.subtotal = item.quantity * item.unit_price
                break
        # Recalcular total
        self.total_amount = self.final_total
    
    def to_dict(self) -> dict:
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id,
            'total_amount': self.total_amount,
            'payment_method': self.payment_method,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'discount': self.discount,
            'tax': self.tax,
            'sale_date': self.sale_date,
            'notes': self.notes,
            'items': [item.to_dict() for item in self.items]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Sale':
        """Crea un objeto Sale desde un diccionario"""
        items = [SaleItem(**item) for item in data.get('items', [])]
        return cls(
            id=data.get('id'),
            total_amount=data['total_amount'],
            items=items,
            payment_method=data.get('payment_method', 'Efectivo'),
            customer_name=data.get('customer_name'),
            customer_phone=data.get('customer_phone'),
            discount=data.get('discount', 0.0),
            tax=data.get('tax', 0.0),
            sale_date=data.get('sale_date'),
            notes=data.get('notes')
        )
    
    def __str__(self) -> str:
        """Representación string de la venta"""
        return f"Venta #{self.id} - ${self.total_amount:.2f} ({self.total_items} items)"
    
    def __repr__(self) -> str:
        """Representación para debugging"""
        return f"Sale(id={self.id}, total={self.total_amount}, items={len(self.items)})"
