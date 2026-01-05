# Project Structure Documentation

## Overview
This document provides a comprehensive overview of the Inventory Management API project structure. The project follows a clean, modular architecture that promotes maintainability, scalability, and separation of concerns.

## Root Directory Structure

```
sdlc_inventory/
├── Inventory_Management_API/          # Main application directory
│   ├── app/                          # Application core
│   ├── tests/                        # Test suite
│   ├── docs/                         # Documentation
│   ├── migrations/                   # Database migrations
│   ├── venv/                         # Virtual environment
│   ├── .git/                         # Git repository
│   ├── .gitignore                    # Git ignore rules
│   ├── requirements.txt              # Python dependencies
│   ├── run.py                        # Application entry point
│   └── error_handlers.py            # Global error handlers
└── venv/                            # Parent level virtual environment
```

## Detailed Directory Breakdown

### 1. Application Core (`app/`)

The `app/` directory contains the main application code organized in a modular fashion:

```
app/
├── __init__.py                      # Flask app factory and initialization
├── config.py                        # Configuration classes
├── models.py                        # SQLAlchemy database models
├── service.py                       # Business logic services
├── interfaces.py                    # Service interface definitions
├── price_decorator.py               # Price calculation decorators
├── authentication/                  # Authentication module
│   └── routes.py                    # Authentication endpoints
├── categories/                      # Category management module
│   └── routes.py                    # Category endpoints
├── products/                        # Product management module
│   ├── __init__.py                  # Package initialization
│   └── routes.py                    # Product endpoints
└── utils/                           # Utility modules
    └── roles_required.py            # Role-based access control
```

#### 1.1 Core Application Files

##### `__init__.py`
- **Purpose**: Flask application factory
- **Responsibilities**:
  - Application initialization
  - Extension registration (SQLAlchemy, JWT, Migrate)
  - Blueprint registration
  - Error handler registration
- **Key Functions**:
  - `create_app()`: Creates and configures Flask application

##### `config.py`
- **Purpose**: Configuration management
- **Classes**:
  - `Config`: Base configuration class
  - `TestConfig`: Test-specific configuration
- **Features**:
  - Environment variable support
  - Database URI configuration
  - Separate test database setup

##### `models.py`
- **Purpose**: Database model definitions
- **Models**:
  - `User`: Authentication and authorization
  - `Category`: Product categorization
  - `Product`: Inventory items
- **Features**:
  - SQLAlchemy ORM mappings
  - Relationship definitions
  - Serialization methods (`to_dict()`)

##### `service.py`
- **Purpose**: Business logic layer
- **Services**:
  - `ProductService`: Product CRUD operations
  - `CategoryService`: Category CRUD operations
  - `DiscountedProductService`: Extended product operations
- **Features**:
  - Data validation
  - Database operations abstraction
  - Business rule implementation

##### `interfaces.py`
- **Purpose**: Service interface definitions
- **Interfaces**:
  - `IProductCreator`, `IProductReader`, `IProductUpdater`, `IProductDeleter`
  - `ICategoryCreator`, `ICategoryReader`, `ICategoryUpdater`, `ICategoryDeleter`
- **Benefits**:
  - Contract definitions
  - Dependency injection support
  - Testability improvements

##### `price_decorator.py`
- **Purpose**: Price calculation system
- **Pattern**: Decorator Pattern implementation
- **Components**:
  - `IPrice`: Price interface
  - `Price`: Base price component
  - `DiscountDecorator`: Discount application
  - `TaxDecorator`: Tax application
- **Benefits**:
  - Flexible pricing calculations
  - Easy to extend with new pricing rules

#### 1.2 Module Directories

##### `authentication/` Module
```
authentication/
└── routes.py                        # Authentication endpoints
```

**Purpose**: User authentication and authorization
**Endpoints**:
- User registration (`POST /auth/register`)
- User login (`POST /auth/login`)
- User management (CRUD operations)
**Features**:
- JWT token generation and validation
- Role-based access control
- Password hashing and verification

##### `categories/` Module
```
categories/
└── routes.py                        # Category management endpoints
```

**Purpose**: Product category management
**Endpoints**:
- Create category (`POST /categories`)
- Get all categories (`GET /categories`)
- Get category by ID (`GET /categories/<id>`)
- Update category (`PUT /categories/update`)
- Delete category (`DELETE /categories/<id>`)
**Features**:
- Category CRUD operations
- Product-category relationships
- Cascade delete handling

##### `products/` Module
```
products/
├── __init__.py                      # Package initialization
└── routes.py                        # Product management endpoints
```

