# Structured Logging Implementation

## Overview

This document outlines the comprehensive structured logging implementation throughout the application using structlog for consistent, searchable, and machine-readable log messages.

## Logging Configuration

### 1. Structured Logging Setup

#### Logger Configuration
```python
# src/core/logging.py
import structlog
import logging
import sys
from typing import Any, Dict
from datetime import datetime

class StructuredLogger:
    """Structured logging configuration"""
    
    def __init__(self):
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup structured logging with processors"""
        # Configure structlog processors
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                self._add_request_id,
                self._add_user_context,
                self._add_environment_context,
                structlog.processors.JSONRenderer() if self._should_use_json() 
                else structlog.dev.ConsoleRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # Configure standard logging
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=logging.INFO
        )
    
    def _should_use_json(self) -> bool:
        """Determine if JSON logging should be used"""
        import os
        return os.getenv('ENVIRONMENT', 'development') == 'production'
    
    def _add_request_id(self, logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Add request ID to log context"""
        from flask import g
        if hasattr(g, 'request_id'):
            event_dict['request_id'] = g.request_id
        return event_dict
    
    def _add_user_context(self, logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Add user context to log messages"""
        from flask import g
        if hasattr(g, 'current_user'):
            event_dict['user_id'] = g.current_user.id
            event_dict['username'] = g.current_user.username
            event_dict['user_role'] = g.current_user.role
        return event_dict
    
    def _add_environment_context(self, logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Add environment context to log messages"""
        import os
        event_dict['environment'] = os.getenv('ENVIRONMENT', 'development')
        event_dict['service'] = 'sdlc_inventory'
        event_dict['version'] = os.getenv('APP_VERSION', '1.0.0')
        return event_dict

# Initialize structured logger
structured_logger = StructuredLogger()
logger = structlog.get_logger()
```

### 2. Environment-Based Configuration

#### Logging Configuration Models
```python
# src/core/config.py
from pydantic import BaseSettings, Field, validator

class LoggingConfig(BaseSettings):
    """Logging configuration"""
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format (json or console)")
    LOG_FILE: Optional[str] = Field(None, description="Log file path")
    LOG_ROTATION: str = Field(default="daily", description="Log rotation strategy")
    LOG_RETENTION: int = Field(default=30, description="Log retention days")
    ENABLE_REQUEST_LOGGING: bool = Field(default=True, description="Enable request logging")
    ENABLE_PERFORMANCE_LOGGING: bool = Field(default=True, description="Enable performance logging")
    ENABLE_SECURITY_LOGGING: bool = Field(default=True, description="Enable security logging")
    
    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v.upper()
    
    @validator('LOG_FORMAT')
    def validate_log_format(cls, v):
        """Validate log format"""
        valid_formats = ['json', 'console']
        if v.lower() not in valid_formats:
            raise ValueError(f"Log format must be one of: {', '.join(valid_formats)}")
        return v.lower()
    
    @validator('LOG_ROTATION')
    def validate_log_rotation(cls, v):
        """Validate log rotation strategy"""
        valid_rotations = ['daily', 'weekly', 'monthly', 'size']
        if v.lower() not in valid_rotations:
            raise ValueError(f"Log rotation must be one of: {', '.join(valid_rotations)}")
        return v.lower()
```

## Logging Implementation

### 1. Application Logging

#### Main Application Logging
```python
# src/api/main.py
import structlog
from flask import Flask, request, g
from src.core.logging import logger
from src.core.config import settings

app = Flask(__name__)

@app.before_request
def before_request():
    """Setup request context for logging"""
    import uuid
    g.request_id = str(uuid.uuid4())
    g.request_start_time = datetime.utcnow()
    
    logger.info(
        "Request started",
        method=request.method,
        url=request.url,
        remote_addr=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        request_id=g.request_id
    )

@app.after_request
def after_request(response):
    """Log request completion"""
    import time
    duration = time.time() - g.request_start_time.timestamp()
    
    logger.info(
        "Request completed",
        method=request.method,
        url=request.url,
        status_code=response.status_code,
        duration_ms=duration * 1000,
        request_id=g.request_id
    )
    
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    """Log unhandled exceptions"""
    logger.error(
        "Unhandled exception",
        exception_type=type(e).__name__,
        exception_message=str(e),
        request_id=getattr(g, 'request_id', None),
        exc_info=True
    )
    return {"error": "Internal server error"}, 500
```

### 2. Service Layer Logging

