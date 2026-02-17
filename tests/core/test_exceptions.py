"""
Exception Handling Tests

This module contains comprehensive tests for custom exceptions
and error handling functionality.
"""

import pytest
from unittest.mock import Mock, patch
from src.core.exceptions import (
    BaseAPIException,
    ValidationErrorException,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    DatabaseError,
    ExceptionHandler,
)


class TestBaseAPIException:
    """Test base API exception."""

    def test_base_exception_creation(self):
        """Test base exception creation with basic parameters."""
        exception = BaseAPIException("Test message")

        assert exception.message == "Test message"
        assert exception.status_code == 500
        assert exception.error_code is None
        assert exception.details == {}

    def test_base_exception_with_all_parameters(self):
        """Test base exception creation with all parameters."""
        details = {"field": "email", "value": "invalid"}
        exception = BaseAPIException(
            message="Validation failed",
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details,
        )

        assert exception.message == "Validation failed"
        assert exception.status_code == 400
        assert exception.error_code == "VALIDATION_ERROR"
        assert exception.details == details

    def test_base_exception_to_dict(self):
        """Test base exception to_dict method."""
        details = {"field": "email"}
        exception = BaseAPIException(
            message="Test error",
            status_code=400,
            error_code="TEST_ERROR",
            details=details,
        )

        result = exception.to_dict()

        assert result["message"] == "Test error"
        assert result["status_code"] == 400
        assert result["error_code"] == "TEST_ERROR"
        assert result["details"] == details
        assert "timestamp" in result

    def test_base_exception_str_representation(self):
        """Test base exception string representation."""
        exception = BaseAPIException("Test message", status_code=400)

        str_repr = str(exception)

        assert "Test message" in str_repr
        assert "400" in str_repr

    def test_base_exception_inheritance(self):
        """Test that BaseAPIException inherits from Exception."""
        exception = BaseAPIException("Test")

        assert isinstance(exception, Exception)
        assert isinstance(exception, BaseAPIException)


class TestSpecificExceptions:
    """Test specific exception classes."""

    def test_validation_error_exception(self):
        """Test ValidationErrorException."""
        details = {"field": "email", "error": "Invalid format"}
        exception = ValidationErrorException("Invalid email", details)

        assert exception.message == "Invalid email"
        assert exception.status_code == 400
        assert exception.error_code == "VALIDATION_ERROR"
        assert exception.details == details

    def test_validation_error_exception_default_message(self):
        """Test ValidationErrorException with default message."""
        exception = ValidationErrorException()

        assert exception.message == "Validation failed"
        assert exception.status_code == 400
        assert exception.error_code == "VALIDATION_ERROR"

    def test_authentication_error_exception(self):
        """Test AuthenticationError."""
        exception = AuthenticationError("Invalid credentials")

        assert exception.message == "Invalid credentials"
        assert exception.status_code == 401
        assert exception.error_code == "AUTHENTICATION_ERROR"

    def test_authentication_error_exception_default(self):
        """Test AuthenticationError with default message."""
        exception = AuthenticationError()

        assert exception.message == "Authentication failed"
        assert exception.status_code == 401
        assert exception.error_code == "AUTHENTICATION_ERROR"

    def test_authorization_error_exception(self):
        """Test AuthorizationError."""
        exception = AuthorizationError("Insufficient permissions")

        assert exception.message == "Insufficient permissions"
        assert exception.status_code == 403
        assert exception.error_code == "AUTHORIZATION_ERROR"

    def test_authorization_error_exception_default(self):
        """Test AuthorizationError with default message."""
        exception = AuthorizationError()

        assert exception.message == "Access denied"
        assert exception.status_code == 403
        assert exception.error_code == "AUTHORIZATION_ERROR"

    def test_not_found_error_exception(self):
        """Test NotFoundError."""
        exception = NotFoundError("User not found")

        assert exception.message == "User not found"
        assert exception.status_code == 404
        assert exception.error_code == "NOT_FOUND"

    def test_not_found_error_exception_default(self):
        """Test NotFoundError with default message."""
        exception = NotFoundError()

        assert exception.message == "Resource not found"
        assert exception.status_code == 404
        assert exception.error_code == "NOT_FOUND"

    def test_conflict_error_exception(self):
        """Test ConflictError."""
        exception = ConflictError("Email already exists")

        assert exception.message == "Email already exists"
        assert exception.status_code == 409
        assert exception.error_code == "CONFLICT"

    def test_conflict_error_exception_default(self):
        """Test ConflictError with default message."""
        exception = ConflictError()

        assert exception.message == "Resource conflict"
        assert exception.status_code == 409
        assert exception.error_code == "CONFLICT"

    def test_database_error_exception(self):
        """Test DatabaseError."""
        exception = DatabaseError("Connection failed")

        assert exception.message == "Connection failed"
        assert exception.status_code == 500
        assert exception.error_code == "DATABASE_ERROR"

    def test_database_error_exception_default(self):
        """Test DatabaseError with default message."""
        exception = DatabaseError()

        assert exception.message == "Database operation failed"
        assert exception.status_code == 500
        assert exception.error_code == "DATABASE_ERROR"


