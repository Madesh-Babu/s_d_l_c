# Get Product by ID API Documentation

## 📋 Overview

The Get Product by ID API provides functionality for authenticated users to retrieve a specific product's information using its unique identifier. This endpoint returns detailed product information including category details.

**Endpoint:** `GET /products/{product_id}`  
**Base URL:** `http://127.0.0.1:5000`  
**Authentication:** Required (JWT Bearer Token)

---

## 🔐 API Endpoint

### GET /products/{product_id}

Retrieve a specific product by its ID.

**URL:** `GET /products/{product_id}`  
**Content-Type:** `application/json`  
**Authentication:** `Bearer {JWT_TOKEN}`  
**Required Role:** Any authenticated user

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| product_id | integer | Yes | Unique product identifier |

#### Request Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| Authorization | string | Yes | Bearer token for authentication |

#### Request Examples

**Get product by ID with admin token:**
```bash
curl -X GET "http://127.0.0.1:5000/products/1" \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN_HERE"
```

**Get product by ID with staff token:**
```bash
curl -X GET "http://127.0.0.1:5000/products/2" \
  -H "Authorization: Bearer YOUR_STAFF_JWT_TOKEN_HERE"
```

**Get product by ID with manager token:**
```bash
curl -X GET "http://127.0.0.1:5000/products/3" \
  -H "Authorization: Bearer YOUR_MANAGER_JWT_TOKEN_HERE"
```

#### Response

**Success Response (200 OK)**
```json
{
  "id": 1,
  "name": "Laptop Pro",
  "description": "High-performance laptop with latest specs",
  "price": 999.99,
  "stock": 50,
  "category": "Electronics"
}
```

**Success Response (200 OK) - Without Category**
```json
{
  "id": 3,
  "name": "Office Chair",
  "description": "Ergonomic office chair",
  "price": 299.99,
  "stock": 15,
  "category": null
}
```

**Error Responses**

**Product Not Found (404 Not Found)**
```json
{
  "error": "Product not found"
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

**Invalid Product ID (404 Not Found)**
```bash
curl -X GET "http://127.0.0.1:5000/products/999" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**Response:**
```json
{
  "error": "Product not found"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique product identifier |
| name | string | Product name |
| description | string | Product description (can be null) |
| price | number | Product price |
| stock | integer | Current stock quantity |
| category | string | Category name or null |

---

## 🚀 Usage Examples

### 1. Get Specific Product (Admin)

**Request:**
```bash
curl -X GET "http://127.0.0.1:5000/products/1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "id": 1,
  "name": "Gaming Laptop",
  "description": "High-end gaming laptop with RTX 4090",
  "price": 1499.99,
  "stock": 25,
  "category": "Electronics"
}
```

### 2. Get Product Without Category

**Request:**
```bash
curl -X GET "http://127.0.0.1:5000/products/3" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "id": 3,
  "name": "Standing Desk",
  "description": "Adjustable standing desk",
  "price": 499.99,
  "stock": 8,
  "category": null
}
```

### 3. Get Product with Staff Role

**Request:**
```bash
curl -X GET "http://127.0.0.1:5000/products/2" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:** (Same as admin - all authenticated users can access)

### 4. Product Not Found

**Request:**
```bash
curl -X GET "http://127.0.0.1:5000/products/999" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "error": "Product not found"
}
```

### 5. Unauthorized Access

**Request:**
```bash
curl -X GET "http://127.0.0.1:5000/products/1"
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
3. **Parameter Validation**: Product ID is extracted from URL path
4. **Product Lookup**: Product is queried from database using service layer
5. **Data Serialization**: Product data is converted to dictionary format
6. **Category Resolution**: Category name is resolved if product has category
7. **Response**: Returns product information or 404 if not found

### Endpoint Implementation

```python
@products_b_p.route("/<int:product_id>", methods=["GET"])
@jwt_required()
def get_products(product_id):
    product = product_service.get_products(product_id)
    if not product:
        return jsonify({'error': "Product not found"}), 404
    return jsonify(product.to_dict())
```

### Service Layer Method

```python
def get_products(self, product_id):
    """Get a specific product by ID"""
    return Product.query.get(product_id)
