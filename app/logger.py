import logging
from logging.config import dictConfig
from time import gmtime
from typing import Optional

class CorrelationIdFilter(logging.Filter):
    def __init__(self, name: str = "", default_value: Optional[str] = None):
        super().__init__(name=name)
        self.default_value = default_value

    def filter(self, record: logging.LogRecord) -> bool:
        cid = "aaa"
        #cid = correlation_id.get(self.default_value)
        record.correlation_id = cid
        return True

def configure_logging() -> None:
    format_string = "[%(levelname)s] [%(asctime)s.%(msecs)03dZ] [%(correlation_id)s] %(message)s"
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "correlation_id": {
                "()": "logger.CorrelationIdFilter",
                "default_value": "-",
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
