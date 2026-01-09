# Testing Guidelines

## Overview

Testing ensures code reliability, prevents regressions, and documents expected behavior. We aim for **80%+ test coverage** on critical code paths.

## Testing Framework

### pytest (Required)
We use pytest for all testing needs:

```bash
# Install pytest and plugins
pip install pytest pytest-asyncio pytest-cov pytest-mock

# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_user_login
```

### Test Configuration
**pytest.ini**:
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --disable-warnings
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
```

## Test Structure

### Directory Structure
```
tests/
├── conftest.py           # Shared fixtures
├── test_auth.py         # Authentication tests
├── test_todo.py         # TODO functionality tests
├── test_database.py     # Database tests
├── integration/
│   ├── test_api.py      # API integration tests
│   └── test_workflows.py # End-to-end workflows
└── fixtures/
    ├── users.json       # Test data
    └── todos.json
```

### Test Naming Convention

#### File Names
```bash
test_module_name.py      # ✅ Good
test_auth.py
test_todo_service.py
test_user_endpoints.py

module_test.py           # ❌ Bad
auth_tests.py           # ❌ Bad
```

#### Function Names
```python
# ✅ Good - descriptive and specific
def test_user_registration_with_valid_email():
    pass

def test_user_login_fails_with_invalid_password():
    pass

def test_todo_creation_requires_authentication():
    pass

# ❌ Bad - too generic
def test_user():
    pass

def test_login():
    pass
```

#### Class Names
```python
# ✅ Good
class TestUserAuthentication:
    pass

class TestTodoOperations:
    pass

# ❌ Bad
class UserTests:
    pass
```

## Test Types

### 1. Unit Tests

Test individual functions and methods in isolation:

```python
import pytest
from src.auth.services import UserService
from src.auth.schemas import UserCreate

class TestUserService:
    """Unit tests for UserService class."""
    
    def test_hash_password_returns_different_hash_each_time(self):
        """Test that password hashing produces unique hashes."""
        service = UserService()
        password = "test_password"
        
        hash1 = service.hash_password(password)
        hash2 = service.hash_password(password)
        
        assert hash1 != hash2
        assert service.verify_password(password, hash1)
        assert service.verify_password(password, hash2)
    
    def test_validate_user_data_rejects_invalid_email(self):
        """Test validation rejects malformed email addresses."""
        service = UserService()
        
        invalid_emails = [
            "not-an-email",
            "missing@domain",
            "@nodomain.com",
            "spaces @domain.com"
        ]
        
        for email in invalid_emails:
            user_data = UserCreate(email=email, password="ValidPass123")
            
            with pytest.raises(ValidationError) as exc_info:
                service.validate_user_data(user_data)
            
            assert "email" in str(exc_info.value).lower()
```

### 2. Integration Tests

Test component interactions:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.main import app
from src.database import get_db
from tests.conftest import override_get_db

class TestAuthenticationEndpoints:
    """Integration tests for auth API endpoints."""
    
    def setup_method(self):
        """Set up test client and database."""
        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)
    
    def test_user_registration_success(self):
        """Test successful user registration flow."""
        user_data = {
            "email": "test@example.com",
            "password": "SecurePass123"
        }
        
        response = self.client.post("/api/v1/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "User registered successfully"
        assert "user_id" in data
    
    def test_login_returns_valid_token(self):
        """Test login returns JWT token for valid credentials."""
        # First register a user
        self.client.post("/api/v1/register", json={
            "email": "test@example.com",
            "password": "SecurePass123"
        })
        
        # Then login
        login_data = {
            "username": "test@example.com",  # FastAPI OAuth2 uses 'username'
            "password": "SecurePass123"
        }
        
        response = self.client.post("/api/v1/token", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
```

### 3. API Tests

Test HTTP endpoints end-to-end:

