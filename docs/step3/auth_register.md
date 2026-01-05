# User Registration API Documentation

## 📋 Overview

The User Registration API provides functionality for creating new user accounts with role-based access control. This endpoint supports user registration with username, email, password, and role assignment for the Inventory Management System.

**Endpoint:** `POST /auth/register`  
**Base URL:** `http://127.0.0.1:5000`  
**Authentication:** Not required

---

## 🔐 API Endpoint

### POST /auth/register

Register a new user account with role-based access control.

**URL:** `POST /auth/register`  
**Content-Type:** `application/json`  
**Authentication:** Not required

#### Request Body

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| username | string | Yes | User's unique username | 3-80 characters |
| email | string | Yes | User's email address | Valid email format (Pydantic validation) |
| password | string | Yes | User's password | 6+ characters (Pydantic validation) |
| role | string | No | User role | "staff", "manager", or "admin" (default: "staff") |

#### Role Definitions

| Role | Permissions | Description |
|------|-------------|-------------|
| `staff` | Read-only access | Can view products and categories |
| `manager` | Read + Create + Update | Can manage products and categories |
| `admin` | Full access | Can manage all system resources |

#### Request Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| Content-Type | string | Yes | Request content type |

#### Request Examples

**Register staff user:**
```bash
curl -X POST "http://127.0.0.1:5000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_staff",
    "email": "john@example.com",
    "password": "secure123",
    "role": "staff"
  }'
```

**Register manager user:**
```bash
curl -X POST "http://127.0.0.1:5000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jane_manager",
    "email": "jane@example.com",
    "password": "manager123",
    "role": "manager"
  }'
```

**Register admin user:**
```bash
curl -X POST "http://127.0.0.1:5000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin_user",
    "email": "admin@example.com",
    "password": "admin123",
    "role": "admin"
  }'
```

**Register with default role (staff):**
```bash
curl -X POST "http://127.0.0.1:5000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "new_user",
    "email": "new@example.com",
    "password": "password123"
  }'
```

#### Response

**Success Response (201 Created)**
```json
{
    "message": "User registered successfully"
}
```

**Error Responses**

**Missing Required Fields (400 Bad Request)**
```json
{
  "error": "1 validation error for UserCreate\n  username\n    Field required [type=missing, input_value={'email': 'test@example.com', 'password': 'password123'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing"
}
```

**Invalid Email (400 Bad Request)**
```json
{
  "error": "1 validation error for UserCreate\n  email\n    Input should match pattern '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$' [type=pattern_match, input_value='invalid-email', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.12/v/pattern_match"
}
```

**Password Too Short (400 Bad Request)**
```json
{
  "error": "1 validation error for UserCreate\n  password\n    Input should be at least 6 characters long [type=string_too_short, input_value='123', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.12/v/string_too_short"
}
```

**Username Already Exists (400 Bad Request)**
```json
{
  "error": "Username already exists"
}
```

**Email Already Registered (400 Bad Request)**
```json
{
  "error": "Email already registered"
}
```

**Invalid Role (400 Bad Request)**
```json
{
  "error": "1 validation error for UserCreate\n  role\n    Input should match pattern '^(staff|manager|admin)$' [type=pattern_match, input_value='invalid_role', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.12/v/pattern_match"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| message | string | Success message |
| error | string | Error description (for error responses) |

---

## 🚀 Usage Examples

### 1. Basic Registration

**Request:**
```bash
curl -X POST "http://127.0.0.1:5000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "role": "staff"
  }'
```

**Response:**
```json
{
    "message": "User registered successfully"
}
```

### 2. Registration Without Role (Defaults to Staff)

**Request:**
```bash
curl -X POST "http://127.0.0.1:5000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "staff_user",
    "email": "staff@example.com",
    "password": "staff123"
  }'
```

**Response:**
```json
{
    "message": "User registered successfully"
}
```

### 3. Invalid Registration Attempts

**Missing Fields:**
```bash
curl -X POST "http://127.0.0.1:5000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "incomplete"
  }'
```

**Response:**
```json
{
    "error": "Missing required fields"
}
```

**Invalid Role:**
```bash
curl -X POST "http://127.0.0.1:5000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "role": "invalid_role"
  }'
