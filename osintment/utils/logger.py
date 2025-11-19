"""Logging configuration for OSINTment"""
import logging
import sys
from rich.logging import RichHandler
from ..core.config import Config


def setup_logger(name: str = 'osintment', level: str = None) -> logging.Logger:
    """
    Setup application logger with rich formatting

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger
    """
    if level is None:
        level = Config.LOG_LEVEL

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Add rich handler for beautiful console output
    handler = RichHandler(
        rich_tracebacks=True,
        show_time=True,
        show_path=False
    )

    handler.setFormatter(
        logging.Formatter(
            '%(message)s',
            datefmt='[%X]'
        )
    )

    logger.addHandler(handler)

    return logger
