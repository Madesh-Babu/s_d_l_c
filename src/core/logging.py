"""
Ultra-Simplified Logging Implementation

This module provides essential logging capabilities with:
- user_id
- timestamp
- filepath and line number
- colorama coloring
- log level and message
"""

import logging
import sys
import os
from typing import Any, Dict
from datetime import datetime

# Import colorama for cross-platform color support
try:
    import colorama
    from colorama import Fore, Style

    colorama.init()  # Initialize colorama
    COLORAMA_AVAILABLE = True
except ImportError:
    # Fallback to basic ANSI codes if colorama is not available
    COLORAMA_AVAILABLE = False

    class Fore:
        RED = "\033[91m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        BLUE = "\033[94m"
        MAGENTA = "\033[95m"
        CYAN = "\033[96m"
        WHITE = "\033[97m"

    class Style:
        RESET_ALL = "\033[0m"
        BRIGHT = "\033[1m"


# Color mapping for log levels
LOG_COLORS = {
    "DEBUG": Style.BRIGHT + (Fore.CYAN if COLORAMA_AVAILABLE else "\033[96m"),
    "INFO": Style.BRIGHT + (Fore.GREEN if COLORAMA_AVAILABLE else "\033[92m"),
    "WARNING": Style.BRIGHT + (Fore.YELLOW if COLORAMA_AVAILABLE else "\033[93m"),
    "ERROR": Style.BRIGHT + (Fore.RED if COLORAMA_AVAILABLE else "\033[91m"),
    "CRITICAL": Style.BRIGHT + (Fore.MAGENTA if COLORAMA_AVAILABLE else "\033[95m"),
}

# Icons for different log levels
LOG_ICONS = {
    "DEBUG": "🔍",
    "INFO": "ℹ️",
    "WARNING": "⚠️",
    "ERROR": "❌",
    "CRITICAL": "🔥",
}

# Colors for different parts of the log message
TIMESTAMP_COLOR = Style.BRIGHT + (Fore.BLUE if COLORAMA_AVAILABLE else "\033[94m")
FILE_COLOR = Style.BRIGHT + (Fore.MAGENTA if COLORAMA_AVAILABLE else "\033[95m")
LINE_COLOR = Style.BRIGHT + (Fore.CYAN if COLORAMA_AVAILABLE else "\033[96m")
USER_COLOR = Style.BRIGHT + (Fore.GREEN if COLORAMA_AVAILABLE else "\033[92m")
MESSAGE_COLOR = Style.BRIGHT + (Fore.WHITE if COLORAMA_AVAILABLE else "\033[97m")
SEPARATOR_COLOR = Style.BRIGHT + (Fore.BLUE if COLORAMA_AVAILABLE else "\033[94m")


class ColoredFormatter(logging.Formatter):
    """Custom formatter with file and line numbers and colors."""

    def format(self, record):
        # Get the color for the log level
        color = LOG_COLORS.get(record.levelname, MESSAGE_COLOR)
        icon = LOG_ICONS.get(record.levelname, "📝")

        # Extract color codes
        reset = Style.RESET_ALL if COLORAMA_AVAILABLE else "\033[0m"
        separator = SEPARATOR_COLOR

        # Extract just the filename from the full path
        filename = record.filename
        if "/" in filename:
            filename = filename.split("/")[-1]

        # Get user_id from record if available
        user_id = getattr(record, "user_id", "N/A")

        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")

        # Format the essential log message
        log_message = (
            f"{TIMESTAMP_COLOR}{timestamp}{reset}{separator} - "
            f"{FILE_COLOR}{filename}{reset}{LINE_COLOR}:{record.lineno}{reset}{separator} - "
            f"{USER_COLOR}user:{user_id}{reset}{separator} - "
            f"{color}{icon} {record.levelname}{reset}{separator} - "
            f"{MESSAGE_COLOR}{record.getMessage()}{reset}"
        )

        return log_message


def setup_logging(log_level: str = "INFO", environment: str = "development") -> None:
    """
    Setup ultra-simplified logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        environment: Environment name (development, staging, production)
    """

    # Configure standard logging with custom formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColoredFormatter())

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.handlers.clear()  # Remove existing handlers
    root_logger.addHandler(handler)

    # Configure structlog to use standard logging
    try:
        import structlog

        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        # Override the standard logging formatter to handle structlog messages
        class StructlogColoredFormatter(ColoredFormatter):
            def format(self, record):
                # Handle structlog messages
                if hasattr(record, "msg") and isinstance(record.msg, dict):
                    # Store the original event_dict and extract user_id
                    event_dict = record.msg
                    user_id = event_dict.get("user_id", "N/A")

                    # Extract the actual message
                    event = event_dict.get("event", str(record.msg))
                    record.msg = event

                    # Set user_id as an attribute for the formatter to use
                    record.user_id = user_id

                return super().format(record)

        # Update the handler to use the structlog-aware formatter
        handler.setFormatter(StructlogColoredFormatter())

    except ImportError:
        # If structlog is not available, use standard logging only
        pass


def get_logger(name: str):
    """
    Get a logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    try:
        import structlog

        return structlog.get_logger(name)
    except ImportError:
        return logging.getLogger(name)


def log_user_action(action: str, user_id: str, **kwargs):
    """
    Log user action with user_id.

    Args:
        action: Action description
        user_id: User ID
        **kwargs: Additional context
    """
    logger = get_logger(__name__)
    logger.info(f"User action: {action}", id=user_id, **kwargs)


def log_api_error(error: str, **kwargs):
    """
    Log API error with context.

    Args:
        error: Error description
        **kwargs: Additional context
    """
    logger = get_logger(__name__)
    logger.error(f"API Error: {error}", **kwargs)


class LoggingMiddleware:
    """Simple middleware for request logging."""

    def __init__(self, app):
        self.app = app
        self.logger = get_logger(__name__)
        self.init_app(app)

    def init_app(self, app):
        """Initialize middleware with Flask app."""
        app.before_request(self.before_request)
        app.after_request(self.after_request)

    def before_request(self):
        """Log request start."""
        from flask import request

        self.logger.info(
            f"Request started: {request.method} {request.path}",
            id=getattr(request, "user_id", "anonymous"),
        )

    def after_request(self, response):
        """Log request completion."""
        from flask import request

        self.logger.info(
            f"Request completed: {request.method} {request.path} - {response.status_code}",
            id=getattr(request, "user_id", "anonymous"),
        )
        return response


# Example usage and testing
if __name__ == "__main__":
    # Setup logging
    setup_logging("INFO", "development")

    # Get logger
    logger = get_logger(__name__)

    # Test logging with essential information
    logger.info("This is a test message", id="12345")
    logger.warning("This is a warning message", id="67890")
    logger.error("This is an error message", id="11111")

    # Test user action logging
    log_user_action("user_login", "12345", ip_address="192.168.1.1")
    log_api_error("Validation failed", endpoint="/auth/register", id="12345")
