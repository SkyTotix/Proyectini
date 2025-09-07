"""
Modelos de datos para el Sistema POS
"""

from .book import Book
from .sale import Sale, SaleItem

__all__ = ['Book', 'Sale', 'SaleItem']