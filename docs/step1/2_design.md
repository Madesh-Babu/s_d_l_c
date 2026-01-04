# System Design

## Backend Framework
- **Flask**: Lightweight Python web framework for building RESTful APIs
- **Python 3.10+**: Core programming language

## API Architecture
- **Blueprint-based Modular Design**: Separation of authentication, products, and categories
- **Service Layer Pattern**: Business logic isolated from route handlers
- **Interface-Based Design**: Abstract base classes to enforce contracts
- **Decorator Pattern**: Used for role checks and pricing logic

## Database & ORM
- **PostgreSQL**: Primary relational database
- **SQLAlchemy**: ORM for database modeling and queries
- **Flask-Migrate**: Database migrations powered by Alembic

## Authentication & Authorization
- **JWT (Flask-JWT-Extended)**: Stateless authentication using access tokens
- **Role-Based Access Control (RBAC)**:
  - Roles: `admin`, `manager`, `staff`
  - Custom `@role_required` decorator
- **Werkzeug Security**:
  - Password hashing
  - Password verification