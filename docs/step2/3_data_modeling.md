# Data Modeling Documentation

## Overview
This document provides comprehensive coverage of the data modeling approach used in the Inventory Management API. The system uses SQLAlchemy ORM with PostgreSQL, implementing a clean, object-oriented approach to data management with proper relationships, validation, and business logic separation.

## Data Modeling Philosophy

### Design Principles
1. **Object-Relational Mapping (ORM)**: Use SQLAlchemy to bridge object-oriented programming with relational databases
2. **Separation of Concerns**: Separate data models from business logic and presentation
3. **Interface-Based Design**: Define contracts for data operations through interfaces
4. **Validation Layer**: Implement data validation at both model and service levels
5. **Relationship Integrity**: Maintain referential integrity through proper foreign key relationships

### Modeling Approach
- **Entity-Relationship Modeling**: Traditional ER approach with clear entity definitions
- **Domain-Driven Design**: Models reflect business domain concepts
- **Active Record Pattern**: Models encapsulate both data and behavior
- **Decorator Pattern**: Flexible pricing calculations through decorators

## Core Data Models

### 1. User Model

#### Purpose
Manages user authentication, authorization, and role-based access control for the inventory system.

#### Model Definition
```python
class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
```

#### Field Specifications

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| `username` | String(80) | UNIQUE, NOT NULL | User login name |
| `email` | String(120) | UNIQUE, NOT NULL | User email address |
| `password_hash` | String(200) | NOT NULL | Hashed password (Werkzeug) |
| `role` | String(20) | NOT NULL | User role (admin/manager/staff) |

#### Business Rules
- **Username Uniqueness**: No duplicate usernames allowed
- **Email Uniqueness**: No duplicate email addresses allowed
- **Password Security**: Passwords are never stored in plain text
- **Role Validation**: Only predefined roles are accepted

#### Methods
```python
def set_password(self, password):
    """Hash and set user password"""
    self.password_hash = generate_password_hash(password)

def check_password(self, password):
    """Verify user password"""
    return check_password_hash(self.password_hash, password)

def to_dict(self):
    """Serialize user to dictionary (excludes sensitive data)"""
    return {
        "id": self.id,
        "username": self.username,
        "role": self.role
    }
```

#### Role-Based Access Control
```python
ROLES = {
    'admin': {
        'permissions': ['create', 'read', 'update', 'delete'],
        'scope': ['users', 'products', 'categories']
    },
    'manager': {
        'permissions': ['create', 'read', 'update'],
        'scope': ['products', 'categories']
    },
    'staff': {
        'permissions': ['read'],
        'scope': ['products', 'categories']
    }
}
```

### 2. Category Model

#### Purpose
Organizes products into logical categories for better inventory management and navigation.

#### Model Definition
```python
class Category(db.Model):
    __tablename__ = "categories"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    products = db.relationship("Product", backref="category", lazy=True, cascade="all, delete")
```

#### Field Specifications

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PRIMARY KEY, AUTO_INCREMENT | Unique category identifier |
| `name` | String(100) | UNIQUE, NOT NULL | Category name |
| `description` | String(255) | NULLABLE | Optional category description |

#### Relationship Configuration
```python
products = db.relationship(
    "Product", 
    backref="category", 
    lazy=True, 
    cascade="all, delete"
)
```

**Relationship Properties**:
- **One-to-Many**: One category can have many products
- **Back Reference**: Product can access its category via `product.category`
- **Lazy Loading**: Products loaded when accessed
- **Cascade Delete**: Deleting a category deletes all associated products

#### Business Rules
- **Category Name Uniqueness**: No duplicate category names
- **Optional Description**: Description field is optional
- **Cascade Deletion**: Category deletion removes all products

#### Methods
```python
def to_dict(self):
    """Serialize category to dictionary"""
    return {
        "id": self.id,
        "name": self.name,
        "description": self.description
    }
```

### 3. Product Model