**Purpose**: Product inventory management
**Endpoints**:
- Create product (`POST /products`)
- Get all products (`GET /products`)
- Get product by ID (`GET /products/<id>`)
- Update product (`PUT /products/update`)
- Delete product (`DELETE /products/delete`)
- Apply discount (`PATCH /products/discount`)
**Features**:
- Product CRUD operations
- Stock management
- Discount and tax calculations
- Category relationships

##### `utils/` Module
```
utils/
└── roles_required.py                # Role-based access control
```

**Purpose**: Shared utility functions and decorators
**Components**:
- `role_required()`: Role-based authorization decorator
**Features**:
- JWT token validation
- Role checking
- Permission enforcement

### 2. Test Suite (`tests/`)

```
tests/
├── conftest.py                      # Pytest configuration and fixtures
└── test_products.py                 # Product-related tests
```

#### 2.1 Test Configuration

##### `conftest.py`
- **Purpose**: Pytest configuration and shared fixtures
- **Fixtures**:
  - `app`: Test application instance
  - `client`: Test client
  - `admin_headers`: Admin authentication headers
  - `customer_headers`: Staff authentication headers
- **Features**:
  - Database setup/teardown
  - Test data initialization
  - Authentication mocking

##### `test_products.py`
- **Purpose**: Product endpoint testing
- **Coverage**:
  - Product CRUD operations
  - Authentication requirements
  - Role-based access control
  - Input validation

### 3. Documentation (`docs/`)

```
docs/
├── step1/                           # Phase 1 documentation
│   ├── 1_planning.md               # Project planning
│   ├── 2_design.md                 # System design
│   ├── 3_user_stories.md           # User requirements
│   ├── 4_api_end_point.md          # API documentation
│   ├── 5_database_schema.md        # Database documentation
│   └── 6_architecture.md           # Architecture documentation
└── step2/                           # Phase 2 documentation
    ├── 1_project_setup.md          # Setup instructions
    └── 2_project_structure.md      # This document
```

#### 3.1 Documentation Organization

**Phase 1 (step1/)**: Planning and Design
- Project planning and requirements
- System design and architecture
- User stories and use cases
- API specifications
- Database schema
- Architecture documentation

**Phase 2 (step2/)**: Implementation and Deployment
- Project setup instructions
- Project structure documentation
- (Future: deployment guides, maintenance docs)

### 4. Database Migrations (`migrations/`)

```
migrations/
├── versions/                        # Migration version files
├── alembic.ini                      # Alembic configuration
├── env.py                          # Migration environment
├── script.py.mako                  # Migration script template
└── README                          # Migration documentation
```

**Purpose**: Database schema version control
**Features**:
- Automatic migration generation
- Version-controlled schema changes
- Rollback capabilities
- Environment-specific migrations

### 5. Root Configuration Files

#### `run.py`
- **Purpose**: Application entry point
- **Functionality**:
  - Application creation
  - Development server startup
  - Debug mode configuration

#### `requirements.txt`
- **Purpose**: Python dependency specification
- **Contents**:
  - Flask framework and extensions
  - Database drivers and ORM
  - Testing frameworks
  - Security utilities
- **Features**:
  - Version pinning
  - Reproducible environments

#### `error_handlers.py`
- **Purpose**: Global error handling
- **Features**:
  - HTTP exception handling
  - Consistent JSON error responses
  - Status code management
  - Error logging

#### `.gitignore`
- **Purpose**: Git version control exclusions
- **Coverage**:
  - Python bytecode files
  - Virtual environments
  - IDE configuration files
  - Sensitive data files
  - Build artifacts

## Architectural Patterns

### 1. Modular Architecture
The application follows a modular design where each functional area is organized into separate modules:

```
Modular Structure:
├── authentication/      # User management
├── categories/         # Category management
├── products/           # Product management
└── utils/              # Shared utilities
```

**Benefits**:
- Clear separation of concerns
- Easy to maintain and extend
- Team development friendly
- Reusable components

### 2. Layered Architecture
The application implements a classic layered architecture:

```
Layer Structure:
├── Presentation Layer     # Routes and controllers
├── Business Logic Layer   # Services and business rules
├── Data Access Layer      # Models and ORM
└── Data Storage Layer     # Database
```

**Benefits**:
- Clear responsibility separation
- Easy to test individual layers
- Flexible technology substitution
- Maintainable codebase

### 3. Blueprint Pattern
Flask Blueprints are used to organize routes:

```
Blueprint Organization:
├── auth_b_p              # Authentication routes
├── products_b_p          # Product routes
└── categories_b_p        # Category routes
```

