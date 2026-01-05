# Project Setup Documentation

## Overview
This document provides comprehensive instructions for setting up the Inventory Management API development environment from scratch. The project is built using Flask, SQLAlchemy, and PostgreSQL with a clean, modular architecture.

## Prerequisites

### System Requirements
- **Operating System**: Linux, macOS, or Windows
- **Python**: Version 3.8 or higher
- **PostgreSQL**: Version 12 or higher
- **Git**: For version control
- **pip**: Python package manager (included with Python)

### Required Software Installation

#### 1. Python Installation
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# macOS (using Homebrew)
brew install python3

# Windows
# Download from https://www.python.org/downloads/
# Ensure "Add Python to PATH" is checked during installation
```

#### 2. PostgreSQL Installation
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS (using Homebrew)
brew install postgresql
brew services start postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/
```

#### 3. Git Installation
```bash
# Ubuntu/Debian
sudo apt install git

# macOS (using Homebrew)
brew install git

# Windows
# Download from https://git-scm.com/download/win
```

## Project Setup Steps

### Step 1: Clone the Repository
```bash
# Clone the project from your repository
git clone <repository-url>
cd sdlc_inventory/Inventory_Management_API
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
# Install all required packages from requirements.txt
pip install -r requirements.txt
```

### Step 4: Database Setup

#### 4.1 Create PostgreSQL Database
```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create databases
CREATE DATABASE "Inventory_Management_API";
CREATE DATABASE "Inventory_Management_test";

# Create user (optional, if not using default postgres user)
CREATE USER inventory_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE "Inventory_Management_API" TO inventory_user;
GRANT ALL PRIVILEGES ON DATABASE "Inventory_Management_test" TO inventory_user;

# Exit PostgreSQL
\q
```

#### 4.2 Configure Database Connection
The application uses environment variables for database configuration. Create a `.env` file in the root directory:

```bash
# Create environment file
touch .env
```

Add the following content to `.env`:
```env
# Development Database
DATABASE_URL=postgresql://postgres:postgresql@127.0.0.1:5432/Inventory_Management_API

# Test Database
TEST_DATABASE_URL=postgresql://postgres:postgresql@127.0.0.1:5432/Inventory_Management_test

# JWT Secret Key (change in production)
JWT_SECRET_KEY=your-secret-key-here

# Flask Environment
FLASK_ENV=development
FLASK_DEBUG=True
```

### Step 5: Initialize Database Migrations
```bash
# Initialize migration repository (if not already done)
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migrations to database
flask db upgrade
```

### Step 6: Run the Application
```bash
# Run the development server
python run.py
```

The application should now be running at `http://127.0.0.1:5000`

## Project Structure

```
Inventory_Management_API/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration classes
│   ├── models.py                # SQLAlchemy models
│   ├── service.py               # Business logic services
│   ├── interfaces.py            # Service interfaces
│   ├── price_decorator.py       # Price calculation decorators
│   ├── authentication/
│   │   └── routes.py            # Authentication endpoints
│   ├── categories/
│   │   └── routes.py            # Category management endpoints
│   ├── products/
│   │   └── routes.py            # Product management endpoints
│   └── utils/
│       └── roles_required.py    # Role-based access control
├── tests/
│   ├── conftest.py              # Pytest configuration
│   └── test_products.py         # Product tests
├── docs/
│   ├── step1/                   # Documentation step 1
│   └── step2/                   # Documentation step 2
├── migrations/                  # Database migration files
├── venv/                        # Virtual environment
├── .gitignore                   # Git ignore file
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
└── error_handlers.py            # Global error handlers
```

## Dependencies Overview

### Core Framework
- **Flask 3.1.2**: Web framework
- **Flask-SQLAlchemy 3.1.1**: ORM for database operations
- **Flask-JWT-Extended 4.7.1**: JWT authentication
- **Flask-Migrate 4.1.0**: Database migrations

### Database
- **SQLAlchemy 2.0.45**: SQL toolkit and ORM
- **Alembic 1.17.2**: Database migration tool
- **PostgreSQL**: Database server (external dependency)

### Testing
- **pytest 9.0.2**: Testing framework
- **Additional testing utilities**: Included in requirements

### Security & Utilities
- **Werkzeug 3.1.4**: WSGI utilities and security
- **PyJWT 2.10.1**: JWT token handling
- **itsdangerous 2.2.0**: Security utilities

## Configuration

### Environment Variables
The application supports the following environment variables:

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `DATABASE_URL` | `postgresql://postgres:postgresql@127.0.0.1:5432/Inventory_Management_API` | Main database connection |
| `TEST_DATABASE_URL` | `postgresql://postgres:postgresql@127.0.0.1:5432/Inventory_Management_test` | Test database connection |
| `JWT_SECRET_KEY` | `a1b2c3d4` | JWT signing secret (change in production) |
| `FLASK_ENV` | `development` | Flask environment mode |
| `FLASK_DEBUG` | `True` | Enable debug mode |

