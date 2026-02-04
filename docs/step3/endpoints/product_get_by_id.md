# GET /products/{product_id}

## Overview
Retrieve detailed information about a specific product by its unique identifier.

## Authentication
JWT token required for all authenticated users.

## Request Headers
| Header | Value | Description |
|--------|-------|-------------|
| Authorization | Bearer {token} | JWT access token |

## URL Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| product_id | integer | Yes | Unique identifier of the product to retrieve |

## Query Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| include_category | boolean | No | false | Include full category details |
| include_discount | boolean | No | true | Include discount information |

## Response Codes
| Code | Description |
|------|-------------|
| 200 | Product retrieved successfully |
| 401 | Authentication token missing or invalid |
| 404 | Product not found |
| 500 | Server error during retrieval |

## Success Response (200)
```json
{
  "id": 1,
  "name": "Wireless Mouse",
  "description": "Ergonomic wireless mouse with USB receiver, 2.4GHz connectivity, and adjustable DPI settings",
  "price": 29.99,
  "stock_quantity": 100,
  "category_id": 1,
  "category_name": "Electronics",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "in_stock": true,
  "discount_percentage": 0,
  "discounted_price": 29.99,
  "sku": "WM-001",
  "weight": 0.5,
  "dimensions": {
    "length": 10.5,
    "width": 6.5,
    "height": 3.8
  },
  "tags": ["wireless", "ergonomic", "usb"],
  "rating": 4.5,
  "review_count": 127
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

### Not Found (404)
```json
{
  "message": "Product not found",
  "status_code": 404,
  "error_code": "NOT_FOUND",
  "details": {
    "product_id": 999,
    "search_criteria": "id"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Business Logic
1. **Token Validation**: Verifies JWT token is valid and not expired
2. **User Authentication**: Extracts user identity from token
3. **Product Lookup**: Retrieves product by ID from database
4. **Category Association**: Includes category information
5. **Discount Calculation**: Calculates discounted price if applicable
6. **Stock Status**: Determines stock availability status
7. **Data Formatting**: Returns product in consistent format
8. **Audit Logging**: Logs product access for analytics

## Product Data Fields

### Basic Information
- **id**: Unique product identifier
- **name**: Product name
- **description**: Detailed product description
- **sku**: Stock keeping unit (optional)
- **tags**: Product tags for search and categorization

### Pricing
- **price**: Current product price
- **discount_percentage**: Current discount percentage
- **discounted_price**: Price after discount calculation

### Inventory
- **stock_quantity**: Current stock level
- **in_stock**: Boolean stock availability status
- **weight**: Product weight in kg (optional)
- **dimensions**: Product dimensions (optional)

### Relationships
- **category_id**: Associated category ID
- **category_name**: Category name for display

### Metadata
- **created_at**: Product creation timestamp
- **updated_at**: Last update timestamp
- **rating**: Average customer rating (optional)
- **review_count**: Number of customer reviews (optional)

## Query Options

### Include Category Details
```
GET /products/1?include_category=true
```
Returns full category object instead of just category name.

### Include/Exclude Discount
```
GET /products/1?include_discount=false
```
Excludes discount information from response.

## Security Considerations
- **Authentication Required**: All users must be authenticated
- **Input Validation**: Product ID parameter is validated
- **Data Filtering**: Sensitive business data may be filtered
- **Access Logging**: Product access is logged for analytics
- **Rate Limiting**: Prevents excessive individual product requests

## Logging Scenarios
- **Success**: Product retrieval with user ID and product ID
- **Not Found**: Requests for non-existent products
- **Authentication**: Authentication success/failure
- **Access Patterns**: Popular product access tracking

## Rate Limiting
Recommended: 300 requests per minute per authenticated user.

## Examples

### Basic Product Retrieval
```bash
curl -H "Authorization: Bearer {token}" \
     http://localhost:5000/products/1
```

### With Category Details
```bash
curl -H "Authorization: Bearer {token}" \
     "http://localhost:5000/products/1?include_category=true"
```

### Without Discount Information
```bash
curl -H "Authorization: Bearer {token}" \
     "http://localhost:5000/products/1?include_discount=false"
```

### Non-existent Product
```bash
curl -H "Authorization: Bearer {token}" \
     http://localhost:5000/products/999
# Returns 404 Not Found
```

### Unauthorized Access
```bash
curl http://localhost:5000/products/1
# Returns 401 Unauthorized
```

## Response Headers
```
X-Product-ID: 1
X-Category-ID: 1
X-In-Stock: true
X-Discount-Available: false
X-Timestamp: 2024-01-15T10:30:00Z
```

## Performance Considerations
- **Database Indexing**: Product ID should be indexed
- **Caching**: Consider caching frequently accessed products
- **Query Optimization**: Efficient single-record queries
- **Category Loading**: Optimize category relationship loading
- **Response Size**: Consider response size for mobile clients

## Error Handling
- **Invalid Product ID**: Returns 404 for non-existent products
- **Authentication Issues**: Proper 401 responses for authentication problems
- **Database Errors**: Generic 500 error for database issues
- **Parameter Validation**: Validation errors for invalid parameters

## Integration Considerations
- **E-commerce**: Product detail pages for online stores
- **Inventory Systems**: Real-time product information
- **Mobile Apps**: Product information for mobile applications
- **Analytics**: Product view tracking and analytics
- **Search Systems**: Product information for search results

## Use Cases
- **Product Details**: Displaying detailed product information
- **Inventory Check**: Checking product availability
- **Price Lookup**: Retrieving current pricing information
- **Product Catalog**: Building product catalogs
- **Mobile Apps**: Product information for mobile applications

## Security Best Practices
- **Access Control**: Ensure proper authentication
- **Input Validation**: Validate product ID parameter
- **Data Protection**: Filter sensitive business data
- **Performance Monitoring**: Monitor popular product access
- **Access Logging**: Track product access patterns

## Testing Considerations
- **Valid Products**: Test retrieval of existing products
- **Non-existent Products**: Test 404 responses
- **Authentication**: Test with and without authentication
- **Query Options**: Test all query parameter combinations
- **Performance**: Test response times for large product data

## Deprecation Notice
None currently planned. Consider versioning for future changes.

## Alternative Endpoints
- `GET /products/` - List all products with filtering
- `POST /products/` - Create new product
- `PUT /products/{product_id}` - Update product information
- `DELETE /products/{product_id}` - Delete product
- `POST /products/{product_id}/discount` - Apply discount to product
