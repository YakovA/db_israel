"""
This module defines the Stock model for the application.
"""

from datetime import date
from typing import Optional
import json

from pydantic import field_validator, BaseModel
from sqlmodel import TEXT, Column, Field, SQLModel


class Stock(SQLModel, table=True):
    """
    Represents a stock in the database.
    """

    symbol: str = Field(primary_key=True)
    afterHours: Optional[float] = None
    close: Optional[float] = None
    from_date: Optional[date] = None
    high: Optional[float] = None
    low: Optional[float] = None
    open: Optional[float] = None
    preMarket: Optional[float] = None
    status: Optional[str] = None
    volume: Optional[int] = None
    performance: Optional[str] = Field(default=None, sa_column=Column(TEXT))
    amount: int = 0

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        """
        Validate that the amount is a non-negative number.
        """
        if v < 0:
            raise ValueError("amount must be >= 0")
        return v

    @field_validator(
        "close", "high", "low", "open", "afterHours", "preMarket", mode="before"
    )
    @classmethod
    def price_non_negative(cls, v):
        """
        Validate that price fields are non-negative.
        """
        if v is not None and v < 0:
            raise ValueError("Price fields must be >= 0")
        return v

    @property
    def performance_dict(self) -> dict:
        """
        Get the performance as a dictionary.
        """
        if self.performance:
            try:
                return json.loads(self.performance)
            except (json.JSONDecodeError, ValueError, TypeError):
                return {}
        return {}

    @performance_dict.setter
    def performance_dict(self, value: dict):
        """
        Set the performance from a dictionary.
        """
        self.performance = json.dumps(value) if value is not None else None


class AmountPayload(BaseModel):
    """
    Payload model for updating stock amount via the API.
    """
    amount: int = Field(..., ge=0)