#### Authentication Service Logging
```python
# src/services/auth_service.py
import structlog
from src.core.logging import logger

class AuthService:
    """Authentication service with structured logging"""
    
    def __init__(self, user_repository, password_service, token_service):
        self.user_repository = user_repository
        self.password_service = password_service
        self.token_service = token_service
        self.logger = logger.bind(service="auth_service")
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with logging"""
        self.logger.info(
            "User authentication attempt",
            username=username,
            action="authenticate"
        )
        
        try:
            user = self.user_repository.get_by_username(username)
            
            if not user:
                self.logger.warning(
                    "Authentication failed - user not found",
                    username=username,
                    reason="user_not_found"
                )
                return None
            
            if not self.password_service.verify_password(password, user.password_hash):
                self.logger.warning(
                    "Authentication failed - invalid password",
                    username=username,
                    user_id=user.id,
                    reason="invalid_password"
                )
                return None
            
            if not user.is_active:
                self.logger.warning(
                    "Authentication failed - user inactive",
                    username=username,
                    user_id=user.id,
                    reason="user_inactive"
                )
                return None
            
            self.logger.info(
                "Authentication successful",
                username=username,
                user_id=user.id,
                user_role=user.role
            )
            
            return user
            
        except Exception as e:
            self.logger.error(
                "Authentication error",
                username=username,
                error_type=type(e).__name__,
                error_message=str(e),
                exc_info=True
            )
            raise
    
    def generate_token(self, user: User) -> str:
        """Generate JWT token with logging"""
        self.logger.info(
            "Token generation",
            user_id=user.id,
            username=user.username,
            action="generate_token"
        )
        
        try:
            token = self.token_service.generate_token(user)
            
            self.logger.info(
                "Token generated successfully",
                user_id=user.id,
                token_length=len(token)
            )
            
            return token
            
        except Exception as e:
            self.logger.error(
                "Token generation failed",
                user_id=user.id,
                error_type=type(e).__name__,
                error_message=str(e),
                exc_info=True
            )
            raise
```

#### Task Service Logging
```python
# src/services/task_service.py
import structlog
from src.core.logging import logger
from typing import List, Optional

class TaskService:
    """Task service with structured logging"""
    
    def __init__(self, task_repository, user_repository):
        self.task_repository = task_repository
        self.user_repository = user_repository
        self.logger = logger.bind(service="task_service")
    
    def create_task(self, task_data: dict, user_id: int) -> Task:
        """Create task with comprehensive logging"""
        self.logger.info(
            "Task creation started",
            user_id=user_id,
            task_title=task_data.get('title'),
            action="create_task"
        )
        
        try:
            # Validate user exists
            user = self.user_repository.get_by_id(user_id)
            if not user:
                self.logger.error(
                    "Task creation failed - user not found",
                    user_id=user_id,
                    task_title=task_data.get('title')
                )
                raise ValueError("User not found")
            
            # Create task
            task = self.task_repository.create({
                **task_data,
                'created_by': user_id
            })
            
            self.logger.info(
                "Task created successfully",
                task_id=task.id,
                user_id=user_id,
                task_title=task.title,
                task_priority=task.priority,
                task_status=task.status
            )
            
            return task
            
        except Exception as e:
            self.logger.error(
                "Task creation failed",
                user_id=user_id,
                task_title=task_data.get('title'),
                error_type=type(e).__name__,
                error_message=str(e),
                exc_info=True
            )
            raise
    
    def update_task(self, task_id: int, update_data: dict, user_id: int) -> Task:
        """Update task with change logging"""
        self.logger.info(
            "Task update started",
            task_id=task_id,
            user_id=user_id,
            update_fields=list(update_data.keys()),
            action="update_task"
        )
        
        try:
            # Get original task for comparison
            original_task = self.task_repository.get_by_id(task_id)
            if not original_task:
                self.logger.error(
                    "Task update failed - task not found",
                    task_id=task_id,
                    user_id=user_id
                )
                raise ValueError("Task not found")
            
            # Update task
            updated_task = self.task_repository.update(task_id, update_data)
            
            # Log specific changes
            changes = []
            for field, new_value in update_data.items():
                old_value = getattr(original_task, field, None)
                if old_value != new_value:
                    changes.append({
                        'field': field,
                        'old_value': old_value,
                        'new_value': new_value
                    })
            
            self.logger.info(
                "Task updated successfully",
                task_id=task_id,
                user_id=user_id,
                changes=changes,
                updated_fields=list(update_data.keys())
            )
            
            return updated_task
            
        except Exception as e:
            self.logger.error(
                "Task update failed",
                task_id=task_id,
                user_id=user_id,
                update_fields=list(update_data.keys()),
                error_type=type(e).__name__,
                error_message=str(e),
                exc_info=True
            )
            raise
```

