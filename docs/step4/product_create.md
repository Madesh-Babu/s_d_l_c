# Create Product Endpoint

## Overview

Creates a new product in the inventory system with validation, category association, and business logic.

## Endpoint Details

- **Method**: `POST`
- **URL**: `/products/`
- **Authentication**: Required (bypassed in development)
- **Content-Type**: `application/json`

## Request Body

```json
{
    "name": "string",
    "description": "string",
    "price": "number",
    "stock_quantity": "integer",
    "category_id": "integer"
}
```

## Response Format

### Success Response (201)
```json
{
    "message": "Product created successfully",
    "product": {
        "id": 1,
        "name": "Wireless Mouse",
        "description": "Ergonomic wireless mouse",
        "price": 29.99,
        "stock_quantity": 100,
        "category_id": 1,
        "created_at": "2024-01-20T10:30:00Z"
    }
}
```

### Error Response (400)
```json
{
    "error": "Validation failed",
    "details": {
        "field": "price",
        "issue": "Price must be positive"
    }
}
```

## Implementation Pattern

### Core Logic
```python
@products_b_p.route('/', methods=['POST'])
def create_product():
    try:
        # Authentication check
        if not (settings.feature_toggles.BYPASS_AUTH and settings.is_development()):
            verify_jwt_in_request()
        
        # Validate input data
        data = request.get_json()
        product_data = ProductCreate(**data)
        
        # Verify category exists
        category = Category.query.get(product_data.category_id)
        if not category:
            raise NotFoundError("Category not found")
        
        # Create product
        new_product = Product(**product_data.dict())
        db.session.add(new_product)
        db.session.commit()
        
        return jsonify({
            "message": "Product created successfully",
            "product": format_product_data(new_product)
        }), 201
        
    except ValidationErrorException as e:
        return exception_handler.handle_exception(e)
```

### Validation Steps
1. **Input Validation**: Use Pydantic schema for basic validation
2. **Category Verification**: Ensure category exists
3. **Business Rules**: Validate price, stock, and other constraints
4. **Data Integrity**: Check relationships and constraints

### Business Logic
- Price must be positive
- Stock quantity cannot be negative
- Category must exist
- Product name must be unique within category

## Key Components

### Pydantic Schema
```python
class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock_quantity: int
    category_id: int
```

### Validation Rules
```python
@field_validator('price')
@classmethod
def validate_price(cls, v):
    if v <= 0:
        raise ValueError('Price must be positive')
    return v

@field_validator('stock_quantity')
@classmethod  
def validate_stock(cls, v):
    if v < 0:
        raise ValueError('Stock quantity cannot be negative')
    return v
```

### Data Formatting
```python
def format_product_data(product):
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": float(product.price),
        "stock_quantity": product.stock_quantity,
        "category_id": product.category_id,
        "created_at": product.created_at.isoformat()
    }
```

## Business Logic

### Product Creation Flow
1. Authenticate user (or bypass in development)
2. Validate input data using Pydantic schema
3. Verify category exists
4. Apply business rules and constraints
5. Create product record
6. Save to database
7. Return formatted response

### Validation Rules
- **Name**: Required, unique within category
- **Description**: Optional but recommended
- **Price**: Must be positive, reasonable limits
- **Stock**: Non-negative integer
- **Category**: Must exist and be active

### Error Handling
- Validation errors with field-specific details
- Category not found errors
- Database constraint violations
- Transaction rollback on failures

## Error Scenarios

### Validation Errors
- Missing required fields
- Invalid price values (negative, zero)
- Negative stock quantities
- Non-existent category ID

### Business Logic Errors
- Duplicate product names in category
- Category not found or inactive
- Invalid data types

### Database Errors
- Connection failures
- Constraint violations
- Transaction rollback issues

## Logging

### Success Logging
```python
logger.info("Product created successfully", 
           product_id=new_product.id,
           product_name=new_product.name,
           category_id=new_product.category_id)
```

### Error Logging
```python
logger.warning("Product creation validation error", 
               error=str(e), 
               product_name=data.get('name'))
```

## Testing Considerations

### Test Cases
- Valid product creation
- Missing required fields
- Invalid price values
- Negative stock quantities
- Non-existent category
- Duplicate product names

### Test Data
```python
valid_product_data = {
    "name": "Wireless Mouse",
    "description": "Ergonomic wireless mouse",
    "price": 29.99,
    "stock_quantity": 100,
    "category_id": 1
}
```

## Performance Considerations

- Efficient category lookup with indexing
- Optimized database transactions
- Proper connection pooling
- Minimal response payload size

## Security Notes

- Input validation and sanitization
- SQL injection prevention through ORM
- Authorization checks for product creation
- Audit logging for product changes

## Development Features

### Authentication Bypass
```python
if settings.feature_toggles.BYPASS_AUTH and settings.is_development():
    # Skip authentication for easier testing
    pass
```

### Debug Information
- Detailed validation errors
- Database query information
- Performance metrics in development mode
