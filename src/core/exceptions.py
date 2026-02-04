"""
Global Exception Handler for the Application

This module provides comprehensive exception handling with custom exceptions
and centralized error management.
"""

import logging
import traceback
from typing import Dict, Any, Optional
from flask import jsonify, current_app
from pydantic import ValidationError


class BaseAPIException(Exception):
    """Base exception for all API-related errors."""
    
    def __init__(self, message: str, status_code: int = 500, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class ValidationErrorException(BaseAPIException):
    """Raised when validation fails."""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, 400, "VALIDATION_ERROR", details)


class AuthenticationError(BaseAPIException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", details: Dict[str, Any] = None):
        super().__init__(message, 401, "AUTHENTICATION_ERROR", details)


class AuthorizationError(BaseAPIException):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Access denied", details: Dict[str, Any] = None):
        super().__init__(message, 403, "AUTHORIZATION_ERROR", details)


class NotFoundError(BaseAPIException):
    """Raised when a resource is not found."""
    
    def __init__(self, message: str = "Resource not found", details: Dict[str, Any] = None):
        super().__init__(message, 404, "NOT_FOUND_ERROR", details)


class ConflictError(BaseAPIException):
    """Raised when a conflict occurs (e.g., duplicate resource)."""
    
    def __init__(self, message: str = "Resource conflict", details: Dict[str, Any] = None):
        super().__init__(message, 409, "CONFLICT_ERROR", details)


class DatabaseError(BaseAPIException):
    """Raised when database operations fail."""
    
    def __init__(self, message: str = "Database operation failed", details: Dict[str, Any] = None):
        super().__init__(message, 500, "DATABASE_ERROR", details)


class ConfigurationError(BaseAPIException):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str = "Configuration error", details: Dict[str, Any] = None):
        super().__init__(message, 500, "CONFIGURATION_ERROR", details)


class RateLimitError(BaseAPIException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Dict[str, Any] = None):
        super().__init__(message, 429, "RATE_LIMIT_ERROR", details)


class ExceptionHandler:
    """Centralized exception handler."""
    
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def handle_exception(self, exception: Exception) -> tuple:
        """
        Handle exceptions and return appropriate Flask response.
        
        Args:
            exception: The exception to handle
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        # Handle custom API exceptions
        if isinstance(exception, BaseAPIException):
            return self._handle_api_exception(exception)
        
        # Handle Pydantic validation errors
        elif isinstance(exception, ValidationError):
            return self._handle_validation_error(exception)
        
        # Handle SQLAlchemy errors
        elif hasattr(exception, '__module__') and 'sqlalchemy' in str(exception.__module__):
            return self._handle_database_error(exception)
        
        # Handle JWT errors
        elif hasattr(exception, '__module__') and 'jwt' in str(exception.__module__):
            return self._handle_jwt_error(exception)
        
        # Handle all other exceptions
        else:
            return self._handle_generic_error(exception)
    
    def _handle_api_exception(self, exception: BaseAPIException) -> tuple:
        """Handle custom API exceptions."""
        self.logger.error(
            f"API Exception: {exception.error_code} - {exception.message}",
            extra={
                "error_code": exception.error_code,
                "status_code": exception.status_code,
                "details": exception.details
            }
        )
        
        response = {
            "error": exception.message,
            "error_code": exception.error_code,
            "status_code": exception.status_code
        }
        
        if exception.details:
            response["details"] = exception.details
        
        # Add stack trace in debug mode
        if current_app and current_app.debug:
            response["traceback"] = traceback.format_exc()
        
        return jsonify(response), exception.status_code
    
    def _handle_validation_error(self, exception: ValidationError) -> tuple:
        """Handle Pydantic validation errors."""
        self.logger.warning(
            f"Validation Error: {str(exception)}",
            extra={
                "error_type": "ValidationError",
                "errors": exception.errors() if hasattr(exception, 'errors') else str(exception)
            }
        )
        
        response = {
            "error": "Validation failed",
            "error_code": "VALIDATION_ERROR",
            "status_code": 400
        }
        
        # Extract validation details
        if hasattr(exception, 'errors'):
            response["details"] = exception.errors()
        else:
            response["details"] = {"validation_errors": str(exception)}
        
        return jsonify(response), 400
    
    def _handle_database_error(self, exception: Exception) -> tuple:
        """Handle database-related errors."""
        self.logger.error(
            f"Database Error: {str(exception)}",
            extra={
                "error_type": "DatabaseError",
                "exception_type": type(exception).__name__
            },
            exc_info=True
        )
        
        # Check for specific database errors
        error_msg = str(exception).lower()
        if "unique constraint" in error_msg or "duplicate key" in error_msg:
            response = {
                "error": "Resource already exists",
                "error_code": "DUPLICATE_RESOURCE",
                "status_code": 409
            }
        elif "foreign key constraint" in error_msg:
            response = {
                "error": "Referenced resource does not exist",
                "error_code": "FOREIGN_KEY_ERROR",
                "status_code": 400
            }
        elif "connection" in error_msg or "timeout" in error_msg:
            response = {
                "error": "Database connection error",
                "error_code": "DATABASE_CONNECTION_ERROR",
                "status_code": 503
            }
        else:
            response = {
                "error": "Database operation failed",
                "error_code": "DATABASE_ERROR",
                "status_code": 500
            }
        
        if current_app and current_app.debug:
            response["traceback"] = traceback.format_exc()
        
        return jsonify(response), response["status_code"]
    
    def _handle_jwt_error(self, exception: Exception) -> tuple:
        """Handle JWT-related errors."""
        self.logger.warning(
            f"JWT Error: {str(exception)}",
            extra={
                "error_type": "JWTError",
                "exception_type": type(exception).__name__
            }
        )
        
        response = {
            "error": "Authentication token error",
            "error_code": "JWT_ERROR",
            "status_code": 401
        }
        
        return jsonify(response), 401
    
    def _handle_generic_error(self, exception: Exception) -> tuple:
        """Handle generic exceptions."""
        self.logger.error(
            f"Unexpected Error: {str(exception)}",
            extra={
                "error_type": type(exception).__name__,
                "exception_module": getattr(exception, '__module__', 'Unknown')
            },
            exc_info=True
        )
        
        response = {
            "error": "An unexpected error occurred",
            "error_code": "INTERNAL_SERVER_ERROR",
            "status_code": 500
        }
        
        if current_app and current_app.debug:
            response["debug_info"] = {
                "exception_type": type(exception).__name__,
                "exception_message": str(exception),
                "traceback": traceback.format_exc()
            }
        
        return jsonify(response), 500


def create_error_response(error_code: str, message: str, status_code: int = 500, details: Dict[str, Any] = None) -> tuple:
    """
    Helper function to create standardized error responses.
    
    Args:
        error_code: Error code for the response
        message: Error message
        status_code: HTTP status code
        details: Additional error details
        
    Returns:
        Tuple of (response_dict, status_code)
    """
    response = {
        "error": message,
        "error_code": error_code,
        "status_code": status_code
    }
    
    if details:
        response["details"] = details
    
    return jsonify(response), status_code


def handle_validation_errors(validation_errors: Dict[str, Any]) -> tuple:
    """
    Helper function to handle validation errors consistently.
    
    Args:
        validation_errors: Dictionary of validation errors
        
    Returns:
        Tuple of (response_dict, status_code)
    """
    return create_error_response(
        error_code="VALIDATION_ERROR",
        message="Validation failed",
        status_code=400,
        details=validation_errors
    )


# Global exception handler instance
exception_handler = ExceptionHandler()