"""
This module manages the application's HTTP client.
"""

# app/core/http_client.py
from httpx import AsyncClient

async_client: AsyncClient | None = None


def get_client() -> AsyncClient:
    """
    Get the HTTP client.

    Raises:
        RuntimeError: If the client is not initialized.

    Returns:
        AsyncClient: The HTTP client instance.
    """
    if async_client is None:
        raise RuntimeError("Client not initialized!")
    return async_client
