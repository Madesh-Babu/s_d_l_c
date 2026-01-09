# Python Style Guide

## Overview

Consistent code style makes our codebase more readable, maintainable, and professional. We follow PEP 8 with some project-specific conventions.

## Development Environment

### Python Version
- **Required**: Python 3.12+
- Check your version: `python --version`

### Code Formatting Tools

#### Black (Required)
Automatic code formatting - non-negotiable formatting decisions:

```bash
# Install
pip install black

# Format entire project
black .

# Format specific file
black auth/models.py

# Check what would be formatted (dry run)
black --check .
```

**Black Configuration** (pyproject.toml):
```toml
[tool.black]
line-length = 88
target-version = ['py312']
include = '\.pyi?$'
exclude = '''
/(
    \.git
    | \.hg
    | \.mypy_cache
    | \.tox
    | \.venv
    | _build
    | buck-out
    | build
    | dist
)/
'''
```

#### Flake8 (Required)
Linting and style checking:

```bash
# Install
pip install flake8

# Check entire project
flake8 .

# Check specific file
flake8 auth/models.py
```

**Flake8 Configuration** (.flake8):
```ini
[flake8]
max-line-length = 88
extend-ignore = 
    E203,  # Whitespace before ':'
    E501,  # Line too long (handled by black)
    W503,  # Line break before binary operator
exclude = 
    .git,
    __pycache__,
    .venv,
    migrations/
```

### IDE Setup

#### VS Code Settings
```json
{
    "python.formatting.provider": "black",
    "python.linting.flake8Enabled": true,
    "python.linting.enabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

## Code Style Standards

### Imports

#### Import Order (isort)
```python
# 1. Standard library
import os
import sys
from datetime import datetime

# 2. Third-party packages
import fastapi
from sqlalchemy import Column, Integer, String

# 3. Local application imports
from .models import User
from .schemas import UserCreate
```

#### Import Guidelines
```python
# ✅ Good
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

# ❌ Bad
from fastapi import *  # Avoid wildcard imports
import fastapi  # Import specific items instead
```

### Type Hints (Required)

#### Function Annotations
```python
# ✅ Good
def create_user(
    user_data: UserCreate, 
    db: Session
) -> User:
    """Create a new user in the database."""
    return User(**user_data.dict())

# ❌ Bad
def create_user(user_data, db):
    return User(**user_data.dict())
```

#### Variable Annotations
```python
# ✅ Good
from typing import List, Optional, Dict, Any

users: List[User] = []
user_count: int = 0
config: Optional[Dict[str, Any]] = None

# Complex types
UserDict = Dict[str, Union[str, int]]
```

#### Return Types
```python
# ✅ Good
def get_user_by_id(user_id: int) -> Optional[User]:
    """Retrieve user by ID, return None if not found."""
    pass

def get_all_users() -> List[User]:
    """Get all users from database."""
    pass

# Async functions
async def create_user_async(user_data: UserCreate) -> User:
    """Asynchronously create a user."""
    pass
```

### Naming Conventions

#### Variables and Functions
```python
# ✅ Good
user_count = 0
total_amount = 100.50
is_authenticated = True

def calculate_total_price(items: List[Item]) -> float:
    pass

# ❌ Bad
userCount = 0  # Use snake_case, not camelCase
c = 0  # Too short, not descriptive
```

#### Classes
```python
# ✅ Good
class UserService:
    pass

class DatabaseConnection:
    pass

class HTTPException:
    pass

# ❌ Bad
class user_service:  # Use PascalCase
class DB_Connection:  # Avoid underscores
```

#### Constants
```python
# ✅ Good
MAX_RETRY_ATTEMPTS = 3
DATABASE_URL = "postgresql://..."
DEFAULT_PAGE_SIZE = 20

# ❌ Bad
max_retry_attempts = 3  # Should be uppercase
```

### Docstrings (Required)

#### Function Docstrings
```python
def authenticate_user(email: str, password: str) -> Optional[User]:
    """
    Authenticate user with email and password.
    
    Args:
        email: User's email address
        password: Plain text password
        
    Returns:
        User object if authentication successful, None otherwise
        
    Raises:
        ValidationError: If email format is invalid
        DatabaseError: If database connection fails
    """
    pass
