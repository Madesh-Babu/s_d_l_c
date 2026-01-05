# Create Category API Documentation

## 📋 Overview

The Create Category API provides functionality for authenticated users with appropriate permissions to add new categories to the inventory system. This endpoint supports category creation with validation and unique name enforcement.

**Endpoint:** `POST /categories/`  
**Base URL:** `http://127.0.0.1:5000`  
**Authentication:** Required (JWT Bearer Token)  
**Required Role:** `admin`, `manager`

---

## 🔐 API Endpoint

### POST /categories/

Create a new category in the system.

**URL:** `POST /categories/`  
**Content-Type:** `application/json`  
**Authentication:** `Bearer {JWT_TOKEN}`  
**Required Role:** `admin`, `manager`

#### Request Body

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| name | string | Yes | Category name | 1-100 characters, unique |
| description | string | No | Category description | 0-255 characters |

#### Request Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| Authorization | string | Yes | Bearer token for authentication |
| Content-Type | string | Yes | Request content type |

#### Request Examples

**Create basic category:**
```bash
curl -X POST "http://127.0.0.1:5000/categories/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "name": "Electronics"
  }'
```

**Create category with description:**
```bash
curl -X POST "http://127.0.0.1:5000/categories/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "name": "Furniture",
    "description": "Office and home furniture items"
  }'
```

**Create category with admin role:**
```bash
curl -X POST "http://127.0.0.1:5000/categories/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN_HERE" \
  -d '{
    "name": "Books",
    "description": "Printed and digital books"
  }'
```

#### Response

**Success Response (201 Created)**
```json
{
  "message": "Category created successfully",
  "category": {
    "id": 1,
    "name": "Electronics"
  }
}
```

**Success Response (201 Created) - With Description**
```json
{
  "message": "Category created successfully",
  "category": {
    "id": 2,
    "name": "Furniture"
  }
}
```

**Error Responses**

**Category Name Required (400 Bad Request)**
```json
{
  "error": "Category name is required"
}
```

**Category Already Exists (400 Bad Request)**
```json
{
  "error": "Category with name 'Electronics' already exists"
}
```