#### Purpose
Represents inventory items with pricing, stock levels, and categorization.

#### Model Definition
```python
class Product(db.Model):
    __tablename__ = "products"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
```

#### Field Specifications

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PRIMARY KEY, AUTO_INCREMENT | Unique product identifier |
| `name` | String(100) | NOT NULL | Product name |
| `description` | String(255) | NULLABLE | Product description |
| `price` | Float | NOT NULL | Product price |
| `stock` | Integer | DEFAULT 0 | Current stock quantity |
| `category_id` | Integer | FOREIGN KEY, NULLABLE | Reference to category |

#### Foreign Key Relationship
```python
category_id = db.Column(
    db.Integer, 
    db.ForeignKey("categories.id"), 
    nullable=True
)
```

**Relationship Properties**:
- **Many-to-One**: Many products can belong to one category
- **Optional Category**: Products can exist without categories
- **Referential Integrity**: Category must exist if specified

#### Business Rules
- **Price Validation**: Price must be a positive number
- **Stock Validation**: Stock must be non-negative integer
- **Category Validation**: Category ID must reference existing category
- **Default Stock**: New products default to 0 stock

#### Methods
```python
def to_dict(self):
    """Serialize product to dictionary with category information"""
    return {
        "id": self.id,
        "name": self.name,
        "description": self.description,
        "price": self.price,
        "stock": self.stock,
        "category": self.category.name if self.category else None
    }
```

## Data Relationships

### Entity Relationship Diagram

```
┌─────────────────┐
│     users       │
├─────────────────┤
│ id (PK)         │
│ username (UN)   │
│ email (UN)      │
│ password_hash   │
│ role            │
└─────────────────┘
        │
        │ (No direct relationships)
        ▼
┌─────────────────┐       1       ┌─────────────────┐
│   categories    │◄──────────────┤    products     │
├─────────────────┤               ├─────────────────┤
│ id (PK)         │               │ id (PK)         │
│ name (UN)       │               │ name            │
│ description     │               │ description     │
└─────────────────┘               │ price           │
        │                         │ stock           │
        │ *                       │ category_id (FK)│
        ▼                         └─────────────────┘
┌─────────────────┐
│    products     │ (Cascade delete)
│ (multiple rows) │
└─────────────────┘
```

### Relationship Types

#### 1. User-System Relationship
- **Type**: Authentication/Authorization relationship
- **Nature**: Users interact with the system but don't have direct database relationships
- **Implementation**: JWT tokens maintain user context during requests

#### 2. Category-Product Relationship
- **Type**: One-to-Many (1:N)
- **Cardinality**: One category can have zero or more products
- **Implementation**: Foreign key in products table
- **Cascade Behavior**: Category deletion triggers product deletion

#### 3. Product-Category Relationship
- **Type**: Many-to-One (N:1)
- **Cardinality**: Many products can belong to one category
- **Optional**: Products can exist without categories
- **Implementation**: Nullable foreign key

## Data Validation Framework

### Validation Layers

#### 1. Model-Level Validation
```python
# Implicit validation through SQLAlchemy constraints
- NOT NULL constraints
- UNIQUE constraints
- FOREIGN KEY constraints
- Data type constraints
```

#### 2. Service-Level Validation
```python
def validate_product_data(data):
    """Validate product data before database operations"""
    required_fields = ["name", "price", "stock"]
    
    # Required field validation
    for field in required_fields:
        if field not in data:
            return False, f"Missing field: {field}"
    
    # Type and value validation
    if not isinstance(data["price"], (int, float)) or data["price"] < 0:
        return False, "Price must be a positive number."
    
    if not isinstance(data["stock"], int) or data["stock"] < 0:
        return False, "Stock must be a non-negative integer."
    
    # Referential integrity validation
    if "category_id" in data:
        category = Category.query.get(data["category_id"])
        if not category:
            return False, "Invalid category ID."
    
    return True, None
```