```

**Response:**
```json
{
    "error": "Invalid role"
}
```

---

## 🔧 Implementation Details

### Validation Process

1. **Pydantic Validation**: Uses `UserCreate` schema for automatic validation
   - Username: 3-80 characters, required
   - Email: Valid email format using regex pattern
   - Password: Minimum 6 characters
   - Role: Must match pattern '^(staff|manager|admin)$'
2. **Uniqueness Check**: Verifies username and email don't already exist
3. **Password Hashing**: Uses Werkzeug's secure password hashing
4. **Database Creation**: Creates new user record in database
5. **Response**: Returns success message

### Validation Rules

- **Username**: Must be unique, 3-80 characters
- **Email**: Must be valid email format, unique
- **Role**: Must be one of: `staff`, `manager`, `admin` (defaults to `staff`)

### Security Features

- **Password Hashing**: Uses Werkzeug's PBKDF2 with SHA-256
- **Input Sanitization**: Validates all input data
- **Uniqueness Enforcement**: Database-level constraints
- **Error Messages**: Generic messages to prevent user enumeration

---

## 🧪 Testing

### Manual Testing with cURL

```bash
# Test successful registration
curl -X POST "http://127.0.0.1:5000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "test123",
    "role": "staff"
  }'

# Test duplicate username
curl -X POST "http://127.0.0.1:5000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "different@example.com",
    "password": "test123"
  }'

# Test invalid role
curl -X POST "http://127.0.0.1:5000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "invaliduser",
    "email": "invalid@example.com",
    "password": "test123",
    "role": "invalid"
  }'
```

### Python Testing Example

```python
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_user_registration():
    # Test successful registration
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "role": "staff"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print("Registration Status:", response.status_code)
    print("Registration Response:", response.json())
    
    # Test duplicate username
    duplicate_data = {
        "username": "testuser",
        "email": "different@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=duplicate_data)
    print("Duplicate Status:", response.status_code)
    print("Duplicate Response:", response.json())

if __name__ == "__main__":
    test_user_registration()
```

---

## 🐛 Error Handling

### Common Error Scenarios

1. **Missing Required Fields** (Pydantic Validation)
   ```json
   {
     "error": "1 validation error for UserCreate\n  username\n    Field required [type=missing, input_value={'email': 'test@example.com', 'password': 'password123'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing"
   }
   ```

2. **Invalid Email Format** (Pydantic Validation)
   ```json
   {
     "error": "1 validation error for UserCreate\n  email\n    Input should match pattern '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$' [type=pattern_match, input_value='invalid-email', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.12/v/pattern_match"
   }
   ```

3. **Password Too Short** (Pydantic Validation)
   ```json
   {
     "error": "1 validation error for UserCreate\n  password\n    Input should be at least 6 characters long [type=string_too_short, input_value='123', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.12/v/string_too_short"
   }
   ```

4. **Invalid Role** (Pydantic Validation)
   ```json
   {
     "error": "1 validation error for UserCreate\n  role\n    Input should match pattern '^(staff|manager|admin)$' [type=pattern_match, input_value='invalid_role', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.12/v/pattern_match"
   }
   ```

5. **Username Already Exists** (Database Constraint)
   ```json
   {
     "error": "Username already exists"
   }
   ```

6. **Email Already Registered** (Database Constraint)
   ```json
   {
     "error": "Email already registered"
   }
   ```

### Error Response Codes

| Status Code | Description |
|-------------|-------------|
| 201 | User registered successfully |
| 400 | Bad request (validation errors) |
| 500 | Internal server error |

---

## 🔄 Related Endpoints

- **POST /auth/login**: User authentication
- **GET /auth/users**: Get all users
- **GET /auth/{user_id}**: Get specific user
- **PUT /auth/update**: Update user information
- **DELETE /auth/delete**: Delete user account

---

## 📝 Notes

- Passwords are never stored in plain text
- Role defaults to `staff` if not specified
- Username and email must be unique across the system
- The endpoint does not return user data for security reasons
- After registration, users must login to obtain an access token
- Email format validation is handled at database level
- All validation errors return 400 status code with descriptive messages
