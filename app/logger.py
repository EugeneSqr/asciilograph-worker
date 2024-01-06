import logging
from logging.config import dictConfig
from time import gmtime
from contextvars import ContextVar
from typing import Optional

_DEFAULT_CORRELATION_ID = "-"

_correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id")

class CorrelationIdFilter(logging.Filter):
    def __init__(self, name: str = ""):
        super().__init__(name=name)

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = _correlation_id.get(_DEFAULT_CORRELATION_ID)
        return True

def set_correlation_id(correlation_id: Optional[str]) -> None:
    _correlation_id.set(_DEFAULT_CORRELATION_ID if correlation_id is None else correlation_id)

def configure_logging() -> None:
    format_string = "[%(levelname)s] [%(asctime)s.%(msecs)03dZ] [%(correlation_id)s] %(message)s"
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "correlation_id": {
                "()": "logger.CorrelationIdFilter",
            },
        },
        "formatters": {
            "default": {
                "()": "logging.Formatter",
                "fmt": format_string,
                "datefmt": "%Y-%m-%dT%H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "filters": ["correlation_id"],
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": {
            "root": {"handlers": ["default"], "level": "INFO"},
        },
    })
    logging.Formatter.converter = gmtime