#### 3. API-Level Validation
```python
# Route-level validation in controllers
- JSON body validation
- Parameter type checking
- Authentication verification
- Authorization checking
```

### Validation Rules Matrix

| Entity | Field | Validation Type | Rule |
|--------|-------|-----------------|------|
| User | username | Model | UNIQUE, NOT NULL, String(80) |
| User | email | Model | UNIQUE, NOT NULL, String(120) |
| User | password | Service | Hashed, minimum length |
| User | role | Service | Enum: [admin, manager, staff] |
| Category | name | Model | UNIQUE, NOT NULL, String(100) |
| Category | description | Service | Optional, String(255) |
| Product | name | Model | NOT NULL, String(100) |
| Product | price | Service | Positive number |
| Product | stock | Service | Non-negative integer |
| Product | category_id | Service | Valid category ID or null |

## Business Logic Modeling

### Service Layer Architecture

#### 1. Interface-Based Design
```python
# Product service interfaces
class IProductCreator(ABC):
    @abstractmethod
    def create_product(self, data): pass

class IProductReader(ABC):
    @abstractmethod
    def get_all_products(self): pass
    @abstractmethod
    def get_products(self, product_id): pass

class IProductUpdater(ABC):
    @abstractmethod
    def update_product(self, product_id, data): pass

class IProductDeleter(ABC):
    @abstractmethod
    def delete_product(self, product_id): pass
```

#### 2. Service Implementation
```python
class ProductService(IProductCreator, IProductReader, IProductUpdater, IProductDeleter):
    """Handles all product-related database operations"""
    
    def create_product(self, data):
        # Validation
        valid, error = validate_product_data(data)
        if not valid:
            raise ValueError(error)
        
        # Creation
        new_product = Product(**data)
        db.session.add(new_product)
        db.session.commit()
        return new_product
    
    def get_all_products(self):
        return Product.query.all()
    
    def get_products(self, product_id):
        return Product.query.get(product_id)
    
    def update_product(self, product_id, data):
        product = Product.query.get(product_id)
        if not product:
            return None
        
        # Validation for updates
        valid, error = validate_product_data(data)
        if not valid:
            raise ValueError(error)
        
        # Update fields
        for key, value in data.items():
            setattr(product, key, value)
        
        db.session.commit()
        return product
    
    def delete_product(self, product_id):
        product = Product.query.get(product_id)
        if not product:
            return False
        
        db.session.delete(product)
        db.session.commit()
        return True
```

### Advanced Business Logic

#### 1. Price Calculation System
```python
# Decorator pattern for flexible pricing
class IPrice(ABC):
    @abstractmethod
    def get_price(self): pass

class Price(IPrice):
    """Base price component"""
    def __init__(self, base_price: float):
        self._base_price = base_price
    
    def get_price(self):
        return self._base_price

class DiscountDecorator(PriceDecorator):
    """Applies discount to base price"""
    def __init__(self, price_component: IPrice, discount_percent: float):
        super().__init__(price_component)
        self.discount_percent = discount_percent
    
    def get_price(self):
        base = self._price_component.get_price()
        return base - (base * (self.discount_percent / 100))

class TaxDecorator(PriceDecorator):
    """Adds tax to price after discount"""
    def __init__(self, price_component: IPrice, tax_percent: float):
        super().__init__(price_component)
        self.tax_percent = tax_percent
    
    def get_price(self):
        base = self._price_component.get_price()
        return base + (base * (self.tax_percent / 100))
```

#### 2. Discount Service
```python
class DiscountedProductService(ProductService):
    """Extends base product logic with discount support"""
    
    @staticmethod
    def apply_discount(product, discount_percentage, tax_percentage=0):
        # Create price calculation chain
        base_price = Price(product.price)
        
        # Apply discount first
        discounted = DiscountDecorator(base_price, discount_percentage)
        
        # Then apply tax if specified
        if tax_percentage > 0:
            final_price = TaxDecorator(discounted, tax_percentage).get_price()
        else:
            final_price = discounted.get_price()
        
        # Update product with new price
        product.price = round(final_price, 2)
        db.session.commit()
        return product
```