```python
class TestTodoAPIWorkflow:
    """End-to-end tests for TODO API workflows."""
    
    def setup_method(self):
        """Set up authenticated test client."""
        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)
        
        # Register and login user
        self.client.post("/api/v1/register", json={
            "email": "test@example.com",
            "password": "SecurePass123"
        })
        
        login_response = self.client.post("/api/v1/token", data={
            "username": "test@example.com",
            "password": "SecurePass123"
        })
        
        token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def test_complete_todo_workflow(self):
        """Test creating, reading, updating, and deleting a todo."""
        # Create todo
        todo_data = {
            "title": "Test Task",
            "description": "Test Description"
        }
        
        create_response = self.client.post(
            "/api/v1/tasks/create",
            json=todo_data,
            headers=self.headers
        )
        
        assert create_response.status_code == 201
        todo_id = create_response.json()["id"]
        
        # Read todo
        get_response = self.client.get(
            f"/api/v1/tasks/{todo_id}",
            headers=self.headers
        )
        
        assert get_response.status_code == 200
        todo = get_response.json()
        assert todo["title"] == "Test Task"
        
        # Update todo
        update_data = {"title": "Updated Task", "is_completed": True}
        update_response = self.client.put(
            f"/api/v1/tasks/{todo_id}",
            json=update_data,
            headers=self.headers
        )
        
        assert update_response.status_code == 200
        updated_todo = update_response.json()
        assert updated_todo["title"] == "Updated Task"
        assert updated_todo["is_completed"] is True
        
        # Delete todo
        delete_response = self.client.delete(
            f"/api/v1/tasks/{todo_id}",
            headers=self.headers
        )
        
        assert delete_response.status_code == 204
        
        # Verify deletion
        get_deleted = self.client.get(
            f"/api/v1/tasks/{todo_id}",
            headers=self.headers
        )
        
        assert get_deleted.status_code == 404
```

## Test Fixtures

