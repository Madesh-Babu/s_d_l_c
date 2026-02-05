# Exception Handling Implementation

## Overview

This document outlines the comprehensive exception handling implementation throughout the application to provide robust error management, consistent error responses, and better debugging capabilities.

## Exception Architecture

### 1. Custom Exception Hierarchy

#### Base Exception Classes
```python
# src/core/exceptions.py
from typing import Any, Dict, Optional, List
from datetime import datetime

class BaseApplicationException(Exception):
    """Base exception for all application exceptions"""
    
    def __init__(
        self,
        message: str,
        error_code: str = None,
        status_code: int = 500,
        details: Dict[str, Any] = None,
        cause: Exception = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.status_code = status_code
        self.details = details or {}
        self.cause = cause
        self.timestamp = datetime.utcnow()
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            "error": self.error_code,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }

class ValidationException(BaseApplicationException):
    """Exception for validation errors"""
    
    def __init__(
        self,
        message: str = "Validation failed",
        validation_errors: List[Dict[str, Any]] = None,
        **kwargs
    ):
        self.validation_errors = validation_errors or []
        details = kwargs.pop('details', {})
        details['validation_errors'] = self.validation_errors
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            details=details,
            **kwargs
        )

class AuthenticationException(BaseApplicationException):
    """Exception for authentication errors"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
            **kwargs
        )

class AuthorizationException(BaseApplicationException):
    """Exception for authorization errors"""
    
    def __init__(self, message: str = "Access denied", **kwargs):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            **kwargs
        )

class NotFoundException(BaseApplicationException):
    """Exception for resource not found errors"""
    
    def __init__(self, message: str = "Resource not found", resource_type: str = None, **kwargs):
        details = kwargs.pop('details', {})
        if resource_type:
            details['resource_type'] = resource_type
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404,
            details=details,
            **kwargs
        )

class ConflictException(BaseApplicationException):
    """Exception for resource conflict errors"""
    
    def __init__(self, message: str = "Resource conflict", **kwargs):
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=409,
            **kwargs
        )

class BusinessLogicException(BaseApplicationException):
    """Exception for business logic violations"""
    
    def __init__(self, message: str = "Business logic violation", **kwargs):
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            status_code=400,
            **kwargs
        )

class DatabaseException(BaseApplicationException):
    """Exception for database-related errors"""
    
    def __init__(self, message: str = "Database error", **kwargs):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=500,
            **kwargs
        )

class ExternalServiceException(BaseApplicationException):
    """Exception for external service errors"""
    
    def __init__(
        self,
        message: str = "External service error",
        service_name: str = None,
        **kwargs
    ):
        details = kwargs.pop('details', {})
        if service_name:
            details['service_name'] = service_name
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            details=details,
            **kwargs
        )

class RateLimitException(BaseApplicationException):
    """Exception for rate limiting"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int = None,
        **kwargs
    ):
        details = kwargs.pop('details', {})
        if retry_after:
            details['retry_after'] = retry_after
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=details,
            **kwargs
        )
```

### 2. Specific Exception Classes

