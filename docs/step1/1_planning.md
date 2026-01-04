# Inventory Management API – Planning & Approach

## Project Overview

The Inventory Management API is a RESTful backend system built using Flask and PostgreSQL.  
It provides secure authentication, role-based authorization, and structured CRUD operations for managing users, categories, and products.

The project follows clean architecture principles by separating routing, business logic, data access, and utilities into independent layers.

---

## Objectives

- Implement JWT-based authentication
- Enforce role-based access control (RBAC)
- Provide CRUD operations for Products and Categories
- Apply discount and tax calculations using the Decorator Design Pattern
- Ensure clean code structure and scalability
- Add centralized error handling
- Validate authorization through automated tests

---

## High-Level Architecture

    Client
    ↓
    Flask Blueprints (Routes)
    ↓
    Service Layer (Business Logic)
    ↓
    SQLAlchemy ORM
    ↓
    PostgreSQL Database


---

## Project Structure
    app/
    ├── authentication/
    │ └── routes.py
    ├── categories/
    │ └── routes.py
    ├── products/
    │ └── routes.py
    ├── utils/
    │ └── roles_required.py
    ├── interfaces.py
    ├── service.py
    ├── models.py
    ├── price_decorator.py
    ├── config.py
    ├── init.py
    tests/
    ├── test_product.py
    ├── conftest.py
    error_handlers.py
    run.py



---

## Authentication Strategy

### JWT Authentication

- Implemented using Flask-JWT-Extended
- Access tokens are generated during login
- User ID is stored as token identity
- Role is optionally added as a JWT claim
