# API Implementation Best Practices

## Overview

This document outlines the best practices and patterns used throughout the API implementation to ensure consistency, security, and maintainability.

## Core Patterns

### 1. Authentication Pattern

All protected endpoints follow this authentication pattern:

```python
@auth_b_p.route('/protected-endpoint', methods=['METHOD'])
def protected_endpoint():
    # Development bypass check
    if settings.feature_toggles.BYPASS_AUTH and settings.is_development():
        logger.info("Request bypassed in development")
        # Proceed with endpoint logic
    
    # Production authentication
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        # Continue with business logic
    except Exception as e:
        logger.error("Authentication failed", error=str(e))
        return jsonify({
            "error": "Authentication required",
            "message": "Valid JWT token required"
        }), 401
```

### 2. Error Handling Pattern

Consistent error handling across all endpoints:

```python
try:
    # Business logic here
    result = process_request(data)
    return jsonify({"message": "Success", "data": result}), 200
    
except ValidationErrorException as e:
    logger.warning("Validation error", error=str(e))
    return exception_handler.handle_exception(e)
    
except AuthenticationError as e:
    logger.warning("Authentication error", error=str(e))
    return exception_handler.handle_exception(e)
    
except DatabaseError as e:
    logger.error("Database error", error=str(e))
    return exception_handler.handle_exception(e)
    
except Exception as e:
    logger.error("Unexpected error", error=str(e), exc_info=True)
    return jsonify({"error": "Internal server error"}), 500
```

### 3. Input Validation Pattern

Standardized input validation using Pydantic:

```python
@auth_b_p.route('/endpoint', methods=['POST'])
def endpoint():
    try:
        # Validate input data
        data = request.get_json()
        if not data:
            raise ValidationErrorException("No data provided")
        
        # Use Pydantic schema for validation
        validated_data = DataSchema(**data)
        
        # Additional business validation
        validate_business_rules(validated_data)
        
        # Process validated data
        result = process_data(validated_data)
        
        return jsonify({"message": "Success", "data": result}), 200
        
    except ValidationError as e:
        raise ValidationErrorException(str(e))
```

## Response Standards

### Success Response Format

```python
# Creation success (201)
return jsonify({
    "message": "Resource created successfully",
    "resource": format_resource_data(resource)
}), 201

# Retrieval success (200)
return jsonify({
    "data": resource_list,
    "pagination": pagination_info,
    "filters_applied": applied_filters
}), 200

# Update success (200)
return jsonify({
    "message": "Resource updated successfully",
    "resource": format_resource_data(updated_resource)
}), 200

# Deletion success (204)
return '', 204
```

### Error Response Format

```python
# Validation error (400)
return jsonify({
    "error": "Validation failed",
    "details": {
        "field": "field_name",
        "issue": "Specific validation issue"
    }
}), 400

# Authentication error (401)
return jsonify({
    "error": "Authentication required",
    "message": "Valid JWT token required"
}), 401

# Authorization error (403)
return jsonify({
    "error": "Access denied",
    "message": "Insufficient permissions"
}), 403

# Not found error (404)
return jsonify({
    "error": "Resource not found",
    "message": "Requested resource does not exist"
}), 404
```

## Database Patterns

### Transaction Management

```python
def create_resource(data):
    try:
        # Create new resource
        new_resource = Resource(**data)
        db.session.add(new_resource)
        
        # Additional database operations
        related_data = create_related_data(new_resource)
        
        # Commit transaction
        db.session.commit()
        
        return new_resource
        
    except Exception as e:
        # Rollback on any error
        db.session.rollback()
        raise DatabaseError("Failed to create resource", details={"error": str(e)})
```

### Query Optimization

```python
# Efficient querying with relationships
def get_products_with_categories():
    return Product.query.options(
        joinedload(Product.category)
    ).all()

# Filtered queries
def get_filtered_products(filters):
    query = Product.query
    
    if filters.get('category_id'):
        query = query.filter(Product.category_id == filters['category_id'])
    
    if filters.get('min_price'):
        query = query.filter(Product.price >= filters['min_price'])
    
    return query.all()
```

## Security Patterns

### Input Sanitization

```python
# Use Pydantic for input validation
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        # Sanitize and validate username
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', v):
            raise ValueError('Invalid username format')
        return v.strip()
```

### SQL Injection Prevention

```python
# Use SQLAlchemy ORM (safe)
users = User.query.filter(User.email == email).all()

# Never use raw SQL with user input
# DANGEROUS: db.session.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

### Password Security

```python
# Secure password hashing
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(self, password):
    self.password_hash = generate_password_hash(password)

