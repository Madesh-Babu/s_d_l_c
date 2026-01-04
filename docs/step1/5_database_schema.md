# Database Schema Documentation

## Overview
The Inventory Management API uses PostgreSQL as the database with SQLAlchemy ORM. The database consists of three main tables: users, categories, and products.

## Database Configuration
- **Database Type**: PostgreSQL
- **Connection URI**: `postgresql://postgres:postgresql@127.0.0.1:5432/Inventory_Management_API`
- **ORM**: SQLAlchemy
- **Migration Tool**: Flask-Migrate

## Database Schema

### 1. Users Table

**Table Name**: `users`

**Purpose**: Stores user authentication and role information for the inventory management system.

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO_INCREMENT | Unique identifier for each user |
| username | String(80) | UNIQUE, NOT NULL | User's login username |
| email | String(120) | UNIQUE, NOT NULL | User's email address |
| password_hash | String(200) | NOT NULL | Hashed password using Werkzeug security |
| role | String(20) | NOT NULL | User role (admin, manager, staff) |

**Role Values**:
- `admin`: Full system access including delete operations
- `manager`: Can create, read, update products and categories, apply discounts
- `staff`: Read-only access to products and categories

**Indexes**:
- Unique index on `username`
- Unique index on `email`

**Security Notes**:
- Passwords are hashed using Werkzeug's `generate_password_hash()`
- Password verification uses `check_password_hash()`

---

### 2. Categories Table

**Table Name**: `categories`

**Purpose**: Stores product categories for organizing inventory items.

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO_INCREMENT | Unique identifier for each category |
| name | String(100) | UNIQUE, NOT NULL | Category name |
| description | String(255) | NULLABLE | Optional category description |

**Relationships**:
- One-to-Many relationship with `products` table
- Cascade delete: When a category is deleted, all associated products are also deleted

**Indexes**:
- Unique index on `name`

**Constraints**:
- Category names must be unique across the system

---

### 3. Products Table

**Table Name**: `products`

**Purpose**: Stores product information including pricing, stock levels, and category associations.

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO_INCREMENT | Unique identifier for each product |
| name | String(100) | NOT NULL | Product name |
| description | String(255) | NULLABLE | Optional product description |
| price | Float | NOT NULL | Product price |
| stock | Integer | DEFAULT 0 | Current stock quantity |
| category_id | Integer | FOREIGN KEY, NULLABLE | Reference to categories.id |

**Foreign Key Relationship**:
- `category_id` references `categories.id`
- Allows NULL values (products can exist without categories)
- No cascade delete on category removal (handled by category relationship)

**Indexes**:
- Foreign key index on `category_id`

**Business Rules**:
- Stock defaults to 0 if not specified
- Price must be a positive number
- Products can exist without being assigned to a category

---

## Entity Relationship Diagram (ERD)

```
┌─────────────────┐       ┌─────────────────┐
│     users       │       │   categories    │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ username (UN)   │       │ name (UN)       │
│ email (UN)      │       │ description     │
│ password_hash   │       └─────────────────┘
│ role            │               │
└─────────────────┘               │
                                  │ 1
                                  │
                                  │ *
                         ┌─────────────────┐
                         │    products     │
                         ├─────────────────┤
                         │ id (PK)         │
                         │ name            │
                         │ description     │
                         │ price           │
                         │ stock           │
                         │ category_id (FK)│
                         └─────────────────┘
```

## Relationships Summary

### Users
- **No direct relationships** with other tables
- Used for authentication and authorization

### Categories
- **One-to-Many** with Products
- One category can have many products
- Cascade delete enabled

### Products
- **Many-to-One** with Categories
- Many products can belong to one category
- Category assignment is optional

## Database Constraints

### Unique Constraints
- `users.username` - No duplicate usernames
- `users.email` - No duplicate email addresses
- `categories.name` - No duplicate category names

### Foreign Key Constraints
- `products.category_id` → `categories.id`
- Referential integrity maintained

### Cascade Rules
- **Category Delete**: When a category is deleted, all associated products are automatically deleted
- **Product Delete**: No cascade effects

## Data Types and Limits

### String Fields
- `users.username`: 80 characters max
- `users.email`: 120 characters max
- `users.password_hash`: 200 characters max
- `users.role`: 20 characters max
- `categories.name`: 100 characters max
- `categories.description`: 255 characters max
- `products.name`: 100 characters max
- `products.description`: 255 characters max

### Numeric Fields
- `users.id`: Integer (auto-increment)
- `categories.id`: Integer (auto-increment)
- `products.id`: Integer (auto-increment)
- `products.price`: Float (decimal precision)
- `products.stock`: Integer (default 0)
- `products.category_id`: Integer

## Sample Data Structure

### Users Table Example
```sql
INSERT INTO users (username, email, password_hash, role) VALUES
('admin', 'admin@example.com', 'hashed_password_here', 'admin'),
('manager1', 'manager@example.com', 'hashed_password_here', 'manager'),
('staff1', 'staff@example.com', 'hashed_password_here', 'staff');
```

### Categories Table Example
```sql
INSERT INTO categories (name, description) VALUES
('Electronics', 'Electronic devices and accessories'),
('Clothing', 'Apparel and fashion items'),
('Books', 'Printed and digital books');
```

### Products Table Example
```sql
INSERT INTO products (name, description, price, stock, category_id) VALUES
('Laptop', 'High-performance laptop', 999.99, 50, 1),
('T-Shirt', 'Cotton t-shirt', 19.99, 100, 2),
('Novel', 'Fiction novel', 14.99, 25, 3);
```

## Database Migration

The application uses Flask-Migrate for database schema management:

- **Migration Location**: `migrations/` directory
- **Migration Commands**:
  - `flask db init` - Initialize migration repository
  - `flask db migrate -m "message"` - Create migration script
  - `flask db upgrade` - Apply migrations to database
  - `flask db downgrade` - Revert last migration

## Performance Considerations

### Indexes
- Primary keys are automatically indexed
- Unique constraints create indexes
- Foreign key relationships are indexed for join performance

### Query Optimization
- Category queries benefit from unique name index
- User lookups optimized by username/email indexes
- Product-category joins optimized by foreign key index

## Security Considerations

### Data Protection
- Passwords are never stored in plain text
- Password hashing uses Werkzeug security functions
- User roles are enforced at application level

### Access Control
- Database access controlled by application layer
- No direct database access for end users
- Role-based permissions implemented in API layer

## Backup and Recovery

### Recommended Backup Strategy
- Regular full database backups
- Transaction log backups for point-in-time recovery
- Test backup restoration procedures

### Critical Data
- User authentication data (users table)
- Product inventory (products table)
- Category structure (categories table)

## Future Enhancements

### Potential Schema Extensions
- **Audit Trail**: Add created_at, updated_at timestamps
- **Product Images**: Add product_image_url field
- **Suppliers**: Add suppliers table with product relationships
- **Orders**: Add orders and order_items tables for sales tracking
- **Inventory History**: Track stock movement history

### Performance Improvements
- Add composite indexes for common query patterns
- Implement database partitioning for large product catalogs
- Add read replicas for improved query performance