```

#### Class Docstrings
```python
class UserService:
    """
    Service class for user-related operations.
    
    Handles user creation, authentication, and management.
    Provides an abstraction layer over the User model.
    """
    
    def __init__(self, db: Session) -> None:
        """
        Initialize UserService with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
```

#### Module Docstrings
```python
"""
User authentication and management module.

This module provides functionality for:
- User registration and login
- Password hashing and verification  
- JWT token generation and validation
- User profile management
"""
```

### Error Handling

#### Exception Handling
```python
# ✅ Good
def get_user_by_id(user_id: int) -> User:
    """Get user by ID with proper error handling."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=404, 
                detail=f"User with id {user_id} not found"
            )
        return user
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

# ❌ Bad
def get_user_by_id(user_id):
    user = db.query(User).filter(User.id == user_id).first()
    return user  # No error handling
```

#### Custom Exceptions
```python
class AuthenticationError(Exception):
    """Raised when user authentication fails."""
    pass

class ValidationError(Exception):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)
```

### Code Organization

#### File Structure
```
src/
├── auth/
│   ├── __init__.py
│   ├── models.py      # Database models
│   ├── schemas.py     # Pydantic schemas
│   ├── services.py    # Business logic
│   └── routes.py      # API endpoints
├── todo/
│   ├── __init__.py
│   ├── models.py
│   ├── schemas.py
│   ├── services.py
│   └── routes.py
└── core/
    ├── __init__.py
    ├── config.py      # Configuration
    ├── database.py    # Database setup
    └── security.py    # Security utilities
```

#### Module Organization
```python
# models.py
"""Database models for user management."""

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    """User model for authentication and profiles."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
```

### Performance Considerations

#### List Comprehensions
```python
# ✅ Good - readable and efficient
active_users = [user for user in users if user.is_active]

# ✅ Good - for complex operations
user_emails = [
    user.email.lower().strip() 
    for user in users 
    if user.is_active and user.email
]

# ❌ Bad - too complex, use regular loops
complex_data = [
    {
        'id': user.id,
        'name': user.name.title() if user.name else 'Unknown',
        'tasks': [task.title for task in user.tasks if task.is_complete]
    }
    for user in users 
    if user.is_active and user.created_at > datetime.now() - timedelta(days=30)
]
```

#### String Formatting
```python
# ✅ Good - f-strings (Python 3.6+)
message = f"User {user.name} has {task_count} tasks"
query = f"SELECT * FROM users WHERE id = {user_id}"

# ✅ Good - for complex formatting
template = "User: {name}, Email: {email}, Tasks: {count}"
message = template.format(
    name=user.name, 
    email=user.email, 
    count=len(user.tasks)
)

# ❌ Bad - old style formatting
message = "User %s has %d tasks" % (user.name, task_count)
```

## Pre-commit Setup

### Install Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
# (See configuration below)

# Install hooks
pre-commit install
```

### Pre-commit Configuration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.12.0
    hooks:
      - id: black
        language_version: python3.12

  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## Quality Checklist

Before submitting code, ensure:

### ✅ Formatting
- [ ] Code formatted with Black
- [ ] Imports organized with isort
- [ ] No flake8 violations

### ✅ Type Safety
- [ ] All functions have type hints
- [ ] Complex types are properly annotated
- [ ] mypy passes without errors

### ✅ Documentation
- [ ] All public functions have docstrings
- [ ] Classes have descriptive docstrings
- [ ] Complex logic has inline comments

### ✅ Error Handling
- [ ] Exceptions are properly caught and handled
- [ ] User-friendly error messages
- [ ] Logging for debugging

## Common Patterns

### FastAPI Endpoint
```python
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserResponse

router = APIRouter()

@router.post("/users/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Create a new user account.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Created user data
        
    Raises:
        HTTPException: If email already exists
    """
    # Check if user exists
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(**user_data.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user
```

---

**Next Steps**: Learn about [Testing Guidelines](testing_guidelines.md) to ensure code quality and reliability.