# Create Product API Documentation

## 📋 Overview

The Create Product API provides functionality for authenticated users with appropriate permissions to add new products to the inventory system. This endpoint supports product creation with validation, category assignment, and stock management.

**Endpoint:** `POST /products/`  
**Base URL:** `http://127.0.0.1:5000`  
**Authentication:** Required (JWT Bearer Token)  
**Required Role:** `admin`, `manager`

---

## 🔐 API Endpoint

### POST /products/

Create a new product in the inventory.

**URL:** `POST /products/`  
**Content-Type:** `application/json`  
**Authentication:** `Bearer {JWT_TOKEN}`  
**Required Role:** `admin`, `manager`

#### Request Body

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| name | string | Yes | Product name | 1-100 characters (Pydantic validation) |
| description | string | No | Product description | 0-255 characters |
| price | number | Yes | Product price | Must be positive (Pydantic validation) |
| stock | integer | Yes | Initial stock quantity | Must be non-negative (Pydantic validation) |
| category_id | integer | No | Category ID | Must be valid category ID |

#### Request Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| Authorization | string | Yes | Bearer token for authentication |
| Content-Type | string | Yes | Request content type |

#### Request Examples

**Create basic product:**
```bash
curl -X POST "http://127.0.0.1:5000/products/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "name": "Laptop Pro",
    "description": "High-performance laptop",
    "price": 999.99,
    "stock": 50
  }'
```

**Create product with category:**
```bash
curl -X POST "http://127.0.0.1:5000/products/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "name": "Wireless Mouse",
    "description": "Ergonomic wireless mouse",
    "price": 29.99,
    "stock": 100,
    "category_id": 1
  }'
```

**Create product with admin role:**
```bash
curl -X POST "http://127.0.0.1:5000/products/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN_HERE" \
  -d '{
    "name": "USB-C Hub",
    "description": "Multi-port USB-C hub",
    "price": 49.99,
    "stock": 25,
    "category_id": 1
  }'
```

#### Response

**Success Response (201 Created)**
```json
{
  "message": "Product added",
  "product": {
    "id": 1,
    "name": "Laptop Pro",
    "description": "High-performance laptop",
    "price": 999.99,
    "stock": 50,
    "category": "Electronics"
  }
}
```

**Success Response (201 Created) - Without Category**
```json
{
  "message": "Product added",
  "product": {
    "id": 2,
    "name": "Basic Product",
    "description": "Simple product description",
    "price": 19.99,
    "stock": 10,
    "category": null
  }
}
```

**Error Responses**

**Missing Required Fields (400 Bad Request)**
```json
{
  "error": "1 validation error for ProductCreate\n  name\n    Field required [type=missing, input_value={'price': 99.99, 'stock': 10}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing"
}
```

**Invalid Price (400 Bad Request)**
```json
{
  "error": "1 validation error for ProductCreate\n  price\n    Input should be greater than 0 [type=greater_than, input_value=-10, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.12/v/greater_than"
}
```

**Invalid Stock (400 Bad Request)**
```json
{
  "error": "1 validation error for ProductCreate\n  stock\n    Input should be greater than or equal to 0 [type=greater_than_equal, input_value=-5, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.12/v/greater_than_equal"
}
```

**Invalid Category (400 Bad Request)**
```json
{
  "error": "Invalid category ID"
}
```

**Missing Name or Price (400 Bad Request)**
```json
{
  "error": "Missing name or price"
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
| product | object | Created product information |
| product.id | integer | Product ID |
| product.name | string | Product name |
| product.description | string | Product description |
| product.price | number | Product price |
| product.stock | integer | Current stock quantity |
| product.category | string | Category name or null |
| error | string | Error description (for error responses) |

---

## 🚀 Usage Examples

### 1. Create Product with Category

**Request:**
```bash
curl -X POST "http://127.0.0.1:5000/products/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "name": "Gaming Laptop",
    "description": "High-end gaming laptop with RTX graphics",
    "price": 1499.99,
    "stock": 25,
    "category_id": 1
  }'
```

**Response:**
```json
{
  "message": "Product added",
  "product": {
    "id": 1,
    "name": "Gaming Laptop",
    "description": "High-end gaming laptop with RTX graphics",
    "price": 1499.99,
    "stock": 25,
    "category": "Electronics"
  }
}
```

### 2. Create Product Without Category

**Request:**
```bash
curl -X POST "http://127.0.0.1:5000/products/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "name": "Office Chair",
    "description": "Ergonomic office chair",
    "price": 299.99,
    "stock": 15
  }'
```

**Response:**
```json
{
  "message": "Product added",
  "product": {
    "id": 2,
    "name": "Office Chair",
    "description": "Ergonomic office chair",
    "price": 299.99,
    "stock": 15,
    "category": null
  }
}
```

### 3. Create Product with Invalid Data

**Request:**
```bash
curl -X POST "http://127.0.0.1:5000/products/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "name": "Invalid Product",
    "price": -10,
    "stock": -5
  }'
```

**Response:**
```json
{
  "error": "Price must be a positive number"
}
```

### 4. Staff User Access Denied

**Request:**
```bash
curl -X POST "http://127.0.0.1:5000/products/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer STAFF_JWT_TOKEN" \
  -d '{
    "name": "Test Product",
    "price": 10.0,
    "stock": 5
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

### Validation Process

1. **Token Validation**: JWT token is validated using `@jwt_required()` decorator
2. **Role Authorization**: User role is checked using `@role_required("admin", "manager")`
3. **Pydantic Validation**: Product data is validated using `ProductCreate` schema
   - Name: 1-100 characters, required
   - Price: Must be greater than 0
   - Stock: Must be greater than or equal to 0
   - Category ID: Optional, validated if provided
