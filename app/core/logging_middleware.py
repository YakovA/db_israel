"""
This module contains the logging middleware for the application.
"""

import logging
import time
import uuid

import structlog.contextvars
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging_config import get_logger

logger = get_logger("request")


# pylint: disable=R0903
class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests.
    """

    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = None
        status_code = 500  # Default if an error occurred

        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        structlog.contextvars.bind_contextvars(request_id=request_id)

        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Request-ID"] = request_id
        except Exception as exc:
            raise exc
        finally:
            process_time = (time.time() - start_time) * 1000
            level = logging.INFO if status_code < 500 else logging.ERROR
            structlog.get_logger().log(level, "request completed", status_code=status_code, duration=process_time)

        return response