### Configuration Classes
The application uses different configuration classes for different environments:

```python
# Development configuration (default)
class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "...")

# Test configuration
class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "...")
```

## Development Workflow

### 1. Making Changes
```bash
# Activate virtual environment
source venv/bin/activate

# Make code changes
# ...

# Run tests
pytest

# If database schema changes:
flask db migrate -m "Description of changes"
flask db upgrade
```

### 2. Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_products.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app
```

### 3. Database Migrations
```bash
# Create new migration
flask db migrate -m "Add new feature"

# Apply migration
flask db upgrade

# Rollback migration (if needed)
flask db downgrade
```

## Common Issues and Solutions

### Issue 1: Database Connection Error
**Problem**: `psycopg2.OperationalError: could not connect to server`

**Solution**:
1. Ensure PostgreSQL is running: `sudo systemctl status postgresql`
2. Check database exists: `sudo -u postgres psql -l`
3. Verify connection string in `.env` file

### Issue 2: Module Import Errors
**Problem**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
1. Ensure virtual environment is activated
2. Install dependencies: `pip install -r requirements.txt`
3. Check you're in the correct directory

### Issue 3: Migration Issues
**Problem**: `alembic.util.exc.CommandError: Can't locate revision identified by`

**Solution**:
1. Drop and recreate database: `sudo -u postgres psql -c "DROP DATABASE Inventory_Management_API;"`
2. Recreate database: `sudo -u postgres psql -c "CREATE DATABASE Inventory_Management_API;"`
3. Run migrations: `flask db upgrade`

### Issue 4: Permission Errors
**Problem**: Permission denied when accessing database

**Solution**:
1. Grant permissions to database user
2. Check PostgreSQL user permissions
3. Ensure correct database ownership

## Production Deployment Considerations

### Security
1. Change default JWT secret key
2. Use environment variables for sensitive data
3. Enable HTTPS in production
4. Use production-grade database credentials

### Performance
1. Use production WSGI server (Gunicorn/uWSGI)
2. Configure database connection pooling
3. Enable database query optimization
4. Implement caching strategies

### Monitoring
1. Set up application logging
2. Monitor database performance
3. Implement health checks
4. Set up error tracking

## API Testing

### Using curl
```bash
# Register a user
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@test.com","password":"password","role":"admin"}'

# Login
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Create product (with token)
curl -X POST http://127.0.0.1:5000/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"name":"Test Product","price":99.99,"stock":10}'
```

### Using Postman
1. Import the API endpoints from the documentation
2. Set up environment variables for base URL and authentication
3. Use the JWT token for authenticated endpoints

## Development Tips

### 1. Code Quality
- Follow PEP 8 style guidelines
- Use meaningful variable names
- Write comprehensive docstrings
- Implement proper error handling

### 2. Testing
- Write unit tests for all service methods
- Test API endpoints with different scenarios
- Use fixtures for test data setup
- Maintain high test coverage

### 3. Database
- Use migrations for all schema changes
- Test migrations on copy of production data
- Backup database before major changes
- Monitor database performance

### 4. Security
- Never commit sensitive data to version control
- Use parameterized queries (SQLAlchemy handles this)
- Validate all input data
- Implement proper authentication and authorization

## Troubleshooting Guide

### Virtual Environment Issues
```bash
# If virtual environment doesn't activate
# Deactivate first
deactivate

# Remove and recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database Issues
```bash
# Reset database completely
sudo -u postgres psql -c "DROP DATABASE IF EXISTS Inventory_Management_API;"
sudo -u postgres psql -c "CREATE DATABASE Inventory_Management_API;"
flask db upgrade
```

### Port Conflicts
```bash
# Check if port 5000 is in use
lsof -i :5000

# Kill process using port 5000
sudo kill -9 <PID>

# Or run on different port
python run.py --port 5001
```

## Next Steps

After completing the setup:

1. **Explore the API**: Read the API documentation in `4_api_end_point.md`
2. **Understand the Architecture**: Review `6_architecture.md`
3. **Run Tests**: Execute the test suite to verify setup
4. **Make Changes**: Start developing new features
5. **Contribute**: Follow the project's contribution guidelines

## Support

For additional help:
1. Check the existing documentation in the `docs/` folder
2. Review the test files for usage examples
3. Examine the error logs for detailed error messages
4. Consult the Flask and SQLAlchemy documentation

This setup guide should provide everything needed to get the Inventory Management API running successfully in a development environment.
