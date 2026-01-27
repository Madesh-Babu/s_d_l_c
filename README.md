# Inventory Management API

## 📋 Overview

A comprehensive Flask-based REST API for inventory management with modern architecture, SOLID principles, and design patterns. This project demonstrates best practices in API development, authentication, structured logging, exception handling, and code organization.

## 🎯 Key Features

- **🔐 Authentication System**: JWT-based authentication with role-based access control
- **🛡️ Development Bypass**: Authentication bypass for local development
- **📊 SOLID Principles**: Clean architecture with proper separation of concerns
- **🎨 Design Patterns**: Singleton, Factory, Decorator, Strategy patterns implemented
- **⚙️ Feature Toggles**: Environment-based configuration management
- **📝 Structured Logging**: JSON-formatted logging with multiple levels and colors
- **✅ Exception Handling**: Comprehensive error management with custom exceptions
- **🚨 Error Management**: Global error handlers with consistent responses
- **✅ Data Validation**: Multi-layer validation using Pydantic
- **🗄️ Database Integration**: PostgreSQL with SQLAlchemy ORM
- **🧪 Testing Ready**: Comprehensive test structure and examples

## 🏗️ Architecture

### **Layered Architecture**
```
┌─────────────────────────────────────┐
│        API Routes (Controllers)      │
├─────────────────────────────────────┤
│         Service Layer (Business)     │
├─────────────────────────────────────┤
│         Data Access (Models/ORM)     │
├─────────────────────────────────────┤
│        Database (PostgreSQL)         │
└─────────────────────────────────────┘
```

### **Project Structure**
```
Inventory_Management_API/
├── src/
│   ├── api/                    # API endpoints
│   │   ├── authentication/     # User auth routes
│   │   ├── products/          # Product management
│   │   └── categories/         # Category management
│   ├── core/                   # Core utilities
│   │   ├── config.py          # Environment configuration
│   │   ├── exceptions.py      # Custom exceptions
│   │   ├── validation.py      # Input validation
│   │   ├── logging.py         # Structured logging
│   │   ├── interfaces.py      # Service interfaces
│   │   └── error_handlers.py   # Global error handlers
│   ├── models/                 # Database models
│   │   ├── models.py          # SQLAlchemy models
│   │   └── schemas.py         # Pydantic schemas
│   ├── services/               # Business logic
│   │   ├── service.py         # Service implementations
│   │   └── price_decorator.py  # Price calculation
│   └── utils/                  # Shared utilities
├── examples/                   # Learning resources
│   ├── solid_principles/       # SOLID examples
│   ├── design_patterns/        # Pattern examples
│   └── before_solid_patterns/  # Before/after comparison
├── tests/                      # Test suite
├── docs/                       # Documentation
│   └── step3/                  # Implementation guides
├── .env.local                  # Environment variables
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8+
- PostgreSQL 12+
- Git

### **Installation**
```bash
# Clone repository
git clone <repository-url>
cd Inventory_Management_API

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env.local
# Edit .env.local with your database credentials

# Database setup
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Run application
python run.py
```

### **Environment Configuration**
Create `.env.local` with:
```bash
# Database
PG_USER=your_username
PG_PASSWORD=your_password
PG_HOST=localhost
PG_PORT=5432
PG_DB=inventory_db

# JWT
JWT_SECRET_KEY=your-secret-key

# Environment
ENVIRONMENT=development
FLASK_DEBUG=True
```

## 🔐 Authentication

### **Development Mode (Bypass Enabled)**
```bash
# No authentication required in development!
curl http://127.0.0.1:5000/auth/users

# Response includes bypass indicator:
{
  "users": [...],
  "auth_bypassed": true,
  "message": "Authentication bypassed in development"
}
```

### **Production Mode (JWT Required)**
```bash
# Register user
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "email": "admin@example.com", "password": "SecurePass123!"}'

# Login
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "SecurePass123!"}'

# Use token for protected routes
curl -H "Authorization: Bearer <token>" http://127.0.0.1:5000/auth/users
```

## 📚 API Endpoints

### **Authentication**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | ❌ |
| POST | `/auth/login` | User login | ❌ |
| POST | `/auth/dev-login` | Development bypass | ❌ |
| GET | `/auth/users` | Get all users | ✅ |
| GET | `/auth/<id>` | Get specific user | ✅ |
| PUT | `/auth/<id>` | Update user | ✅ |
| DELETE | `/auth/<id>` | Delete user | ✅ |

### **Products**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/products/` | Get all products | ✅ |
| POST | `/products/` | Create product | ✅ |
| GET | `/products/<id>` | Get product | ✅ |
| PUT | `/products/<id>` | Update product | ✅ |
| DELETE | `/products/<id>` | Delete product | ✅ |

