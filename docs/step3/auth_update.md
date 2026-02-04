# Update User API Documentation

## 📋 Overview

The Update User API provides functionality for authenticated users to update user information including username, email, password, and role. This endpoint allows partial updates of user data with flexible field selection.

**Endpoint:** `PUT /auth/update`  
**Base URL:** `http://127.0.0.1:5000`  
**Authentication:** Required (JWT Bearer Token)

---

## 🔐 API Endpoint

### PUT /auth/update

Update user information.

**URL:** `PUT /auth/update`  
**Content-Type:** `application/json`  
**Authentication:** `Bearer {JWT_TOKEN}`  
**Required Role:** Any authenticated user

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | Yes | User ID to update |
| username | string | No | New username (must be unique) |
| email | string | No | New email (must be unique) |
| password | string | No | New password |
| role | string | No | New role (`staff`, `manager`, `admin`) |

#### Request Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| Authorization | string | Yes | Bearer token for authentication |
| Content-Type | string | Yes | Request content type |

#### Request Examples

**Update username and email:**
```bash
curl -X PUT "http://127.0.0.1:5000/auth/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "id": 1,
    "username": "updated_admin",
    "email": "updated@example.com"
  }'
```

**Update password:**
```bash
curl -X PUT "http://127.0.0.1:5000/auth/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "id": 2,
    "password": "newpassword123"
  }'
```

**Update role:**
```bash
curl -X PUT "http://127.0.0.1:5000/auth/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "id": 3,
    "role": "manager"
  }'
```

**Update all fields:**
```bash
curl -X PUT "http://127.0.0.1:5000/auth/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "id": 1,
    "username": "super_admin",
    "email": "super_admin@example.com",
    "password": "superpass123",
    "role": "admin"
  }'
```

#### Response

**Success Response (200 OK)**
```json
{
  "message": "User updated",
  "user": {
    "id": 1,
    "username": "updated_admin",
    "email": "updated@example.com",
    "role": "admin"
  }
}
```

**Error Responses**

**Missing User ID (400 Bad Request)**
```json
{
  "error": "User ID is required"
}
```

**User Not Found (404 Not Found)**
```json
{
  "error": {
    "type": "NotFound",
    "message": "The requested resource could not be found.",
    "status_code": 404
  }
}
```

**Unauthorized (401 Unauthorized)**
```json
{
  "error": {
    "type": "Unauthorized",
    "message": "You are not authorized to access this resource.",
    "status_code": 401
  }
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| message | string | Success message |
| user | object | Updated user information |
| user.id | integer | User ID |
| user.username | string | Updated username |
| user.email | string | Updated email |
| user.role | string | Updated role |
| error | string | Error description (for error responses) |

---

## 🚀 Usage Examples

### 1. Update Username and Email

**Request:**
```bash
curl -X PUT "http://127.0.0.1:5000/auth/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "id": 1,
    "username": "new_admin",
    "email": "new_admin@example.com"
  }'
```

**Response:**
```json
{
  "message": "User updated",
  "user": {
    "id": 1,
    "username": "new_admin",
    "email": "new_admin@example.com",
    "role": "admin"
  }
}
```

### 2. Update Password Only

**Request:**
```bash
curl -X PUT "http://127.0.0.1:5000/auth/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "id": 2,
    "password": "newsecurepassword"
  }'
```

**Response:**
```json
{
  "message": "User updated",
  "user": {
    "id": 2,
    "username": "manager1",
    "email": "manager@example.com",
    "role": "manager"
  }
}
```

### 3. Update User Role

**Request:**
```bash
curl -X PUT "http://127.0.0.1:5000/auth/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "id": 3,
    "role": "admin"
  }'
```

**Response:**
```json
{
  "message": "User updated",
  "user": {
    "id": 3,
    "username": "staff1",
    "email": "staff@example.com",
    "role": "admin"
  }
}
```

### 4. Update Non-Existent User

**Request:**
```bash
curl -X PUT "http://127.0.0.1:5000/auth/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "id": 999,
    "username": "nonexistent"
  }'
```

**Response:**
```json
{
  "error": {
    "type": "NotFound",
    "message": "The requested resource could not be found.",
    "status_code": 404
  }
}
```

### 5. Missing User ID

**Request:**
```bash
curl -X PUT "http://127.0.0.1:5000/auth/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "username": "test"
  }'
```

**Response:**
```json
{
  "error": "User ID is required"
}
```

---

## 🔧 Implementation Details

### Update Process

1. **Token Validation**: JWT token is validated using `@jwt_required()` decorator
2. **Input Validation**: Validates user ID is provided in request body
3. **User Lookup**: User is queried from database using `get_or_404()`
4. **Field Updates**: Updates only provided fields (partial update support)
5. **Password Handling**: Hashes new password if provided
6. **Database Commit**: Saves changes to database
7. **Response**: Returns updated user information

### Security Features

- **JWT Authentication**: Requires valid bearer token
- **Password Hashing**: New passwords are automatically hashed
- **Partial Updates**: Only updates fields that are provided
- **Database Constraints**: Unique constraints enforced at database level

### Endpoint Implementation

```python
@auth_b_p.route("/update", methods=["PUT"])
@jwt_required()
def update_user():
    data = request.get_json()
    user_id = data.get("id")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user = User.query.get_or_404(user_id)

    # Update only provided fields
    if "username" in data:
        user.username = data["username"]
    if "email" in data:
        user.email = data["email"]
    if "password" in data:
        user.set_password(data["password"])
    if "role" in data:
        user.role = data["role"]

    db.session.commit()
    return jsonify({
        "message": "User updated",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }), 200