#### Domain-Specific Exceptions
```python
# src/exceptions/auth_exceptions.py
from src.core.exceptions import AuthenticationException, ValidationException

class UserNotFoundException(AuthenticationException):
    """Exception when user is not found"""
    
    def __init__(self, username: str = None, user_id: int = None):
        message = "User not found"
        details = {}
        
        if username:
            details['username'] = username
            message = f"User '{username}' not found"
        elif user_id:
            details['user_id'] = user_id
            message = f"User with ID {user_id} not found"
        
        super().__init__(message=message, details=details)

class InvalidPasswordException(AuthenticationException):
    """Exception for invalid password"""
    
    def __init__(self, username: str = None):
        message = "Invalid password"
        details = {}
        
        if username:
            details['username'] = username
        
        super().__init__(message=message, details=details)

class UserInactiveException(AuthenticationException):
    """Exception when user account is inactive"""
    
    def __init__(self, username: str = None):
        message = "User account is inactive"
        details = {}
        
        if username:
            details['username'] = username
        
        super().__init__(message=message, details=details)

class TokenExpiredException(AuthenticationException):
    """Exception when JWT token has expired"""
    
    def __init__(self):
        super().__init__(message="Token has expired")

class TokenInvalidException(AuthenticationException):
    """Exception when JWT token is invalid"""
    
    def __init__(self, reason: str = None):
        message = "Invalid token"
        details = {}
        
        if reason:
            details['reason'] = reason
        
        super().__init__(message=message, details=details)

# src/exceptions/task_exceptions.py
from src.core.exceptions import NotFoundException, BusinessLogicException

class TaskNotFoundException(NotFoundException):
    """Exception when task is not found"""
    
    def __init__(self, task_id: int = None):
        message = "Task not found"
        details = {}
        
        if task_id:
            details['task_id'] = task_id
            message = f"Task with ID {task_id} not found"
        
        super().__init__(message=message, resource_type="Task", details=details)

class TaskStatusTransitionException(BusinessLogicException):
    """Exception for invalid task status transitions"""
    
    def __init__(self, current_status: str, target_status: str):
        message = f"Cannot transition task from '{current_status}' to '{target_status}'"
        details = {
            'current_status': current_status,
            'target_status': target_status
        }
        super().__init__(message=message, details=details)

class TaskDependencyException(BusinessLogicException):
    """Exception for task dependency violations"""
    
    def __init__(self, message: str, dependency_task_id: int = None):
        details = {}
        
        if dependency_task_id:
            details['dependency_task_id'] = dependency_task_id
        
        super().__init__(message=message, details=details)

class TaskAssignmentException(BusinessLogicException):
    """Exception for task assignment errors"""
    
    def __init__(self, message: str, user_id: int = None, task_id: int = None):
        details = {}
        
        if user_id:
            details['user_id'] = user_id
        if task_id:
            details['task_id'] = task_id
        
        super().__init__(message=message, details=details)
```

## Exception Handling Middleware

### 1. Flask Exception Handlers

#### Global Exception Handler
```python
# src/middleware/exception_handler.py
import structlog
from flask import jsonify, request, g
from src.core.exceptions import BaseApplicationException
from src.core.logging import logger

class ExceptionHandler:
    """Global exception handler for Flask application"""
    
    def __init__(self, app=None):
        self.app = app
        self.logger = logger.bind(service="exception_handler")
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize exception handlers for Flask app"""
        app.register_error_handler(BaseApplicationException, self.handle_application_exception)
        app.register_error_handler(Exception, self.handle_unexpected_exception)
        
        # Register specific exception handlers
        app.register_error_handler(404, self.handle_not_found)
        app.register_error_handler(405, self.handle_method_not_allowed)
        app.register_error_handler(500, self.handle_internal_server_error)
    
    def handle_application_exception(self, error: BaseApplicationException):
        """Handle application-specific exceptions"""
        self.logger.error(
            "Application exception occurred",
            error_type=error.__class__.__name__,
            error_message=error.message,
            error_code=error.error_code,
            status_code=error.status_code,
            details=error.details,
            request_id=getattr(g, 'request_id', None),
            user_id=getattr(g, 'current_user', {}).get('id', None),
            endpoint=request.endpoint,
            method=request.method,
            path=request.path,
            exc_info=True
        )
        
        response = {
            "success": False,
            "error": error.error_code,
            "message": error.message,
            "details": error.details,
            "timestamp": error.timestamp.isoformat()
        }
        
        if getattr(g, 'request_id', None):
            response["request_id"] = g.request_id
        
        return jsonify(response), error.status_code
    
    def handle_unexpected_exception(self, error: Exception):
        """Handle unexpected exceptions"""
        self.logger.error(
            "Unexpected exception occurred",
            error_type=error.__class__.__name__,
            error_message=str(error),
            request_id=getattr(g, 'request_id', None),
            user_id=getattr(g, 'current_user', {}).get('id', None),
            endpoint=request.endpoint,
            method=request.method,
            path=request.path,
            exc_info=True
        )
        
        response = {
            "success": False,
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if getattr(g, 'request_id', None):
            response["request_id"] = g.request_id
        
        # In development, include more details
        if os.getenv('ENVIRONMENT') == 'development':
            response["details"] = {
                "error_type": error.__class__.__name__,
                "error_message": str(error)
            }
        
        return jsonify(response), 500
    
    def handle_not_found(self, error):
        """Handle 404 not found errors"""
        self.logger.warning(
            "Resource not found",
            path=request.path,
            method=request.method,
            request_id=getattr(g, 'request_id', None)
        )
        
        response = {
            "success": False,
            "error": "NOT_FOUND",
            "message": "The requested resource was not found",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if getattr(g, 'request_id', None):
            response["request_id"] = g.request_id
        
        return jsonify(response), 404
    
    def handle_method_not_allowed(self, error):
        """Handle 405 method not allowed errors"""
        self.logger.warning(
            "Method not allowed",
            path=request.path,
            method=request.method,
            request_id=getattr(g, 'request_id', None)
        )
        
        response = {
            "success": False,
            "error": "METHOD_NOT_ALLOWED",
            "message": "The requested method is not allowed for this resource",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if getattr(g, 'request_id', None):
            response["request_id"] = g.request_id
        
        return jsonify(response), 405
    
    def handle_internal_server_error(self, error):
        """Handle 500 internal server errors"""
        self.logger.error(
            "Internal server error",
            error_type=error.__class__.__name__,
            error_message=str(error),
            request_id=getattr(g, 'request_id', None),
            endpoint=request.endpoint,
            method=request.method,
            path=request.path,
            exc_info=True
        )
        
        response = {
            "success": False,
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An internal server error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if getattr(g, 'request_id', None):
            response["request_id"] = g.request_id
        
        return jsonify(response), 500
```

