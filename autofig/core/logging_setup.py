"""Logging configuration for Autofig."""

import logging
import logging.handlers
from pathlib import Path

from .config import LOG_DIR, AUTOFIG_LOG_LEVEL, LOG_FORMAT


def setup_logging(name: str = "autofig", log_level: str = None) -> logging.Logger:
    """Set up logging with file and console handlers.
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    if log_level is None:
        log_level = AUTOFIG_LOG_LEVEL
    
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Create formatters
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (rotating)
    log_file = LOG_DIR / f"{name}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "autofig") -> logging.Logger:
    """Get or create a logger.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
