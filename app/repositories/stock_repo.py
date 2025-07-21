"""
This module contains the StockRepo class for interacting with the stock data in memory (in-memory implementation).
"""

from typing import Optional, Dict
from ..models.stock import Stock
from .base_repo import StockRepoProtocol

class StockRepo(StockRepoProtocol):
    """
    In-memory repository for stock data, providing an interface for data operations.
    """
    def __init__(self):
        self._stocks: Dict[str, Stock] = {}

    def get(self, symbol: str) -> Optional[Stock]:
        """
        Get a stock by its symbol.
        """
        return self._stocks.get(symbol.upper())

    def upsert(self, stock: Stock) -> Stock:
        """
        Update a stock if it exists, or insert it if it does not.
        """
        self._stocks[stock.symbol.upper()] = stock
        return stock
