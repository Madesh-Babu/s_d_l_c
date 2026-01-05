# Delete User API Documentation

## 📋 Overview

The Delete User API provides functionality for authenticated users to permanently remove user accounts from the system. This endpoint deletes user records and all associated data, with the action being irreversible.

**Endpoint:** `DELETE /auth/delete`  
**Base URL:** `http://127.0.0.1:5000`  
**Authentication:** Required (JWT Bearer Token)

---

## 🔐 API Endpoint

### DELETE /auth/delete

Delete a user account from the system.

**URL:** `DELETE /auth/delete`  
**Content-Type:** `application/json`  
**Authentication:** `Bearer {JWT_TOKEN}`  
**Required Role:** Any authenticated user

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | Yes | User ID to delete |

#### Request Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| Authorization | string | Yes | Bearer token for authentication |
| Content-Type | string | Yes | Request content type |

#### Request Examples

**Delete user account:**
```bash
curl -X DELETE "http://127.0.0.1:5000/auth/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "id": 3
  }'
```

**Delete admin user:**
```bash
curl -X DELETE "http://127.0.0.1:5000/auth/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "id": 1
  }'
```

**Delete manager user:**
```bash
curl -X DELETE "http://127.0.0.1:5000/auth/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "id": 2
  }'
```

#### Response

**Success Response (200 OK)**
```json
{
  "message": "User staff1 deleted successfully"
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
| message | string | Success message with deleted username |
| error | string | Error description (for error responses) |

---

## 🚀 Usage Examples

### 1. Delete Staff User

**Request:**
```bash
curl -X DELETE "http://127.0.0.1:5000/auth/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "id": 3
  }'
```

**Response:**
```json
{
  "message": "User staff1 deleted successfully"
}
```

### 2. Delete Manager User

**Request:**
```bash
curl -X DELETE "http://127.0.0.1:5000/auth/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "id": 2
  }'
```

**Response:**
```json
{
  "message": "User manager1 deleted successfully"
}
```

### 3. Delete Admin User

**Request:**
```bash
curl -X DELETE "http://127.0.0.1:5000/auth/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "id": 1
  }'
```

**Response:**
```json
{
  "message": "User admin deleted successfully"
}
```

### 4. Delete Non-Existent User

**Request:**
```bash
curl -X DELETE "http://127.0.0.1:5000/auth/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "id": 999
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
curl -X DELETE "http://127.0.0.1:5000/auth/delete" \
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

### 6. Unauthorized Access

**Request:**
```bash
curl -X DELETE "http://127.0.0.1:5000/auth/delete" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1
  }'
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

### Deletion Process

1. **Token Validation**: JWT token is validated using `@jwt_required()` decorator
2. **Input Validation**: Validates user ID is provided in request body
3. **User Lookup**: User is queried from database using `get_or_404()`
4. **Username Capture**: Stores username for success message
5. **Database Deletion**: Removes user record from database
6. **Database Commit**: Permanently saves the deletion
7. **Response**: Returns success message with deleted username

### Security Features

- **JWT Authentication**: Requires valid bearer token
- **Permanent Deletion**: Action is irreversible
- **Database Constraints**: Referential integrity handled by database
- **404 Handling**: Uses Flask's `get_or_404()` for consistent error handling

### Endpoint Implementation

```python
@auth_b_p.route("/delete", methods=["DELETE"])
@jwt_required()
def delete_user():
    data = request.get_json()
    user_id = data.get("id")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user = User.query.get_or_404(user_id)
    username = user.username  # Store for message
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"message": f"User {username} deleted successfully"}), 200
```

### Database Considerations

- **Cascade Deletes**: Related data may be affected by database constraints
- **Foreign Keys**: Other tables referencing users may have cascade rules
- **Transaction Safety**: Deletion is wrapped in database transaction
- **Irreversible Action**: Cannot undo deletion once committed

---

## 🧪 Testing

### Manual Testing with cURL

```bash
# First, get authentication token
TOKEN=$(curl -s -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | jq -r '.access_token')

