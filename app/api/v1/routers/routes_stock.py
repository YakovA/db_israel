"""
This module contains API endpoints for stock-related operations.
"""

from fastapi import APIRouter, Body, Path, status, Depends

from app.models.stock import Stock, AmountPayload
from app.services.stock_service import get_stock, update_amount
from app.dependencies.repo import get_repo
from app.repositories.stock_repo import StockRepo

router = APIRouter(prefix="/stock", tags=["stock"])


@router.get("/{symbol}", response_model=Stock)
async def get_stock_endpoint(
    symbol: str = Path(..., description="Ticker symbol"),
    repo: StockRepo = Depends(get_repo),
):
    """
    Get stock information by its symbol.
    """
    return await get_stock(symbol, repo)


@router.post("/{symbol}", response_model=Stock, status_code=status.HTTP_202_ACCEPTED)
async def update_amount_endpoint(
    symbol: str = Path(...),
    payload: AmountPayload = Body(..., example={"amount": 10}),
    repo: StockRepo = Depends(get_repo),
):
    """
    Update the amount of a stock.
    """

    delta = payload.amount
    return await update_amount(symbol, delta, repo)
