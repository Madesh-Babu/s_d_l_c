# Centralized Error Handling Setup

## Overview

This document outlines the centralized error handling setup implemented throughout the application to provide consistent error management, proper logging, and standardized error responses across all components.

## Error Handling Architecture

### 1. Error Handling Middleware

#### Global Error Handler
```python
# src/middleware/error_handler.py
import structlog
from flask import jsonify, request, g
from typing import Dict, Any, Optional
from datetime import datetime
import traceback
import os

from src.core.exceptions import BaseApplicationException
from src.core.logging import logger

class CentralizedErrorHandler:
    """Centralized error handling middleware"""
    
    def __init__(self, app=None):
        self.app = app
        self.logger = logger.bind(service="error_handler")
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize error handlers for Flask app"""
        # Register exception handlers
        app.register_error_handler(BaseApplicationException, self.handle_application_exception)
        app.register_error_handler(Exception, self.handle_unexpected_exception)
        app.register_error_handler(404, self.handle_not_found)
        app.register_error_handler(405, self.handle_method_not_allowed)
        app.register_error_handler(413, self.handle_payload_too_large)
        app.register_error_handler(422, self.handle_unprocessable_entity)
        app.register_error_handler(429, self.handle_rate_limit_exceeded)
        app.register_error_handler(500, self.handle_internal_server_error)
        app.register_error_handler(502, self.handle_bad_gateway)
        app.register_error_handler(503, self.handle_service_unavailable)
        
        # Setup before/after request hooks
        app.before_request(self._setup_request_context)
        app.after_request(self._log_request_completion)
    
    def _setup_request_context(self):
        """Setup request context for error handling"""
        import uuid
        g.request_id = str(uuid.uuid4())
        g.request_start_time = datetime.utcnow()
        g.error_occurred = False
    
    def _log_request_completion(self, response):
        """Log request completion with error status"""
        if g.error_occurred:
            self.logger.warning(
                "Request completed with error",
                request_id=g.request_id,
                status_code=response.status_code
            )
        return response
    
    def create_error_response(
        self,
        error_code: str,
        message: str,
        status_code: int,
        details: Optional[Dict[str, Any]] = None,
        include_stack_trace: bool = False
    ) -> Dict[str, Any]:
        """Create standardized error response"""
        response = {
            "success": False,
            "error": error_code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add request ID if available
        if hasattr(g, 'request_id'):
            response["request_id"] = g.request_id
        
        # Add details if provided
        if details:
            response["details"] = details
        
        # Add stack trace in development
        if include_stack_trace and os.getenv('ENVIRONMENT') == 'development':
            response["stack_trace"] = traceback.format_exc()
        
        return response
    
    def handle_application_exception(self, error: BaseApplicationException):
        """Handle application-specific exceptions"""
        g.error_occurred = True
        
        # Log the error with full context
        self.logger.error(
            "Application exception occurred",
            error_type=error.__class__.__name__,
            error_code=error.error_code,
            error_message=error.message,
            status_code=error.status_code,
            details=error.details,
            request_id=getattr(g, 'request_id', None),
            user_id=getattr(g, 'current_user', {}).get('id', None),
            endpoint=request.endpoint,
            method=request.method,
            path=request.path,
            user_agent=request.headers.get('User-Agent'),
            remote_addr=request.remote_addr,
            exc_info=True
        )
        
        # Create error response
        response_data = self.create_error_response(
            error_code=error.error_code,
            message=error.message,
            status_code=error.status_code,
            details=error.details,
            include_stack_trace=True
        )
        
        return jsonify(response_data), error.status_code
    
    def handle_unexpected_exception(self, error: Exception):
        """Handle unexpected exceptions"""
        g.error_occurred = True
        
        # Log the unexpected error
        self.logger.error(
            "Unexpected exception occurred",
            error_type=error.__class__.__name__,
            error_message=str(error),
            request_id=getattr(g, 'request_id', None),
            user_id=getattr(g, 'current_user', {}).get('id', None),
            endpoint=request.endpoint,
            method=request.method,
            path=request.path,
            user_agent=request.headers.get('User-Agent'),
            remote_addr=request.remote_addr,
            exc_info=True
        )
        
        # Create generic error response
        response_data = self.create_error_response(
            error_code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            status_code=500,
            include_stack_trace=True
        )
        
        # Add development details
        if os.getenv('ENVIRONMENT') == 'development':
            response_data["details"] = {
                "error_type": error.__class__.__name__,
                "error_message": str(error)
            }
        
        return jsonify(response_data), 500
    
    def handle_not_found(self, error):
        """Handle 404 not found errors"""
        g.error_occurred = True
        
        self.logger.warning(
            "Resource not found",
            path=request.path,
            method=request.method,
            request_id=getattr(g, 'request_id', None),
            user_agent=request.headers.get('User-Agent'),
            remote_addr=request.remote_addr
        )
        
        response_data = self.create_error_response(
            error_code="NOT_FOUND",
            message="The requested resource was not found",
            status_code=404
        )
        
        return jsonify(response_data), 404
    
    def handle_method_not_allowed(self, error):
        """Handle 405 method not allowed errors"""
        g.error_occurred = True
        
        self.logger.warning(
            "Method not allowed",
            path=request.path,
            method=request.method,
            request_id=getattr(g, 'request_id', None),
            user_agent=request.headers.get('User-Agent'),
            remote_addr=request.remote_addr
        )
        
        response_data = self.create_error_response(
            error_code="METHOD_NOT_ALLOWED",
            message="The requested method is not allowed for this resource",
            status_code=405
        )
        
        return jsonify(response_data), 405
    
    def handle_unprocessable_entity(self, error):
        """Handle 422 unprocessable entity errors"""
        g.error_occurred = True
        
        self.logger.warning(
            "Unprocessable entity",
            path=request.path,
            method=request.method,
            request_id=getattr(g, 'request_id', None),
            error_message=str(error)
        )
        
        response_data = self.create_error_response(
            error_code="UNPROCESSABLE_ENTITY",
            message="The request could not be processed",
            status_code=422,
            details={"error_details": str(error)}
        )
        
        return jsonify(response_data), 422
    
    def handle_payload_too_large(self, error):
        """Handle 413 payload too large errors"""
        g.error_occurred = True
        
        self.logger.warning(
            "Payload too large",
            path=request.path,
            method=request.method,
            request_id=getattr(g, 'request_id', None),
            content_length=request.content_length
        )
        
        response_data = self.create_error_response(
            error_code="PAYLOAD_TOO_LARGE",
            message="The request payload is too large",
            status_code=413,
            details={"max_size": "10MB"}
        )
        
        return jsonify(response_data), 413
    
    def handle_rate_limit_exceeded(self, error):
        """Handle 429 rate limit exceeded errors"""
        g.error_occurred = True
        
        self.logger.warning(
            "Rate limit exceeded",
            path=request.path,
            method=request.method,
            request_id=getattr(g, 'request_id', None),
            remote_addr=request.remote_addr
        )
        
        response_data = self.create_error_response(
            error_code="RATE_LIMIT_EXCEEDED",
            message="Rate limit exceeded",
            status_code=429,
            details={"retry_after": 60}
        )
        
        return jsonify(response_data), 429
    
    def handle_internal_server_error(self, error):
        """Handle 500 internal server errors"""
        g.error_occurred = True
        
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
        
        response_data = self.create_error_response(
            error_code="INTERNAL_SERVER_ERROR",
            message="An internal server error occurred",
            status_code=500,
            include_stack_trace=True
        )
        
        return jsonify(response_data), 500
    
    def handle_bad_gateway(self, error):
        """Handle 502 bad gateway errors"""
        g.error_occurred = True
        
        self.logger.error(
            "Bad gateway error",
            request_id=getattr(g, 'request_id', None),
            endpoint=request.endpoint,
            method=request.method,
            path=request.path
        )
        
        response_data = self.create_error_response(
            error_code="BAD_GATEWAY",
            message="Bad gateway - external service unavailable",
            status_code=502
        )
        
        return jsonify(response_data), 502
    
    def handle_service_unavailable(self, error):
        """Handle 503 service unavailable errors"""
        g.error_occurred = True
        
        self.logger.error(
            "Service unavailable",
            request_id=getattr(g, 'request_id', None),
            endpoint=request.endpoint,
            method=request.method,
            path=request.path
        )
        
        response_data = self.create_error_response(
            error_code="SERVICE_UNAVAILABLE",
            message="Service temporarily unavailable",
            status_code=503,
            details={"retry_after": 30}
        )
        
        return jsonify(response_data), 503
```