```

### Password Security

```python
# Password hashing in User model
def set_password(self, password):
    """Hash and set user password securely"""
    self.password_hash = generate_password_hash(password)
```

---

## 🧪 Testing

### Manual Testing with cURL

```bash
# First, get authentication token
TOKEN=$(curl -s -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | jq -r '.access_token')

# Test updating username
curl -X PUT "http://127.0.0.1:5000/auth/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "id": 1,
    "username": "updated_admin"
  }'

# Test updating password
curl -X PUT "http://127.0.0.1:5000/auth/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "id": 1,
    "password": "newpassword123"
  }'

# Test updating role
curl -X PUT "http://127.0.0.1:5000/auth/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "id": 2,
    "role": "admin"
  }'

# Test missing user ID
curl -X PUT "http://127.0.0.1:5000/auth/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "username": "test"
  }'

# Test non-existent user
curl -X PUT "http://127.0.0.1:5000/auth/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "id": 999,
    "username": "test"
  }'
```

### Python Testing Example

```python
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_update_user():
    # Login to get token
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test updating username
        update_data = {
            "id": 1,
            "username": "updated_admin",
            "email": "updated@example.com"
        }
        
        response = requests.put(f"{BASE_URL}/auth/update", json=update_data, headers=headers)
        print("Update Status:", response.status_code)
        print("Update Response:", json.dumps(response.json(), indent=2))
        
        # Test updating password
        password_data = {
            "id": 1,
            "password": "newpassword123"
        }
        
        response = requests.put(f"{BASE_URL}/auth/update", json=password_data, headers=headers)
        print("Password Update Status:", response.status_code)
        
        # Test updating role
        role_data = {
            "id": 2,
            "role": "admin"
        }
        
        response = requests.put(f"{BASE_URL}/auth/update", json=role_data, headers=headers)
        print("Role Update Status:", response.status_code)
        
        # Test missing user ID
        invalid_data = {"username": "test"}
        response = requests.put(f"{BASE_URL}/auth/update", json=invalid_data, headers=headers)
        print("Missing ID Status:", response.status_code)
        print("Missing ID Response:", response.json())
    
    # Test unauthorized access
    unauthorized_data = {"id": 1, "username": "test"}
    unauthorized_response = requests.put(f"{BASE_URL}/auth/update", json=unauthorized_data)
    print("Unauthorized Status:", unauthorized_response.status_code)
    print("Unauthorized Response:", unauthorized_response.json())

if __name__ == "__main__":
    test_update_user()
```

---

## 🐛 Error Handling

### Common Error Scenarios

1. **Missing User ID**
   ```json
   {
     "error": "User ID is required"
   }
   ```

2. **User Not Found**
   ```json
   {
     "error": {
       "type": "NotFound",
       "message": "The requested resource could not be found.",
       "status_code": 404
     }
   }
   ```

3. **Unauthorized Access**
   ```json
   {
     "error": {
       "type": "Unauthorized",
       "message": "You are not authorized to access this resource.",
       "status_code": 401
     }
   }
   ```

4. **Database Constraint Violation** (if username/email already exists)
   ```json
   {
     "error": {
       "type": "InternalServerError",
       "message": "Database constraint violation",
       "status_code": 500
     }
   }
   ```

### Error Response Codes

| Status Code | Description |
|-------------|-------------|
| 200 | User updated successfully |
| 400 | Bad request (missing user ID) |
| 401 | Unauthorized / Invalid token |
| 404 | User not found |
| 500 | Internal server error |

### Security Considerations

- **No Access Control**: Any authenticated user can update any user
- **Password Security**: New passwords are automatically hashed
- **Role Changes**: Users can change roles without restrictions
- **Data Validation**: Limited validation on input data
- **Audit Trail**: No logging of user changes

---

## 🔄 Related Endpoints

- **POST /auth/register**: User registration
- **POST /auth/login**: User authentication
- **GET /auth/users**: Get all users
- **GET /auth/{user_id}**: Get specific user
- **DELETE /auth/delete**: Delete user account

---

## 📝 Notes

- Supports partial updates (only provided fields are updated)
- Password changes are automatically hashed for security
- No validation for unique constraints (handled by database)
- All authenticated users can update any user's data
- Consider implementing role-based access control in production
- Database constraints will prevent duplicate usernames/emails
- No audit logging for user changes
- Returns updated user information in response
