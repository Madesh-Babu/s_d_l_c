# User Login Endpoint

## Overview

Authenticates a user and provides a JWT token for accessing protected endpoints.

## Endpoint Details

- **Method**: `POST`
- **URL**: `/auth/login`
- **Authentication**: Not required
- **Content-Type**: `application/json`

## Request Body

```json
{
    "username": "string",
    "password": "string"
}
```

## Response Format

### Success Response (200)
```json
{
    "message": "Login successful",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "role": "staff"
    }
}
```

### Error Response (401)
```json
{
    "error": "Authentication failed",
    "message": "Invalid username or password"
}
```

## Implementation Pattern

### Core Logic
```python
@auth_b_p.route('/login', methods=['POST'])
def login():
    try:
        # Validate input data
        data = request.get_json()
        login_data = UserLogin(**data)
        
        # Find user by username
        user = User.query.filter_by(username=login_data.username).first()
        if not user:
            raise AuthenticationError("Invalid username or password")
        
        # Verify password
        if not user.check_password(login_data.password):
            raise AuthenticationError("Invalid username or password")
        
        # Generate JWT token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify(login_response), 200
        
    except AuthenticationError as e:
        return exception_handler.handle_exception(e)
```

### Authentication Flow
1. **Input Validation**: Validate username and password format
2. **User Lookup**: Find user by username in database
3. **Password Verification**: Compare hashed password with input
4. **Token Generation**: Create JWT token with user identity
5. **Response Formatting**: Return token and user information

### Security Measures
- Password comparison using secure hashing
- JWT token with expiration
- Consistent error messages (don't reveal if user exists)
- Login attempt logging
- Rate limiting consideration

## Key Components

### Pydantic Schema
```python
class UserLogin(BaseModel):
    username: str
    password: str
```

### JWT Configuration
```python
# Token generation
access_token = create_access_token(
    identity=str(user.id),
    additional_claims={"role": user.role}
)
```

### Password Verification
```python
def check_password(self, password):
    return bcrypt.check_password_hash(self.password_hash, password)
```

## Business Logic

### Authentication Process
1. Validate input format and required fields
2. Look up user by username
3. Verify password using secure comparison
4. Generate JWT token with user claims
5. Log successful authentication
6. Return token and user data

### JWT Token Structure
- **Identity**: User ID as string
- **Claims**: User role and permissions
- **Expiration**: Configurable token lifetime
- **Algorithm**: HS256 for secure signing

### Error Handling
- Generic error messages for security
- Detailed logging for troubleshooting
- Proper HTTP status codes
- Exception handling for database errors

## Error Scenarios

### Authentication Failures
- Invalid username
- Incorrect password
- Non-existent user account
- Locked or disabled accounts

### Validation Errors
- Missing username or password
- Invalid input format
- Empty credentials

### System Errors
- Database connection failures
- Token generation failures
- Unexpected server errors

## Logging

### Success Logging
```python
logger.info("User login successful", 
           user_id=user.id, 
           username=user.username,
           role=user.role)
```

### Security Logging
```python
logger.warning("Login authentication error", 
               error=str(e), 
               username=data.get('username'))
```

## Testing Considerations

### Test Cases
- Valid login with correct credentials
- Invalid username scenarios
- Incorrect password attempts
- Missing credentials
- Token generation verification
- JWT token validation

### Test Data
```python
valid_login_data = {
    "username": "testuser",
    "password": "StrongPass123!"
}
```

## Performance Considerations

- Efficient user lookup with indexed username field
- Optimized password hashing comparison
- Fast JWT token generation
- Database connection pooling

## Security Notes

- Use secure password hashing (bcrypt)
- Implement consistent error messages
- Consider rate limiting for login attempts
- Use secure JWT token generation
- Log authentication attempts
- Set appropriate token expiration times

## Development Features

### Authentication Bypass
```python
if settings.feature_toggles.BYPASS_AUTH and settings.is_development():
    # Development login without authentication
    return jsonify({
        "access_token": "dev_token",
        "user": mock_user_data
    })
```

### Debug Information
- Token contents in development mode
- Detailed error messages
- Authentication bypass for testing
