"""
This module contains health check endpoints for the service.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session


router = APIRouter(prefix="", tags=["health"])


@router.get("/healthz", include_in_schema=False)
async def healthz():
    """
    Simple health check endpoint.
    """
    return JSONResponse(content={"status": "ok"})


@router.get("/readyz", include_in_schema=False)
async def readyz():
    """
    Readiness probe endpoint. 
    """
    return JSONResponse(content={"status": "ok", "database": "not checked"}, status_code=200)
