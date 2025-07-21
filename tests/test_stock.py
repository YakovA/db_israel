import pytest
import pytest_asyncio
import respx
import httpx
import re
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.stock_service import parse_performance

from app.core import http_client
from app.core.config import get_settings

@pytest_asyncio.fixture(autouse=True, scope="function")
async def setup_http_client():
    http_client.async_client = AsyncClient()
    yield
    http_client.async_client = None

@pytest.mark.asyncio
@respx.mock
async def test_get_stock():
    settings = get_settings()
    polygon_url = f"https://api.polygon.io/v1/open-close/IBM/2025-07-18?apiKey={settings.POLYGON_API_KEY}"

    respx.get(polygon_url).mock(
        return_value=httpx.Response(
            200,
            json={"status": "OK", "from": "2025-07-18", "symbol": "IBM", "open": 283.38, "high": 287.16, "low": 282.22, "close": 285.87, "volume": 4478165.0, "afterHours": 286.38, "preMarket": 282.5}
        )
    )
    respx.get(re.compile(r"https://www\.marketwatch\.com/investing/stock/IBM", re.IGNORECASE)).mock(
        return_value=httpx.Response(
            200,
            text="""
        <div class="element--table performance">
            <table>
                <tr class="table__row">
                    <td class="table__cell">1 Week</td>
                    <td class="table__cell"><li class="content__item value ignore-color">+2%</li></td>
                </tr>
            </table>
        </div>
        """
    )
)

    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/stock/IBM")
    assert resp.status_code == 200
    data = resp.json()
    assert data["symbol"] == "IBM"
    assert data["afterHours"] == 286.38
    assert "1 Week" in data["performance"]

@pytest.mark.asyncio
async def test_post_stock_amount():
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/stock/IBM", json={"amount": 5})
    assert response.status_code == 202