### 3. Repository Layer Logging

#### Repository Logging
```python
# src/repositories/base_repository.py
import structlog
from src.core.logging import logger
from typing import Any, List, Optional

class BaseRepository:
    """Base repository with structured logging"""
    
    def __init__(self, model_class):
        self.model_class = model_class
        self.logger = logger.bind(
            service="repository",
            model=model_class.__name__
        )
    
    def get_by_id(self, id: int) -> Optional[Any]:
        """Get entity by ID with logging"""
        self.logger.debug(
            "Repository query started",
            operation="get_by_id",
            entity_id=id
        )
        
        try:
            result = self.model_class.query.get(id)
            
            self.logger.debug(
                "Repository query completed",
                operation="get_by_id",
                entity_id=id,
                found=result is not None
            )
            
            return result
            
        except Exception as e:
            self.logger.error(
                "Repository query failed",
                operation="get_by_id",
                entity_id=id,
                error_type=type(e).__name__,
                error_message=str(e),
                exc_info=True
            )
            raise
    
    def create(self, data: dict) -> Any:
        """Create entity with logging"""
        self.logger.info(
            "Repository create started",
            operation="create",
            entity_type=self.model_class.__name__,
            data_fields=list(data.keys())
        )
        
        try:
            entity = self.model_class(**data)
            db.session.add(entity)
            db.session.commit()
            
            self.logger.info(
                "Repository create completed",
                operation="create",
                entity_type=self.model_class.__name__,
                entity_id=entity.id,
                entity_id_field=getattr(entity, 'id', None)
            )
            
            return entity
            
        except Exception as e:
            self.logger.error(
                "Repository create failed",
                operation="create",
                entity_type=self.model_class.__name__,
                error_type=type(e).__name__,
                error_message=str(e),
                exc_info=True
            )
            db.session.rollback()
            raise
```

## Security Logging

### 1. Authentication Security Logging

#### Security Event Logging
```python
# src/services/security_logger.py
import structlog
from src.core.logging import logger
from datetime import datetime
from typing import Optional

class SecurityLogger:
    """Security event logging"""
    
    def __init__(self):
        self.logger = logger.bind(service="security")
    
    def log_login_attempt(self, username: str, success: bool, 
                         ip_address: str, user_agent: str, 
                         user_id: Optional[int] = None):
        """Log login attempt"""
        self.logger.info(
            "Login attempt",
            username=username,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            user_id=user_id,
            timestamp=datetime.utcnow().isoformat(),
            event_type="authentication"
        )
    
    def log_failed_login(self, username: str, reason: str, 
                        ip_address: str, user_agent: str):
        """Log failed login with reason"""
        self.logger.warning(
            "Failed login attempt",
            username=username,
            reason=reason,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow().isoformat(),
            event_type="authentication_failure"
        )
    
    def log_password_change(self, user_id: int, username: str, 
                           ip_address: str, success: bool):
        """Log password change"""
        self.logger.info(
            "Password change",
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            success=success,
            timestamp=datetime.utcnow().isoformat(),
            event_type="password_change"
        )
    
    def log_permission_denied(self, user_id: int, username: str, 
                           resource: str, action: str, 
                           ip_address: str):
        """Log permission denied event"""
        self.logger.warning(
            "Permission denied",
            user_id=user_id,
            username=username,
            resource=resource,
            action=action,
            ip_address=ip_address,
            timestamp=datetime.utcnow().isoformat(),
            event_type="authorization_failure"
        )
    
    def log_suspicious_activity(self, description: str, details: dict, 
                              severity: str = "medium"):
        """Log suspicious activity"""
        self.logger.error(
            "Suspicious activity detected",
            description=description,
            details=details,
            severity=severity,
            timestamp=datetime.utcnow().isoformat(),
            event_type="security_alert"
        )
```

### 2. API Security Logging

