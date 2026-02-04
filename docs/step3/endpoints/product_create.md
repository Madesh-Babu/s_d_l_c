# POST /products/

## Overview
Create a new product in the inventory system with validation and category association.

## Authentication
JWT token required with admin or manager role privileges.

## Request Headers
| Header | Value | Description |
|--------|-------|-------------|
| Authorization | Bearer {token} | JWT access token with admin/manager role |
| Content-Type | application/json | Request content type |

## Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Product name (minimum 2 characters) |
| description | string | No | Product description |
| price | number | Yes | Product price (must be greater than 0) |
| stock_quantity | number | Yes | Stock quantity (must be 0 or greater) |
| category_id | integer | Yes | Category ID (must exist) |

## Response Codes
| Code | Description |
|------|-------------|
| 201 | Product created successfully |
| 401 | Authentication token missing or invalid |
| 403 | User lacks required permissions |
| 400 | Validation errors for input data |
| 404 | Category not found |
| 409 | Product name already exists in category |
| 500 | Server error during creation |

## Success Response (201)
```json
{
  "message": "Product added",
  "product": {
    "id": 1,
    "name": "Wireless Mouse",
    "description": "Ergonomic wireless mouse with USB receiver",
    "price": 29.99,
    "stock_quantity": 100,
    "category_id": 1,
    "category_name": "Electronics",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "created_by": {
    "id": 2,
    "username": "admin_user",
    "role": "admin"
  }
}
```

## Error Responses

### Unauthorized (401)
```json
{
  "message": "Authentication token is required",
  "status_code": 401,
  "error_code": "AUTHENTICATION_ERROR",
  "details": {
    "reason": "token_missing"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Forbidden (403)
```json
{
  "message": "Admin or manager access required",
  "status_code": 403,
  "error_code": "AUTHORIZATION_ERROR",
  "details": {
    "user_role": "staff",
    "required_roles": ["admin", "manager"]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Validation Error (400)
```json
{
  "message": "Validation failed",
  "status_code": 400,
  "error_code": "VALIDATION_ERROR",
  "details": {
    "name": "Product name must be at least 2 characters",
    "price": "Price must be greater than 0",
    "stock_quantity": "Stock quantity cannot be negative"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Category Not Found (404)
```json
{
  "message": "Category not found",
  "status_code": 404,
  "error_code": "NOT_FOUND",
  "details": {
    "category_id": 999,
    "search_criteria": "id"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Conflict Error (409)
```json
{
  "message": "Product with this name already exists in this category",
  "status_code": 409,
  "error_code": "CONFLICT",
  "details": {
    "product_name": "Wireless Mouse",
    "category_id": 1,
    "existing_product_id": 5
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Business Logic
1. **Token Validation**: Verifies JWT token is valid and not expired
2. **User Authentication**: Extracts user identity from token
3. **Permission Check**: Validates user has admin or manager role
4. **Input Validation**: Validates all required fields and data types
5. **Category Validation**: Checks if category exists in database
6. **Business Rule Validation**: Validates price and stock constraints
7. **Duplicate Checking**: Checks for duplicate product names in category
8. **Product Creation**: Creates product record in database
9. **Audit Logging**: Logs product creation with user details

## Validation Rules
- **Name**: Minimum 2 characters, maximum 255 characters
- **Price**: Must be greater than 0, maximum 10 digits with 2 decimal places
- **Stock Quantity**: Must be 0 or greater, maximum 1,000,000
- **Category ID**: Must reference existing category
- **Description**: Optional, maximum 1000 characters

## Business Rules
- **Positive Pricing**: Products cannot have zero or negative prices
- **Non-negative Stock**: Stock quantity cannot be negative
- **Category Association**: Products must belong to a valid category
- **Name Uniqueness**: Product names must be unique within a category
- **Permission Control**: Only admins and managers can create products

## Security Considerations
- **Permission Enforcement**: Strict access control based on user role
- **Input Validation**: All input data is validated and sanitized
- **Category Validation**: Ensures data integrity with category relationships
- **Audit Trail**: All product creations are logged with user details
- **Data Integrity**: Prevents duplicate products in categories

## Logging Scenarios
- **Success**: Product creation with product details and creator
- **Permission Denied**: Unauthorized creation attempts
- **Validation Errors**: Input validation failures
- **Category Issues**: Invalid category references
- **Duplicate Prevention**: Attempts to create duplicate products

## Rate Limiting
Recommended: 50 requests per minute per authenticated user.

## Examples

### Successful Product Creation
```bash
curl -X POST \
     -H "Authorization: Bearer {admin_token}" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Wireless Mouse",
       "description": "Ergonomic wireless mouse with USB receiver",
       "price": 29.99,
       "stock_quantity": 100,
       "category_id": 1
     }' \
     http://localhost:5000/products/
```

### Manager Creating Product
```bash
curl -X POST \
     -H "Authorization: Bearer {manager_token}" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "USB Keyboard",
       "description": "Mechanical keyboard with RGB backlighting",
       "price": 79.99,
       "stock_quantity": 50,
       "category_id": 1
     }' \
     http://localhost:5000/products/
```

### Unauthorized Creation (Staff)
```bash
curl -X POST \
     -H "Authorization: Bearer {staff_token}" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Monitor",
       "price": 199.99,
       "stock_quantity": 25,
       "category_id": 1
     }' \
     http://localhost:5000/products/
# Returns 403 Forbidden
```

### Invalid Price
```bash
curl -X POST \
     -H "Authorization: Bearer {admin_token}" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Invalid Product",
       "price": -10,
       "stock_quantity": 100,
       "category_id": 1
     }' \
     http://localhost:5000/products/
