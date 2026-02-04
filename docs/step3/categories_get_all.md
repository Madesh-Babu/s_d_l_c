# Get All Categories API Documentation

## 📋 Overview

The Get All Categories API provides functionality for authenticated users to retrieve all categories in the inventory system. This endpoint returns a comprehensive list of categories with their basic information.

**Endpoint:** `GET /categories/`  
**Base URL:** `http://127.0.0.1:5000`  
**Authentication:** Required (JWT Bearer Token)

---

## 🔐 API Endpoint

### GET /categories/

Retrieve all categories in the system.

**URL:** `GET /categories/`  
**Content-Type:** `application/json`  
**Authentication:** `Bearer {JWT_TOKEN}`  
**Required Role:** Any authenticated user

#### Request Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| Authorization | string | Yes | Bearer token for authentication |

#### Request Examples

**Get all categories with admin token:**
```bash
curl -X GET "http://127.0.0.1:5000/categories/" \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN_HERE"
```

**Get all categories with staff token:**
```bash
curl -X GET "http://127.0.0.1:5000/categories/" \
  -H "Authorization: Bearer YOUR_STAFF_JWT_TOKEN_HERE"
```

**Get all categories with manager token:**
```bash
curl -X GET "http://127.0.0.1:5000/categories/" \
  -H "Authorization: Bearer YOUR_MANAGER_JWT_TOKEN_HERE"
```

#### Response

**Success Response (200 OK)**
```json
[
  {
    "id": 1,
    "name": "Electronics"
  },
  {
    "id": 2,
    "name": "Furniture"
  },
  {
    "id": 3,
    "name": "Office Supplies"
  },
  {
    "id": 4,
    "name": "Books"
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
| id | integer | Unique category identifier |
| name | string | Category name |

---

## 🚀 Usage Examples

### 1. Get All Categories (Admin)

**Request:**
```bash
curl -X GET "http://127.0.0.1:5000/categories/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Electronics"
  },
  {
    "id": 2,
    "name": "Furniture"
  },
  {
    "id": 3,
    "name": "Office Supplies"
  }
]
```

### 2. Get All Categories (Staff User)

**Request:**
```bash
curl -X GET "http://127.0.0.1:5000/categories/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:** (Same as admin - all authenticated users can access)

### 3. Empty Category List

**Request:**
```bash
curl -X GET "http://127.0.0.1:5000/categories/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
[]
```

### 4. Unauthorized Access

**Request:**
```bash
curl -X GET "http://127.0.0.1:5000/categories/"
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

### Retrieval Process

1. **Token Validation**: JWT token is validated using `@jwt_required()` decorator
2. **User Verification**: Token identity is extracted and verified
3. **Data Retrieval**: All categories are queried from database
4. **Data Serialization**: Category data is converted to dictionary format
5. **Response**: Returns list of categories with ID and name

### Data Serialization

```python
# Category model serialization
def to_dict(self):
    return {
        "id": self.id,
        "name": self.name,
        "description": self.description
    }
```

### Endpoint Implementation

```python
@categories_b_p.route("/", methods=["GET"])
@jwt_required()
def get_categories():
    categories = category_service.get_all_categories()
    return jsonify([{"id": c.id, "name": c.name} for c in categories]), 200
```

### Service Layer Method

```python
def get_all_categories(self):
    """Get all categories"""
    return Category.query.all()
```

### Response Format

The endpoint returns a simplified format with only ID and name:
- Description field is excluded for brevity
- Consistent with product category references
- Optimized for dropdown/select UI components

---

## 🧪 Testing

### Manual Testing with cURL

```bash
# First, get authentication token
TOKEN=$(curl -s -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | jq -r '.access_token')

# Get all categories
curl -X GET "http://127.0.0.1:5000/categories/" \
  -H "Authorization: Bearer $TOKEN"

# Test with different user roles
for role in "staff" "manager" "admin"; do
  ROLE_TOKEN=$(curl -s -X POST "http://127.0.0.1:5000/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"${role}_user\", \"password\": \"${role}123\"}" \
    | jq -r '.access_token')
  
  echo "Testing with ${role} token:"
  curl -X GET "http://127.0.0.1:5000/categories/" \
    -H "Authorization: Bearer $ROLE_TOKEN"
done

# Test without token
curl -X GET "http://127.0.0.1:5000/categories/"

# Test with invalid token
curl -X GET "http://127.0.0.1:5000/categories/" \
  -H "Authorization: Bearer invalid_token"
```

### Python Testing Example

```python
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_get_all_categories():
    # Test with different user roles
    roles = ["admin", "manager", "staff"]
    
    for role in roles:
        # Login
        login_data = {"username": f"{role}_user", "password": f"{role}123"}
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get all categories
            categories_response = requests.get(f"{BASE_URL}/categories/", headers=headers)
            print(f"{role.title()} User Access Status:", categories_response.status_code)
            
            if categories_response.status_code == 200:
                categories = categories_response.json()
                print(f"{role.title()} User Categories Count:", len(categories))
                if categories:
                    print(f"Sample Category: {categories[0]['name']}")
            else:
                print(f"{role.title()} User Error:", categories_response.json())
    
    # Test unauthorized access
    unauthorized_response = requests.get(f"{BASE_URL}/categories/")
    print("Unauthorized Status:", unauthorized_response.status_code)
    print("Unauthorized Response:", unauthorized_response.json())

if __name__ == "__main__":
    test_get_all_categories()
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
| 200 | Categories retrieved successfully |
| 401 | Unauthorized / Invalid token |
| 500 | Internal server error |

### Performance Considerations

- **No Pagination**: Returns all categories at once
- **Lightweight Response**: Only ID and name fields returned
- **Fast Query**: Simple category table query
- **Memory Efficient**: Minimal data per category
- **Cache Friendly**: Categories change infrequently

---

## 🔄 Related Endpoints

- **POST /categories/**: Create new category
- **GET /categories/{category_id}**: Get specific category
- **PUT /categories/update**: Update category
- **DELETE /categories/{category_id}**: Delete category
- **GET /products/**: Get products (with category information)
- **POST /products/**: Create product (with category assignment)

---

## 📝 Notes

- All authenticated users (staff, manager, admin) can access this endpoint
- Categories are returned in database order (typically by creation time)
- Only ID and name fields are returned (description excluded)
- Empty array returned when no categories exist
- No pagination implemented (returns all categories)
- Response format optimized for UI dropdown components
- Categories are commonly used for product categorization
- Consider implementing caching for frequently accessed categories
- Category names are case-sensitive and must be unique
- No sorting options available (uses database default order)
