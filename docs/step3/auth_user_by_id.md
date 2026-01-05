# Get User by ID API Documentation

## 📋 Overview

The Get User by ID API provides functionality for authenticated users to retrieve a specific user's information by their unique identifier. This endpoint returns user details excluding sensitive data like passwords for security purposes.

**Endpoint:** `GET /auth/{user_id}`  
**Base URL:** `http://127.0.0.1:5000`  
**Authentication:** Required (JWT Bearer Token)

---

## 🔐 API Endpoint

### GET /auth/{user_id}

Retrieve a specific user by their ID.

**URL:** `GET /auth/{user_id}`  
**Content-Type:** `application/json`  
**Authentication:** `Bearer {JWT_TOKEN}`  
**Required Role:** Any authenticated user

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | integer | Yes | Unique user identifier |

#### Request Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| Authorization | string | Yes | Bearer token for authentication |

#### Request Examples

**Get user by ID with admin token:**
```bash
curl -X GET "http://127.0.0.1:5000/auth/1" \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN_HERE"
```

**Get user by ID with staff token:**
```bash
curl -X GET "http://127.0.0.1:5000/auth/3" \
  -H "Authorization: Bearer YOUR_STAFF_JWT_TOKEN_HERE"
```

**Get user by ID with manager token:**
```bash
curl -X GET "http://127.0.0.1:5000/auth/2" \
  -H "Authorization: Bearer YOUR_MANAGER_JWT_TOKEN_HERE"
```

#### Response

**Success Response (200 OK)**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com"
}
```

**Error Responses**

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

**Invalid User ID (404 Not Found)**
```bash
curl -X GET "http://127.0.0.1:5000/auth/999" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
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

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique user identifier |
| username | string | User's login identifier |
| email | string | User's email address |

---

## 🚀 Usage Examples

### 1. Get Specific User (Admin)

**Request:**
```bash
curl -X GET "http://127.0.0.1:5000/auth/1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com"
}
```

### 2. Get Manager User

**Request:**
```bash
curl -X GET "http://127.0.0.1:5000/auth/2" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "id": 2,
  "username": "manager1",
  "email": "manager@example.com"
}
```

### 3. Get Staff User

**Request:**
```bash
curl -X GET "http://127.0.0.1:5000/auth/3" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "id": 3,
  "username": "staff1",
  "email": "staff@example.com"
}
```

### 4. User Not Found

**Request:**
```bash
curl -X GET "http://127.0.0.1:5000/auth/999" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
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

### 5. Unauthorized Access

**Request:**
```bash
curl -X GET "http://127.0.0.1:5000/auth/1"
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
3. **Parameter Validation**: User ID is extracted from URL path
4. **User Lookup**: User is queried from database using `get_or_404()`
5. **Data Serialization**: User data is converted to safe format
6. **Response**: Returns user information without sensitive data

### Security Features

- **JWT Authentication**: Requires valid bearer token
- **Data Filtering**: Excludes sensitive fields (password_hash, role)
- **Access Control**: All authenticated users can access any user
- **404 Handling**: Uses Flask's `get_or_404()` for consistent error handling

### Endpoint Implementation

```python
@auth_b_p.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email
    }), 200
```

### URL Parameter Handling

The endpoint uses Flask's URL parameter binding:
- `<int:user_id>` automatically converts the parameter to integer
- Invalid integer URLs will return 404 before reaching the function
- `get_or_404()` handles database lookup with automatic 404 on not found

---

## 🧪 Testing

### Manual Testing with cURL

```bash
# First, get authentication token
TOKEN=$(curl -s -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | jq -r '.access_token')

# Test existing user
curl -X GET "http://127.0.0.1:5000/auth/1" \
  -H "Authorization: Bearer $TOKEN"

# Test non-existent user
curl -X GET "http://127.0.0.1:5000/auth/999" \
  -H "Authorization: Bearer $TOKEN"

# Test invalid user ID (non-integer)
curl -X GET "http://127.0.0.1:5000/auth/invalid" \
  -H "Authorization: Bearer $TOKEN"

# Test without token
curl -X GET "http://127.0.0.1:5000/auth/1"

# Test with invalid token
curl -X GET "http://127.0.0.1:5000/auth/1" \
  -H "Authorization: Bearer invalid_token"
```

### Python Testing Example

```python
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_get_user_by_id():
    # Login to get token
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test existing user
        user_response = requests.get(f"{BASE_URL}/auth/1", headers=headers)
        print("Get User Status:", user_response.status_code)
        print("User Response:", json.dumps(user_response.json(), indent=2))
        
        # Test non-existent user
        not_found_response = requests.get(f"{BASE_URL}/auth/999", headers=headers)
        print("Not Found Status:", not_found_response.status_code)
        print("Not Found Response:", not_found_response.json())
        
        # Test with different user roles
        for user_id in [1, 2, 3]:
            user_response = requests.get(f"{BASE_URL}/auth/{user_id}", headers=headers)
            print(f"User {user_id} Status:", user_response.status_code)
            if user_response.status_code == 200:
                print(f"User {user_id} Data:", user_response.json())
    
    # Test unauthorized access
    unauthorized_response = requests.get(f"{BASE_URL}/auth/1")
    print("Unauthorized Status:", unauthorized_response.status_code)
    print("Unauthorized Response:", unauthorized_response.json())

if __name__ == "__main__":
    test_get_user_by_id()
```

---

## 🐛 Error Handling

### Common Error Scenarios

1. **User Not Found**
   ```json
   {
     "error": {
       "type": "NotFound",
       "message": "The requested resource could not be found.",
       "status_code": 404
     }
   }
   ```

2. **Invalid User ID (Non-integer)**
   ```json
   {
     "error": {
       "type": "NotFound",
       "message": "The requested resource could not be found.",
       "status_code": 404
     }
   }
   ```

3. **Missing Authentication Token**
   ```json
   {
     "error": {
       "type": "Unauthorized",
       "message": "You are not authorized to access this resource.",
       "status_code": 401
     }
   }
   ```

4. **Invalid Token**
   ```json
   {
     "error": {
       "type": "Unauthorized",
       "message": "You are not authorized to access this resource.",
       "status_code": 401
     }
   }
   ```

### Error Response Codes

| Status Code | Description |
|-------------|-------------|
| 200 | User retrieved successfully |
| 401 | Unauthorized / Invalid token |
| 404 | User not found / Invalid user ID |
| 500 | Internal server error |

### Security Considerations

- **No Access Control**: All authenticated users can access any user's data
- **Data Exposure**: Only non-sensitive user data is returned
- **User Enumeration**: Possible to test for existing user IDs
- **Rate Limiting**: Consider implementing for production

---

## 🔄 Related Endpoints

- **POST /auth/register**: User registration
- **POST /auth/login**: User authentication
- **GET /auth/users**: Get all users
- **PUT /auth/update**: Update user information
- **DELETE /auth/delete**: Delete user account

---

## 📝 Notes

- Returns user information regardless of the requesting user's role
- Password hashes and roles are excluded from response for security
- Uses Flask's `get_or_404()` for automatic 404 handling
- User ID must be a valid integer
- Consider implementing role-based access control in production
- No pagination needed as it returns single user
- URL parameter validation is handled automatically by Flask