# Returns 400 Validation Error
```

### Non-existent Category
```bash
curl -X POST \
     -H "Authorization: Bearer {admin_token}" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Orphan Product",
       "price": 49.99,
       "stock_quantity": 100,
       "category_id": 999
     }' \
     http://localhost:5000/products/
# Returns 404 Category Not Found
```

## Response Headers
```
X-Product-ID: 1
X-Created-By: 2
X-Category-ID: 1
X-Timestamp: 2024-01-15T10:30:00Z
```

## Performance Considerations
- **Database Indexing**: Category ID and product name should be indexed
- **Transaction Management**: Use transactions for data integrity
- **Duplicate Checking**: Efficient queries for duplicate detection
- **Audit Logging**: Asynchronous logging to prevent delays

## Error Handling
- **Input Validation**: Detailed validation error messages
- **Permission Errors**: Clear error messages for insufficient permissions
- **Category Validation**: Specific error for invalid categories
- **Database Errors**: Generic error for database issues
- **Conflict Errors**: Detailed information about duplicates

## Integration Considerations
- **Inventory Management**: Integration with inventory tracking systems
- **Category Management**: Integration with category management
- **Audit Systems**: Feed creation events to audit logging
- **Reporting Systems**: Integration with sales and reporting systems

## Use Cases
- **Product Addition**: Adding new products to inventory
- **Stock Management**: Initial stock entry for new products
- **Category Organization**: Organizing products by categories
- **Price Management**: Setting initial product prices

## Security Best Practices
- **Regular Audits**: Review product creation logs
- **Permission Validation**: Always validate user permissions
- **Input Sanitization**: Validate and sanitize all input data
- **Data Integrity**: Maintain referential integrity
- **Change Tracking**: Track product creation and modifications

## Testing Considerations
- **Admin Creation**: Test admin product creation
- **Manager Creation**: Test manager product creation
- **Unauthorized Access**: Test permission enforcement
- **Validation Testing**: Test all validation rules
- **Duplicate Prevention**: Test duplicate detection

## Deprecation Notice
None currently planned. Consider versioning for future changes.

## Alternative Endpoints
- `GET /products/` - List all products
- `GET /products/{product_id}` - Get specific product
- `PUT /products/{product_id}` - Update product information
- `DELETE /products/{product_id}` - Delete product
