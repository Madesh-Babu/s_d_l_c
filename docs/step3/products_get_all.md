# Get All Products API Documentation

## 📋 Overview

The Get All Products API provides functionality for authenticated users to retrieve all products in the inventory system. This endpoint returns a comprehensive list of products with their details including category information.

**Endpoint:** `GET /products/`  
**Base URL:** `http://127.0.0.1:5000`  
**Authentication:** Required (JWT Bearer Token)

---

## 🔐 API Endpoint

### GET /products/

Retrieve all products in the inventory.

**URL:** `GET /products/`  
**Content-Type:** `application/json`  
**Authentication:** `Bearer {JWT_TOKEN}`  
**Required Role:** Any authenticated user

#### Request Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| Authorization | string | Yes | Bearer token for authentication |

#### Request Examples

**Get all products with admin token:**
```bash
curl -X GET "http://127.0.0.1:5000/products/" \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN_HERE"
```

**Get all products with staff token:**
```bash
curl -X GET "http://127.0.0.1:5000/products/" \
  -H "Authorization: Bearer YOUR_STAFF_JWT_TOKEN_HERE"
```

**Get all products with manager token:**
```bash
curl -X GET "http://127.0.0.1:5000/products/" \
  -H "Authorization: Bearer YOUR_MANAGER_JWT_TOKEN_HERE"
```

#### Response

**Success Response (200 OK)**
```json
[
  {
    "id": 1,
    "name": "Laptop Pro",
    "description": "High-performance laptop",
    "price": 999.99,
    "stock": 50,
    "category": "Electronics"
  },
  {
    "id": 2,
    "name": "Wireless Mouse",
    "description": "Ergonomic wireless mouse",
    "price": 29.99,
    "stock": 100,
    "category": "Electronics"
  },
  {
    "id": 3,
    "name": "Office Chair",
    "description": "Ergonomic office chair",
    "price": 299.99,
    "stock": 15,
    "category": null
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
| id | integer | Unique product identifier |
| name | string | Product name |
| description | string | Product description (can be null) |
| price | number | Product price |
| stock | integer | Current stock quantity |
| category | string | Category name or null |

---

## 🚀 Usage Examples

### 1. Get All Products (Admin)

**Request:**
```bash
curl -X GET "http://127.0.0.1:5000/products/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Gaming Laptop",
    "description": "High-end gaming laptop with RTX graphics",
    "price": 1499.99,
    "stock": 25,
    "category": "Electronics"
  },
  {
    "id": 2,
    "name": "Mechanical Keyboard",
    "description": "RGB mechanical keyboard",
    "price": 89.99,
    "stock": 40,
    "category": "Electronics"
  }
]
```

### 2. Get All Products (Staff User)

**Request:**
```bash
curl -X GET "http://127.0.0.1:5000/products/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:** (Same as admin - all authenticated users can access)

### 3. Empty Product List

**Request:**
```bash
curl -X GET "http://127.0.0.1:5000/products/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
[]
```

### 4. Unauthorized Access

**Request:**
```bash
curl -X GET "http://127.0.0.1:5000/products/"
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
3. **Data Retrieval**: All products are queried from database
4. **Data Serialization**: Product data is converted to dictionary format
5. **Category Resolution**: Category names are resolved for each product
6. **Response**: Returns list of products with category information

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

### Endpoint Implementation

```python
@products_b_p.route("/", methods=["GET"])
@jwt_required()
def get_all_products():
    products = product_service.get_all_products()
    return jsonify([p.to_dict() for p in products])
```

### Category Resolution

The endpoint automatically resolves category names:
- Products with categories show the category name
- Products without categories show `null`
- Category lookup is performed for each product

---

## 🧪 Testing

### Manual Testing with cURL

```bash
# First, get authentication token
TOKEN=$(curl -s -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | jq -r '.access_token')

# Get all products
curl -X GET "http://127.0.0.1:5000/products/" \
  -H "Authorization: Bearer $TOKEN"

# Test with different user roles
for role in "staff" "manager" "admin"; do
  ROLE_TOKEN=$(curl -s -X POST "http://127.0.0.1:5000/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"${role}_user\", \"password\": \"${role}123\"}" \
    | jq -r '.access_token')
  
  echo "Testing with ${role} token:"
  curl -X GET "http://127.0.0.1:5000/products/" \
    -H "Authorization: Bearer $ROLE_TOKEN"
done

# Test without token
curl -X GET "http://127.0.0.1:5000/products/"

# Test with invalid token
curl -X GET "http://127.0.0.1:5000/products/" \
  -H "Authorization: Bearer invalid_token"
```

### Python Testing Example

```python
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_get_all_products():
    # Test with different user roles
    roles = ["admin", "manager", "staff"]
    
    for role in roles:
        # Login
        login_data = {"username": f"{role}_user", "password": f"{role}123"}
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get all products
            products_response = requests.get(f"{BASE_URL}/products/", headers=headers)
            print(f"{role.title()} User Access Status:", products_response.status_code)
            
            if products_response.status_code == 200:
                products = products_response.json()
                print(f"{role.title()} User Products Count:", len(products))
                if products:
                    print(f"Sample Product: {products[0]['name']}")
            else:
                print(f"{role.title()} User Error:", products_response.json())
    
    # Test unauthorized access
    unauthorized_response = requests.get(f"{BASE_URL}/products/")
    print("Unauthorized Status:", unauthorized_response.status_code)
    print("Unauthorized Response:", unauthorized_response.json())

if __name__ == "__main__":
    test_get_all_products()
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
| 200 | Products retrieved successfully |
| 401 | Unauthorized / Invalid token |
| 500 | Internal server error |

### Performance Considerations

- **No Pagination**: Returns all products at once (consider pagination for large datasets)
- **Category Lookup**: Performs database joins for category resolution
- **Memory Usage**: Large product lists may consume significant memory
- **Response Size**: Response size grows with product count

---

## 🔄 Related Endpoints

- **POST /products/**: Create new product
- **GET /products/{product_id}**: Get specific product
- **PUT /products/update**: Update product
- **DELETE /products/delete**: Delete product
- **PATCH /products/discount**: Apply discount to product
- **GET /categories/**: Get all categories

---

## 📝 Notes

- All authenticated users (staff, manager, admin) can access this endpoint
- Products are returned in database order (typically by creation time)
- Category names are resolved and included in response
- Products without categories show `null` for category field
- No pagination implemented (returns all products)
- Empty array returned when no products exist
- Consider implementing pagination for production use
- Response size depends on number of products in database
- Category lookup may impact performance with large datasets