## Data Access Patterns

### 1. Repository Pattern Implementation
```python
# Service classes act as repositories
class CategoryService(ICategoryUpdater, ICategoryReader, ICategoryCreator, ICategoryDeleter):
    """Repository pattern for category operations"""
    
    def create_category(self, name):
        # Check for duplicates
        if Category.query.filter_by(name=name).first():
            return None, {"error": "Category already exists"}
        
        # Create and save
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        return category, None
    
    def get_all_categories(self):
        return Category.query.all()
    
    def get_category(self, category_id):
        return Category.query.get_or_404(category_id)
    
    def update_category(self, category_id, data):
        category = Category.query.get(category_id)
        if not category:
            return None
        
        # Dynamic field updates
        for key, value in data.items():
            setattr(category, key, value)
        
        db.session.commit()
        return category
    
    def delete_category(self, category_id):
        category = Category.query.get_or_404(category_id)
        db.session.delete(category)
        db.session.commit()
        return True
```

### 2. Query Optimization Patterns
```python
# Efficient queries with proper joins
def get_products_with_categories():
    """Get products with category information in one query"""
    return Product.query.options(
        db.joinedload(Product.category)
    ).all()

# Filtered queries
def get_products_by_category(category_id):
    """Get products filtered by category"""
    return Product.query.filter_by(category_id=category_id).all()

# Aggregated queries
def get_category_product_counts():
    """Get product counts per category"""
    from sqlalchemy import func
    
    return db.session.query(
        Category.id,
        Category.name,
        func.count(Product.id).label('product_count')
    ).outerjoin(Product).group_by(Category.id).all()
```

## Data Integrity and Constraints

### 1. Database-Level Constraints
```sql
-- PostgreSQL constraints (generated by SQLAlchemy)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    role VARCHAR(20) NOT NULL
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(255)
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    price FLOAT NOT NULL,
    stock INTEGER DEFAULT 0,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL
);
```

### 2. Application-Level Constraints
```python
# Business rule enforcement
def validate_business_rules(product_data, operation='create'):
    """Enforce business rules beyond database constraints"""
    
    if operation == 'create':
        # New products must have positive price
        if product_data.get('price', 0) <= 0:
            raise ValueError("Product price must be positive")
        
        # Stock cannot be negative
        if product_data.get('stock', 0) < 0:
            raise ValueError("Stock cannot be negative")
    
    elif operation == 'update':
        # Price changes must be reasonable
        if 'price' in product_data and product_data['price'] <= 0:
            raise ValueError("Price must be positive")
        
        # Stock adjustments must be valid
        if 'stock' in product_data and product_data['stock'] < 0:
            raise ValueError("Stock cannot be negative")
    
    return True
```

### 3. Transaction Management
```python
# Atomic operations
def transfer_product_stock(product_id, from_location, to_location, quantity):
    """Transfer stock between locations atomically"""
    try:
        # Start transaction
        product = Product.query.get_or_404(product_id)
        
        # Validate sufficient stock
        if product.stock < quantity:
            raise ValueError("Insufficient stock for transfer")
        
        # Perform transfer
        product.stock -= quantity
        # ... location logic would go here
        
        # Commit transaction
        db.session.commit()
        return True
    
    except Exception as e:
        # Rollback on error
        db.session.rollback()
        raise e
```

## Data Migration Strategy

### 1. Migration Files Structure
```python
# Alembic migration example
"""Add product categories

Revision ID: 001_add_categories
Revises: 
Create Date: 2024-01-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create categories table
    op.create_table('categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Add category_id to products
    op.add_column('products', sa.Column('category_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_product_category', 'products', 'categories', ['category_id'], ['id'])

def downgrade():
    # Remove foreign key and column
    op.drop_constraint('fk_product_category', 'products', type_='foreignkey')
    op.drop_column('products', 'category_id')
    
    # Drop categories table
    op.drop_table('categories')
```