def check_password(self, password):
    return check_password_hash(self.password_hash, password)
```

## Logging Patterns

### Structured Logging

```python
logger.info("User action completed", 
           user_id=current_user_id,
           action="resource_created",
           resource_id=resource.id,
           ip_address=request.remote_addr)

logger.warning("Validation failed", 
           error=str(e),
           endpoint=request.endpoint,
           user_id=get_jwt_identity())

logger.error("Database operation failed", 
           error=str(e),
           operation="create_user",
           exc_info=True)
```

### Performance Logging

```python
import time

@auth_b_p.route('/endpoint', methods=['GET'])
def endpoint():
    start_time = time.time()
    
    try:
        # Endpoint logic
        result = process_request()
        
        execution_time = (time.time() - start_time) * 1000
        logger.info("Endpoint completed", 
                   execution_time_ms=execution_time,
                   result_count=len(result))
        
        return jsonify(result)
        
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        logger.error("Endpoint failed", 
                     execution_time_ms=execution_time,
                     error=str(e))
        raise
```

## Development Features

### Authentication Bypass

```python
def check_authentication():
    """Check if authentication can be bypassed in development."""
    if settings.feature_toggles.BYPASS_AUTH and settings.is_development():
        logger.info("Authentication bypassed in development")
        return True
    return False
```

### Debug Information

```python
def add_debug_info(response_data):
    """Add debug information in development mode."""
    if settings.is_development():
        response_data['debug'] = {
            "environment": settings.ENVIRONMENT,
            "feature_toggles": settings.feature_toggles.get_enabled_features(),
            "request_id": request.request_id if hasattr(request, 'request_id') else None
        }
    return response_data
```

## Testing Patterns

### Test Structure

```python
class TestEndpoint:
    def test_success_case(self, client, sample_data):
        """Test successful endpoint operation."""
        response = client.post('/endpoint', json=sample_data)
        assert response.status_code == 200
        assert 'data' in response.json
    
    def test_validation_error(self, client):
        """Test input validation."""
        response = client.post('/endpoint', json={})
        assert response.status_code == 400
        assert 'error' in response.json
    
    def test_authentication_required(self, client):
        """Test authentication requirement."""
        response = client.get('/protected-endpoint')
        assert response.status_code == 401
```

### Test Fixtures

```python
@pytest.fixture
def sample_product_data():
    return {
        "name": "Test Product",
        "description": "Test Description",
        "price": 29.99,
        "stock_quantity": 100,
        "category_id": 1
    }

@pytest.fixture
def auth_headers(client, admin_user):
    token = create_access_token(identity=str(admin_user.id))
    return {"Authorization": f"Bearer {token}"}
```

## Configuration Patterns

### Environment-Specific Behavior

```python
def get_endpoint_config():
    """Get endpoint configuration based on environment."""
    config = {
        "enable_debug": settings.is_development(),
        "enable_caching": not settings.is_testing(),
        "rate_limit": settings.feature_toggles.ENABLE_RATE_LIMITING
    }
    return config
```

### Feature Toggle Integration

```python
@auth_b_p.route('/feature-endpoint', methods=['GET'])
def feature_endpoint():
    if not settings.feature_toggles.ENABLE_NEW_FEATURE:
        return jsonify({
            "error": "Feature not available",
            "message": "This feature is currently disabled"
        }), 403
    
    # Proceed with feature logic
    return jsonify({"message": "Feature is active"})
```

## Performance Patterns

### Caching Strategy

```python
from flask_caching import cache

@cache.memoize(timeout=300)  # Cache for 5 minutes
def get_expensive_data():
    # Expensive database query or computation
    return complex_calculation()

@auth_b_p.route('/cached-endpoint', methods=['GET'])
def cached_endpoint():
    data = get_expensive_data()
    return jsonify(data)
```

### Pagination

```python
def get_paginated_results(query, page=1, per_page=20):
    """Get paginated results from query."""
    per_page = min(per_page, 100)  # Max 100 per page
    pagination = query.paginate(page=page, per_page=per_page)
    
    return {
        "data": [format_item(item) for item in pagination.items],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        }
    }
```

## Conclusion

These patterns ensure consistency across the API implementation while maintaining security, performance, and maintainability. Following these standards helps in:

- **Consistency**: Uniform behavior across all endpoints
- **Security**: Proper authentication and input validation
- **Maintainability**: Clear, predictable code structure
- **Testability**: Standardized testing approaches
- **Performance**: Optimized database and response handling
- **Development Experience**: Helpful debugging and bypass features

Each endpoint implementation should follow these patterns while adapting to specific business requirements.
