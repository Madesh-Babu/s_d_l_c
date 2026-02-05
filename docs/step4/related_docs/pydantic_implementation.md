# Pydantic Implementation

## Overview

This document outlines the comprehensive Pydantic implementation throughout the application for data validation, serialization, and type safety.

## Pydantic Models

### 1. User Models

#### User Creation Model
```python
# src/models/user.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    """Model for user creation requests"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: str = Field(default="staff", regex="^(admin|manager|staff)$")
    
    @validator('password')
    def validate_password_strength(cls, v):
        """Validate password strength"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format"""
        if not v.isalnum() and '_' not in v:
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v.lower()

class UserUpdate(BaseModel):
    """Model for user update requests"""
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, regex="^(admin|manager|staff)$")
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    """Model for user response data"""
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """Model for user login requests"""
    username: str
    password: str

class UserLoginResponse(BaseModel):
    """Model for login response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
```

### 2. Task Models

#### Task Creation Model
```python
# src/models/task.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"

class TaskPriority(str, Enum):
    """Task priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskCreate(BaseModel):
    """Model for task creation requests"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    depends_on: Optional[int] = None
    
    @validator('title')
    def validate_title(cls, v):
        """Validate task title"""
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @validator('due_date')
    def validate_due_date(cls, v):
        """Validate due date is in the future"""
        if v and v <= datetime.now():
            raise ValueError('Due date must be in the future')
        return v
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags format"""
        if v:
            for tag in v:
                if not tag.strip():
                    raise ValueError('Tags cannot be empty')
                if len(tag) > 50:
                    raise ValueError('Tag length cannot exceed 50 characters')
        return [tag.strip() for tag in v] if v else []

class TaskUpdate(BaseModel):
    """Model for task update requests"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    
    @validator('title')
    def validate_title(cls, v):
        """Validate task title"""
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip() if v else v
    
    @validator('due_date')
    def validate_due_date(cls, v):
        """Validate due date is in the future"""
        if v and v <= datetime.now():
            raise ValueError('Due date must be in the future')
        return v

class TaskResponse(BaseModel):
    """Model for task response data"""
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    assigned_to: Optional[int]
    created_by: int
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    tags: List[str]
    depends_on: Optional[int]
    
    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    """Model for task list response"""
    tasks: List[TaskResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool
```

### 3. Configuration Models

#### Configuration Models
```python
# src/core/config.py
from pydantic import BaseSettings, Field, validator
from typing import Optional, List

class FeatureToggles(BaseSettings):
    """Feature toggles configuration"""
    BYPASS_AUTH: bool = Field(default=False, description="Bypass authentication in development")
    ENABLE_LOGGING: bool = Field(default=True, description="Enable structured logging")
    ENABLE_RATE_LIMITING: bool = Field(default=True, description="Enable API rate limiting")
    ENABLE_CORS: bool = Field(default=True, description="Enable CORS")
    ENABLE_METRICS: bool = Field(default=False, description="Enable application metrics")
    
    @validator('BYPASS_AUTH')
    def validate_bypass_auth(cls, v, info):
        """Ensure auth bypass is only enabled in development"""
        if hasattr(info, 'context') and info.context:
            env = info.context.get('ENVIRONMENT', 'development')
        else:
            env = 'development'
        
        if v and env not in ['development', 'local', 'dev']:
            raise ValueError("Authentication bypass can only be enabled in development")
        return v

class DatabaseConfig(BaseSettings):
    """Database configuration"""
    DATABASE_URL: str = Field(..., description="Database connection URL")
    DATABASE_POOL_SIZE: int = Field(default=10, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, description="Database max overflow connections")
    DATABASE_POOL_TIMEOUT: int = Field(default=30, description="Database pool timeout")
    
    @validator('DATABASE_URL')
    def validate_database_url(cls, v):
        """Validate database URL format"""
        if not v.startswith(('postgresql://', 'mysql://', 'sqlite:///')):
            raise ValueError("Invalid database URL format")
        return v

class JWTConfig(BaseSettings):
    """JWT configuration"""
    JWT_SECRET_KEY: str = Field(..., description="JWT secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="JWT token expiration time")
    
    @validator('JWT_SECRET_KEY')
    def validate_secret_key(cls, v):
        """Validate JWT secret key strength"""
        if len(v) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        return v

class LoggingConfig(BaseSettings):
    """Logging configuration"""
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format")
    LOG_FILE: Optional[str] = Field(None, description="Log file path")
    
    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v.upper()

class EnvironmentConfig(BaseSettings):
    """Main environment configuration"""
    ENVIRONMENT: str = Field(default="development", description="Application environment")
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    HOST: str = Field(default="localhost", description="Application host")
    PORT: int = Field(default=5000, description="Application port")
    
    # Sub-configurations
    feature_toggles: FeatureToggles = FeatureToggles()
    database: DatabaseConfig = DatabaseConfig()
    jwt: JWTConfig = JWTConfig()
    logging: LoggingConfig = LoggingConfig()
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True
```

