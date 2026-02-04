# GET /products/

## Overview
Retrieve a list of all products in the inventory with optional filtering, sorting, and pagination capabilities.

## Authentication
JWT token required for all authenticated users.

## Request Headers
| Header | Value | Description |
|--------|-------|-------------|
| Authorization | Bearer {token} | JWT access token |

## Query Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page | integer | No | 1 | Page number for pagination |
| per_page | integer | No | 20 | Items per page (max 100) |
| category_id | integer | No | - | Filter by category ID |
| min_price | number | No | - | Filter by minimum price |
| max_price | number | No | - | Filter by maximum price |
| search | string | No | - | Search by product name or description |
| sort_by | string | No | created_at | Sort field (name, price, created_at, stock_quantity) |
| sort_order | string | No | desc | Sort order (asc, desc) |
| in_stock | boolean | No | - | Filter by stock availability (true/false) |

## Response Codes
| Code | Description |
|------|-------------|
| 200 | Products retrieved successfully |
| 401 | Authentication token missing or invalid |
| 400 | Invalid query parameters |
| 500 | Server error during retrieval |

## Success Response (200)
```json
[
  {
    "id": 1,
    "name": "Wireless Mouse",
    "description": "Ergonomic wireless mouse with USB receiver",
    "price": 29.99,
    "stock_quantity": 100,
    "category_id": 1,
    "category_name": "Electronics",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "in_stock": true,
    "discount_percentage": 0
  },
  {
    "id": 2,
    "name": "USB Keyboard",
    "description": "Mechanical keyboard with RGB backlighting",
    "price": 79.99,
    "stock_quantity": 0,
    "category_id": 1,
    "category_name": "Electronics",
    "created_at": "2024-01-14T09:15:00Z",
    "updated_at": "2024-01-15T08:30:00Z",
    "in_stock": false,
    "discount_percentage": 10
  }
]
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

### Invalid Parameters (400)
```json
{
  "message": "Invalid query parameters",
  "status_code": 400,
  "error_code": "VALIDATION_ERROR",
  "details": {
    "min_price": "Must be a positive number",
    "per_page": "Must be between 1 and 100"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Business Logic
1. **Token Validation**: Verifies JWT token is valid and not expired
2. **User Authentication**: Extracts user identity from token
3. **Parameter Validation**: Validates all query parameters
4. **Query Building**: Constructs database query with filters
5. **Filtering**: Applies category, price, search, and stock filters
6. **Sorting**: Applies sorting based on specified field and order
7. **Pagination**: Implements pagination for large result sets
8. **Data Formatting**: Returns products in consistent format
9. **Audit Logging**: Logs access attempt and result

## Filtering Options

### Category Filtering
```
GET /products/?category_id=1
```
Returns products only from the specified category.

### Price Range Filtering
```
GET /products/?min_price=10&max_price=100
```
Returns products within the specified price range.

### Search Filtering
```
GET /products/?search=wireless
```
Returns products with "wireless" in name or description.

### Stock Availability Filtering
```
GET /products/?in_stock=true
```
Returns products that are currently in stock.

### Combined Filtering
```
GET /products/?category_id=1&min_price=20&in_stock=true
```
Applies multiple filters simultaneously.

## Sorting Options

### Sort Fields
- `name`: Sort by product name
- `price`: Sort by price
- `created_at`: Sort by creation date (default)
- `stock_quantity`: Sort by stock quantity
- `updated_at`: Sort by last update date

### Sort Orders
- `asc`: Ascending order
- `desc`: Descending order (default)

### Sorting Examples
```
GET /products/?sort_by=price&sort_order=asc
GET /products/?sort_by=name&sort_order=desc
GET /products/?sort_by=stock_quantity&sort_order=desc
```

## Pagination
- **Default Page**: 1
- **Default Per Page**: 20
- **Maximum Per Page**: 100
- **Page Numbers**: Start from 1

### Pagination Headers
```
X-Total-Count: 150
X-Page: 1
X-Per-Page: 20
X-Total-Pages: 8
X-Has-Next: true
X-Has-Previous: false
```

## Security Considerations
- **Authentication Required**: All users must be authenticated
- **Input Validation**: All query parameters are validated
- **Data Filtering**: Sensitive data is excluded from response
- **Access Logging**: All access attempts are logged
- **Rate Limiting**: Prevents excessive database queries

## Logging Scenarios
- **Success**: Product list retrieval with filtering parameters
- **Authentication**: Authentication success/failure
- **Access Patterns**: User access patterns and preferences
- **Performance**: Slow query performance logging

## Rate Limiting
Recommended: 200 requests per minute per authenticated user.

## Examples

### Basic Product List
```bash
curl -H "Authorization: Bearer {token}" \
     http://localhost:5000/products/
```

### With Pagination
```bash
curl -H "Authorization: Bearer {token}" \
     "http://localhost:5000/products/?page=2&per_page=10"
```

### Filter by Category
```bash
curl -H "Authorization: Bearer {token}" \
     "http://localhost:5000/products/?category_id=1"
```

### Filter by Price Range
```bash
curl -H "Authorization: Bearer {token}" \
     "http://localhost:5000/products/?min_price=50&max_price=200"
```

### Search Products
```bash
curl -H "Authorization: Bearer {token}" \
     "http://localhost:5000/products/?search=wireless"
```

### Sort by Price
```bash
curl -H "Authorization: Bearer {token}" \
     "http://localhost:5000/products/?sort_by=price&sort_order=asc"
```

### In Stock Only
```bash
curl -H "Authorization: Bearer {token}" \
     "http://localhost:5000/products/?in_stock=true"
```

### Complex Query
```bash
curl -H "Authorization: Bearer {token}" \
     "http://localhost:5000/products/?category_id=1&min_price=20&max_price=100&in_stock=true&sort_by=price&sort_order=asc&page=1&per_page=10"
```

## Response Headers
```
X-Total-Count: 150
X-Page: 1
X-Per-Page: 20
X-Total-Pages: 8
X-Filter-Applied: category_id,min_price
X-Sort-Applied: price,asc
X-Timestamp: 2024-01-15T10:30:00Z
```

## Performance Considerations
- **Database Indexing**: Category ID, price, name fields should be indexed
- **Query Optimization**: Efficient database queries with proper joins
- **Caching**: Consider caching frequent queries
- **Pagination**: Essential for large product databases
- **Full-Text Search**: Consider search indexing for better performance

## Error Handling
- **Parameter Validation**: Clear error messages for invalid parameters
- **Authentication**: Proper 401 responses for authentication issues
- **Database Errors**: Generic error for database issues
- **Performance**: Timeout handling for slow queries

## Integration Considerations
- **E-commerce Integration**: Product catalog for online stores
- **Inventory Systems**: Real-time inventory data
- **Search Systems**: Integration with search engines
- **Analytics**: Product performance analytics
- **Reporting**: Sales and inventory reporting

## Use Cases
- **Product Catalog**: Displaying products to users
- **Inventory Management**: Managing stock levels
- **Product Search**: Finding specific products
- **Price Comparison**: Comparing product prices
- **Stock Analysis**: Analyzing stock availability

## Security Best Practices
- **Access Control**: Ensure proper authentication
- **Input Validation**: Validate all query parameters
- **Data Protection**: Filter sensitive business data
- **Performance Monitoring**: Monitor query performance
- **Access Logging**: Track product access patterns

## Testing Considerations
- **Basic Retrieval**: Test basic product listing
- **Filtering**: Test all filter combinations
- **Sorting**: Test all sorting options
- **Pagination**: Test pagination edge cases
- **Performance**: Test with large datasets

## Deprecation Notice
None currently planned. Consider versioning for future changes.

## Alternative Endpoints
- `GET /products/{product_id}` - Get specific product
- `POST /products/` - Create new product
- `PUT /products/{product_id}` - Update product
- `DELETE /products/{product_id}` - Delete product
