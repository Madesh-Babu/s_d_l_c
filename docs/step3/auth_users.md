# Get All Users API Documentation

## 📋 Overview

The Get All Users API provides functionality for authenticated users to retrieve all user accounts in the system. This endpoint returns a list of users with their basic information, excluding sensitive data like passwords and roles for security purposes.

**Endpoint:** `GET /auth/users`  
**Base URL:** `http://127.0.0.1:5000`  
**Authentication:** Required (JWT Bearer Token)

---

## 🔐 API Endpoint

### GET /auth/users

Retrieve all users in the system.

**URL:** `GET /auth/users`  
**Content-Type:** `application/json`  
**Authentication:** `Bearer {JWT_TOKEN}`  
**Required Role:** Any authenticated user

#### Request Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| Authorization | string | Yes | Bearer token for authentication |

#### Request Examples

**Get all users with admin token:**
```bash
curl -X GET "http://127.0.0.1:5000/auth/users" \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN_HERE"
```

**Get all users with staff token:**
```bash
curl -X GET "http://127.0.0.1:5000/auth/users" \
  -H "Authorization: Bearer YOUR_STAFF_JWT_TOKEN_HERE"
```

**Get all users with manager token:**
```bash
curl -X GET "http://127.0.0.1:5000/auth/users" \
  -H "Authorization: Bearer YOUR_MANAGER_JWT_TOKEN_HERE"
```

#### Response

**Success Response (200 OK)**
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com"
  },
  {
    "id": 2,
    "username": "manager1",
    "email": "manager@example.com"
  },
  {
    "id": 3,
    "username": "staff1",
    "email": "staff@example.com"
  },
  {
    "id": 4,
    "username": "staff2",
    "email": "staff2@example.com"
  }
]
```

**Empty Response (200 OK)**
```json
[]
```

**Error Responses**

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

**Invalid Token (401 Unauthorized)**
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
| id | integer | Unique user identifier |
| username | string | User's login identifier |
| email | string | User's email address |

---

## 🚀 Usage Examples

### 1. Get All Users (Admin)

**Request:**
```bash
curl -X GET "http://127.0.0.1:5000/auth/users" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com"
  },
  {
    "id": 2,
    "username": "manager1",
    "email": "manager@example.com"
  },
  {
    "id": 3,
    "username": "staff1",
    "email": "staff@example.com"
  }
]
```

### 2. Get All Users (Staff User)

**Request:**
```bash
curl -X GET "http://127.0.0.1:5000/auth/users" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:** (Same as admin - all authenticated users can access)

### 3. Empty User List

**Request:**
```bash
curl -X GET "http://127.0.0.1:5000/auth/users" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
[]
```

### 4. Unauthorized Access

**Request:**
```bash
curl -X GET "http://127.0.0.1:5000/auth/users"
```

**Response:**
```json
{
  "error": {
    "type": "Unauthorized",
    "message": "You are not authorized to access this resource.",
    "status_code": 401
  }
}
```

---

## 🔧 Implementation Details

### Authentication Flow

1. **Token Validation**: JWT token is validated using `@jwt_required()` decorator
2. **User Verification**: Token identity is extracted and verified
3. **Data Retrieval**: All users are queried from database
4. **Data Serialization**: User data is converted to safe format
5. **Response**: Returns list of users without sensitive information

### Security Features

- **JWT Authentication**: Requires valid bearer token
- **Data Filtering**: Excludes sensitive fields (password_hash, role)
- **Access Control**: All authenticated users can access
- **Input Validation**: No input parameters to validate

### Data Serialization

```python
# User model serialization (excludes sensitive data)
def to_dict(self):
    return {
        "id": self.id,
        "username": self.username,
        "role": self.role  # Note: This is excluded in the endpoint response
    }
```

### Endpoint Implementation

```python
@auth_b_p.route("/users", methods=['GET'])
@jwt_required()
def get_all_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "username": user.username, "email": user.email} 
                   for user in users]), 200
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

# Get all users
curl -X GET "http://127.0.0.1:5000/auth/users" \
  -H "Authorization: Bearer $TOKEN"

# Test without token
curl -X GET "http://127.0.0.1:5000/auth/users"

# Test with invalid token
curl -X GET "http://127.0.0.1:5000/auth/users" \
  -H "Authorization: Bearer invalid_token"
```

### Python Testing Example

```python
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_get_all_users():
    # Login to get token
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get all users
        users_response = requests.get(f"{BASE_URL}/auth/users", headers=headers)
        print("Get Users Status:", users_response.status_code)
        print("Users Response:", json.dumps(users_response.json(), indent=2))
        
        # Test with different user roles
        for role in ["staff", "manager"]:
            login_data = {"username": f"{role}_user", "password": f"{role}123"}
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                token = response.json().get("access_token")
                headers = {"Authorization": f"Bearer {token}"}
                users_response = requests.get(f"{BASE_URL}/auth/users", headers=headers)
                print(f"{role.title()} User Access Status:", users_response.status_code)
    
    # Test unauthorized access
    unauthorized_response = requests.get(f"{BASE_URL}/auth/users")
    print("Unauthorized Status:", unauthorized_response.status_code)
    print("Unauthorized Response:", unauthorized_response.json())

if __name__ == "__main__":
    test_get_all_users()
```

---

## 🐛 Error Handling

### Common Error Scenarios

1. **Missing Authentication Token**
   ```json
   {
     "error": {
       "type": "Unauthorized",
       "message": "You are not authorized to access this resource.",
       "status_code": 401
     }
   }
   ```

2. **Invalid Token**
   ```json
   {
     "error": {
       "type": "Unauthorized",
       "message": "You are not authorized to access this resource.",
       "status_code": 401
     }
   }
   ```

3. **Expired Token**
   ```json
   {
     "error": {
       "type": "Unauthorized",
       "message": "Token has expired",
       "status_code": 401
     }
   }
   ```

### Error Response Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Users retrieved successfully |
| 401 | Unauthorized / Invalid token |
| 500 | Internal server error |

### Security Considerations

- **No Rate Limiting**: Consider implementing for production
- **Data Exposure**: Only non-sensitive user data is returned
- **Access Control**: All authenticated users can access (consider role-based filtering)
- **Token Validation**: Automatic JWT validation

---

## 🔄 Related Endpoints

- **POST /auth/register**: User registration
- **POST /auth/login**: User authentication
- **GET /auth/{user_id}**: Get specific user
- **PUT /auth/update**: Update user information
- **DELETE /auth/delete**: Delete user account

---

## 📝 Notes

- Returns all users regardless of the requesting user's role
- Password hashes and roles are excluded from response for security
- Empty array is returned when no users exist
- All authenticated users (staff, manager, admin) can access this endpoint
- Consider implementing role-based filtering in production
- Response preserves user creation order from database
- No pagination implemented (returns all users at once)
