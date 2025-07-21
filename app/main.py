"""
Main application file for the DBISRAEL Stocks API.

This file creates and configures the FastAPI application.
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from httpx import AsyncClient

from app.api.v1.routers import routes_health, routes_stock
from app.core import http_client
from app.core.config import get_settings
from app.core.errors import ExternalAPIError, external_api_error_handler
from app.core.logging_config import setup_logging
from app.core.logging_middleware import LoggingMiddleware

setup_logging()

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Asynchronous context manager for the application's lifespan.
    Initializes and closes the HTTP client.
    """
    http_client.async_client = AsyncClient(timeout=settings.HTTP_TIMEOUT)
    yield
    await http_client.async_client.aclose()


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: The configured FastAPI application.
    """
    app_instance = FastAPI(
        title="DBISRAEL Stocks API", lifespan=lifespan, version="1.0.0"
    )
    app_instance.add_middleware(LoggingMiddleware)

    if settings.DEBUG:
        app_instance.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app_instance.include_router(routes_stock.router)
    app_instance.include_router(routes_health.router)

    app_instance.add_exception_handler(ExternalAPIError, external_api_error_handler)
    return app_instance


app = create_app()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