**Benefits**:
- Modular route organization
- Easy to add new modules
- Clean URL structure
- Independent testing

## File Naming Conventions

### Python Files
- **Modules**: `snake_case.py` (e.g., `models.py`, `service.py`)
- **Packages**: `snake_case/` (e.g., `authentication/`, `products/`)
- **Classes**: `PascalCase` (e.g., `ProductService`, `UserModel`)
- **Functions**: `snake_case` (e.g., `create_product`, `validate_data`)

### Documentation Files
- **Files**: `snake_case.md` (e.g., `project_setup.md`)
- **Sections**: `Title Case` (e.g., "Project Overview")
- **Code Blocks**: Language-specific syntax highlighting

### Configuration Files
- **Standard names**: `requirements.txt`, `.gitignore`, `run.py`
- **Environment files**: `.env`, `.env.example`
- **Configuration classes**: `Config`, `TestConfig`, `ProductionConfig`

## Import Structure

### Application Imports
```python
# Standard library
import os
from abc import ABC, abstractmethod

# Third-party libraries
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import jwt_required

# Application modules
from app.models import db, Product, Category
from app.service import ProductService
from app.utils.roles_required import role_required
```

### Module Imports
```python
# Relative imports within app package
from . import db
from .models import Product
from .service import ProductService
```

## Data Flow Architecture

### Request Flow
```
HTTP Request
    ↓
Authentication Middleware
    ↓
Role-Based Authorization
    ↓
Route Handler (Blueprint)
    ↓
Service Layer (Business Logic)
    ↓
Model Layer (Data Access)
    ↓
Database
    ↓
Response (Reverse Flow)
```

### Module Dependencies
```
routes.py → service.py → models.py → database
    ↓           ↓           ↓
decorators → interfaces → config
```

## Testing Structure

### Test Organization
```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_auth.py             # Authentication tests
├── test_products.py         # Product tests
├── test_categories.py       # Category tests
└── integration/             # Integration tests
    └── test_api_flow.py     # End-to-end tests
```

### Test Categories
- **Unit Tests**: Individual function and method testing
- **Integration Tests**: Module interaction testing
- **API Tests**: Endpoint testing with HTTP requests
- **Database Tests**: Model and migration testing

## Configuration Management

### Environment-Based Configuration
```
Configuration Hierarchy:
├── Config (Base)
├── DevelopmentConfig
├── TestConfig
├── ProductionConfig
└── Environment Variables
```

### Configuration Sources
1. **Default values** in configuration classes
2. **Environment variables** for sensitive data
3. **Configuration files** for structured settings
4. **Runtime arguments** for development overrides

## Security Structure

### Authentication Flow
```
User Credentials
    ↓
Validation (routes.py)
    ↓
Password Verification (models.py)
    ↓
JWT Generation (flask-jwt-extended)
    ↓
Token Storage (Client)
```

### Authorization Flow
```
JWT Token
    ↓
Token Validation (roles_required.py)
    ↓
Role Extraction
    ↓
Permission Check
    ↓
Resource Access
```

## Development Workflow Integration

### Git Workflow
```
Development Structure:
├── feature/                 # Feature branches
├── develop/                 # Integration branch
├── main/                    # Production branch
└── hotfix/                  # Emergency fixes
```

### Code Organization Principles
1. **Single Responsibility**: Each module has one clear purpose
2. **Don't Repeat Yourself**: Shared functionality in utils/
3. **Separation of Concerns**: Clear layer boundaries
4. **Dependency Injection**: Interface-based design

## Extension Points

### Adding New Modules
1. Create module directory in `app/`
2. Add `routes.py` with Flask Blueprint
3. Implement service classes in `service.py`
4. Define models in `models.py`
5. Register blueprint in `__init__.py`
6. Add tests in `tests/`

### Adding New Features
1. Define interfaces in `interfaces.py`
2. Implement services in `service.py`
3. Add routes in appropriate module
4. Create comprehensive tests
5. Update documentation

## Maintenance Considerations

### Code Organization Benefits
- **Easy Navigation**: Logical file structure
- **Team Collaboration**: Clear module boundaries
- **Testing**: Isolated components
- **Debugging**: Clear responsibility areas

### Scalability Features
- **Modular Growth**: Easy to add new modules
- **Database Scaling**: Migration support
- **Configuration**: Environment-based settings
- **Documentation**: Comprehensive guides

This project structure provides a solid foundation for the Inventory Management API while supporting future growth and maintenance requirements.
