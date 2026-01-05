# User Registration Documentation

## Overview
This document provides comprehensive documentation for the user registration system in the Inventory Management API. The system implements secure user registration with role-based access control, password hashing, and JWT-based authentication.

## Registration System Architecture

### User Model Structure
```python
class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
```

### Security Features
- **Password Hashing**: Uses Werkzeug's secure password hashing
- **Unique Constraints**: Enforces unique usernames and emails
- **Role-Based Access**: Three-tier permission system
- **JWT Authentication**: Stateless token-based authentication

## User Registration API

### Endpoint Details
- **URL**: `POST /auth/register`
- **Description**: Register a new user account
- **Authentication**: Not required
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
    "email": "string", 
    "password": "string",
    "role": "string"
}
```

#### Field Specifications

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `username` | String | Yes | 3-80 chars, unique | User's login identifier |
| `email` | String | Yes | Valid email format, unique | User's email address |
| `password` | String | Yes | Minimum 6 characters | User's password |
| `role` | String | No | staff/manager/admin | User's permission level |

#### Role Definitions

| Role | Permissions | Description |
|------|-------------|-------------|
| `staff` | Read-only access | Can view products and categories |
| `manager` | Read + Create + Update | Can manage products and categories |
| `admin` | Full access | Can manage all system resources |

### Response Format

#### Success Response (201 Created)
```json
{
    "message": "User registered successfully"
}
```

#### Error Responses

**Missing Required Fields (400 Bad Request)**
```json
{
    "error": "Missing required fields"
}
```

**Invalid Role (400 Bad Request)**
```json
{
    "error": "Invalid role"
}
```

**Username Already Exists (400 Bad Request)**
```json
{
    "error": "Username already existis"
}
```

**Email Already Registered (400 Bad Request)**
```json
{
    "error": "Email already registered"
}
```

## Registration Process Flow

### Step-by-Step Registration

```mermaid
graph TD
    A[Client Request] --> B[Validate Input Data]
    B --> C[Check Username Uniqueness]
    C --> D[Check Email Uniqueness]
    D --> E[Hash Password]
    E --> F[Create User Object]
    F --> G[Save to Database]
    G --> H[Return Success Response]
    
    B --> I[Validation Error]
    C --> J[Username Exists]
    D --> K[Email Exists]
    
    I --> L[400 Bad Request]
    J --> L
    K --> L
```

### Validation Logic

#### 1. Input Validation
```python
# Required fields check
if not data or not data.get('username') or not data.get('password') or not data.get('email'):
    return jsonify({"error":"Missing required fields"}), 400

# Role validation
role = data.get("role", "staff")  # Default to staff
if role not in ["staff", "manager", "admin"]:
    return jsonify({"error":"Invalid role"}), 400
```

#### 2. Uniqueness Validation
```python
# Username uniqueness
if User.query.filter_by(username=data['username']).first():
    return jsonify({"error":"Username already existis"}), 400

# Email uniqueness  
if User.query.filter_by(email=data['email']).first():
    return jsonify({"error": "Email already registered"}), 400
```

#### 3. Password Security
```python
# Password hashing (automatic in User model)
new_user = User(
    username=data['username'],
    email=data["email"],
    role=role
)
new_user.set_password(data['password'])  # Secure hashing
```

## User Model Methods

### Password Management
```python
def set_password(self, password):
    """Hash and set user password securely"""
    self.password_hash = generate_password_hash(password)

def check_password(self, password):
    """Verify user password against hash"""
    return check_password_hash(self.password_hash, password)
```

### Data Serialization
```python
def to_dict(self):
    """Convert user to dictionary (excludes sensitive data)"""
    return {
        "id": self.id,
        "username": self.username,
        "role": self.role
    }
```

## Authentication Integration

### Login Process
After registration, users can authenticate using:

#### Login Endpoint
- **URL**: `POST /auth/login`
- **Request Body**:
```json
{
    "username": "string",
    "password": "string"
}
```

#### Login Response
```json
{
    "message": "Login successful",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### JWT Token Usage
```python
# Include token in subsequent requests
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Role-Based Access Control

### Permission Matrix

| Endpoint | Staff | Manager | Admin |
|----------|-------|---------|-------|
| GET /products | ✅ | ✅ | ✅ |
| POST /products | ❌ | ✅ | ✅ |
| PUT /products | ❌ | ✅ | ✅ |
| DELETE /products | ❌ | ❌ | ✅ |
| GET /categories | ✅ | ✅ | ✅ |
| POST /categories | ❌ | ✅ | ✅ |
| PUT /categories | ❌ | ✅ | ✅ |
| DELETE /categories | ❌ | ❌ | ✅ |

### Implementation
```python
# Role-based route protection
@jwt_required()
@role_required("admin", "manager")
def add_product():
    # Only admin and manager can access
    pass
```

## Security Considerations

### Password Security
- **Hashing Algorithm**: Werkzeug uses PBKDF2 with SHA-256
- **Salt**: Automatically generated unique salt per password
- **Iterations**: Configurable iteration count for security
- **Storage**: Only hashes stored, never plain text passwords

### Input Validation
- **Username**: Length validation, character restrictions
- **Email**: Format validation using database constraints
- **Password**: Minimum length requirements (application level)
- **Role**: Enumerated valid roles only

### Database Security
- **Unique Constraints**: Enforced at database level
- **Not Null Constraints**: Required fields enforced
- **Data Types**: Proper data type constraints

## Usage Examples

### Example Registration Requests

#### Staff User Registration
```bash
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_staff",
    "email": "john@example.com", 
    "password": "secure123",
    "role": "staff"
  }'
```

#### Manager Registration
```bash
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jane_manager",
    "email": "jane@example.com",
    "password": "manager123", 
    "role": "manager"
  }'
```

#### Admin Registration
```bash
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin_user",
    "email": "admin@example.com",
    "password": "admin123",
    "role": "admin"
  }'
```

### Example Registration Flow

#### 1. Register User
```bash
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Response**:
```json
{
    "message": "User registered successfully"
}
```

#### 2. Login to Get Token
```bash
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

**Response**:
```json
{
    "message": "Login successful",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 3. Use Token for API Access
```bash
curl -X GET http://127.0.0.1:5000/products \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

## Error Handling

### Common Registration Errors

#### 1. Missing Fields
**Request**:
```json
{
    "username": "testuser"
}
```

**Response**:
```json
{
    "error": "Missing required fields"
}
```

#### 2. Invalid Role
**Request**:
```json
{
    "username": "testuser",
    "email": "test@example.com", 
    "password": "password123",
    "role": "invalid_role"
}
```

**Response**:
```json
{
    "error": "Invalid role"
}
```

#### 3. Duplicate Username
**Request**:
```json
{
    "username": "existing_user",
    "email": "new@example.com",
    "password": "password123"
}
```

**Response**:
```json
{
    "error": "Username already existis"
}
```

#### 4. Duplicate Email
**Request**:
```json
{
    "username": "new_user",
    "email": "existing@example.com", 
    "password": "password123"
}
```

**Response**:
```json
{
    "error": "Email already registered"
}
```

## Testing the Registration System

### Unit Test Examples
```python
def test_user_registration_success(client):
    """Test successful user registration"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "role": "staff"
    }
    
    response = client.post('/auth/register', 
                          json=user_data)
    
    assert response.status_code == 201
    assert response.json == {"message": "User registered successfully"}

def test_duplicate_username(client):
    """Test registration with duplicate username"""
    # First registration
    user_data = {
        "username": "testuser",
        "email": "test1@example.com", 
        "password": "password123"
    }
    client.post('/auth/register', json=user_data)
    
    # Duplicate registration
    duplicate_data = {
        "username": "testuser",
        "email": "test2@example.com",
        "password": "password123"
    }
    
    response = client.post('/auth/register', json=duplicate_data)
    assert response.status_code == 400
    assert "Username already existis" in response.json["error"]
```

### Integration Test Scenarios
- Successful registration with all roles
- Validation of all required fields
- Uniqueness constraint enforcement
- Password hashing verification
- Login after registration

## Best Practices

### For Developers
1. **Always validate input** before processing
2. **Use secure password hashing** (never store plain text)
3. **Implement proper error handling** with meaningful messages
4. **Enforce uniqueness constraints** at database level
5. **Use HTTPS in production** to protect credentials

### For Users
1. **Choose strong passwords** with minimum 6 characters
2. **Use valid email addresses** for account recovery
3. **Select appropriate roles** based on required permissions
4. **Keep credentials secure** and don't share tokens

### For System Administrators
1. **Monitor registration attempts** for unusual activity
2. **Implement rate limiting** to prevent abuse
3. **Regular security audits** of user accounts
4. **Backup user data** regularly

## Future Enhancements

### Planned Features
1. **Email Verification**: Confirm email addresses during registration
2. **Password Strength Requirements**: Enforce complex password policies
3. **Account Lockout**: Temporary lock after failed login attempts
4. **Two-Factor Authentication**: Additional security layer
5. **User Profile Management**: Extended user information
6. **Registration Invitations**: Admin-approved registrations

### Security Improvements
1. **Rate Limiting**: Prevent brute force attacks
2. **CAPTCHA**: Bot protection during registration
3. **Audit Logging**: Track registration activities
4. **Password Expiration**: Force periodic password changes

## Troubleshooting

### Common Issues

#### Registration Fails with 400 Error
**Causes**:
- Missing required fields
- Invalid role specified
- Username or email already exists
- Invalid JSON format

**Solutions**:
- Check all required fields are present
- Verify role is one of: staff, manager, admin
- Choose unique username and email
- Ensure valid JSON syntax

#### Login Fails After Registration
**Causes**:
- Incorrect password
- Username not found
- Database sync issues

**Solutions**:
- Verify password is correct
- Check username spelling
- Restart application if needed

#### Database Constraint Errors
**Causes**:
- Database connection issues
- Constraint violations
- Migration problems

**Solutions**:
- Check database connection
- Run database migrations
- Verify database schema

This documentation provides a comprehensive guide to the user registration system, ensuring secure and effective user management for the Inventory Management API.