### 2. Service Layer Exception Handling

#### Service Exception Handling
```python
# src/services/base_service.py
import structlog
from typing import Any, Optional
from src.core.exceptions import BaseApplicationException, DatabaseException
from src.core.logging import logger

class BaseService:
    """Base service with exception handling"""
    
    def __init__(self):
        self.logger = logger.bind(service=self.__class__.__name__)
    
    def handle_exception(self, error: Exception, operation: str, context: dict = None):
        """Handle exceptions in service layer"""
        context = context or {}
        
        if isinstance(error, BaseApplicationException):
            # Re-raise application exceptions
            self.logger.error(
                f"Service exception in {operation}",
                operation=operation,
                error_type=error.__class__.__name__,
                error_message=error.message,
                context=context,
                exc_info=True
            )
            raise
        
        # Wrap unexpected exceptions
        self.logger.error(
            f"Unexpected exception in {operation}",
            operation=operation,
            error_type=error.__class__.__name__,
            error_message=str(error),
            context=context,
            exc_info=True
        )
        
        raise DatabaseException(
            message=f"Database operation failed during {operation}",
            cause=error,
            details={"operation": operation, "context": context}
        )
    
    def execute_with_exception_handling(self, operation: str, func, *args, **kwargs):
        """Execute function with exception handling"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.handle_exception(e, operation, {"args": args, "kwargs": kwargs})

# src/services/auth_service.py
from src.services.base_service import BaseService
from src.exceptions.auth_exceptions import (
    UserNotFoundException,
    InvalidPasswordException,
    UserInactiveException
)

class AuthService(BaseService):
    """Authentication service with comprehensive exception handling"""
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with exception handling"""
        operation = "authenticate_user"
        context = {"username": username}
        
        try:
            self.logger.info(
                "User authentication attempt",
                operation=operation,
                username=username
            )
            
            # Get user from database
            user = self.user_repository.get_by_username(username)
            
            if not user:
                self.logger.warning(
                    "Authentication failed - user not found",
                    operation=operation,
                    username=username
                )
                raise UserNotFoundException(username=username)
            
            # Verify password
            if not self.password_service.verify_password(password, user.password_hash):
                self.logger.warning(
                    "Authentication failed - invalid password",
                    operation=operation,
                    username=username,
                    user_id=user.id
                )
                raise InvalidPasswordException(username=username)
            
            # Check if user is active
            if not user.is_active:
                self.logger.warning(
                    "Authentication failed - user inactive",
                    operation=operation,
                    username=username,
                    user_id=user.id
                )
                raise UserInactiveException(username=username)
            
            self.logger.info(
                "Authentication successful",
                operation=operation,
                username=username,
                user_id=user.id
            )
            
            return user
            
        except Exception as e:
            if isinstance(e, BaseApplicationException):
                raise
            self.handle_exception(e, operation, context)
    
    def generate_token(self, user: User) -> str:
        """Generate JWT token with exception handling"""
        operation = "generate_token"
        context = {"user_id": user.id, "username": user.username}
        
        try:
            self.logger.info(
                "Token generation started",
                operation=operation,
                user_id=user.id,
                username=user.username
            )
            
            token = self.token_service.generate_token(user)
            
            self.logger.info(
                "Token generated successfully",
                operation=operation,
                user_id=user.id,
                username=user.username,
                token_length=len(token)
            )
            
            return token
            
        except Exception as e:
            if isinstance(e, BaseApplicationException):
                raise
            self.handle_exception(e, operation, context)
```

