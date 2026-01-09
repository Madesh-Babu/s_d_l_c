"""
Structured Logging Implementation using structlog

This module provides structured logging capabilities with JSON output,
context management, and correlation ID tracking for the Inventory Management API.
"""

import logging
import logging.config
import sys
import json
import uuid
from contextvars import ContextVar
from typing import Any, Dict, Optional
from datetime import datetime

import structlog
from structlog.stdlib import LoggerFactory
from structlog.processors import JSONRenderer, TimeStamper, add_log_level, StackInfoRenderer

# Context variables for request tracking
correlation_id: ContextVar[str] = ContextVar("correlation_id", default=None)
user_id: ContextVar[str] = ContextVar("user_id", default=None)
request_path: ContextVar[str] = ContextVar("request_path", default=None)
request_method: ContextVar[str] = ContextVar("request_method", default=None)
service_name: ContextVar[str] = ContextVar("service_name", default="inventory-api")


def add_caller_info_processor(logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add caller information (filename and line number) to log entries."""
    record = event_dict.get("_record")
    if record:
        event_dict["caller"] = {
            "filename": record.filename,
            "line_number": record.lineno,
            "function": record.funcName
        }
    return event_dict


def add_context_processor(logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add context variables to log entries."""
    context_vars = {
        "correlation_id": correlation_id.get(),
        "user_id": user_id.get(),
        "request_path": request_path.get(),
        "request_method": request_method.get(),
        "service_name": service_name.get()
    }
    
    # Only add non-None context variables
    for key, value in context_vars.items():
        if value is not None:
            event_dict[key] = value
    
    return event_dict


def add_environment_info_processor(logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add environment information to log entries."""
    event_dict["environment"] = event_dict.get("environment", "development")
    event_dict["timestamp"] = datetime.utcnow().isoformat()
    return event_dict


def _configure_standard_logging(log_level: str = "INFO") -> None:
    """Configure standard Python logging for structlog integration."""
    
    # Create custom formatter for JSON output
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "service_name": service_name.get(),
                "correlation_id": correlation_id.get(),
                "user_id": user_id.get(),
                "request_path": request_path.get(),
                "request_method": request_method.get(),
                "caller": {
                    "filename": record.filename,
                    "line_number": record.lineno,
                    "function": record.funcName
                }
            }
            
            # Add exception info if present
            if record.exc_info:
                log_entry["exception"] = self.formatException(record.exc_info)
            
            # Add extra fields from record
            for key, value in record.__dict__.items():
                if key not in ["name", "msg", "args", "levelname", "levelno", "pathname", 
                              "filename", "module", "lineno", "funcName", "created", 
                              "msecs", "relativeCreated", "thread", "threadName", 
                              "processName", "process", "getMessage", "exc_info", 
                              "exc_text", "stack_info"]:
                    log_entry[key] = value
            
            return json.dumps(log_entry, default=str)
    
    # Configure logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JSONFormatter,
            },
            "console": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "json",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "json",
                "filename": "logs/inventory_api.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
        },
        "loggers": {
            "": {  # Root logger
                "level": log_level,
                "handlers": ["console", "file"],
            },
            "app": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
        },
    }
    
    logging.config.dictConfig(logging_config)


def setup_logging(log_level: str = "INFO", environment: str = "development") -> None:
    """
    Initialize structured logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        environment: Environment name (development, staging, production)
    """
    
    # Configure standard logging
    _configure_standard_logging(log_level)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            add_log_level,
            add_caller_info_processor,
            add_context_processor,
            add_environment_info_processor,
            structlog.stdlib.PositionalArgumentsFormatter(),
            TimeStamper(fmt="iso"),
            StackInfoRenderer(),
            JSONRenderer()
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Set service name based on environment
    service_name.set(f"inventory-api-{environment}")


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured structlog logger instance
    """
    return structlog.get_logger(name)


def generate_correlation_id() -> str:
    """Generate a unique correlation ID for request tracking."""
    return str(uuid.uuid4())


def add_correlation_context(
    correlation_id_val: Optional[str] = None,
    user_id_val: Optional[str] = None,
    request_path_val: Optional[str] = None,
    request_method_val: Optional[str] = None
) -> None:
    """
    Add context variables for the current request.
    
    Args:
        correlation_id_val: Unique correlation ID for the request
        user_id_val: User ID performing the action
        request_path_val: API endpoint path
        request_method_val: HTTP method
    """
    if correlation_id_val:
        correlation_id.set(correlation_id_val)
    if user_id_val:
        user_id.set(user_id_val)
    if request_path_val:
        request_path.set(request_path_val)
    if request_method_val:
        request_method.set(request_method_val)


class RequestLoggingContext:
    """Context manager for request-specific logging context."""
    
    def __init__(
        self,
        correlation_id_val: Optional[str] = None,
        user_id_val: Optional[str] = None,
        request_path_val: Optional[str] = None,
        request_method_val: Optional[str] = None
    ):
        self.correlation_id_val = correlation_id_val or generate_correlation_id()
        self.user_id_val = user_id_val
        self.request_path_val = request_path_val
        self.request_method_val = request_method_val
        
        # Store previous context values
        self.prev_correlation_id = correlation_id.get()
        self.prev_user_id = user_id.get()
        self.prev_request_path = request_path.get()
        self.prev_request_method = request_method.get()
    
    def __enter__(self):
        """Set the logging context."""
        add_correlation_context(
            self.correlation_id_val,
            self.user_id_val,
            self.request_path_val,
            self.request_method_val
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Reset the logging context."""
        correlation_id.set(self.prev_correlation_id)
        user_id.set(self.prev_user_id)
        request_path.set(self.prev_request_path)
        request_method.set(self.prev_request_method)


class LoggingMiddleware:
    """Flask middleware for request logging with correlation tracking."""
    
    def __init__(self, app, logger_name: str = "flask.middleware"):
        self.app = app
        self.logger = get_logger(logger_name)
        self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with Flask app."""
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        app.teardown_appcontext(self._teardown_request)
    
    def _before_request(self):
        """Set up logging context before each request."""
        from flask import request, g
        
        # Generate correlation ID
        corr_id = generate_correlation_id()
        g.correlation_id = corr_id
        g.start_time = datetime.utcnow()
        
        # Set logging context
        add_correlation_context(
            correlation_id_val=corr_id,
            request_path_val=request.path,
            request_method_val=request.method
        )
        
        # Log request start
        self.logger.info(
            "Request started",
            method=request.method,
            path=request.path,
            query_string=dict(request.args),
            user_agent=request.headers.get("User-Agent"),
            remote_addr=request.remote_addr
        )
    
    def _after_request(self, response):
        """Log request completion."""
        from flask import request, g
        
        try:
            # Calculate request duration
            start_time = getattr(g, 'start_time', datetime.utcnow())
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Log request completion
            self.logger.info(
                "Request completed",
                method=request.method,
                path=request.path,
                status_code=response.status_code,
                duration_seconds=duration,
                response_size=len(response.get_data() or b'')
            )
        except Exception as e:
            self.logger.error("Error in after_request logging", error=str(e))
        
        return response
    
    def _teardown_request(self, exception):
        """Clean up request context."""
        from flask import g
        
        if exception:
            self.logger.error(
                "Request failed with exception",
                exception=str(exception),
                exc_info=True
            )
        
        # Clean up context variables
        correlation_id.set(None)
        user_id.set(None)
        request_path.set(None)
        request_method.set(None)


# Utility functions for common logging patterns
def log_user_action(action: str, user_id: str, **kwargs):
    """Log user action with context."""
    logger = get_logger(__name__)
    logger.info(f"User action: {action}", user_id=user_id, action=action, **kwargs)


def log_api_error(error: str, error_code: str = None, **kwargs):
    """Log API error with context."""
    logger = get_logger(__name__)
    logger.error(f"API error: {error}", error=error, error_code=error_code, **kwargs)


def log_business_event(event: str, **kwargs):
    """Log business event with context."""
    logger = get_logger(__name__)
    logger.info(f"Business event: {event}", event=event, **kwargs)


def log_performance(operation: str, duration: float, **kwargs):
    """Log performance metrics."""
    logger = get_logger(__name__)
    logger.info(
        f"Performance: {operation}",
        operation=operation,
        duration_seconds=duration,
        **kwargs
    )
