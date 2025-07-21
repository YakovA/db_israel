"""
This module contains the configuration settings for the application.
"""

from functools import lru_cache

from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables and a .env file.
    """

    POLYGON_API_KEY: str = Field(..., min_length=32, description="API Key for Polygon")
    DEBUG: bool = False
    HTTP_TIMEOUT: int = 10
    CACHE_TTL: int = 60
    POLYGON_URL: str
    MWATCH_URL: str
    model_config = ConfigDict(env_file=".env")

    # pylint: disable=R0903


@lru_cache
def get_settings() -> "Settings":
    """
    Get the application settings.

    This function is cached to avoid reloading the settings multiple times.

    Returns:
        Settings: The application settings object.
    """
    return Settings()