## Repository Layer Exception Handling

### 1. Database Exception Handling

#### Repository Exception Handling
```python
# src/repositories/base_repository.py
import structlog
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from src.core.exceptions import DatabaseException, ConflictException, NotFoundException
from src.core.logging import logger

class BaseRepository:
    """Base repository with database exception handling"""
    
    def __init__(self, model_class):
        self.model_class = model_class
        self.logger = logger.bind(service=f"{model_class.__name__}Repository")
    
    def handle_database_exception(self, error: Exception, operation: str, context: dict = None):
        """Handle database exceptions"""
        context = context or {}
        
        if isinstance(error, IntegrityError):
            self.logger.error(
                "Database integrity error",
                operation=operation,
                error_type=error.__class__.__name__,
                error_message=str(error),
                context=context,
                exc_info=True
            )
            raise ConflictException(
                message="Data integrity violation occurred",
                details={"operation": operation, "context": context},
                cause=error
            )
        
        elif isinstance(error, OperationalError):
            self.logger.error(
                "Database operational error",
                operation=operation,
                error_type=error.__class__.__name__,
                error_message=str(error),
                context=context,
                exc_info=True
            )
            raise DatabaseException(
                message="Database operation failed",
                details={"operation": operation, "context": context},
                cause=error
            )
        
        elif isinstance(error, SQLAlchemyError):
            self.logger.error(
                "Database error",
                operation=operation,
                error_type=error.__class__.__name__,
                error_message=str(error),
                context=context,
                exc_info=True
            )
            raise DatabaseException(
                message="Database error occurred",
                details={"operation": operation, "context": context},
                cause=error
            )
        
        else:
            self.logger.error(
                "Unexpected database error",
                operation=operation,
                error_type=error.__class__.__name__,
                error_message=str(error),
                context=context,
                exc_info=True
            )
            raise DatabaseException(
                message="Unexpected database error",
                details={"operation": operation, "context": context},
                cause=error
            )
    
    def get_by_id(self, id: int) -> Optional[Any]:
        """Get entity by ID with exception handling"""
        operation = "get_by_id"
        context = {"id": id}
        
        try:
            result = self.model_class.query.get(id)
            
            if not result:
                self.logger.debug(
                    "Entity not found",
                    operation=operation,
                    entity_type=self.model_class.__name__,
                    id=id
                )
            
            return result
            
        except Exception as e:
            self.handle_database_exception(e, operation, context)
    
    def create(self, data: dict) -> Any:
        """Create entity with exception handling"""
        operation = "create"
        context = {"data_fields": list(data.keys())}
        
        try:
            entity = self.model_class(**data)
            db.session.add(entity)
            db.session.commit()
            
            self.logger.info(
                "Entity created successfully",
                operation=operation,
                entity_type=self.model_class.__name__,
                entity_id=getattr(entity, 'id', None),
                context=context
            )
            
            return entity
            
        except Exception as e:
            db.session.rollback()
            self.handle_database_exception(e, operation, context)
    
    def update(self, id: int, data: dict) -> Any:
        """Update entity with exception handling"""
        operation = "update"
        context = {"id": id, "data_fields": list(data.keys())}
        
        try:
            entity = self.model_class.query.get(id)
            
            if not entity:
                self.logger.warning(
                    "Entity not found for update",
                    operation=operation,
                    entity_type=self.model_class.__name__,
                    id=id
                )
                raise NotFoundException(
                    message=f"{self.model_class.__name__} not found",
                    resource_type=self.model_class.__name__
                )
            
            for key, value in data.items():
                setattr(entity, key, value)
            
            db.session.commit()
            
            self.logger.info(
                "Entity updated successfully",
                operation=operation,
                entity_type=self.model_class.__name__,
                entity_id=id,
                context=context
            )
            
            return entity
            
        except Exception as e:
            db.session.rollback()
            if isinstance(e, BaseApplicationException):
                raise
            self.handle_database_exception(e, operation, context)
    
    def delete(self, id: int) -> bool:
        """Delete entity with exception handling"""
        operation = "delete"
        context = {"id": id}
        
        try:
            entity = self.model_class.query.get(id)
            
            if not entity:
                self.logger.warning(
                    "Entity not found for deletion",
                    operation=operation,
                    entity_type=self.model_class.__name__,
                    id=id
                )
                return False
            
            db.session.delete(entity)
            db.session.commit()
            
            self.logger.info(
                "Entity deleted successfully",
                operation=operation,
                entity_type=self.model_class.__name__,
                entity_id=id
            )
            
            return True
            
        except Exception as e:
            db.session.rollback()
            self.handle_database_exception(e, operation, context)
```