### **Categories**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/categories/` | Get all categories | ✅ |
| POST | `/categories/` | Create category | ✅ |
| GET | `/categories/<id>` | Get category | ✅ |
| PUT | `/categories/<id>` | Update category | ✅ |
| DELETE | `/categories/<id>` | Delete category | ✅ |

## 🎯 SOLID Principles & Design Patterns

### **SOLID Principles Implementation**
- **Single Responsibility**: Each class has one purpose
- **Open/Closed**: Extensible without modification
- **Liskov Substitution**: Subtypes replaceable for base types
- **Interface Segregation**: Small, focused interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

### **Design Patterns Used**
- **Singleton**: Database connection management
- **Factory Method**: Service creation
- **Decorator Pattern**: Price calculation system
- **Strategy Pattern**: Different validation strategies
- **Template Method**: Exception handling hierarchy

### **Learning Resources**
```
examples/
├── solid_principles/           # SOLID principles examples
│   ├── single_responsibility/ # SRP before/after
│   └── README.md              # SOLID overview
├── design_patterns/           # Pattern examples
│   ├── decorator/             # Decorator pattern demo
│   └── README.md              # Patterns overview
└── before_solid_patterns/     # Before implementation
    ├── validation_before.py   # Monolithic validation
    ├── services_before.py     # Fat services
    └── README.md              # Problems demonstrated
```

## ⚙️ Configuration & Feature Toggles

### **Environment-Based Configuration**
```python
# Development
DevelopmentConfig:
    BYPASS_AUTH=True          # Skip login in dev
    ENABLE_RATE_LIMITING=False # No rate limiting

# Production  
ProductionConfig:
    BYPASS_AUTH=False         # Must login in prod
    ENABLE_RATE_LIMITING=True  # Protect API
```

### **Feature Toggles**
- `BYPASS_AUTH`: Skip authentication in development
- `ENABLE_RATE_LIMITING`: API rate limiting
- `ENABLE_CORS`: Cross-origin requests
- `ENABLE_REQUEST_LOGGING`: Detailed logging
- `ENABLE_SWAGGER_DOCS`: API documentation

## 📊 Examples & Usage

### **Price Calculation with Decorators**
```python
from src.services.price_decorator import Price, DiscountDecorator, TaxDecorator

# Base price
base_price = Price(100.0)

# Apply 10% discount
discounted = DiscountDecorator(base_price, 10)

# Apply 8% tax
final_price = TaxDecorator(discounted, 8)
print(f"Final price: ${final_price.get_price():.2f}")  # $97.20
```

### **Service Interfaces**
```python
from src.core.interfaces import IProductCreator, IProductReader

class ProductService(IProductCreator, IProductReader):
    def create_product(self, data): ...
    def get_all_products(self): ...
    def get_product(self, id): ...
```

### **Custom Exceptions**
```python
from src.core.exceptions import ValidationErrorException, DatabaseError

try:
    validate_user_data(data)
except ValidationErrorException as e:
    return jsonify(e.details), 400
```

## 📝 Structured Logging System

### **Logging Features**
- **JSON Format**: Structured log output for easy parsing
- **Multiple Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Colored Output**: Visual distinction for different log levels
- **Context Information**: User ID, request ID, timestamps
- **File Logging**: Persistent log storage with rotation
- **Environment-Based**: Different logging levels per environment

### **Logging Usage**
```python
from src.core.logging import get_logger, log_user_action, log_api_error

logger = get_logger(__name__)

# Basic logging
logger.info("User logged in", user_id=123, username="admin")

# User action logging
log_user_action("user_created", user_id=123, details={"username": "new_user"})

# API error logging
log_api_error("validation_failed", endpoint="/auth/register", 
              error="Invalid email format", user_id=123)
```

### **Log Output Examples**
```json
{
  "timestamp": "2024-01-20T10:30:45.123Z",
  "level": "INFO",
  "logger": "src.api.authentication.routes",
  "message": "User login successful",
  "user_id": 123,
  "username": "admin",
  "ip_address": "127.0.0.1",
  "request_id": "req_abc123"
}
```

## 🚨 Exception & Error Handling

### **Custom Exception Hierarchy**
```python
# Base exception
class BaseAPIException(Exception):
    def __init__(self, message, status_code=500, error_code=None, details=None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}

# Specific exceptions
class ValidationErrorException(BaseAPIException):
    def __init__(self, message, details=None):
        super().__init__(message, 400, "VALIDATION_ERROR", details)

class AuthenticationError(BaseAPIException):
    def __init__(self, message="Authentication failed"):
        super().__init__(message, 401, "AUTHENTICATION_ERROR")

class DatabaseError(BaseAPIException):
    def __init__(self, message="Database operation failed"):
        super().__init__(message, 500, "DATABASE_ERROR")
```

