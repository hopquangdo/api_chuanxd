import logging
import contextvars

from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

request_id_ctx = contextvars.ContextVar("request_id", default=None)

class RequestIdFilter(logging.Filter):
    """
    Log filter to inject request_id into log records.
    """
    def filter(self, record):
        record.request_id = request_id_ctx.get() or "N/A"
        return True

def setup_logger(
    name: str,
    log_file: str = "logs/app.log",
    level: int = logging.INFO
) -> logging.Logger:
    """
    Setup a reusable logger with console + file output.
    Log file will be located at the project root.
    """

    log_path = Path(log_file)
    if not log_path.is_absolute():
        log_path = BASE_DIR / log_path

    os.makedirs(log_path.parent, exist_ok=True)

    logger = logging.getLogger(name)

    # If handlers already exist, just return the logger to prevent duplicate logs
    if logger.handlers:
        return logger

    logger.setLevel(level)
    
    # Add RequestIdFilter
    req_id_filter = RequestIdFilter()
    logger.addFilter(req_id_filter)

    # Format including request ID
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(request_id)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(req_id_filter)
    logger.addHandler(console_handler)

    # File handler (log rotation)
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(req_id_filter)
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger

