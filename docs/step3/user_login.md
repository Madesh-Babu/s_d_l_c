# User Login Documentation

## Overview
This document provides comprehensive documentation for the user login system in the Inventory Management API. The system implements JWT-based stateless authentication with secure password verification and role-based access control.

## Login System Architecture

### Authentication Flow
```mermaid
graph TD
    A[User Credentials] --> B[Validate Input]
    B --> C[Find User in Database]
    C --> D[Verify Password Hash]
    D --> E[Generate JWT Token]
    E --> F[Return Token to Client]
    F --> G[Client Stores Token]
    G --> H[Include Token in API Requests]
    H --> I[Server Validates Token]
    I --> J[Grant Access to Resources]
    
    B --> K[Input Validation Error]
    C --> L[User Not Found]
    D --> M[Password Mismatch]
    
    K --> N[400 Bad Request]
    L --> O[401 Unauthorized]
    M --> O
```

### JWT Configuration
```python
# JWT Configuration in app/__init__.py
app.config['JWT_SECRET_KEY'] = 'a1b2c3d4'
jwt = JWTManager(app)
```

### Security Features
- **JWT Tokens**: Stateless authentication with expiration
- **Password Hashing**: Secure verification using Werkzeug
- **Role-Based Access**: Token includes user role for authorization
- **Input Validation**: Comprehensive credential validation

## User Login API

### Endpoint Details
- **URL**: `POST /auth/login`
- **Description**: Authenticate user and receive JWT access token
- **Authentication**: Not required (this is the authentication endpoint)
- **Content-Type**: `application/json`

### Request Format

#### Request Headers
```http
Content-Type: application/json
```

#### Request Body
```json
{
    "username": "string",
    "password": "string"
}
```

#### Field Specifications

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `username` | String | Yes | Existing username | User's login identifier |
| `password` | String | Yes | User's password | Plain text password |

### Response Format

#### Success Response (200 OK)
```json
{
    "message": "Login successful",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6dHJ1ZSwiaWF0IjoxNjM5NTI0NjAwLCJqdGkiOiJhYjEyMzQ1NiIsInN1YiI6IjEiLCJpc3MiOiJodHRwOi8vMTI3LjAuMC4xOjUwMDAvYXV0aC9sb2dpbiIsImV4cCI6MTYzOTUyNDkwMCwicm9sZSI6InN0YWZmIn0.example"
}
```

#### Error Responses

**Missing Credentials (400 Bad Request)**
```json
{
    "error": "Missing username or password"
}
```

**Invalid Credentials (401 Unauthorized)**
```json
{
    "error": "Invalid username or password"
}
```

## Login Implementation Details

### Login Route Implementation
```python
@auth_b_p.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Input validation
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Missing username or password"}), 400

    # User lookup
    user = User.query.filter_by(username=data['username']).first()

    # Password verification
    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Invalid username or password"}), 401

    # JWT token generation
    access_token = create_access_token(identity=str(user.id))

    return jsonify({"message": "Login successful", "access_token": access_token}), 200
```

### Password Verification Process
```python
# User model password verification
def check_password(self, password):
    """Verify user password against stored hash"""
    return check_password_hash(self.password_hash, password)
```

### JWT Token Generation
```python
# Token creation with user identity
access_token = create_access_token(identity=str(user.id))
```

## Token Usage and Management

### Token Format
The JWT token contains the following claims:
- **sub**: User ID (subject)
- **iat**: Issued at time
- **exp**: Expiration time
- **jti**: JWT ID (unique identifier)
- **iss**: Issuer (API endpoint)
- **role**: User role (for authorization)

### Token Usage in API Requests

#### Authorization Header
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### Example API Request with Token
```bash
curl -X GET http://127.0.0.1:5000/products \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### Token Validation Process
```python
# Token validation in protected routes
@jwt_required()
def protected_route():
    current_user_id = get_jwt_identity()
    # Access granted
```

## Role-Based Authentication

### Token Role Claims
JWT tokens can include role information for authorization:

```python
# Enhanced token creation with role claims
access_token = create_access_token(
    identity=str(user.id),
    additional_claims={"role": user.role}
)
```

### Role Verification
```python
# Role-based access control implementation
def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()
            claims = get_jwt()

            # Check role from token claims
            token_role = claims.get("role")
            if token_role:
                if token_role not in roles:
                    raise Forbidden("Access forbidden: insufficient permissions")
                return fn(*args, **kwargs)

            # Fallback to database lookup
            try:
                user = User.query.get(int(identity))
                if not user or user.role not in roles:
                    raise Forbidden("Access forbidden: insufficient permissions")
                return fn(*args, **kwargs)
            except ValueError:
                raise Unauthorized("Invalid token identity type")
        return decorator
    return wrapper
```

## Usage Examples

### Basic Login Example

#### Request
```bash
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

#### Success Response
```json
{
    "message": "Login successful",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6dHJ1ZSwiaWF0IjoxNjM5NTI0NjAwLCJqdGkiOiJhYjEyMzQ1NiIsInN1YiI6IjEiLCJpc3MiOiJodHRwOi8vMTI3LjAuMC4xOjUwMDAvYXV0aC9sb2dpbiIsImV4cCI6MTYzOTUyNDkwMCwicm9sZSI6ImFkbWluIn0.example"
}
```

### Using Token for API Access

#### Get Products with Authentication
```bash
curl -X GET http://127.0.0.1:5000/products \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

#### Create Product (Requires Manager/Admin Role)
```bash
curl -X POST http://127.0.0.1:5000/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -d '{
    "name": "New Product",
    "price": 99.99,
    "stock": 10
  }'
```

## Error Handling

### Common Login Errors

#### 1. Missing Credentials
**Request**:
```json
{
    "username": "admin"
}
```

**Response**:
```json
{
    "error": "Missing username or password"
}
```

#### 2. User Not Found
**Request**:
```json
{
    "username": "nonexistent_user",
    "password": "password123"
}
```

**Response**:
```json
{
    "error": "Invalid username or password"
}
```

#### 3. Incorrect Password
**Request**:
```json
{
    "username": "admin",
    "password": "wrong_password"
}
```

**Response**:
```json
{
    "error": "Invalid username or password"
}
```

#### 4. Invalid JSON Format
**Request**:
```
invalid json
```

**Response**:
```json
{
    "error": "The browser (or proxy) sent a request that this server could not understand."
}
```

### Token-Related Errors

#### 1. Missing Token
**Request**:
```bash
curl -X GET http://127.0.0.1:5000/products
```

**Response**:
```json
{
    "error": {
        "type": "Unauthorized",
        "message": "You are not authorized to access this resource.",
        "status_code": 401
    }
}
```

#### 2. Invalid Token
**Request**:
```bash
curl -X GET http://127.0.0.1:5000/products \
  -H "Authorization: Bearer invalid_token"
```

**Response**:
```json
{
    "error": {
        "type": "Unauthorized",
        "message": "You are not authorized to access this resource.",
        "status_code": 401
    }
}
```

#### 3. Expired Token
**Request**:
```bash
curl -X GET http://127.0.0.1:5000/products \
  -H "Authorization: Bearer expired_token"
```

**Response**:
```json
{
    "error": {
        "type": "Unauthorized",
        "message": "Token has expired",
        "status_code": 401
    }
}
```

#### 4. Insufficient Permissions
**Request**:
```bash
curl -X POST http://127.0.0.1:5000/products \
  -H "Authorization: Bearer staff_token" \
  -d '{"name": "Product", "price": 10.0, "stock": 5}'
```

**Response**:
```json
{
    "error": {
        "type": "Forbidden",
        "message": "Access forbidden: insufficient permissions.",
        "status_code": 403
    }
}
```

## Security Considerations

### Password Security
- **Hashing Algorithm**: PBKDF2 with SHA-256
- **Salt**: Unique salt per password hash
- **Verification**: Constant-time comparison to prevent timing attacks
- **Storage**: Only hashes stored, never plain text passwords

### JWT Security
- **Secret Key**: Configurable JWT secret key
- **Token Expiration**: Tokens have limited lifetime
- **Algorithm**: HS256 for token signing
- **Claims**: Minimal information in tokens

### Authentication Security
- **Input Validation**: Comprehensive credential validation
- **Error Messages**: Generic error messages to prevent user enumeration
- **Rate Limiting**: Recommended for production (not implemented)
- **HTTPS**: Required for production to protect credentials

## Testing the Login System

### Unit Test Examples
```python
def test_login_success(client):
    """Test successful login"""
    # Create test user
    user = User(username="testuser", email="test@example.com", role="staff")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    
    # Login request
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    
    response = client.post('/auth/login', json=login_data)
    
    assert response.status_code == 200
    assert "access_token" in response.json
    assert response.json["message"] == "Login successful"

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    login_data = {
        "username": "nonexistent",
        "password": "wrongpassword"
    }
    
    response = client.post('/auth/login', json=login_data)
    
    assert response.status_code == 401
    assert "Invalid username or password" in response.json["error"]