### **Global Error Handlers**
```python
from src.core.error_handlers import register_error_handlers

# Automatic registration of error handlers
register_error_handlers(app)

# Consistent error responses
{
  "error": "Validation failed",
  "error_code": "VALIDATION_ERROR",
  "message": "Invalid email format",
  "details": {
    "field": "email",
    "value": "invalid-email"
  },
  "timestamp": "2024-01-20T10:30:45.123Z"
}
```

### **Error Handling Features**
- **Consistent Format**: All errors follow the same response structure
- **Error Codes**: Machine-readable error identifiers
- **Detailed Messages**: Human-readable error descriptions
- **Context Information**: Additional error details and metadata
- **Logging Integration**: Automatic error logging with context
- **HTTP Status Codes**: Proper status code mapping

## 🧪 Testing

### **Running Tests**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_authentication.py
```

### **Test Structure**
```
tests/
├── conftest.py              # Test fixtures
├── test_authentication.py   # Auth tests
├── test_products.py        # Product tests
└── test_categories.py      # Category tests
```

## 🔧 Development Features

### **Authentication Bypass**
```python
# Automatic bypass in development
if settings.feature_toggles.BYPASS_AUTH and settings.is_development():
    return jsonify({"data": data, "auth_bypassed": True})
```

### **Data Validation**
```python
from src.models.schemas import UserCreate
from pydantic import ValidationError

try:
    user_data = UserCreate(**request_data)
except ValidationError as e:
    return jsonify({"error": str(e)}), 400
```

### **Environment Detection**
```python
from src.core.config import settings

if settings.is_development():
    # Development-specific logic
    enable_debug_features()
elif settings.is_production():
    # Production-specific logic
    enable_security_features()
```

## 📈 Performance & Security

### **Security Features**
- JWT token authentication
- Password hashing with Werkzeug
- Role-based access control
- Input validation and sanitization
- SQL injection prevention with ORM
- CORS configuration
- Environment-based security settings

### **Performance Features**
- Database connection pooling
- Query optimization with SQLAlchemy
- Efficient logging with structured format
- Environment-based configuration
- Feature toggles for performance control

## 🚀 Deployment

### **Environment Variables**
```bash
# Production
ENVIRONMENT=production
FLASK_DEBUG=False
BYPASS_AUTH=False
ENABLE_RATE_LIMITING=True
LOG_LEVEL=WARNING
```

### **Database Setup**
```bash
# Production database
export DATABASE_URL=postgresql://user:pass@host:5432/db

# Run migrations
flask db upgrade
```

## 📋 Requirements

### **Core Dependencies**
```
Flask==3.1.2
Flask-JWT-Extended==4.7.1
Flask-SQLAlchemy==3.1.1
psycopg2-binary==2.9.9
Pydantic==2.12.5
pydantic-settings==2.6.1
colorama==0.4.6
```

### **Development Dependencies**
```
pytest==8.3.3
pytest-cov==6.0.0
black==24.10.0
isort==5.13.2
flake8==7.1.1
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎯 Implementation Status

### ✅ **Completed Features**
- [x] **Authentication System**: JWT-based auth with role-based access
- [x] **Development Bypass**: Authentication bypass for local development
- [x] **Structured Logging**: JSON-formatted logging with colors and context
- [x] **Exception Handling**: Custom exception hierarchy with global handlers
- [x] **Error Management**: Consistent error responses with proper status codes
- [x] **SOLID Principles**: Clean architecture implementation
- [x] **Design Patterns**: Singleton, Factory, Decorator patterns
- [x] **Feature Toggles**: Environment-based configuration
- [x] **Data Validation**: Multi-layer validation with Pydantic
- [x] **Database Integration**: PostgreSQL with SQLAlchemy
- [x] **API Endpoints**: Complete CRUD operations
- [x] **Documentation**: Comprehensive examples and guides

### 🔄 **In Progress**
- [ ] **API Documentation**: Swagger/OpenAPI specification
- [ ] **Performance Optimization**: Query optimization and caching
- [ ] **Advanced Features**: Search, filtering, pagination
- [ ] **Monitoring**: Health checks and metrics

### ⏳ **Planned**
- [ ] **Deployment**: Production deployment guide
- [ ] **Testing**: Comprehensive test coverage
- [ ] **Security**: Additional security hardening
- [ ] **Scaling**: Performance and scalability improvements

## 🎯 Success Metrics

- ✅ **Code Quality**: Clean, maintainable, and well-documented
- ✅ **Architecture**: SOLID principles and design patterns
- ✅ **Security**: Authentication, authorization, and validation
- ✅ **Logging**: Structured logging with proper context
- ✅ **Error Handling**: Comprehensive exception management
- ✅ **Performance**: Optimized queries and efficient configuration
- ✅ **Documentation**: Complete API documentation and examples

---

**Built with ❤️ using Flask, SQLAlchemy, and modern Python practices**
