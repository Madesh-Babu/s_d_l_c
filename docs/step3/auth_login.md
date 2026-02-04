# User Login API Documentation

## 📋 Overview

The User Login API provides functionality for authenticating users and generating JWT access tokens for secure API access. This endpoint validates user credentials and returns a bearer token for subsequent authenticated requests to the Inventory Management System.

**Endpoint:** `POST /auth/login`  
**Base URL:** `http://127.0.0.1:5000`  
**Authentication:** Not required

---

## 🔐 API Endpoint

### POST /auth/login

Authenticate user credentials and receive JWT access token.

**URL:** `POST /auth/login`  
**Content-Type:** `application/json`  
**Authentication:** Not required

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | string | Yes | User's login identifier |
| password | string | Yes | User's password |

#### Request Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| Content-Type | string | Yes | Request content type |

#### Request Examples

**Standard login:**
```bash
curl -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Staff user login:**
```bash
curl -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_staff",
    "password": "staff123"
  }'
```

**Manager user login:**
```bash
curl -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jane_manager",
    "password": "manager123"
  }'
```

#### Response

**Success Response (200 OK)**
```json
{
    "message": "Login successful",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6dHJ1ZSwiaWF0IjoxNjM5NTI0NjAwLCJqdGkiOiJhYjEyMzQ1NiIsInN1YiI6IjEiLCJpc3MiOiJodHRwOi8vMTI3LjAuMC4xOjUwMDAvYXV0aC9sb2dpbiIsImV4cCI6MTYzOTUyNDkwMCwicm9sZSI6ImFkbWluIn0.example"
}
```

**Error Responses**

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

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| message | string | Success message |
| access_token | string | JWT bearer token for authentication |
| error | string | Error description (for error responses) |

---

## 🚀 Usage Examples

### 1. Successful Login

**Request:**
```bash
curl -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Response:**
```json
{
    "message": "Login successful",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6dHJ1ZSwiaWF0IjoxNjM5NTI0NjAwLCJqdGkiOiJhYjEyMzQ1NiIsInN1YiI6IjEiLCJpc3MiOiJodHRwOi8vMTI3LjAuMC4xOjUwMDAvYXV0aC9sb2dpbiIsImV4cCI6MTYzOTUyNDkwMCwicm9sZSI6ImFkbWluIn0.example"
}
```

### 2. Login with Different User Roles

**Staff Login:**
```bash
curl -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "staff_user",
    "password": "staff123"
  }'
```

**Manager Login:**
```bash
curl -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "manager_user",
    "password": "manager123"
  }'
```

### 3. Failed Login Attempts

**Missing Password:**
```bash
curl -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin"
  }'
```

**Response:**
```json
{
    "error": "Missing username or password"
}
```

**Invalid Credentials:**
```bash
curl -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "wrongpassword"
  }'
```

**Response:**
```json
{
    "error": "Invalid username or password"
}
```

**Non-existent User:**
```bash
curl -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nonexistent_user",
    "password": "password123"
  }'
```

**Response:**
```json
{
    "error": "Invalid username or password"
}
```

---

## 🔧 Token Usage

### Using the Access Token

After successful login, use the returned token in subsequent API requests:

```bash
# Store token in variable
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Use token in API requests
curl -X GET "http://127.0.0.1:5000/products/" \
  -H "Authorization: Bearer $TOKEN"

curl -X GET "http://127.0.0.1:5000/categories/" \
  -H "Authorization: Bearer $TOKEN"
```

### Token Format

The JWT token contains the following claims:
- **sub**: User ID (subject)
- **iat**: Issued at time
- **exp**: Expiration time
- **jti**: JWT ID (unique identifier)
- **iss**: Issuer (API endpoint)

### Token Validation

The token is automatically validated by the `@jwt_required()` decorator on protected endpoints:

```python
@jwt_required()
def protected_route():
    current_user_id = get_jwt_identity()
    # Access granted
```

---

## 🔧 Implementation Details

### Authentication Process

1. **Input Validation**: Validates username and password are provided
2. **User Lookup**: Finds user by username in database
3. **Password Verification**: Compares provided password with stored hash
4. **Token Generation**: Creates JWT token with user identity
5. **Response**: Returns token and success message

### Security Features

- **Password Hashing**: Uses Werkzeug's secure password verification
- **JWT Tokens**: Stateless authentication with expiration
- **Generic Error Messages**: Prevents user enumeration attacks
- **Token Expiration**: Tokens have limited lifetime for security

### Password Verification

```python
# User model password verification
def check_password(self, password):
    """Verify user password against stored hash"""
    return check_password_hash(self.password_hash, password)
```

### JWT Configuration

```python
# JWT configuration in app/__init__.py
app.config['JWT_SECRET_KEY'] = 'a1b2c3d4'
jwt = JWTManager(app)
```

---

## 🧪 Testing

### Manual Testing with cURL

```bash
# Test successful login
curl -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# Test missing credentials
curl -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin"
  }'

# Test invalid credentials
curl -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "wrongpassword"
  }'

# Test with token usage
TOKEN=$(curl -s -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | jq -r '.access_token')

curl -X GET "http://127.0.0.1:5000/products/" \
  -H "Authorization: Bearer $TOKEN"
```

### Python Testing Example

```python
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_user_login():
    # Test successful login
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print("Login Status:", response.status_code)
    print("Login Response:", response.json())
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        print("Token obtained:", token[:50] + "...")
        
        # Test token usage
        headers = {"Authorization": f"Bearer {token}"}
        products_response = requests.get(f"{BASE_URL}/products/", headers=headers)
        print("Products Access Status:", products_response.status_code)
    
    # Test invalid credentials
    invalid_data = {
        "username": "admin",
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=invalid_data)
    print("Invalid Login Status:", response.status_code)
    print("Invalid Login Response:", response.json())

if __name__ == "__main__":
    test_user_login()
```

---

## 🐛 Error Handling

### Common Error Scenarios

1. **Missing Username or Password**
   ```json
   {
     "error": "Missing username or password"
   }
   ```

2. **Invalid Username or Password**
   ```json
   {
     "error": "Invalid username or password"
   }
   ```

3. **Invalid JSON Format**
   ```json
   {
     "error": "The browser (or proxy) sent a request that this server could not understand."
   }
   ```

### Error Response Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Login successful |
| 400 | Bad request (missing fields) |
| 401 | Unauthorized (invalid credentials) |
| 500 | Internal server error |

### Security Considerations

- **Generic Error Messages**: Same error for invalid username or password
- **Rate Limiting**: Recommended for production (not implemented)
- **Account Lockout**: Recommended for repeated failed attempts
- **HTTPS**: Required in production to protect credentials

---

## 🔄 Related Endpoints

- **POST /auth/register**: User registration
- **GET /auth/users**: Get all users
- **GET /auth/{user_id}**: Get specific user
- **PUT /auth/update**: Update user information
- **DELETE /auth/delete**: Delete user account
- **GET /products/**: Get products (requires authentication)
- **GET /categories/**: Get categories (requires authentication)

---

## 📝 Notes

- Tokens are stateless and contain user identity
- Password verification uses constant-time comparison
- JWT secret key should be changed in production
- Token expiration is configured at application level
- Invalid credentials return generic error message for security
- Tokens must be included in `Authorization: Bearer {token}` header
- All protected endpoints require valid JWT token