### 2. Error Response Formatter

#### Response Formatting
```python
# src/utils/response_formatter.py
from typing import Dict, Any, Optional, List
from datetime import datetime
from flask import g

class ResponseFormatter:
    """Centralized response formatting utilities"""
    
    @staticmethod
    def create_success_response(
        data: Any = None,
        message: str = "Operation successful",
        status_code: int = 200,
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create standardized success response"""
        response = {
            "success": True,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if data is not None:
            response["data"] = data
        
        if meta:
            response["meta"] = meta
        
        if hasattr(g, 'request_id'):
            response["request_id"] = g.request_id
        
        return response, status_code
    
    @staticmethod
    def create_error_response(
        error_code: str,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
        errors: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create standardized error response"""
        response = {
            "success": False,
            "error": error_code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if details:
            response["details"] = details
        
        if errors:
            response["errors"] = errors
        
        if hasattr(g, 'request_id'):
            response["request_id"] = g.request_id
        
        return response, status_code
    
    @staticmethod
    def create_validation_error_response(
        validation_errors: List[Dict[str, Any]],
        message: str = "Validation failed"
    ) -> Dict[str, Any]:
        """Create validation error response"""
        return ResponseFormatter.create_error_response(
            error_code="VALIDATION_ERROR",
            message=message,
            status_code=422,
            errors=validation_errors
        )
    
    @staticmethod
    def create_paginated_response(
        data: List[Any],
        total: int,
        page: int,
        per_page: int,
        has_next: bool,
        has_prev: bool,
        message: str = "Data retrieved successfully"
    ) -> Dict[str, Any]:
        """Create paginated response"""
        meta = {
            "pagination": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "has_next": has_next,
                "has_prev": has_prev,
                "pages": (total + per_page - 1) // per_page
            }
        }
        
        return ResponseFormatter.create_success_response(
            data=data,
            message=message,
            meta=meta
        )
```

