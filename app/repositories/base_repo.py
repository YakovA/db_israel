"""
This module contains the base protocol for the stock repository.
"""

from typing import Protocol, Optional
from app.models.stock import Stock

class StockRepoProtocol(Protocol):
    """
    Protocol for the stock repository.
    """
    def get(self, symbol: str) -> Optional[Stock]:
        """
        Get a stock by its symbol.
        """

    def upsert(self, stock: Stock) -> Stock:
        """
        Upsert a stock into the repository.
        """
