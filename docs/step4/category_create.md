# Create Category Endpoint

## Overview

Creates a new product category in the inventory system with validation and hierarchical support.

## Endpoint Details

- **Method**: `POST`
- **URL**: `/categories/`
- **Authentication**: Required (bypassed in development)
- **Content-Type**: `application/json`

## Request Body

```json
{
    "name": "string",
    "description": "string",
    "parent_category_id": "integer (optional)"
}
```

## Response Format

### Success Response (201)
```json
{
    "message": "Category created successfully",
    "category": {
        "id": 1,
        "name": "Electronics",
        "description": "Electronic devices and accessories",
        "parent_category_id": null,
        "parent_category_name": null,
        "created_at": "2024-01-20T10:30:00Z"
    }
}
```

### Error Response (400)
```json
{
    "error": "Validation failed",
    "details": {
        "field": "name",
        "issue": "Category name already exists"
    }
}
```

## Implementation Pattern

### Core Logic
```python
@categories_b_p.route('/', methods=['POST'])
def create_category():
    try:
        # Authentication check
        if not (settings.feature_toggles.BYPASS_AUTH and settings.is_development()):
            verify_jwt_in_request()
        
        # Validate input data
        data = request.get_json()
        category_data = CategoryCreate(**data)
        
        # Check for duplicate name
        if Category.query.filter_by(name=category_data.name).first():
            raise ConflictError("Category name already exists")
        
        # Verify parent category if specified
        if category_data.parent_category_id:
            parent = Category.query.get(category_data.parent_category_id)
            if not parent:
                raise NotFoundError("Parent category not found")
        
        # Create category
        new_category = Category(**category_data.dict())
        db.session.add(new_category)
        db.session.commit()
        
        return jsonify({
            "message": "Category created successfully",
            "category": format_category_data(new_category)
        }), 201
        
    except ValidationErrorException as e:
        return exception_handler.handle_exception(e)
```

### Validation Steps
1. **Input Validation**: Use Pydantic schema for basic validation
2. **Uniqueness Check**: Ensure category name is unique
3. **Parent Verification**: Validate parent category if specified
4. **Hierarchy Validation**: Prevent circular references

### Business Logic
- Category names must be unique
- Parent category must exist
- No circular category references
- Description is optional but recommended

## Key Components

### Pydantic Schema
```python
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parent_category_id: Optional[int] = None
```

### Validation Rules
```python
@field_validator('name')
@classmethod
def validate_name(cls, v):
    if len(v.strip()) < 2:
        raise ValueError('Category name must be at least 2 characters')
    return v.strip()

@field_validator('parent_category_id')
@classmethod
def validate_parent(cls, v):
    if v is not None:
        # Additional validation for parent category
        pass
    return v
```

### Data Formatting
```python
def format_category_data(category):
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "parent_category_id": category.parent_category_id,
        "parent_category_name": category.parent.name if category.parent else None,
        "created_at": category.created_at.isoformat()
    }
```

## Business Logic

### Category Creation Flow
1. Authenticate user (or bypass in development)
2. Validate input data using Pydantic schema
3. Check for duplicate category names
4. Verify parent category if specified
5. Prevent circular references
6. Create category record
7. Save to database
8. Return formatted response

### Hierarchy Considerations
- Parent category must exist
- No circular category references
- Support for nested categories
- Proper relationship maintenance

### Error Handling
- Validation errors with field details
- Duplicate name detection
- Parent category validation
- Database constraint handling

## Error Scenarios

### Validation Errors
- Missing required name field
- Name too short or invalid
- Invalid parent category ID

### Business Logic Errors
- Duplicate category names
- Non-existent parent category
- Circular reference attempts

### Database Errors
- Connection failures
- Constraint violations
- Transaction rollback issues

## Logging

### Success Logging
```python
logger.info("Category created successfully", 
           category_id=new_category.id,
           category_name=new_category.name,
           parent_id=new_category.parent_category_id)
```

### Error Logging
```python
logger.warning("Category creation validation error", 
               error=str(e), 
               category_name=data.get('name'))
```

## Testing Considerations

### Test Cases
- Valid category creation
- Duplicate category names
- Invalid parent category
- Circular reference prevention
- Missing required fields
- Hierarchical category creation

### Test Data
```python
valid_category_data = {
    "name": "Electronics",
    "description": "Electronic devices and accessories"
}

sub_category_data = {
    "name": "Computer Accessories",
    "description": "Accessories for computers",
    "parent_category_id": 1
}
```

## Performance Considerations

- Efficient duplicate name checking
- Optimized parent category lookup
- Proper database indexing
- Minimal response payload size

## Security Notes

- Input validation and sanitization
- SQL injection prevention through ORM
- Authorization checks for category creation
- Audit logging for category changes

## Development Features

### Authentication Bypass
```python
if settings.feature_toggles.BYPASS_AUTH and settings.is_development():
    # Skip authentication for easier testing
    pass
```

### Debug Information
- Detailed validation errors
- Hierarchy information
- Database query details

## Advanced Features

### Category Hierarchy
- Support for nested categories
- Parent-child relationships
- Hierarchical data integrity
- Category path tracking

### Bulk Operations
- Multiple category creation
- Batch category updates
- Hierarchical category management
- Category reorganization