### 3. Error Monitoring and Alerting

#### Error Monitoring
```python
# src/monitoring/error_monitor.py
import structlog
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading

from src.core.logging import logger

class ErrorMonitor:
    """Error monitoring and alerting system"""
    
    def __init__(self):
        self.logger = logger.bind(service="error_monitor")
        self.error_counts = defaultdict(int)
        self.error_history = deque(maxlen=1000)
        self.alert_thresholds = {
            'error_rate_per_minute': 10,
            'same_error_count': 5,
            'critical_error_types': ['DatabaseException', 'ExternalServiceException']
        }
        self.lock = threading.Lock()
    
    def record_error(
        self,
        error_type: str,
        error_code: str,
        message: str,
        context: Dict[str, Any] = None
    ):
        """Record error for monitoring"""
        with self.lock:
            # Increment error count
            self.error_counts[error_type] += 1
            
            # Add to history
            error_record = {
                'timestamp': datetime.utcnow(),
                'error_type': error_type,
                'error_code': error_code,
                'message': message,
                'context': context or {}
            }
            self.error_history.append(error_record)
            
            # Check for alerts
            self._check_alert_conditions(error_record)
    
    def _check_alert_conditions(self, error_record: Dict[str, Any]):
        """Check if alert conditions are met"""
        error_type = error_record['error_type']
        error_code = error_record['error_code']
        
        # Check critical error types
        if error_type in self.alert_thresholds['critical_error_types']:
            self._send_critical_alert(error_record)
        
        # Check error rate
        if self._get_error_rate_per_minute() > self.alert_thresholds['error_rate_per_minute']:
            self._send_rate_alert()
        
        # Check same error count
        if self.error_counts[error_type] >= self.alert_thresholds['same_error_count']:
            self._send_repeat_error_alert(error_record)
    
    def _get_error_rate_per_minute(self) -> int:
        """Get error rate per minute"""
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        recent_errors = [
            error for error in self.error_history
            if error['timestamp'] > one_minute_ago
        ]
        return len(recent_errors)
    
    def _send_critical_alert(self, error_record: Dict[str, Any]):
        """Send critical error alert"""
        self.logger.error(
            "CRITICAL ERROR ALERT",
            error_type=error_record['error_type'],
            error_code=error_record['error_code'],
            message=error_record['message'],
            context=error_record['context'],
            alert_type="critical"
        )
        
        # Here you could integrate with external alerting systems
        # like Slack, PagerDuty, email, etc.
    
    def _send_rate_alert(self):
        """Send high error rate alert"""
        self.logger.error(
            "HIGH ERROR RATE ALERT",
            errors_per_minute=self._get_error_rate_per_minute(),
            threshold=self.alert_thresholds['error_rate_per_minute'],
            alert_type="rate"
        )
    
    def _send_repeat_error_alert(self, error_record: Dict[str, Any]):
        """Send repeat error alert"""
        self.logger.error(
            "REPEAT ERROR ALERT",
            error_type=error_record['error_type'],
            error_code=error_record['error_code'],
            count=self.error_counts[error_record['error_type']],
            threshold=self.alert_thresholds['same_error_count'],
            alert_type="repeat"
        )
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        with self.lock:
            total_errors = len(self.error_history)
            error_types = dict(self.error_counts)
            
            # Calculate error rate
            error_rate = self._get_error_rate_per_minute()
            
            # Get most recent errors
            recent_errors = list(self.error_history)[-10:]
            
            return {
                'total_errors': total_errors,
                'error_rate_per_minute': error_rate,
                'error_types': error_types,
                'recent_errors': recent_errors,
                'alert_thresholds': self.alert_thresholds
            }
    
    def reset_statistics(self):
        """Reset error statistics"""
        with self.lock:
            self.error_counts.clear()
            self.error_history.clear()
            self.logger.info("Error statistics reset")

# Global error monitor instance
error_monitor = ErrorMonitor()
```