def test_login_missing_fields(client):
    """Test login with missing fields"""
    login_data = {
        "username": "testuser"
    }
    
    response = client.post('/auth/login', json=login_data)
    
    assert response.status_code == 400
    assert "Missing username or password" in response.json["error"]
```

### Integration Test Scenarios
- Login with all user roles (staff, manager, admin)
- Token usage in protected endpoints
- Role-based access control verification
- Token expiration handling
- Password verification accuracy

## Best Practices

### For Developers
1. **Never store plain text passwords**
2. **Use HTTPS in production**
3. **Implement rate limiting** for login attempts
4. **Set appropriate token expiration times**
5. **Validate all input data** before processing
6. **Use generic error messages** for security

### For Users
1. **Choose strong passwords** with complexity requirements
2. **Don't share credentials** with others
3. **Log out from applications** when finished
4. **Use different passwords** for different services
5. **Report suspicious activity** immediately

### For System Administrators
1. **Monitor login attempts** for unusual patterns
2. **Implement account lockout** policies
3. **Regular security audits** of authentication system
4. **Keep JWT secret keys** secure and rotate regularly
5. **Monitor token usage** and expiration

## Token Lifecycle Management

### Token Creation
```python
# Standard token creation
access_token = create_access_token(identity=str(user.id))

# Token with additional claims
access_token = create_access_token(
    identity=str(user.id),
    additional_claims={"role": user.role}
)

# Token with custom expiration
access_token = create_access_token(
    identity=str(user.id),
    expires_delta=timedelta(hours=2)
)
```

### Token Validation
```python
# In protected routes
@jwt_required()
def protected_endpoint():
    current_user_id = get_jwt_identity()
    # Process request
```

### Token Refresh (Future Enhancement)
```python
# Token refresh endpoint (planned feature)
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_token = create_access_token(identity=current_user_id)
    return jsonify({"access_token": new_token})
```

## Performance Considerations

### Database Optimization
- **User Lookup**: Efficient username indexing
- **Password Verification**: Optimized hash comparison
- **Connection Pooling**: Database connection management

### JWT Performance
- **Token Validation**: Fast cryptographic verification
- **Stateless Authentication**: No server-side session storage
- **Token Caching**: Optional token validation caching

### Security vs Performance Balance
- **Hash Iterations**: Balance between security and speed
- **Token Size**: Minimize token payload for performance
- **Validation Frequency**: Optimize token validation frequency

## Troubleshooting

### Common Login Issues

#### Login Returns 401 Unauthorized
**Possible Causes**:
- Incorrect username or password
- User account doesn't exist
- Password hash verification failure

**Solutions**:
- Verify credentials are correct
- Check user exists in database
- Ensure password hashing is working correctly

#### Token Validation Fails
**Possible Causes**:
- JWT secret key mismatch
- Token format is invalid
- Token has expired

**Solutions**:
- Check JWT secret key configuration
- Verify token format and structure
- Check token expiration time

#### Role-Based Access Denied
**Possible Causes**:
- User role doesn't match required permissions
- Role claims missing from token
- Role verification logic error

**Solutions**:
- Verify user role in database
- Check token includes role claims
- Review role-based access control logic

### Debugging Tips
1. **Check application logs** for detailed error messages
2. **Verify database connection** and user data
3. **Test with known good credentials** to isolate issues
4. **Use JWT debugging tools** to verify token contents
5. **Check configuration files** for proper settings

## Future Enhancements

### Planned Features
1. **Token Refresh**: Implement refresh token mechanism
2. **Multi-Factor Authentication**: Add 2FA support
3. **Account Lockout**: Temporary lock after failed attempts
4. **Login History**: Track user login attempts
5. **Session Management**: Active session monitoring
6. **Social Login**: OAuth integration options

### Security Improvements
1. **Rate Limiting**: Prevent brute force attacks
2. **Device Fingerprinting**: Enhanced security monitoring
3. **IP Whitelisting**: Restrict access by location
4. **Password Policies**: Enforce complex password requirements
5. **Audit Logging**: Comprehensive authentication logging

### Performance Enhancements
1. **Token Caching**: Cache validated tokens
2. **Database Optimization**: Improve user lookup performance
3. **Load Balancing**: Distribute authentication load
4. **CDN Integration**: Optimize token validation

This documentation provides a comprehensive guide to the user login system, ensuring secure and effective authentication for the Inventory Management API.