class TestExceptionHandler:
    """Test exception handler functionality."""

    def test_exception_handler_initialization(self):
        """Test exception handler initialization."""
        handler = ExceptionHandler()

        assert handler.logger is not None
        assert isinstance(handler.logger, object)

    def test_handle_base_exception(self):
        """Test handling base API exception."""
        handler = ExceptionHandler()
        exception = BaseAPIException("Test error", status_code=400)

        response = handler.handle_exception(exception)

        assert response[1] == 400  # Status code
        response_data = response[0]
        assert response_data["message"] == "Test error"
        assert response_data["status_code"] == 400

    def test_handle_validation_exception(self):
        """Test handling validation exception."""
        handler = ExceptionHandler()
        details = {"field": "email", "error": "Invalid format"}
        exception = ValidationErrorException("Invalid data", details)

        response = handler.handle_exception(exception)

        assert response[1] == 400
        response_data = response[0]
        assert response_data["message"] == "Invalid data"
        assert response_data["error_code"] == "VALIDATION_ERROR"
        assert response_data["details"] == details

    def test_handle_authentication_exception(self):
        """Test handling authentication exception."""
        handler = ExceptionHandler()
        exception = AuthenticationError("Invalid token")

        response = handler.handle_exception(exception)

        assert response[1] == 401
        response_data = response[0]
        assert response_data["message"] == "Invalid token"
        assert response_data["error_code"] == "AUTHENTICATION_ERROR"

    def test_handle_authorization_exception(self):
        """Test handling authorization exception."""
        handler = ExceptionHandler()
        exception = AuthorizationError("Access denied")

        response = handler.handle_exception(exception)

        assert response[1] == 403
        response_data = response[0]
        assert response_data["message"] == "Access denied"
        assert response_data["error_code"] == "AUTHORIZATION_ERROR"

    def test_handle_not_found_exception(self):
        """Test handling not found exception."""
        handler = ExceptionHandler()
        exception = NotFoundError("Resource not found")

        response = handler.handle_exception(exception)

        assert response[1] == 404
        response_data = response[0]
        assert response_data["message"] == "Resource not found"
        assert response_data["error_code"] == "NOT_FOUND"

    def test_handle_conflict_exception(self):
        """Test handling conflict exception."""
        handler = ExceptionHandler()
        exception = ConflictError("Duplicate resource")

        response = handler.handle_exception(exception)

        assert response[1] == 409
        response_data = response[0]
        assert response_data["message"] == "Duplicate resource"
        assert response_data["error_code"] == "CONFLICT"

    def test_handle_database_exception(self):
        """Test handling database exception."""
        handler = ExceptionHandler()
        exception = DatabaseError("Query failed")

        response = handler.handle_exception(exception)

        assert response[1] == 500
        response_data = response[0]
        assert response_data["message"] == "Query failed"
        assert response_data["error_code"] == "DATABASE_ERROR"

    def test_handle_generic_exception(self):
        """Test handling generic Python exception."""
        handler = ExceptionHandler()
        exception = ValueError("Generic error")

        response = handler.handle_exception(exception)

        assert response[1] == 500
        response_data = response[0]
        assert response_data["message"] == "Internal server error"
        assert response_data["error_code"] == "INTERNAL_ERROR"

    def test_handle_exception_with_logging(self, mock_logger):
        """Test that exceptions are logged."""
        handler = ExceptionHandler()
        handler.logger = mock_logger

        exception = ValidationErrorException("Test error")
        handler.handle_exception(exception)

        # Should log the error
        mock_logger.error.assert_called()

    def test_handle_exception_with_none_logger(self):
        """Test handling exception when logger is None."""
        handler = ExceptionHandler()
        handler.logger = None

        exception = ValidationErrorException("Test error")

        # Should not raise an error
        response = handler.handle_exception(exception)
        assert response[1] == 400

    def test_exception_response_format(self):
        """Test exception response format consistency."""
        handler = ExceptionHandler()
        exception = ValidationErrorException("Test error", {"field": "email"})

        response = handler.handle_exception(exception)
        response_data = response[0]

        # Check required fields
        required_fields = ["message", "status_code", "error_code", "timestamp"]
        for field in required_fields:
            assert field in response_data

        # Check data types
        assert isinstance(response_data["message"], str)
        assert isinstance(response_data["status_code"], int)
        assert isinstance(response_data["error_code"], str)
        assert isinstance(response_data["timestamp"], str)


class TestExceptionIntegration:
    """Test exception integration with Flask."""

    def test_exception_in_flask_context(self, app):
        """Test exception handling in Flask context."""
        with app.test_request_context():
            handler = ExceptionHandler()
            exception = ValidationErrorException("Test error")

            response = handler.handle_exception(exception)

            assert response[1] == 400
            assert isinstance(response[0], dict)

    def test_exception_chaining(self):
        """Test exception chaining."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise ValidationErrorException("Validation failed") from e
        except ValidationErrorException as e:
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, ValueError)

    def test_exception_pickling(self):
        """Test that exceptions can be pickled/unpickled."""
        import pickle

        original = ValidationErrorException("Test error", {"field": "email"})

        # Pickle and unpickle
        pickled = pickle.dumps(original)
        unpickled = pickle.loads(pickled)

        assert unpickled.message == original.message
        assert unpickled.status_code == original.status_code
        assert unpickled.details == original.details

    def test_exception_equality(self):
        """Test exception equality comparison."""
        exc1 = ValidationErrorException("Test error")
        exc2 = ValidationErrorException("Test error")
        exc3 = AuthenticationError("Test error")

        # Exceptions with same type and message should be equal
        assert exc1.message == exc2.message
        assert exc1.status_code == exc2.status_code

        # Different types should not be equal
        assert exc1.error_code != exc3.error_code