### 4. Error Recovery Mechanisms

#### Error Recovery
```python
# src/utils/error_recovery.py
import structlog
from typing import Callable, Any, Optional
from functools import wraps
import time
import random

from src.core.logging import logger

class ErrorRecovery:
    """Error recovery mechanisms"""
    
    def __init__(self):
        self.logger = logger.bind(service="error_recovery")
    
    def retry_with_backoff(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """Decorator for retrying functions with exponential backoff"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    
                    except Exception as e:
                        last_exception = e
                        
                        if attempt == max_retries:
                            self.logger.error(
                                "Function failed after all retries",
                                function=func.__name__,
                                attempt=attempt,
                                max_retries=max_retries,
                                error_type=type(e).__name__,
                                error_message=str(e)
                            )
                            raise
                        
                        # Calculate delay
                        delay = min(base_delay * (exponential_base ** attempt), max_delay)
                        
                        if jitter:
                            delay = delay * (0.5 + random.random() * 0.5)
                        
                        self.logger.warning(
                            "Function failed, retrying",
                            function=func.__name__,
                            attempt=attempt,
                            max_retries=max_retries,
                            delay=delay,
                            error_type=type(e).__name__,
                            error_message=str(e)
                        )
                        
                        time.sleep(delay)
                
                # This should never be reached
                raise last_exception
            
            return wrapper
        return decorator
    
    def circuit_breaker(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        """Decorator for circuit breaker pattern"""
        def decorator(func: Callable) -> Callable:
            # Circuit breaker state
            state = {
                'failure_count': 0,
                'last_failure_time': None,
                'state': 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
            }
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Check circuit state
                if state['state'] == 'OPEN':
                    if time.time() - state['last_failure_time'] > recovery_timeout:
                        state['state'] = 'HALF_OPEN'
                        self.logger.info(
                            "Circuit breaker transitioning to HALF_OPEN",
                            function=func.__name__
                        )
                    else:
                        raise Exception("Circuit breaker is OPEN")
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Reset on success
                    if state['state'] == 'HALF_OPEN':
                        state['state'] = 'CLOSED'
                        state['failure_count'] = 0
                        self.logger.info(
                            "Circuit breaker transitioning to CLOSED",
                            function=func.__name__
                        )
                    
                    return result
                
                except expected_exception as e:
                    state['failure_count'] += 1
                    state['last_failure_time'] = time.time()
                    
                    if state['failure_count'] >= failure_threshold:
                        state['state'] = 'OPEN'
                        self.logger.error(
                            "Circuit breaker transitioning to OPEN",
                            function=func.__name__,
                            failure_count=state['failure_count'],
                            threshold=failure_threshold
                        )
                    
                    self.logger.warning(
                        "Function failed in circuit breaker",
                        function=func.__name__,
                        failure_count=state['failure_count'],
                        circuit_state=state['state'],
                        error_type=type(e).__name__,
                        error_message=str(e)
                    )
                    
                    raise
            
            return wrapper
        return decorator
    
    def fallback_handler(self, fallback_func: Callable):
        """Decorator for fallback handling"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    self.logger.warning(
                        "Function failed, using fallback",
                        function=func.__name__,
                        fallback_function=fallback_func.__name__,
                        error_type=type(e).__name__,
                        error_message=str(e)
                    )
                    return fallback_func(*args, **kwargs)
            
            return wrapper
        return decorator

# Global error recovery instance
error_recovery = ErrorRecovery()
```

