"""Centralized logging configuration for Autofig.

All modules use this to get a configured logger.
Ensures consistent logging across the application.
"""

import logging
import logging.handlers
from pathlib import Path
from .config import LOG_LEVEL, LOG_FORMAT, LOGS_DIR


def setup_logging(name: str = "autofig") -> logging.Logger:
    """Set up logging for Autofig.
    
    Configures:
    - Console handler (stdout)
    - File handler (logs/autofig.log)
    - Consistent format
    
    Args:
        name: Logger name (module name)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure root logger once (avoid duplicate handlers)
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(LOG_LEVEL)
    
    # Create logs directory if it doesn't exist
    Path(LOGS_DIR).mkdir(parents=True, exist_ok=True)
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    
    # File handler (logs/autofig.log)
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            Path(LOGS_DIR) / "autofig.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3
        )
        file_handler.setLevel(LOG_LEVEL)
        file_formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not set up file logging: {e}")
    
    # Add console handler
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.
    
    Simpler alternative to logging.getLogger() that ensures setup.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        setup_logging(name)
    return logger