**Invalid Description (400 Bad Request)**
```json
{
  "error": "Description must be a string"
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

**Forbidden (403 Forbidden)**
```json
{
  "error": {
    "type": "Forbidden",
    "message": "Access forbidden: insufficient permissions.",
    "status_code": 403
  }
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| message | string | Success message |
| category | object | Created category information |
| category.id | integer | Category ID |
| category.name | string | Category name |
| error | string | Error description (for error responses) |

---

## 🚀 Usage Examples

### 1. Create Basic Category

**Request:**
```bash
curl -X POST "http://127.0.0.1:5000/categories/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "name": "Electronics"
  }'
```

**Response:**
```json
{
  "message": "Category created successfully",
  "category": {
    "id": 1,
    "name": "Electronics"
  }
}
```

### 2. Create Category with Description

**Request:**
```bash
curl -X POST "http://127.0.0.1:5000/categories/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "name": "Office Supplies",
    "description": "Office and business supplies"
  }'
```

**Response:**
```json
{
  "message": "Category created successfully",
  "category": {
    "id": 2,
    "name": "Office Supplies"
  }
}
```

### 3. Create Category with Manager Role

**Request:**
```bash
curl -X POST "http://127.0.0.1:5000/categories/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer MANAGER_JWT_TOKEN" \
  -d '{
    "name": "Clothing",
    "description": "Apparel and fashion items"
  }'
```

**Response:** (Same as admin - both roles can create categories)

### 4. Duplicate Category Name

**Request:**
```bash
curl -X POST "http://127.0.0.1:5000/categories/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "name": "Electronics"
  }'
```

**Response:**
```json
{
  "error": "Category with name 'Electronics' already exists"
}
```

### 5. Missing Category Name

**Request:**
```bash
curl -X POST "http://127.0.0.1:5000/categories/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "description": "Category without name"
  }'
```

**Response:**
```json
{
  "error": "Category name is required"
}
```

### 6. Staff User Access Denied

**Request:**
```bash
curl -X POST "http://127.0.0.1:5000/categories/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer STAFF_JWT_TOKEN" \
  -d '{
    "name": "Staff Category"
  }'
```

**Response:**
```json
{
  "error": {
    "type": "Forbidden",
    "message": "Access forbidden: insufficient permissions.",
    "status_code": 403
  }
}
```

---

## 🔧 Implementation Details

### Creation Process

1. **Token Validation**: JWT token is validated using `@jwt_required()` decorator
2. **Role Authorization**: User role is checked using `@role_required("admin", "manager")`
3. **Input Validation**: Category data is validated using `validate_category_data()`
4. **Uniqueness Check**: Verifies category name doesn't already exist
5. **Category Creation**: New category record is created in database
6. **Database Commit**: Category is saved to database
7. **Response**: Returns created category information

### Validation Rules

```python
def validate_category_data(data):
    """Validate the category JSON payload."""
    if not data:
        return False, "Request data is missing."

    if "name" not in data or not data["name"].strip():
        return False, "Category name is required."

    # Check description field (if given)
    if "description" in data and not isinstance(data["description"], str):
        return False, "Description must be a string."

    # Check for duplicate category name
    existing_category = Category.query.filter_by(name=data["name"]).first()
    if existing_category:
        return False, f"Category with name '{data['name']}' already exists"

    return True, None
```

### Security Features

- **JWT Authentication**: Requires valid bearer token
- **Role-Based Access**: Only admin and manager roles can create categories
- **Input Validation**: Comprehensive data validation
- **Uniqueness Enforcement**: Category names must be unique
- **Database Constraints**: Enforced at database level

### Endpoint Implementation

```python
@categories_b_p.route("/", methods=["POST"])
@jwt_required()
@role_required("admin", "manager")
def create_category():
    data = request.get_json()
    valid, error = validate_category_data(data)
    
    if not valid:
        return jsonify({"error": error}), 400
    
    if not data or "name" not in data:
        return jsonify({"error": "Category name is required"}), 400

    category, err = category_service.create_category(data["name"])
    if err:
        return jsonify(err), 400

    return jsonify({
        "message": "Category created successfully",
        "category": {"id": category.id, "name": category.name}
    }), 201
```

### Service Layer Method

```python
def create_category(self, name):
    """Create a new category"""
    if Category.query.filter_by(name=name).first():
        return None, {"error": "Category already exists"}

    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
    return category, None
```

---

## 🧪 Testing

### Manual Testing with cURL

```bash
# First, get authentication token for admin
ADMIN_TOKEN=$(curl -s -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | jq -r '.access_token')

# Test successful category creation
curl -X POST "http://127.0.0.1:5000/categories/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "name": "Electronics",
    "description": "Electronic devices and accessories"
  }'

# Test category without description
curl -X POST "http://127.0.0.1:5000/categories/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "name": "Furniture"
  }'

# Test duplicate category name
curl -X POST "http://127.0.0.1:5000/categories/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "name": "Electronics"
  }'

# Test missing category name
curl -X POST "http://127.0.0.1:5000/categories/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "description": "Category without name"
  }'

# Test with manager token
MANAGER_TOKEN=$(curl -s -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "manager_user", "password": "manager123"}' \
  | jq -r '.access_token')

curl -X POST "http://127.0.0.1:5000/categories/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -d '{
    "name": "Books",
    "description": "Printed and digital books"
  }'

# Test staff access (should fail)
STAFF_TOKEN=$(curl -s -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "staff_user", "password": "staff123"}' \
  | jq -r '.access_token')

curl -X POST "http://127.0.0.1:5000/categories/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -d '{
    "name": "Staff Category"
  }'
```

### Python Testing Example

```python
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_create_category():
    # Login as admin
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        admin_token = response.json().get("access_token")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Test successful category creation
        category_data = {
            "name": "Test Category",
            "description": "Test category description"
        }
        
        response = requests.post(f"{BASE_URL}/categories/", json=category_data, headers=admin_headers)
        print("Create Category Status:", response.status_code)
        print("Create Category Response:", json.dumps(response.json(), indent=2))
        
        # Test category without description
        simple_data = {"name": "Simple Category"}
        response = requests.post(f"{BASE_URL}/categories/", json=simple_data, headers=admin_headers)
        print("Simple Category Status:", response.status_code)
        
        # Test duplicate category name
        duplicate_data = {"name": "Test Category"}
        response = requests.post(f"{BASE_URL}/categories/", json=duplicate_data, headers=admin_headers)
        print("Duplicate Category Status:", response.status_code)
        print("Duplicate Category Response:", response.json())
        
        # Test missing category name
        missing_data = {"description": "No name provided"}
        response = requests.post(f"{BASE_URL}/categories/", json=missing_data, headers=admin_headers)
        print("Missing Name Status:", response.status_code)
        print("Missing Name Response:", response.json())
    
    # Test manager access
    manager_login = {"username": "manager_user", "password": "manager123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=manager_login)
    
    if response.status_code == 200:
        manager_token = response.json().get("access_token")
        manager_headers = {"Authorization": f"Bearer {manager_token}"}
        
        category_data = {"name": "Manager Category", "description": "Created by manager"}
        response = requests.post(f"{BASE_URL}/categories/", json=category_data, headers=manager_headers)
        print("Manager Access Status:", response.status_code)
        print("Manager Access Response:", response.json())
    
    # Test staff access (should fail)
    staff_login = {"username": "staff_user", "password": "staff123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=staff_login)
    
    if response.status_code == 200:
        staff_token = response.json().get("access_token")
        staff_headers = {"Authorization": f"Bearer {staff_token}"}
        
        category_data = {"name": "Staff Category"}
        response = requests.post(f"{BASE_URL}/categories/", json=category_data, headers=staff_headers)
        print("Staff Access Status:", response.status_code)
        print("Staff Access Response:", response.json())

if __name__ == "__main__":
    test_create_category()
```

---

## 🐛 Error Handling

### Common Error Scenarios

1. **Missing Category Name**
   ```json
   {
     "error": "Category name is required"
   }
   ```

2. **Category Already Exists**
   ```json
   {
     "error": "Category with name 'Electronics' already exists"
   }
   ```

3. **Invalid Description Type**
   ```json
   {
     "error": "Description must be a string"
   }
   ```

4. **Insufficient Permissions**
   ```json
   {
     "error": {
       "type": "Forbidden",
       "message": "Access forbidden: insufficient permissions.",
       "status_code": 403
     }
   }
   ```

### Error Response Codes

| Status Code | Description |
|-------------|-------------|
| 201 | Category created successfully |
| 400 | Bad request (validation errors) |
| 401 | Unauthorized / Invalid token |
| 403 | Forbidden / Insufficient permissions |
| 500 | Internal server error |

---

## 🔄 Related Endpoints

- **GET /categories/**: Get all categories
- **GET /categories/{category_id}**: Get specific category
- **PUT /categories/update**: Update category
- **DELETE /categories/{category_id}**: Delete category
- **POST /products/**: Create product (with category assignment)
- **GET /products/**: Get products (with category information)

---

## 📝 Notes

- Only admin and manager roles can create categories
- Category names must be unique across the system
- Description is optional and can be null
- Category names are trimmed of whitespace
- Returns basic category information (ID and name only)
- Case-sensitive uniqueness check for category names
- No limit on number of categories that can be created
- Categories can be deleted (cascade delete affects products)
- Consider implementing category hierarchy in future versions
- No audit logging for category creation
- Database constraints enforce uniqueness at the database level
