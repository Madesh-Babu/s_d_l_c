# Get All Users Endpoint

## Overview

Retrieves a list of all users in the system. This endpoint supports authentication bypass in development mode.

## Endpoint Details

- **Method**: `GET`
- **URL**: `/auth/users`
- **Authentication**: Required (bypassed in development)
- **Content-Type**: `application/json`

## Response Format

### Success Response (200) - Development Mode
```json
{
    "users": [
        {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com"
        },
        {
            "id": 2,
            "username": "staff",
            "email": "staff@example.com"
        }
    ],
    "auth_bypassed": true,
    "message": "Authentication bypassed in development"
}
```

### Success Response (200) - Production Mode
```json
{
    "users": [
        {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com"
        }
    ]
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
@auth_b_p.route("/users", methods=['GET'])
def get_all_users():
    # Development bypass check
    if settings.feature_toggles.BYPASS_AUTH and settings.is_development():
        logger.info("Get all users request (BYPASSED)")
        users = User.query.all()
        user_list = [{"id": user.id, "username": user.username, "email": user.email} 
                     for user in users]
        return jsonify({
            "users": user_list,
            "auth_bypassed": True,
            "message": "Authentication bypassed in development"
        }), 200
    
    # Production authentication
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        users = User.query.all()
        user_list = [{"id": user.id, "username": user.username, "email": user.email} 
                     for user in users]
        return jsonify(user_list), 200
    except Exception as e:
        logger.error("JWT verification failed", error=str(e))
        return jsonify({
            "error": "Authentication required",
            "message": "Valid JWT token required"
        }), 401
```

### Authentication Logic
1. **Development Bypass**: Check if bypass is enabled and in development mode
2. **JWT Verification**: Verify token in production mode
3. **User Query**: Retrieve all users from database
4. **Data Formatting**: Format user data for response
5. **Response**: Return user list with appropriate metadata

### Data Filtering
- Excludes sensitive information (passwords, internal fields)
- Returns only essential user data
- Consistent format across development and production

## Key Components

### Development Bypass
```python
if settings.feature_toggles.BYPASS_AUTH and settings.is_development():
    # Skip authentication in development
    return jsonify({
        "users": user_list,
        "auth_bypassed": True,
        "message": "Authentication bypassed in development"
    })
```

### JWT Verification
```python
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

verify_jwt_in_request()
current_user_id = get_jwt_identity()
```

### User Data Formatting
```python
user_list = [{"id": user.id, "username": user.username, "email": user.email} 
             for user in users]
```

## Business Logic

### User Retrieval Process
1. Check for development bypass
2. Verify JWT token if required
3. Query all users from database
4. Format user data (exclude sensitive fields)
5. Return appropriate response format

### Data Security
- Password hashes never included in response
- Internal database fields excluded
- Consistent data structure
- Role-based access considerations

### Development Features
- Authentication bypass for easier testing
- Debug information in response
- Clear indication of bypass status

## Error Scenarios

### Authentication Errors
- Missing or invalid JWT token
- Expired tokens
- Malformed token structure

### Database Errors
- Connection failures
- Query execution errors
- Data formatting issues

### System Errors
- Unexpected server errors
- Configuration issues
- Service dependencies

## Logging

### Development Logging
```python
logger.info("Get all users request (BYPASSED)")
```

### Production Logging
```python
logger.info("Users retrieved successfully", 
           user_id=current_user_id, 
           user_count=len(user_list))
```

### Error Logging
```python
logger.error("JWT verification failed", error=str(e))
```

## Testing Considerations

### Test Cases
- Development bypass functionality
- JWT authentication in production
- Empty user list handling
- Database error scenarios
- Response format validation

### Test Data
```python
# Development test
response = client.get('/auth/users')
assert response.json['auth_bypassed'] == True

# Production test
response = client.get('/auth/users', headers=auth_headers)
assert 'auth_bypassed' not in response.json
```

## Performance Considerations

- Database query optimization
- Efficient data serialization
- Connection pooling utilization
- Response size considerations

## Security Notes

- Sensitive data exclusion from responses
- Proper JWT verification in production
- Development bypass only in development environment
- Access logging and monitoring

## Development vs Production

### Development Mode
- Authentication bypass enabled
- Debug information included
- Verbose error messages
- Enhanced logging

### Production Mode
- Strict JWT authentication required
- Minimal error messages
- Security-focused responses
- Essential logging only
