import logging
import json
from datetime import datetime, timezone
from contextvars import ContextVar

# Stores request_id for the current request — accessible anywhere
request_id_var: ContextVar[str] = ContextVar("request_id", default="startup")


class JSONFormatter(logging.Formatter):
    """Format every log line as a JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "request_id": request_id_var.get(),
        }
        # Merge any extra fields passed in
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
        return json.dumps(log_entry)


def setup_logging(log_level: str = "INFO") -> None:
    """Configure JSON logging for the whole application."""
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    root_logger.handlers.clear()
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger."""
    return logging.getLogger(name)
