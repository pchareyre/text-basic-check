"""
Centralized logging configuration for genaids-editor.

Provides standardized logger setup with consistent formatting and levels.
"""
import logging
import os
from typing import Optional

DEFAULT_LOG_LEVEL = os.getenv("GENAIDS_LOG_LEVEL", "INFO").upper()


def setup_logger(name: str, level: Optional[str] = None, verbose: bool = False) -> logging.Logger:
    """
    Setup standardized logger for genaids-editor modules.

    Args:
        name: Module name (use __name__)
        level: Log level override (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        verbose: If True, force DEBUG level

    Returns:
        Configured logger instance

    Examples:
        >>> # In a module
        >>> from genaids_editor.utils.logging_config import setup_logger
        >>> logger = setup_logger(__name__)
        >>> logger.info("Processing started")

        >>> # With verbose mode
        >>> logger = setup_logger(__name__, verbose=True)
        >>> logger.debug("Detailed debug info")

        >>> # Custom level
        >>> logger = setup_logger(__name__, level="WARNING")
    """
    logger = logging.getLogger(name)

    # Determine log level
    if verbose:
        log_level = logging.DEBUG
    elif level:
        log_level = getattr(logging, level.upper(), logging.INFO)
    else:
        log_level = getattr(logging, DEFAULT_LOG_LEVEL, logging.INFO)

    logger.setLevel(log_level)

    # Avoid duplicate handlers
    if logger.hasHandlers():
        return logger

    # Console handler with formatting
    handler = logging.StreamHandler()
    handler.setLevel(log_level)

    # Format: [2026-01-01 14:30:45] [INFO] [module.name] Message
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get existing logger or create with default config.

    Convenience function for simple logger creation.

    Args:
        name: Module name (use __name__)

    Returns:
        Logger instance

    Examples:
        >>> from genaids_editor.utils.logging_config import get_logger
        >>> logger = get_logger(__name__)
    """
    return setup_logger(name)