## Exception Testing

### 1. Exception Testing

#### Exception Test Cases
```python
# tests/unit/test_exception_handling.py
import pytest
from unittest.mock import Mock, patch
from src.core.exceptions import (
    BaseApplicationException,
    ValidationException,
    AuthenticationException,
    NotFoundException,
    DatabaseException
)
from src.exceptions.auth_exceptions import (
    UserNotFoundException,
    InvalidPasswordException
)
from src.services.auth_service import AuthService
from src.repositories.base_repository import BaseRepository

class TestBaseApplicationException:
    """Test base application exception"""
    
    def test_exception_creation(self):
        """Test exception creation with basic parameters"""
        exception = BaseApplicationException(
            message="Test error",
            error_code="TEST_ERROR",
            status_code=400,
            details={"key": "value"}
        )
        
        assert exception.message == "Test error"
        assert exception.error_code == "TEST_ERROR"
        assert exception.status_code == 400
        assert exception.details == {"key": "value"}
        assert exception.timestamp is not None
    
    def test_exception_to_dict(self):
        """Test exception serialization to dictionary"""
        exception = BaseApplicationException(
            message="Test error",
            error_code="TEST_ERROR",
            status_code=400,
            details={"key": "value"}
        )
        
        result = exception.to_dict()
        
        assert result["error"] == "TEST_ERROR"
        assert result["message"] == "Test error"
        assert result["status_code"] == 400
        assert result["details"] == {"key": "value"}
        assert "timestamp" in result

class TestValidationException:
    """Test validation exception"""
    
    def test_validation_exception_creation(self):
        """Test validation exception creation"""
        validation_errors = [
            {"field": "username", "message": "Username is required"},
            {"field": "password", "message": "Password is too short"}
        ]
        
        exception = ValidationException(
            message="Validation failed",
            validation_errors=validation_errors
        )
        
        assert exception.message == "Validation failed"
        assert exception.error_code == "VALIDATION_ERROR"
        assert exception.status_code == 422
        assert exception.validation_errors == validation_errors
        assert "validation_errors" in exception.details

class TestAuthenticationExceptions:
    """Test authentication exceptions"""
    
    def test_user_not_found_exception(self):
        """Test user not found exception"""
        exception = UserNotFoundException(username="testuser")
        
        assert exception.error_code == "AUTHENTICATION_ERROR"
        assert exception.status_code == 401
        assert "testuser" in exception.message
        assert exception.details["username"] == "testuser"
    
    def test_invalid_password_exception(self):
        """Test invalid password exception"""
        exception = InvalidPasswordException(username="testuser")
        
        assert exception.error_code == "AUTHENTICATION_ERROR"
        assert exception.status_code == 401
        assert exception.details["username"] == "testuser"

class TestServiceExceptionHandling:
    """Test service exception handling"""
    
    def test_auth_service_exception_handling(self):
        """Test authentication service exception handling"""
        # Mock dependencies
        mock_user_repo = Mock()
        mock_password_service = Mock()
        mock_token_service = Mock()
        
        auth_service = AuthService()
        auth_service.user_repository = mock_user_repo
        auth_service.password_service = mock_password_service
        auth_service.token_service = mock_token_service
        
        # Test user not found
        mock_user_repo.get_by_username.return_value = None
        
        with pytest.raises(UserNotFoundException) as exc_info:
            auth_service.authenticate_user("nonexistent", "password")
        
        assert exc_info.value.details["username"] == "nonexistent"
    
    def test_service_unexpected_exception_handling(self):
        """Test service unexpected exception handling"""
        # Mock dependencies to raise unexpected exception
        mock_user_repo = Mock()
        mock_user_repo.get_by_username.side_effect = Exception("Database connection failed")
        
        auth_service = AuthService()
        auth_service.user_repository = mock_user_repo
        
        with pytest.raises(DatabaseException) as exc_info:
            auth_service.authenticate_user("testuser", "password")
        
        assert exc_info.value.error_code == "DATABASE_ERROR"
        assert exc_info.value.status_code == 500

class TestRepositoryExceptionHandling:
    """Test repository exception handling"""
    
    def test_repository_not_found_handling(self):
        """Test repository not found handling"""
        # Mock model class
        mock_model_class = Mock()
        mock_model_class.__name__ = "TestModel"
        
        repository = BaseRepository(mock_model_class)
        
        # Mock database query to return None
        with patch('src.repositories.base_repository.db') as mock_db:
            mock_db.session.query.return_value.get.return_value = None
            
            result = repository.get_by_id(999)
            
            assert result is None
    
    def test_repository_integrity_error_handling(self):
        """Test repository integrity error handling"""
        # Mock model class
        mock_model_class = Mock()
        mock_model_class.__name__ = "TestModel"
        
        repository = BaseRepository(mock_model_class)
        
        # Mock integrity error
        from sqlalchemy.exc import IntegrityError
        mock_integrity_error = IntegrityError("statement", "params", "orig")
        
        with patch('src.repositories.base_repository.db') as mock_db:
            mock_db.session.add.side_effect = mock_integrity_error
            
            with pytest.raises(ConflictException) as exc_info:
                repository.create({"name": "test"})
            
            assert exc_info.value.error_code == "CONFLICT"
            assert exc_info.value.status_code == 409
```