### 5. Integration with Flask Application

#### Flask Integration
```python
# src/app.py
from flask import Flask
from src.middleware.error_handler import CentralizedErrorHandler
from src.monitoring.error_monitor import error_monitor
from src.utils.response_formatter import ResponseFormatter

def create_app():
    """Create Flask application with centralized error handling"""
    app = Flask(__name__)
    
    # Initialize centralized error handler
    error_handler = CentralizedErrorHandler(app)
    
    # Configure error monitoring
    app.config['ERROR_MONITOR'] = error_monitor
    
    # Add error monitoring to request context
    @app.before_request
    def setup_error_monitoring():
        """Setup error monitoring for request"""
        g.error_monitor = error_monitor
    
    @app.errorhandler(Exception)
    def handle_exception_with_monitoring(error):
        """Handle exception with monitoring"""
        # Record error for monitoring
        error_monitor.record_error(
            error_type=type(error).__name__,
            error_code=getattr(error, 'error_code', 'UNKNOWN'),
            message=str(error),
            context={
                'endpoint': request.endpoint,
                'method': request.method,
                'path': request.path,
                'user_id': getattr(g, 'current_user', {}).get('id', None)
            }
        )
        
        # Let centralized error handler handle the response
        return error_handler.handle_unexpected_exception(error)
    
    # Add error statistics endpoint
    @app.route('/admin/error-stats')
    def get_error_statistics():
        """Get error statistics (admin only)"""
        if not getattr(g, 'current_user', {}).get('role') == 'admin':
            return ResponseFormatter.create_error_response(
                error_code="ACCESS_DENIED",
                message="Admin access required",
                status_code=403
            )
        
        stats = error_monitor.get_error_statistics()
        return ResponseFormatter.create_success_response(
            data=stats,
            message="Error statistics retrieved"
        )
    
    return app
```

## Error Handling Testing

### 1. Error Handler Tests

