"""
This module defines custom exception classes and their handlers.
"""

from fastapi import Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse


class ExternalAPIError(HTTPException):
    """
    Custom exception for errors related to external API calls.
    """

    def __init__(self, detail: str = "Failed to fetch external API"):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)


async def external_api_error_handler(_: Request, exc: ExternalAPIError):
    """
    Exception handler for ExternalAPIError.
    """
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