# Test deleting existing user
curl -X DELETE "http://127.0.0.1:5000/auth/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "id": 3
  }'

# Test deleting non-existent user
curl -X DELETE "http://127.0.0.1:5000/auth/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "id": 999
  }'

# Test missing user ID
curl -X DELETE "http://127.0.0.1:5000/auth/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "username": "test"
  }'

# Test without authentication
curl -X DELETE "http://127.0.0.1:5000/auth/delete" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1
  }'

# Test with invalid token
curl -X DELETE "http://127.0.0.1:5000/auth/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer invalid_token" \
  -d '{
    "id": 1
  }'
```

### Python Testing Example

```python
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_delete_user():
    # Login to get token
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # First, create a test user to delete
        user_data = {
            "username": "test_delete_user",
            "email": "delete@example.com",
            "password": "test123",
            "role": "staff"
        }
        
        create_response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        print("Create User Status:", create_response.status_code)
        
        if create_response.status_code == 201:
            # Get the user ID (assuming it's the last created user)
            users_response = requests.get(f"{BASE_URL}/auth/users", headers=headers)
            if users_response.status_code == 200:
                users = users_response.json()
                test_user_id = max([user["id"] for user in users]) if users else None
                
                if test_user_id:
                    # Test deleting the user
                    delete_data = {"id": test_user_id}
                    delete_response = requests.delete(f"{BASE_URL}/auth/delete", 
                                                    json=delete_data, headers=headers)
                    print("Delete Status:", delete_response.status_code)
                    print("Delete Response:", delete_response.json())
        
        # Test deleting non-existent user
        non_existent_data = {"id": 999}
        non_existent_response = requests.delete(f"{BASE_URL}/auth/delete", 
                                                json=non_existent_data, headers=headers)
        print("Non-existent Delete Status:", non_existent_response.status_code)
        print("Non-existent Delete Response:", non_existent_response.json())
        
        # Test missing user ID
        missing_data = {"username": "test"}
        missing_response = requests.delete(f"{BASE_URL}/auth/delete", 
                                          json=missing_data, headers=headers)
        print("Missing ID Status:", missing_response.status_code)
        print("Missing ID Response:", missing_response.json())
    
    # Test unauthorized access
    unauthorized_data = {"id": 1}
    unauthorized_response = requests.delete(f"{BASE_URL}/auth/delete", json=unauthorized_data)
    print("Unauthorized Status:", unauthorized_response.status_code)
    print("Unauthorized Response:", unauthorized_response.json())

if __name__ == "__main__":
    test_delete_user()
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

4. **Database Constraint Violation** (if user has related data)
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
| 200 | User deleted successfully |
| 400 | Bad request (missing user ID) |
| 401 | Unauthorized / Invalid token |
| 404 | User not found |
| 500 | Internal server error |

### Security Considerations

- **No Access Control**: Any authenticated user can delete any user
- **Permanent Action**: Deletion cannot be undone
- **Data Integrity**: Related data may be affected
- **Self-Deletion**: Users can delete their own accounts
- **Admin Deletion**: Admin accounts can be deleted by any user
- **No Audit Trail**: No logging of deletion actions

---

## 🔄 Related Endpoints

- **POST /auth/register**: User registration
- **POST /auth/login**: User authentication
- **GET /auth/users**: Get all users
- **GET /auth/{user_id}**: Get specific user
- **PUT /auth/update**: Update user information

---

## 📝 Notes

- Deletion is permanent and cannot be undone
- All authenticated users can delete any user account
- Database constraints may prevent deletion if user has related data
- Success message includes the deleted username for confirmation
- No soft delete implementation - records are permanently removed
- Consider implementing role-based access control in production
- No confirmation step required - deletion is immediate
- Related data handling depends on database cascade rules
- No audit logging for deletion actions
- Users can delete their own accounts while logged in