### 4. API Response Models

#### Standard Response Models
```python
# src/models/responses.py
from pydantic import BaseModel, Field
from typing import Optional, Any, List
from datetime import datetime

class APIResponse(BaseModel):
    """Standard API response model"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    message: Optional[str] = None
    details: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ValidationErrorResponse(BaseModel):
    """Validation error response model"""
    success: bool = False
    error: str = "Validation Error"
    message: str = "Request validation failed"
    validation_errors: List[dict]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginatedResponse(BaseModel):
    """Paginated response model"""
    success: bool = True
    data: List[Any]
    pagination: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SuccessResponse(BaseModel):
    """Success response model"""
    success: bool = True
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

## Pydantic Validation

### 1. Custom Validators

#### Email Validation
```python
# src/core/validators.py
from pydantic import validator
import re

def validate_email_format(cls, v):
    """Custom email validation"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, v):
        raise ValueError('Invalid email format')
    return v.lower()

def validate_password_strength(cls, v):
    """Enhanced password validation"""
    errors = []
    
    if len(v) < 8:
        errors.append('Password must be at least 8 characters long')
    if len(v) > 128:
        errors.append('Password must not exceed 128 characters')
    if not any(c.isupper() for c in v):
        errors.append('Password must contain at least one uppercase letter')
    if not any(c.islower() for c in v):
        errors.append('Password must contain at least one lowercase letter')
    if not any(c.isdigit() for c in v):
        errors.append('Password must contain at least one digit')
    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
        errors.append('Password must contain at least one special character')
    
    if errors:
        raise ValueError(' '.join(errors))
    return v

def validate_username_format(cls, v):
    """Username format validation"""
    if len(v) < 3:
        raise ValueError('Username must be at least 3 characters long')
    if len(v) > 50:
        raise ValueError('Username must not exceed 50 characters')
    if not re.match(r'^[a-zA-Z0-9_]+$', v):
        raise ValueError('Username can only contain letters, numbers, and underscores')
    return v.lower()
```

### 2. Field Validation

#### Common Field Validators
```python
# src/models/common.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class TimestampedModel(BaseModel):
    """Base model with timestamps"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True

class SoftDeleteModel(TimestampedModel):
    """Model with soft delete functionality"""
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = None

class ValidatedModel(BaseModel):
    """Base model with common validations"""
    
    @validator('*', pre=True, always=True)
    def strip_string_fields(cls, v):
        """Strip whitespace from string fields"""
        if isinstance(v, str):
            return v.strip()
        return v
    
    @validator('*', pre=True, always=True)
    def validate_none_values(cls, v):
        """Handle None values consistently"""
        if v == "":
            return None
        return v