#### API Security Middleware
```python
# src/middleware/security_logging.py
import structlog
from flask import request, g
from src.core.logging import logger
from src.services.security_logger import SecurityLogger

security_logger = SecurityLogger()

def log_api_security():
    """Log API security events"""
    # Log rate limiting
    if hasattr(g, 'rate_limited'):
        security_logger.log_suspicious_activity(
            "Rate limit exceeded",
            {
                "ip_address": request.remote_addr,
                "endpoint": request.endpoint,
                "method": request.method,
                "user_agent": request.headers.get('User-Agent')
            },
            severity="low"
        )
    
    # Log suspicious user agents
    user_agent = request.headers.get('User-Agent', '')
    if any(suspicious in user_agent.lower() for suspicious in ['bot', 'crawler', 'scanner']):
        security_logger.log_suspicious_activity(
            "Suspicious user agent detected",
            {
                "ip_address": request.remote_addr,
                "user_agent": user_agent,
                "endpoint": request.endpoint,
                "method": request.method
            },
            severity="medium"
        )
    
    # Log authentication bypass in development
    if hasattr(g, 'auth_bypassed') and g.auth_bypassed:
        security_logger.log_suspicious_activity(
            "Authentication bypass used",
            {
                "ip_address": request.remote_addr,
                "endpoint": request.endpoint,
                "method": request.method,
                "environment": os.getenv('ENVIRONMENT', 'unknown')
            },
            severity="info"  # Lower severity in development
        )
```

## Performance Logging

### 1. Performance Monitoring

#### Performance Logging
```python
# src/utils/performance_logger.py
import structlog
import time
from functools import wraps
from src.core.logging import logger

class PerformanceLogger:
    """Performance monitoring and logging"""
    
    def __init__(self):
        self.logger = logger.bind(service="performance")
    
    def log_slow_query(self, query: str, duration: float, 
                      threshold: float = 1.0):
        """Log slow database queries"""
        if duration > threshold:
            self.logger.warning(
                "Slow database query detected",
                query=query[:200],  # Truncate long queries
                duration_seconds=duration,
                threshold_seconds=threshold,
                event_type="performance"
            )
    
    def log_api_performance(self, endpoint: str, method: str, 
                          duration: float, status_code: int,
                          threshold: float = 2.0):
        """Log API performance metrics"""
        if duration > threshold:
            self.logger.warning(
                "Slow API endpoint detected",
                endpoint=endpoint,
                method=method,
                duration_seconds=duration,
                status_code=status_code,
                threshold_seconds=threshold,
                event_type="performance"
            )
    
    def log_memory_usage(self, component: str, memory_mb: float):
        """Log memory usage"""
        self.logger.info(
            "Memory usage",
            component=component,
            memory_mb=memory_mb,
            event_type="performance"
        )

# Performance decorator
def log_performance(operation_name: str = None):
    """Decorator to log function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(
                    "Function performance",
                    function=func.__name__,
                    operation=operation_name or func.__name__,
                    duration_seconds=duration,
                    success=True,
                    event_type="performance"
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                logger.error(
                    "Function performance with error",
                    function=func.__name__,
                    operation=operation_name or func.__name__,
                    duration_seconds=duration,
                    success=False,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    event_type="performance"
                )
                
                raise
        
        return wrapper
    return decorator
```

## Log Analysis and Monitoring

### 1. Log Queries

#### Common Log Queries
```python
# src/utils/log_queries.py

class LogAnalyzer:
    """Log analysis utilities"""
    
    @staticmethod
    def get_failed_logins(time_range_hours: int = 24):
        """Query for failed login attempts"""
        return {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"event_type": "authentication_failure"}},
                        {"range": {"timestamp": {"gte": f"now-{time_range_hours}h"}}}
                    ]
                }
            },
            "aggs": {
                "failed_by_ip": {
                    "terms": {"field": "ip_address"}
                },
                "failed_by_username": {
                    "terms": {"field": "username"}
                }
            }
        }
    
    @staticmethod
    def get_slow_endpoints(time_range_hours: int = 24, threshold_seconds: float = 2.0):
        """Query for slow API endpoints"""
        return {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"event_type": "performance"}},
                        {"range": {"duration_seconds": {"gte": threshold_seconds}}},
                        {"range": {"timestamp": {"gte": f"now-{time_range_hours}h"}}}
                    ]
                }
            },
            "aggs": {
                "slow_endpoints": {
                    "terms": {"field": "endpoint"}
                },
                "avg_duration": {
                    "avg": {"field": "duration_seconds"}
                }
            }
        }
    
    @staticmethod
    def get_security_alerts(time_range_hours: int = 24):
        """Query for security alerts"""
        return {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"event_type": "security_alert"}},
                        {"range": {"timestamp": {"gte": f"now-{time_range_hours}h"}}}
                    ]
                }
            },
            "aggs": {
                "alerts_by_severity": {
                    "terms": {"field": "severity"}
                },
                "alerts_by_type": {
                    "terms": {"field": "description.keyword"}}
                }
            }
        }
```

## Testing Logging

### 1. Logging Tests