### 2. Data Seeding
```python
# Seed data for development
def seed_categories():
    """Seed initial categories"""
    categories = [
        Category(name="Electronics", description="Electronic devices and accessories"),
        Category(name="Clothing", description="Apparel and fashion items"),
        Category(name="Books", description="Printed and digital books"),
        Category(name="Home & Garden", description="Home improvement and garden supplies")
    ]
    
    for category in categories:
        db.session.add(category)
    
    db.session.commit()

def seed_admin_user():
    """Seed admin user"""
    admin = User(
        username="admin",
        email="admin@example.com",
        role="admin"
    )
    admin.set_password("admin123")
    
    db.session.add(admin)
    db.session.commit()
```

## Performance Considerations

### 1. Query Optimization
```python
# Efficient queries with proper indexing
class ProductRepository:
    @staticmethod
    def get_products_paginated(page=1, per_page=10, category_id=None):
        """Get paginated products with optional category filter"""
        query = Product.query
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        return query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
    
    @staticmethod
    def search_products(search_term):
        """Search products by name or description"""
        return Product.query.filter(
            db.or_(
                Product.name.ilike(f'%{search_term}%'),
                Product.description.ilike(f'%{search_term}%')
            )
        ).all()
```

### 2. Caching Strategy
```python
# Application-level caching (future enhancement)
from functools import lru_cache

class CategoryService:
    @staticmethod
    @lru_cache(maxsize=128)
    def get_category_cached(category_id):
        """Cached category retrieval"""
        return Category.query.get(category_id)
    
    @staticmethod
    def invalidate_cache():
        """Clear category cache"""
        CategoryService.get_category_cached.cache_clear()
```

## Data Modeling Best Practices

### 1. Naming Conventions
- **Table Names**: Plural, snake_case (e.g., `products`, `categories`)
- **Column Names**: snake_case (e.g., `category_id`, `password_hash`)
- **Model Classes**: PascalCase (e.g., `Product`, `Category`)
- **Foreign Keys**: `{table}_id` pattern (e.g., `category_id`)

### 2. Relationship Design
- **Clear Relationships**: Define relationships explicitly in models
- **Proper Cascading**: Use appropriate cascade rules
- **Lazy Loading**: Default to lazy loading for performance
- **Back References**: Provide convenient navigation

### 3. Validation Strategy
- **Multi-Layer Validation**: Model, service, and API layers
- **Clear Error Messages**: Provide actionable error information
- **Input Sanitization**: Clean and validate all inputs
- **Business Rule Enforcement**: Implement domain-specific rules

### 4. Serialization
- **Consistent Format**: Use `to_dict()` methods for JSON serialization
- **Selective Exposure**: Exclude sensitive data (passwords, etc.)
- **Relationship Handling**: Include related object information appropriately
- **Data Transformation**: Format data for API consumption

## Future Enhancements

### 1. Advanced Relationships
```python
# Many-to-many relationships (future)
product_tags = db.Table('product_tags',
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class Product(db.Model):
    tags = db.relationship('Tag', secondary=product_tags, backref='products')
```

### 2. Audit Trail
```python
# Audit logging (future)
class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(20), nullable=False)  # INSERT, UPDATE, DELETE
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
```

### 3. Soft Deletes
```python
# Soft delete implementation (future)
class Product(db.Model):
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    def soft_delete(self):
        self.deleted_at = datetime.utcnow()
        db.session.commit()
    
    @classmethod
    def get_active_products(cls):
        return cls.query.filter(cls.deleted_at.is_(None)).all()
```

This data modeling documentation provides a comprehensive foundation for understanding and extending the Inventory Management API's data architecture while maintaining data integrity, performance, and scalability.