```

## Pydantic in API Layer

### 1. Request Validation

#### FastAPI Integration
```python
# src/api/authentication/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.models.user import UserCreate, UserLogin, UserResponse
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register new user"""
    try:
        user = auth_service.register_user(user_data.dict())
        return user
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.errors()
        )

@router.post("/login", response_model=dict)
async def login(login_data: UserLogin):
    """User login"""
    try:
        result = auth_service.authenticate_user(
            login_data.username, 
            login_data.password
        )
        return result
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
```

### 2. Response Serialization

#### Response Models
```python
# src/api/responses.py
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class UserListResponse(BaseModel):
    """User list response model"""
    users: List[UserResponse]
    total: int
    page: int
    per_page: int

class TaskDetailResponse(BaseModel):
    """Task detail response model"""
    task: TaskResponse
    comments: List[CommentResponse]
    history: List[TaskHistoryResponse]

class DashboardResponse(BaseModel):
    """Dashboard response model"""
    user_stats: dict
    task_stats: dict
    recent_activities: List[ActivityResponse]
```

## Pydantic Testing

### 1. Model Testing

#### Validation Testing
```python
# tests/unit/test_models_validation.py
import pytest
from pydantic import ValidationError
from src.models.user import UserCreate, UserUpdate
from src.models.task import TaskCreate, TaskUpdate

class TestUserModels:
    """Test user model validation"""
    
    def test_valid_user_creation(self):
        """Test valid user creation data"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "role": "staff"
        }
        
        user = UserCreate(**user_data)
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == "staff"
    
    def test_invalid_email(self):
        """Test invalid email validation"""
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "TestPassword123!",
            "role": "staff"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "email" in str(exc_info.value)
    
    def test_weak_password(self):
        """Test weak password validation"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "weak",
            "role": "staff"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "password" in str(exc_info.value)

class TestTaskModels:
    """Test task model validation"""
    
    def test_valid_task_creation(self):
        """Test valid task creation data"""
        task_data = {
            "title": "Test Task",
            "description": "Test task description",
            "status": "pending",
            "priority": "medium",
            "tags": ["test", "development"]
        }
        
        task = TaskCreate(**task_data)
        assert task.title == "Test Task"
        assert task.status == "pending"
        assert task.tags == ["test", "development"]
    
    def test_invalid_due_date(self):
        """Test invalid due date validation"""
        past_date = datetime(2020, 1, 1)
        task_data = {
            "title": "Test Task",
            "due_date": past_date
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(**task_data)
        
        assert "due_date" in str(exc_info.value)
```

### 2. Integration Testing

#### API Validation Testing
```python
# tests/api/test_validation.py
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

class TestAPIValidation:
    """Test API validation with Pydantic models"""
    
    def test_register_user_validation(self):
        """Test user registration validation"""
        # Test invalid data
        invalid_data = {
            "username": "",  # Invalid
            "email": "invalid-email",  # Invalid
            "password": "weak",  # Invalid
            "role": "invalid_role"  # Invalid
        }
        
        response = client.post("/auth/register", json=invalid_data)
        assert response.status_code == 422
        
        errors = response.json()["detail"]
        assert any("username" in str(error) for error in errors)
        assert any("email" in str(error) for error in errors)
        assert any("password" in str(error) for error in errors)
        assert any("role" in str(error) for error in errors)
    
    def test_create_task_validation(self):
        """Test task creation validation"""
        # Test invalid data
        invalid_data = {
            "title": "",  # Invalid
            "priority": "invalid_priority",  # Invalid
            "due_date": "2020-01-01T00:00:00"  # Invalid (past date)
        }
        
        response = client.post("/tasks", json=invalid_data)
        assert response.status_code == 422
        
        errors = response.json()["detail"]
        assert any("title" in str(error) for error in errors)
        assert any("priority" in str(error) for error in errors)
        assert any("due_date" in str(error) for error in errors)
```

## Pydantic Best Practices

### 1. Model Design
- **Keep models focused** on specific responsibilities
- **Use descriptive field names** with clear types
- **Implement proper validation** for all fields
- **Use enums** for fixed value sets
- **Provide default values** where appropriate

### 2. Validation Rules
- **Validate at the model level** for business rules
- **Use custom validators** for complex validation logic
- **Provide clear error messages** for validation failures
- **Validate data format** and content separately
- **Handle edge cases** explicitly

### 3. Performance
- **Use lazy validation** when possible
- **Avoid expensive operations** in validators
- **Cache validation results** for repeated validations
- **Use field validation** for simple checks
- **Use model validation** for complex checks

### 4. Testing
- **Test all validation rules** thoroughly
- **Test edge cases** and boundary conditions
- **Test error messages** for clarity
- **Test model serialization** and deserialization
- **Test integration** with API layer

## Benefits of Pydantic Implementation

### 1. Type Safety
- **Compile-time type checking** with mypy
- **Runtime validation** of data types
- **Automatic type conversion** where appropriate
- **Clear type hints** for better IDE support

### 2. Data Validation
- **Automatic validation** of incoming data
- **Custom validation rules** for business logic
- **Clear error messages** for validation failures
- **Consistent validation** across the application

### 3. Serialization
- **Automatic serialization** to/from JSON
- **Custom serialization** logic when needed
- **Consistent data formats** across APIs
- **Easy integration** with web frameworks

### 4. Documentation
- **Automatic API documentation** generation
- **Clear field descriptions** and constraints
- **Self-documenting models** with type hints
- **Generated schemas** for external consumers

## Conclusion

The Pydantic implementation provides:
- **Robust data validation** with clear error messages
- **Type safety** throughout the application
- **Consistent data models** across all layers
- **Automatic serialization** and documentation
- **Comprehensive testing** of validation logic
- **Performance optimization** with efficient validation

This implementation serves as a solid foundation for data handling and validation throughout the application.
