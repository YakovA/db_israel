"""
This module contains the business logic for fetching and managing stock data.
"""
import asyncio
from typing import Dict
from datetime import date, timedelta

import cachetools
from bs4 import BeautifulSoup
from fastapi import Depends

from app.core.config import get_settings
from app.core.errors import ExternalAPIError
from app.core.http_client import get_client
from app.core.logging_config import get_logger
from app.models.stock import Stock
from app.dependencies.repo import get_repo
from app.repositories.base_repo import StockRepoProtocol

settings = get_settings()
_cache = cachetools.TTLCache(maxsize=1024, ttl=settings.CACHE_TTL)

POLYGON_URL = settings.POLYGON_URL
MWATCH_URL = settings.MWATCH_URL

logger = get_logger(__name__)


async def fetch_polygon(symbol: str) -> Stock:
    """
    Fetch stock data from the Polygon API.

    Args:
        symbol (str): The stock symbol.

    Raises:
        ExternalAPIError: If the API call fails.

    Returns:
        Stock: A dictionary containing the stock data from Polygon.
    """
    logger.info("Fetching polygon data", symbol=symbol)
    last_trade_date = date.today() - timedelta(days=1)
    url = POLYGON_URL.format(symbol=symbol.upper(), key=settings.POLYGON_API_KEY, last_trade_day=last_trade_date.strftime("%Y-%m-%d"))
    client = get_client()
    r = await client.get(url)
    if r.status_code != 200:
        logger.error("Polygon API error", status_code=r.status_code, url=url)
        raise ExternalAPIError(f"Polygon returned {r.status_code}")
    data = r.json()
    if data.get("status") != "OK":
        logger.warning("No data from Polygon", symbol=symbol)
        raise ExternalAPIError("No data from Polygon")

    logger.info("Polygon data fetched", symbol=symbol, result=data)

    def to_float(val):
        try:
            return float(val) if val is not None else None
        except (ValueError, TypeError):
            return None

    def to_int(val):
        try:
            return int(val) if val is not None else None
        except (ValueError, TypeError):
            return None

    def to_date(val):
        try:
            return date.fromisoformat(val) if val else None
        except (ValueError, TypeError):
            return None

    return {
        "afterHours": to_float(data.get("afterHours")),
        "close": to_float(data.get("close")),
        "from_date": to_date(data.get("from")),
        "high": to_float(data.get("high")),
        "low": to_float(data.get("low")),
        "open": to_float(data.get("open")),
        "preMarket": to_float(data.get("preMarket")),
        "status": data.get("status"),
        "volume": to_int(data.get("volume")),
    }

async def parse_html_async(html: str):
    """
    Parse the performance data from the MarketWatch HTML.
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, parse_performance, html)

def parse_performance(html: str) -> dict:
    """
    Parse the performance data from the MarketWatch HTML.

    Args:
        html (str): The HTML content of the MarketWatch page.

    Returns:
        dict: A dictionary containing the performance data.
    """
    soup = BeautifulSoup(html, "lxml")
    perf = {}

    # Search for Performance
    table_container = soup.select_one("div.element--table.performance")
    if not table_container:
        return perf

    # Iterate over the rows in the table
    rows = table_container.find_all("tr", class_="table__row")
    for row in rows:
        cells = row.find_all("td", class_="table__cell")
        if len(cells) != 2:
            continue
        label = cells[0].get_text(strip=True)
        value_elem = cells[1].find("li", class_="content__item value ignore-color")
        if value_elem:
            value = value_elem.get_text(strip=True)
            perf[label] = value

    return perf


async def fetch_marketwatch(symbol: str) -> Dict:
    """
    Fetch stock performance data from MarketWatch.

    Args:
        symbol (str): The stock symbol.

    Raises:
        ExternalAPIError: If the API call fails.

    Returns:
        Dict: A dictionary containing the stock's performance data.
    """
    logger.info("Fetching marketwatch data", symbol=symbol)
    url = MWATCH_URL.format(symbol=symbol.upper())
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }
    client = get_client()
    r = await client.get(url, headers=headers)
    if r.status_code != 200:
        logger.error("Marketwatch API error", status_code=r.status_code, url=url)
        raise ExternalAPIError(f"Marketwatch returned {r.status_code}")
    html = r.text
    performance = await parse_html_async(html)
    logger.info("Marketwatch data fetched", symbol=symbol, performance=performance)
    return {"performance": performance}


async def get_stock(symbol: str, repo: StockRepoProtocol = Depends(get_repo)) -> Stock:
    """
    Get stock data from cache or by fetching from external APIs.

    Args:
        symbol (str): The stock symbol.

    Returns:
        Stock: The stock object.
    """
    if symbol in _cache:
        return _cache[symbol]

    polygon_coro = fetch_polygon(symbol)
    mw_coro = fetch_marketwatch(symbol)
    polygon_data, perf_data = await asyncio.gather(polygon_coro, mw_coro)

    stock = repo.get(symbol) or Stock(symbol=symbol.upper())
    for k, v in polygon_data.items():
        setattr(stock, k, v)
    stock.performance_dict = perf_data.get("performance", {})

    _cache[symbol] = stock
    return stock


async def update_amount(symbol: str, delta: int, repo: StockRepoProtocol = Depends(get_repo)) -> Stock:
    """
    Update the amount of a stock.

    Args:
        symbol (str): The stock symbol.
        delta (int): The change in amount.

    Returns:
        Stock: The updated stock object.
    """
    stock = await get_stock(symbol, repo)
    stock.amount += delta
    _cache[symbol] = stock
    return stock