## Exception Best Practices

### 1. Exception Design Principles

#### Exception Design Guidelines
```python
# src/core/exception_guidelines.py

class ExceptionDesignPrinciples:
    """Guidelines for exception design and usage"""
    
    @staticmethod
    def create_meaningful_exceptions():
        """Create exceptions with meaningful names and messages"""
        # Good: Specific exception with clear purpose
        class UserNotFoundException(AuthenticationException):
            pass
        
        # Bad: Generic exception without context
        class Error(Exception):
            pass
    
    @staticmethod
    def include_relevant_context():
        """Include relevant context in exceptions"""
        # Good: Include relevant details
        raise UserNotFoundException(
            username=username,
            user_id=user_id,
            timestamp=datetime.utcnow()
        )
        
        # Bad: No context
        raise Exception("User not found")
    
    @staticmethod
    def use_appropriate_status_codes():
        """Use appropriate HTTP status codes"""
        # Good: Correct status codes
        class NotFoundException(BaseApplicationException):
            status_code = 404
        
        class ValidationException(BaseApplicationException):
            status_code = 422
        
        # Bad: Wrong status codes
        class NotFoundException(BaseApplicationException):
            status_code = 500  # Should be 404
    
    @staticmethod
    def handle_exceptions_at_appropriate_levels():
        """Handle exceptions at appropriate levels"""
        # Good: Handle at service layer
        class AuthService:
            def authenticate_user(self, username, password):
                try:
                    # Authentication logic
                    pass
                except DatabaseError as e:
                    # Log and re-raise
                    self.logger.error("Database error during authentication")
                    raise
        
        # Bad: Handle at wrong level
        class UserRepository:
            def get_user(self, username):
                try:
                    # Database query
                    pass
                except Exception as e:
                    # Should not handle HTTP errors here
                    return jsonify({"error": str(e)}), 500
```

## Benefits of Exception Handling Implementation

### 1. Error Management
- **Consistent error responses** across all endpoints
- **Proper HTTP status codes** for different error types
- **Detailed error information** for debugging
- **User-friendly error messages** for API consumers

### 2. Debugging and Monitoring
- **Structured error logging** with context
- **Error tracking** with request IDs
- **Performance monitoring** for error rates
- **Alerting** for critical errors

### 3. Security
- **Information disclosure prevention** in production
- **Error sanitization** for external consumers
- **Security event logging** for suspicious activities
- **Rate limiting** for error-prone endpoints

### 4. Maintainability
- **Centralized exception handling** logic
- **Reusable exception classes** across modules
- **Clear exception hierarchy** for easy understanding
- **Comprehensive testing** of exception scenarios

## Conclusion

The exception handling implementation provides:
- **Comprehensive exception hierarchy** for different error types
- **Centralized error handling** with consistent responses
- **Detailed logging and monitoring** for debugging
- **Security safeguards** for production environments
- **Extensive testing** of exception scenarios
- **Best practices** for exception design and usage

This implementation serves as a robust foundation for error management throughout the application.