#### Logging Configuration Tests
```python
# tests/unit/test_logging.py
import pytest
import structlog
from unittest.mock import patch, MagicMock
from src.core.logging import StructuredLogger

class TestStructuredLogging:
    """Test structured logging configuration"""
    
    def test_logger_initialization(self):
        """Test logger initialization"""
        logger_config = StructuredLogger()
        assert logger_config is not None
    
    def test_json_logging_in_production(self):
        """Test JSON logging in production environment"""
        with patch.dict('os.environ', {'ENVIRONMENT': 'production'}):
            logger_config = StructuredLogger()
            assert logger_config._should_use_json() is True
    
    def test_console_logging_in_development(self):
        """Test console logging in development environment"""
        with patch.dict('os.environ', {'ENVIRONMENT': 'development'}):
            logger_config = StructuredLogger()
            assert logger_config._should_use_json() is False
    
    def test_request_id_addition(self):
        """Test request ID addition to log context"""
        logger_config = StructuredLogger()
        
        # Mock Flask g object
        mock_g = MagicMock()
        mock_g.request_id = "test-request-id"
        
        with patch('src.core.logging.g', mock_g):
            event_dict = {"test": "data"}
            result = logger_config._add_request_id(None, "info", event_dict)
            assert result["request_id"] == "test-request-id"
    
    def test_user_context_addition(self):
        """Test user context addition to log messages"""
        logger_config = StructuredLogger()
        
        # Mock Flask g object with user
        mock_user = MagicMock()
        mock_user.id = 123
        mock_user.username = "testuser"
        mock_user.role = "staff"
        
        mock_g = MagicMock()
        mock_g.current_user = mock_user
        
        with patch('src.core.logging.g', mock_g):
            event_dict = {"test": "data"}
            result = logger_config._add_user_context(None, "info", event_dict)
            assert result["user_id"] == 123
            assert result["username"] == "testuser"
            assert result["user_role"] == "staff"

class TestServiceLogging:
    """Test service layer logging"""
    
    def test_auth_service_logging(self):
        """Test authentication service logging"""
        from src.services.auth_service import AuthService
        
        # Mock dependencies
        mock_user_repo = MagicMock()
        mock_password_service = MagicMock()
        mock_token_service = MagicMock()
        
        auth_service = AuthService(
            mock_user_repo, 
            mock_password_service, 
            mock_token_service
        )
        
        # Test successful authentication logging
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.is_active = True
        
        mock_user_repo.get_by_username.return_value = mock_user
        mock_password_service.verify_password.return_value = True
        
        with patch.object(auth_service.logger, 'info') as mock_log:
            result = auth_service.authenticate_user("testuser", "password")
            assert result == mock_user
            mock_log.assert_called()
    
    def test_task_service_logging(self):
        """Test task service logging"""
        from src.services.task_service import TaskService
        
        # Mock dependencies
        mock_task_repo = MagicMock()
        mock_user_repo = MagicMock()
        
        task_service = TaskService(mock_task_repo, mock_user_repo)
        
        # Test task creation logging
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user_repo.get_by_id.return_value = mock_user
        
        mock_task = MagicMock()
        mock_task.id = 1
        mock_task.title = "Test Task"
        mock_task.priority = "medium"
        mock_task.status = "pending"
        
        mock_task_repo.create.return_value = mock_task
        
        with patch.object(task_service.logger, 'info') as mock_log:
            result = task_service.create_task({"title": "Test Task"}, 1)
            assert result == mock_task
            mock_log.assert_called()
```

## Benefits of Structured Logging

### 1. Searchability
- **Machine-readable format** enables easy searching
- **Consistent field names** across all log messages
- **Structured data** allows complex queries
- **JSON format** integrates with log analysis tools

### 2. Debugging
- **Rich context** in every log message
- **Request tracing** with unique IDs
- **User context** for better debugging
- **Error details** with stack traces

### 3. Monitoring
- **Performance metrics** in log data
- **Security events** with detailed information
- **Business metrics** tracking
- **System health** monitoring

### 4. Compliance
- **Audit trails** for security events
- **Data access logging** for compliance
- **Change tracking** for audit requirements
- **Retention policies** for log data

## Conclusion

The structured logging implementation provides:
- **Consistent log format** across all components
- **Rich context** for better debugging and monitoring
- **Machine-readable logs** for analysis and alerting
- **Security event tracking** for compliance
- **Performance monitoring** for optimization
- **Comprehensive testing** of logging functionality

This implementation serves as a robust foundation for observability and monitoring throughout the application.
