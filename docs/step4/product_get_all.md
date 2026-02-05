# Get All Products Endpoint

## Overview

Retrieves a list of all products in the inventory with optional filtering and pagination support.

## Endpoint Details

- **Method**: `GET`
- **URL**: `/products/`
- **Authentication**: Required (bypassed in development)
- **Content-Type**: `application/json`

## Query Parameters (Optional)

```json
{
    "category_id": "integer",
    "min_price": "number",
    "max_price": "number",
    "in_stock": "boolean",
    "page": "integer",
    "per_page": "integer"
}
```

## Response Format

### Success Response (200)
```json
{
    "products": [
        {
            "id": 1,
            "name": "Wireless Mouse",
            "description": "Ergonomic wireless mouse",
            "price": 29.99,
            "stock_quantity": 100,
            "category_id": 1,
            "category_name": "Electronics",
            "created_at": "2024-01-20T10:30:00Z"
        }
    ],
    "pagination": {
        "page": 1,
        "per_page": 20,
        "total": 1,
        "pages": 1
    },
    "filters_applied": {
        "category_id": null,
        "min_price": null,
        "max_price": null,
        "in_stock": null
    }
}
```

### Error Response (401)
```json
{
    "error": "Authentication required",
    "message": "Valid JWT token required"
}
```

## Implementation Pattern

### Core Logic
```python
@products_b_p.route('/', methods=['GET'])
def get_all_products():
    try:
        # Authentication check
        if not (settings.feature_toggles.BYPASS_AUTH and settings.is_development()):
            verify_jwt_in_request()
        
        # Build query with filters
        query = Product.query
        
        # Apply filters if provided
        if request.args.get('category_id'):
            query = query.filter(Product.category_id == request.args.get('category_id'))
        
        if request.args.get('min_price'):
            query = query.filter(Product.price >= float(request.args.get('min_price')))
        
        if request.args.get('max_price'):
            query = query.filter(Product.price <= float(request.args.get('max_price')))
        
        if request.args.get('in_stock') == 'true':
            query = query.filter(Product.stock_quantity > 0)
        
        # Pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        pagination = query.paginate(page=page, per_page=per_page)
        
        # Format response
        products = [format_product_with_category(p) for p in pagination.items]
        
        return jsonify({
            "products": products,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "pages": pagination.pages
            },
            "filters_applied": get_applied_filters()
        }), 200
        
    except Exception as e:
        logger.error("Failed to retrieve products", error=str(e))
        return jsonify({"error": "Failed to retrieve products"}), 500
```

### Query Building
1. **Base Query**: Start with Product query
2. **Filter Application**: Apply optional filters
3. **Pagination**: Apply pagination parameters
4. **Data Formatting**: Format products with category info
5. **Response Assembly**: Build complete response structure

### Filtering Logic
- **Category Filter**: Filter by specific category
- **Price Range**: Filter by minimum and maximum price
- **Stock Filter**: Filter by stock availability
- **Pagination**: Control page size and number

## Key Components

### Filter Application
```python
def apply_filters(query, args):
    if args.get('category_id'):
        query = query.filter(Product.category_id == args.get('category_id'))
    
    if args.get('min_price'):
        query = query.filter(Product.price >= float(args.get('min_price')))
    
    if args.get('max_price'):
        query = query.filter(Product.price <= float(args.get('max_price')))
    
    if args.get('in_stock') == 'true':
        query = query.filter(Product.stock_quantity > 0)
    
    return query
```

### Data Formatting
```python
def format_product_with_category(product):
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": float(product.price),
        "stock_quantity": product.stock_quantity,
        "category_id": product.category_id,
        "category_name": product.category.name if product.category else None,
        "created_at": product.created_at.isoformat()
    }
```

### Pagination
```python
page = int(request.args.get('page', 1))
per_page = min(int(request.args.get('per_page', 20)), 100)  # Max 100 per page
pagination = query.paginate(page=page, per_page=per_page)
```

## Business Logic

### Product Retrieval Process
1. Authenticate user (or bypass in development)
2. Build base query
3. Apply optional filters
4. Apply pagination
5. Execute query
6. Format product data with category information
7. Return paginated response

### Filter Validation
- Validate numeric parameters
- Ensure reasonable pagination limits
- Handle invalid filter values gracefully
- Provide filter feedback in response

### Performance Considerations
- Efficient query building
- Proper database indexing
- Reasonable pagination limits
- Optimized data formatting

## Error Scenarios

### Authentication Errors
- Missing or invalid JWT token
- Expired tokens
- Permission issues

### Validation Errors
- Invalid numeric parameters
- Negative page numbers
- Excessive per_page values

### Database Errors
- Connection failures
- Query execution errors
- Data formatting issues

## Logging

### Success Logging
```python
logger.info("Products retrieved successfully", 
           user_id=get_jwt_identity(),
           product_count=len(products),
           filters_applied=get_applied_filters())
```

### Error Logging
```python
logger.error("Failed to retrieve products", 
           error=str(e),
           user_id=get_jwt_identity())
```

## Testing Considerations

### Test Cases
- Basic product retrieval
- Category filtering
- Price range filtering
- Stock availability filtering
- Pagination functionality
- Empty result handling

### Test Data
```python
# Test filtering
response = client.get('/products/?category_id=1&min_price=10&max_price=50')

# Test pagination
response = client.get('/products/?page=1&per_page=10')
```

## Performance Considerations

- Database query optimization
- Efficient filter application
- Proper indexing on filter fields
- Reasonable pagination limits
- Connection pooling utilization

## Security Notes

- Input validation for all parameters
- SQL injection prevention through ORM
- Authorization checks for product access
- Rate limiting consideration

## Development Features

### Authentication Bypass
```python
if settings.feature_toggles.BYPASS_AUTH and settings.is_development():
    # Skip authentication for easier testing
    pass
```

### Debug Information
- Query information in development
- Filter application details
- Performance metrics
- Detailed error messages