4. **Category Validation**: Category ID is validated if provided
5. **Product Creation**: New product record is created in database
6. **Database Commit**: Product is saved to database
7. **Response**: Returns created product information

### Validation Rules

```python
# Pydantic schema for product creation
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    category_id: Optional[int] = None
```

### Endpoint Implementation

```python
@products_b_p.route("/", methods=["POST"])
@jwt_required()
@role_required("admin","manager")
def add_product():
    data = request.get_json()
    
    try:
        product_data = ProductCreate(**data)
        valid, error = validate_product_data(data)
        if not valid:
            return jsonify({"error": error}), 400
        
        product = product_service.create_product(data)
        return jsonify({"message": "Product added", "product": product.to_dict()}), 201
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
```

### Security Features

- **JWT Authentication**: Requires valid bearer token
- **Role-Based Access**: Only admin and manager roles can create products
- **Input Validation**: Comprehensive data validation
- **Category Validation**: Ensures category exists if specified
- **Database Constraints**: Enforced at database level

### Endpoint Implementation

```python
@products_b_p.route("/", methods=["POST"])
@jwt_required()
@role_required("admin", "manager")
def add_product():
    data = request.get_json()
    valid, error = validate_product_data(data)
    if not valid:
        return jsonify({"error": error}), 400
    
    if not data or 'name' not in data or 'price' not in data:
        return jsonify({"error": "Missing name or price"}), 400
    
    product = product_service.create_product(data)
    return jsonify({"message": "Product added", "product": product.to_dict()}), 201
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

# Create a category first
curl -X POST "http://127.0.0.1:5000/categories/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "name": "Electronics",
    "description": "Electronic devices"
  }'

# Test successful product creation
curl -X POST "http://127.0.0.1:5000/products/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "name": "Test Product",
    "description": "Test description",
    "price": 99.99,
    "stock": 10,
    "category_id": 1
  }'

# Test with missing fields
curl -X POST "http://127.0.0.1:5000/products/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "name": "Incomplete Product"
  }'

# Test with invalid price
curl -X POST "http://127.0.0.1:5000/products/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "name": "Invalid Product",
    "price": -10,
    "stock": 5
  }'

# Test staff access (should fail)
STAFF_TOKEN=$(curl -s -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "staff_user", "password": "staff123"}' \
  | jq -r '.access_token')

curl -X POST "http://127.0.0.1:5000/products/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -d '{
    "name": "Staff Product",
    "price": 10.0,
    "stock": 5
  }'
```

### Python Testing Example

```python
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_create_product():
    # Login as admin
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        admin_token = response.json().get("access_token")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create a category first
        category_data = {"name": "Test Category", "description": "Test category"}
        category_response = requests.post(f"{BASE_URL}/categories/", 
                                         json=category_data, headers=admin_headers)
        
        # Test successful product creation
        product_data = {
            "name": "Test Product",
            "description": "Test description",
            "price": 99.99,
            "stock": 10,
            "category_id": 1
        }
        
        response = requests.post(f"{BASE_URL}/products/", json=product_data, headers=admin_headers)
        print("Create Product Status:", response.status_code)
        print("Create Product Response:", json.dumps(response.json(), indent=2))
        
        # Test validation errors
        invalid_data = {"name": "Invalid", "price": -10, "stock": -5}
        response = requests.post(f"{BASE_URL}/products/", json=invalid_data, headers=admin_headers)
        print("Invalid Data Status:", response.status_code)
        print("Invalid Data Response:", response.json())
        
        # Test missing fields
        missing_data = {"name": "Incomplete"}
        response = requests.post(f"{BASE_URL}/products/", json=missing_data, headers=admin_headers)
        print("Missing Fields Status:", response.status_code)
        print("Missing Fields Response:", response.json())
    
    # Test staff access (should fail)
    staff_login = {"username": "staff_user", "password": "staff123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=staff_login)
    
    if response.status_code == 200:
        staff_token = response.json().get("access_token")
        staff_headers = {"Authorization": f"Bearer {staff_token}"}
        
        product_data = {"name": "Staff Product", "price": 10.0, "stock": 5}
        response = requests.post(f"{BASE_URL}/products/", json=product_data, headers=staff_headers)
        print("Staff Access Status:", response.status_code)
        print("Staff Access Response:", response.json())

if __name__ == "__main__":
    test_create_product()
```

---

## 🐛 Error Handling

### Common Error Scenarios

1. **Missing Required Fields**
   ```json
   {
     "error": "Missing field: stock"
   }
   ```

2. **Invalid Price**
   ```json
   {
     "error": "Price must be a positive number"
   }
   ```

3. **Invalid Stock**
   ```json
   {
     "error": "Stock must be a non-negative integer"
   }
   ```

4. **Invalid Category ID**
   ```json
   {
     "error": "Invalid category ID"
   }
   ```

5. **Insufficient Permissions**
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
| 201 | Product created successfully |
| 400 | Bad request (validation errors) |
| 401 | Unauthorized / Invalid token |
| 403 | Forbidden / Insufficient permissions |
| 500 | Internal server error |

---

## 🔄 Related Endpoints

- **GET /products/**: Get all products
- **GET /products/{product_id}**: Get specific product
- **PUT /products/update**: Update product
- **DELETE /products/delete**: Delete product
- **PATCH /products/discount**: Apply discount to product
- **GET /categories/**: Get all categories

---

## 📝 Notes

- Only admin and manager roles can create products
- Category assignment is optional
- Price must be a positive number
- Stock must be a non-negative integer
- Category ID must reference an existing category
- Product names are not required to be unique
- Description is optional and can be null
- Returns complete product information including category name
- Stock defaults to 0 if not specified (but field is required in current implementation)
