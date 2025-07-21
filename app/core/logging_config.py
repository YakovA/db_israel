"""
This module configures the logging for the application using structlog.
"""

from logging.config import dictConfig

import structlog

from app.core.config import get_settings

settings = get_settings()


def setup_logging():
    """
    Set up the logging configuration for the application.

    The log format is set to JSON for production and a more readable console format for development.
    """
    # If DEV then colorful, if PROD then JSON
    renderer = (
        structlog.dev.ConsoleRenderer()
        if settings.DEBUG
        else structlog.processors.JSONRenderer()
    )

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "structlog": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": renderer,
                "foreign_pre_chain": [
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.add_logger_name,
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                ],
            },
        },
        "handlers": {
            "default": {
                "level": "DEBUG" if settings.DEBUG else "INFO",
                "class": "logging.StreamHandler",
                "formatter": "structlog",
            },
        },
        "root": {
            "handlers": ["default"],
            "level": "DEBUG" if settings.DEBUG else "INFO",
        },
    }

    dictConfig(logging_config)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.CallsiteParameterAdder(),
            renderer,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name=None):
    """
    Get a logger instance.

    Args:
        name (str, optional): The name of the logger. Defaults to None.

    Returns:
        The logger instance.
    """
    return structlog.get_logger(name)
