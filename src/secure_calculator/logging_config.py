"""Minimal structured logging without request values or other sensitive data."""

import json
import logging
import sys
import time
from typing import Any


class JsonFormatter(logging.Formatter):
    """Emit stable JSON records containing only approved fields."""

    def converter(self, timestamp: float | None) -> time.struct_time:
        """Convert a logging timestamp to UTC with an explicit stable type."""
        return time.gmtime(timestamp)

    def format(self, record: logging.LogRecord) -> str:
        event: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(event, separators=(",", ":"), ensure_ascii=True)


def configure_logging(level: int = logging.WARNING) -> None:
    """Configure the application logger once."""
    logger = logging.getLogger("secure_calculator")
    if logger.handlers:
        return
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