### conftest.py
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base
from src.models import User, Task

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create clean database session for each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture
def sample_user(db_session):
    """Create sample user for testing."""
    user = User(
        email="test@example.com",
        hashed_password="$2b$12$hashed_password_here"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def sample_todo(db_session, sample_user):
    """Create sample todo for testing."""
    todo = Task(
        title="Test Task",
        description="Test Description",
        owner_id=sample_user.id
    )
    db_session.add(todo)
    db_session.commit()
    db_session.refresh(todo)
    return todo
```

## Testing Patterns

### Parameterized Tests
```python
import pytest

class TestPasswordValidation:
    """Test password validation with multiple scenarios."""
    
    @pytest.mark.parametrize("password,expected", [
        ("ValidPass123", True),
        ("Another$ecure1", True),
        ("short", False),
        ("nouppercase123", False),
        ("NOLOWERCASE123", False),
        ("NoNumbers!", False),
        ("", False),
    ])
    def test_password_validation(self, password, expected):
        """Test password validation with various inputs."""
        from src.auth.services import UserService
        
        service = UserService()
        result = service.is_valid_password(password)
        assert result == expected
```

### Exception Testing
```python
def test_user_creation_fails_with_duplicate_email(db_session):
    """Test that creating users with duplicate emails raises error."""
    # Create first user
    user1 = User(email="test@example.com", hashed_password="hash1")
    db_session.add(user1)
    db_session.commit()
    
    # Attempt to create second user with same email
    user2 = User(email="test@example.com", hashed_password="hash2")
    db_session.add(user2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()
```

### Mock Testing
```python
from unittest.mock import Mock, patch

def test_email_service_handles_smtp_failure():
    """Test email service gracefully handles SMTP failures."""
    from src.services.email import EmailService
    
    with patch('smtplib.SMTP') as mock_smtp:
        # Configure mock to raise exception
        mock_smtp.return_value.send_message.side_effect = SMTPException("Server error")
        
        email_service = EmailService()
        result = email_service.send_welcome_email("test@example.com", "Test User")
        
        # Should handle error gracefully
        assert result is False
        mock_smtp.return_value.send_message.assert_called_once()
```

### Async Testing
```python
import pytest

@pytest.mark.asyncio
async def test_async_user_creation():
    """Test asynchronous user creation."""
    from src.auth.services import AsyncUserService
    
    service = AsyncUserService()
    user_data = UserCreate(email="async@example.com", password="SecurePass123")
    
    user = await service.create_user_async(user_data)
    
    assert user.email == "async@example.com"
    assert user.id is not None
```

## Test Data Management

### Test Data Files
**tests/fixtures/users.json**:
```json
{
  "valid_users": [
    {
      "email": "user1@example.com",
      "password": "SecurePass123"
    },
    {
      "email": "user2@example.com", 
      "password": "AnotherPass456"
    }
  ],
  "invalid_users": [
    {
      "email": "invalid-email",
      "password": "short"
    }
  ]
}
```

**Loading Test Data**:
```python
import json
import pytest
from pathlib import Path

@pytest.fixture
def user_test_data():
    """Load user test data from JSON file."""
    data_file = Path(__file__).parent / "fixtures" / "users.json"
    with open(data_file) as f:
        return json.load(f)

def test_user_registration_with_test_data(user_test_data):
    """Test user registration using fixture data."""
    for user_data in user_test_data["valid_users"]:
        # Test each valid user
        response = client.post("/api/v1/register", json=user_data)
        assert response.status_code == 201
```

## Coverage Requirements

### Minimum Coverage
- **Overall**: 80% minimum
- **Critical paths**: 95% (authentication, data operations)
- **New code**: 90% for all new features

### Coverage Commands
```bash
# Generate coverage report
pytest --cov=src --cov-report=html

# View coverage in browser
open htmlcov/index.html

# Check coverage of specific module
pytest --cov=src.auth --cov-report=term-missing

# Fail if coverage below threshold
pytest --cov=src --cov-fail-under=80
```

### Coverage Configuration
**.coveragerc**:
```ini
[run]
source = src
omit = 
    */venv/*
    */migrations/*
    */tests/*
    */__pycache__/*
    */conftest.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

## Testing Best Practices

### ✅ Good Testing Practices

#### **Clear Test Names**
```python
# ✅ Good - specific and descriptive
def test_user_login_fails_with_incorrect_password():
    pass

def test_todo_creation_requires_valid_jwt_token():
    pass

# ❌ Bad - vague and generic
def test_user():
    pass

def test_login():
    pass
```

#### **One Assertion Focus**
```python
# ✅ Good - focused test
def test_user_registration_creates_user_with_hashed_password():
    user_data = UserCreate(email="test@example.com", password="SecurePass123")
    user = user_service.create_user(user_data)
    
    assert user.hashed_password != "SecurePass123"
    assert user_service.verify_password("SecurePass123", user.hashed_password)

# ❌ Bad - testing multiple concerns
def test_user_operations():
    # Creates user
    # Updates user  
    # Deletes user
    # Tests authentication
    pass
```

#### **Arrange-Act-Assert Pattern**
```python
def test_todo_update_changes_title():
    # Arrange
    todo = Todo(title="Original Title", owner_id=1)
    db.add(todo)
    db.commit()
    
    # Act
    updated_todo = todo_service.update_todo(todo.id, {"title": "New Title"})
    
    # Assert
    assert updated_todo.title == "New Title"
```

### ❌ Common Testing Mistakes

#### **Testing Implementation, Not Behavior**
```python
# ❌ Bad - tests internal implementation
def test_password_hashing_uses_bcrypt():
    assert "bcrypt" in str(hash_password("password"))

# ✅ Good - tests behavior
def test_hashed_password_can_be_verified():
    password = "test_password"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
```

#### **Flaky Tests**
```python
# ❌ Bad - depends on timing
def test_task_creation_timestamp():
    import time
    task = create_task("Test")
    time.sleep(0.1)  # Flaky!
    assert task.created_at < datetime.now()

# ✅ Good - explicit time control
def test_task_creation_timestamp():
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 1, 1)
        task = create_task("Test")
        assert task.created_at == datetime(2023, 1, 1)
```

## Running Tests

### Local Development
```bash
# Run all tests
pytest

# Run tests with output
pytest -v

# Run specific test file  
pytest tests/test_auth.py

# Run tests matching pattern
pytest -k "test_user"

# Run failed tests only
pytest --lf

# Run in parallel (with pytest-xdist)
pytest -n auto
```

### CI/CD Integration
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

**Next Steps**: Learn about [Security Practices](security_practices.md) to ensure your code is secure and follows best practices.