#### Error Handler Test Cases
```python
# tests/unit/test_error_handler.py
import pytest
import json
from unittest.mock import Mock, patch
from flask import Flask
from src.middleware.error_handler import CentralizedErrorHandler
from src.core.exceptions import (
    BaseApplicationException,
    ValidationException,
    AuthenticationException
)

class TestCentralizedErrorHandler:
    """Test centralized error handler"""
    
    def setup_method(self):
        """Setup test environment"""
        self.app = Flask(__name__)
        self.error_handler = CentralizedErrorHandler()
        self.error_handler.init_app(self.app)
        self.client = self.app.test_client()
    
    def test_application_exception_handling(self):
        """Test application exception handling"""
        @self.app.route('/test-app-exception')
        def test_app_exception():
            raise ValidationException(
                message="Test validation error",
                validation_errors=[{"field": "test", "message": "Test error"}]
            )
        
        response = self.client.get('/test-app-exception')
        
        assert response.status_code == 422
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert data['error'] == 'VALIDATION_ERROR'
        assert data['message'] == 'Test validation error'
        assert 'validation_errors' in data['details']
        assert 'request_id' in data
    
    def test_unexpected_exception_handling(self):
        """Test unexpected exception handling"""
        @self.app.route('/test-unexpected')
        def test_unexpected():
            raise Exception("Unexpected error")
        
        response = self.client.get('/test-unexpected')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert data['error'] == 'INTERNAL_SERVER_ERROR'
        assert data['message'] == 'An unexpected error occurred'
        assert 'request_id' in data
    
    def test_not_found_handling(self):
        """Test 404 not found handling"""
        response = self.client.get('/nonexistent-endpoint')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert data['error'] == 'NOT_FOUND'
        assert 'request_id' in data
    
    def test_method_not_allowed_handling(self):
        """Test 405 method not allowed handling"""
        @self.app.route('/test-method', methods=['GET'])
        def test_method():
            return "OK"
        
        response = self.client.post('/test-method')
        
        assert response.status_code == 405
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert data['error'] == 'METHOD_NOT_ALLOWED'
        assert 'request_id' in data
    
    def test_error_response_format(self):
        """Test error response format consistency"""
        @self.app.route('/test-format')
        def test_format():
            raise AuthenticationException(message="Test auth error")
        
        response = self.client.get('/test-format')
        data = json.loads(response.data)
        
        # Check required fields
        required_fields = ['success', 'error', 'message', 'timestamp']
        for field in required_fields:
            assert field in data
        
        # Check field types
        assert isinstance(data['success'], bool)
        assert isinstance(data['error'], str)
        assert isinstance(data['message'], str)
        assert isinstance(data['timestamp'], str)
    
    @patch.dict('os.environ', {'ENVIRONMENT': 'development'})
    def test_development_stack_trace(self):
        """Test stack trace inclusion in development"""
        @self.app.route('/test-stack-trace')
        def test_stack_trace():
            raise Exception("Test error")
        
        response = self.client.get('/test-stack-trace')
        data = json.loads(response.data)
        
        assert 'stack_trace' in data
        assert 'Test error' in data['stack_trace']

class TestResponseFormatter:
    """Test response formatter"""
    
    def test_success_response_format(self):
        """Test success response format"""
        response, status_code = ResponseFormatter.create_success_response(
            data={"test": "data"},
            message="Success message"
        )
        
        assert status_code == 200
        assert response['success'] is True
        assert response['message'] == "Success message"
        assert response['data'] == {"test": "data"}
        assert 'timestamp' in response
    
    def test_error_response_format(self):
        """Test error response format"""
        response, status_code = ResponseFormatter.create_error_response(
            error_code="TEST_ERROR",
            message="Test error",
            status_code=400,
            details={"detail": "test"}
        )
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "TEST_ERROR"
        assert response['message'] == "Test error"
        assert response['details'] == {"detail": "test"}
        assert 'timestamp' in response
    
    def test_validation_error_response(self):
        """Test validation error response"""
        validation_errors = [
            {"field": "username", "message": "Required"},
            {"field": "email", "message": "Invalid format"}
        ]
        
        response, status_code = ResponseFormatter.create_validation_error_response(
            validation_errors=validation_errors
        )
        
        assert status_code == 422
        assert response['error'] == "VALIDATION_ERROR"
        assert response['errors'] == validation_errors
    
    def test_paginated_response(self):
        """Test paginated response format"""
        response, status_code = ResponseFormatter.create_paginated_response(
            data=[{"id": 1}, {"id": 2}],
            total=10,
            page=1,
            per_page=2,
            has_next=True,
            has_prev=False
        )
        
        assert status_code == 200
        assert response['success'] is True
        assert len(response['data']) == 2
        assert response['meta']['pagination']['total'] == 10
        assert response['meta']['pagination']['page'] == 1
        assert response['meta']['pagination']['has_next'] is True
```

## Benefits of Centralized Error Handling

### 1. Consistency
- **Standardized error responses** across all endpoints
- **Consistent error codes** and messages
- **Uniform logging format** for all errors
- **Reliable error tracking** with request IDs

### 2. Monitoring and Alerting
- **Real-time error monitoring** with statistics
- **Automatic alerting** for critical errors
- **Error rate tracking** and threshold alerts
- **Historical error analysis** for patterns

### 3. Debugging and Maintenance
- **Comprehensive error context** for debugging
- **Stack traces** in development environments
- **Error categorization** for better understanding
- **Centralized error handling** logic

### 4. User Experience
- **User-friendly error messages** for API consumers
- **Proper HTTP status codes** for different error types
- **Request tracking** for support and debugging
- **Consistent API behavior** during errors

## Conclusion

The centralized error handling setup provides:
- **Comprehensive error management** across all application layers
- **Consistent error responses** with standardized format
- **Real-time monitoring** and alerting capabilities
- **Recovery mechanisms** for improved reliability
- **Extensive testing** of error scenarios
- **Better debugging** and maintenance experience

This implementation serves as a robust foundation for error handling throughout the application.