```

### Data Serialization

```python
# Product model serialization
def to_dict(self):
    return {
        "id": self.id,
        "name": self.name,
        "description": self.description,
        "price": self.price,
        "stock": self.stock,
        "category": self.category.name if self.category else None,
    }
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

# Test existing product
curl -X GET "http://127.0.0.1:5000/products/1" \
  -H "Authorization: Bearer $TOKEN"

# Test non-existent product
curl -X GET "http://127.0.0.1:5000/products/999" \
  -H "Authorization: Bearer $TOKEN"

# Test invalid product ID (non-integer)
curl -X GET "http://127.0.0.1:5000/products/invalid" \
  -H "Authorization: Bearer $TOKEN"

# Test without token
curl -X GET "http://127.0.0.1:5000/products/1"

# Test with different user roles
for role in "staff" "manager" "admin"; do
  ROLE_TOKEN=$(curl -s -X POST "http://127.0.0.1:5000/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"${role}_user\", \"password\": \"${role}123\"}" \
    | jq -r '.access_token')
  
  echo "Testing ${role} access to product 1:"
  curl -X GET "http://127.0.0.1:5000/products/1" \
    -H "Authorization: Bearer $ROLE_TOKEN"
done
```

### Python Testing Example

```python
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_get_product_by_id():
    # Login as admin
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test existing product
        product_response = requests.get(f"{BASE_URL}/products/1", headers=headers)
        print("Get Product Status:", product_response.status_code)
        print("Product Response:", json.dumps(product_response.json(), indent=2))
        
        # Test product without category
        no_category_response = requests.get(f"{BASE_URL}/products/3", headers=headers)
        print("No Category Product Status:", no_category_response.status_code)
        print("No Category Product Response:", json.dumps(no_category_response.json(), indent=2))
        
        # Test non-existent product
        not_found_response = requests.get(f"{BASE_URL}/products/999", headers=headers)
        print("Not Found Status:", not_found_response.status_code)
        print("Not Found Response:", not_found_response.json())
        
        # Test with different user roles
        for role in ["staff", "manager"]:
            role_login = {"username": f"{role}_user", "password": f"{role}123"}
            role_response = requests.post(f"{BASE_URL}/auth/login", json=role_login)
            
            if role_response.status_code == 200:
                role_token = role_response.json().get("access_token")
                role_headers = {"Authorization": f"Bearer {role_token}"}
                
                product_response = requests.get(f"{BASE_URL}/products/1", headers=role_headers)
                print(f"{role.title()} Access Status:", product_response.status_code)
    
    # Test unauthorized access
    unauthorized_response = requests.get(f"{BASE_URL}/products/1")
    print("Unauthorized Status:", unauthorized_response.status_code)
    print("Unauthorized Response:", unauthorized_response.json())

if __name__ == "__main__":
    test_get_product_by_id()
```

---

## 🐛 Error Handling

### Common Error Scenarios

1. **Product Not Found**
   ```json
   {
     "error": "Product not found"
   }
   ```

2. **Invalid Product ID (Non-integer)**
   ```json
   {
     "error": "Product not found"
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
| 200 | Product retrieved successfully |
| 401 | Unauthorized / Invalid token |
| 404 | Product not found / Invalid product ID |
| 500 | Internal server error |

### URL Parameter Handling

- Flask automatically converts `<int:product_id>` to integer
- Invalid integer URLs return 404 before reaching the function
- Non-integer URLs also return 404
- Valid integer but non-existent product returns 404

---

## 🔄 Related Endpoints

- **POST /products/**: Create new product
- **GET /products/**: Get all products
- **PUT /products/update**: Update product
- **DELETE /products/delete**: Delete product
- **PATCH /products/discount**: Apply discount to product
- **GET /categories/**: Get all categories

---

## 📝 Notes

- Returns product information regardless of the requesting user's role
- Category name is resolved and included if product has a category
- Products without categories show `null` for category field
- Uses service layer for database operations
- Simple 404 response for not found cases
- URL parameter validation is handled automatically by Flask
- No pagination needed as it returns single product
- Consider implementing caching for frequently accessed products
- Response includes all product fields including stock and price information
