"""
Application logging configuration module.

This module centralizes the logging configuration for Private Doc Agent.

It configures logs to be written both to the console and to a local file.
The goal is to make the application easier to debug and observe while
keeping logging behavior consistent across all services.

Logging strategy:
- Logs are written to console and to logs/app.log.
- Log files rotate automatically to avoid unlimited growth.
- A separator line can be written between API executions to improve readability.
"""

import logging
from logging.handlers import RotatingFileHandler

from app.config import BASE_DIR


# Directory where local log files will be stored.
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"

# Visual separator used to identify different API executions in the log file.
LOG_SEPARATOR = "-" * 96


def setup_logging() -> None:
    """
    Configures application-wide logging.

    The configuration includes:
    - Console logging for development visibility.
    - Rotating file logging to avoid unlimited log growth.
    - A consistent log format with timestamp, level, logger name and message.

    This function should be called once when the FastAPI application starts.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Avoid adding duplicate handlers when Uvicorn reloads the application.
    if root_logger.handlers:
        return

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format))

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format))

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


def log_execution_separator(logger_name: str = "app.execution") -> None:
    """
    Writes a visual separator line to the application logs.

    This function is useful to visually separate different API executions
    when reviewing logs during local development or debugging.

    The separator starts with a newline so the visual line appears clearly
    separated from the previous log entry.

    Args:
        logger_name: Name of the logger that will write the separator.
    """
    logger = logging.getLogger(logger_name)
    logger.info("\n%s", LOG_SEPARATOR)