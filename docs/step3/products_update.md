# Update Product API Documentation

## 📋 Overview

The Update Product API provides functionality for authenticated users with appropriate permissions to modify existing product information. This endpoint supports partial updates of product data including name, description, price, stock, and category assignment.

**Endpoint:** `PUT /products/update`  
**Base URL:** `http://127.0.0.1:5000`  
**Authentication:** Required (JWT Bearer Token)  
**Required Role:** `admin`, `manager`

---

## 🔐 API Endpoint

### PUT /products/update

Update an existing product's information.

**URL:** `PUT /products/update`  
**Content-Type:** `application/json`  
**Authentication:** `Bearer {JWT_TOKEN}`  
**Required Role:** `admin`, `manager`

#### Request Body

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| id | integer | Yes | Product ID to update | Must be valid product ID |
| name | string | No | New product name | 1-100 characters |
| description | string | No | New product description | 0-255 characters |
| price | number | No | New product price | Must be positive |
| stock | integer | No | New stock quantity | Must be non-negative |
| category_id | integer | No | New category ID | Must be valid category |

#### Request Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| Authorization | string | Yes | Bearer token for authentication |
| Content-Type | string | Yes | Request content type |

#### Request Examples

**Update product name and price:**
```bash
curl -X PUT "http://127.0.0.1:5000/products/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "id": 1,
    "name": "Updated Laptop Pro",
    "price": 899.99
  }'
```

**Update stock and category:**
```bash
curl -X PUT "http://127.0.0.1:5000/products/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "id": 2,
    "stock": 75,
    "category_id": 1
  }'
```

**Update all fields:**
```bash
curl -X PUT "http://127.0.0.1:5000/products/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "id": 1,
    "name": "Premium Gaming Laptop",
    "description": "High-end gaming laptop with RGB lighting",
    "price": 1299.99,
    "stock": 30,
    "category_id": 1
  }'
```

#### Response

**Success Response (200 OK)**
```json
{
  "message": "Product updated",
  "product": {
    "id": 1,
    "name": "Updated Laptop Pro",
    "description": "High-performance laptop",
    "price": 899.99,
    "stock": 45,
    "category": "Electronics"
  }
}
```

**Error Responses**

**Missing Product ID (400 Bad Request)**
```json
{
  "error": "Product ID is required"
}
```

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
| product | object | Updated product information |
| product.id | integer | Product ID |
| product.name | string | Updated product name |
| product.description | string | Updated product description |
| product.price | number | Updated product price |
| product.stock | integer | Updated stock quantity |
| product.category | string | Category name or null |
| error | string | Error description (for error responses) |

---

## 🚀 Usage Examples

### 1. Update Product Name and Price

**Request:**
```bash
curl -X PUT "http://127.0.0.1:5000/products/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "id": 1,
    "name": "Premium Laptop",
    "price": 1099.99
  }'
```

**Response:**
```json
{
  "message": "Product updated",
  "product": {
    "id": 1,
    "name": "Premium Laptop",
    "description": "High-performance laptop",
    "price": 1099.99,
    "stock": 50,
    "category": "Electronics"
  }
}
```

### 2. Update Stock Only

**Request:**
```bash
curl -X PUT "http://127.0.0.1:5000/products/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "id": 2,
    "stock": 150
  }'
```

**Response:**
```json
{
  "message": "Product updated",
  "product": {
    "id": 2,
    "name": "Wireless Mouse",
    "description": "Ergonomic wireless mouse",
    "price": 29.99,
    "stock": 150,
    "category": "Electronics"
  }
}
```

### 3. Update Category Assignment

**Request:**
```bash
curl -X PUT "http://127.0.0.1:5000/products/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "id": 3,
    "category_id": 2
  }'
```

**Response:**
```json
{
  "message": "Product updated",
  "product": {
    "id": 3,
    "name": "Office Chair",
    "description": "Ergonomic office chair",
    "price": 299.99,
    "stock": 15,
    "category": "Furniture"
  }
}
```

### 4. Update Non-Existent Product

**Request:**
```bash
curl -X PUT "http://127.0.0.1:5000/products/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "id": 999,
    "name": "Non-existent Product"
  }'
```

**Response:**
```json
{
  "error": "Product not found"
}
```

### 5. Staff User Access Denied

**Request:**
```bash
curl -X PUT "http://127.0.0.1:5000/products/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer STAFF_JWT_TOKEN" \
  -d '{
    "id": 1,
    "name": "Staff Update"
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

### Update Process

1. **Token Validation**: JWT token is validated using `@jwt_required()` decorator
2. **Role Authorization**: User role is checked using `@role_required("admin", "manager")`
3. **Input Validation**: Product ID is validated in request body
4. **Product Lookup**: Product is queried from database using service layer
5. **Field Updates**: Updates only provided fields (partial update support)
6. **Validation**: Product data validation is performed during update
7. **Database Commit**: Changes are saved to database
8. **Response**: Returns updated product information

### Partial Update Support

The endpoint supports partial updates - only fields provided in the request body are updated:

```python
# Update only provided fields
for key, value in data.items():
    setattr(product, key, value)
```

### Endpoint Implementation

```python
@products_b_p.route("/update", methods=["PUT"])
@jwt_required()
@role_required("admin", "manager")
def update_product():
    data = request.get_json()
    if "id" not in data:
        return jsonify({"error": "Product ID is required"}), 400

    updated_product = product_service.update_product(data["id"], data)
    if not updated_product:
        return jsonify({"error": "Product not found"}), 404

    return jsonify({"message": "Product updated", "product": updated_product.to_dict()}), 200
```

### Service Layer Method

```python
def update_product(self, product_id, data):
    """Update product information"""
    product = Product.query.get(product_id)
    if not product:
        return None
    
    for key, value in data.items():
        setattr(product, key, value)
    
    db.session.commit()
    return product
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

# Test updating product name and price
curl -X PUT "http://127.0.0.1:5000/products/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "id": 1,
    "name": "Updated Product Name",
    "price": 199.99
  }'

# Test updating stock only
curl -X PUT "http://127.0.0.1:5000/products/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "id": 1,
    "stock": 100
  }'

# Test updating category
curl -X PUT "http://127.0.0.1:5000/products/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "id": 1,
    "category_id": 1
  }'

# Test missing product ID
curl -X PUT "http://127.0.0.1:5000/products/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "name": "Test Update"
  }'

# Test non-existent product
curl -X PUT "http://127.0.0.1:5000/products/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "id": 999,
    "name": "Non-existent"
  }'

# Test staff access (should fail)
STAFF_TOKEN=$(curl -s -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "staff_user", "password": "staff123"}' \
  | jq -r '.access_token')

curl -X PUT "http://127.0.0.1:5000/products/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -d '{
    "id": 1,
    "name": "Staff Update"
  }'
```

### Python Testing Example

```python
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_update_product():
    # Login as admin
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        admin_token = response.json().get("access_token")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Test updating name and price
        update_data = {
            "id": 1,
            "name": "Updated Product",
            "price": 199.99
        }
        
        response = requests.put(f"{BASE_URL}/products/update", json=update_data, headers=admin_headers)
        print("Update Status:", response.status_code)
        print("Update Response:", json.dumps(response.json(), indent=2))
        
        # Test updating stock only
        stock_data = {"id": 1, "stock": 150}
        response = requests.put(f"{BASE_URL}/products/update", json=stock_data, headers=admin_headers)
        print("Stock Update Status:", response.status_code)
        
        # Test missing product ID
        missing_data = {"name": "Test"}
        response = requests.put(f"{BASE_URL}/products/update", json=missing_data, headers=admin_headers)
        print("Missing ID Status:", response.status_code)
        print("Missing ID Response:", response.json())
        
        # Test non-existent product
        non_existent_data = {"id": 999, "name": "Test"}
        response = requests.put(f"{BASE_URL}/products/update", json=non_existent_data, headers=admin_headers)
        print("Non-existent Status:", response.status_code)
        print("Non-existent Response:", response.json())
    
    # Test staff access (should fail)
    staff_login = {"username": "staff_user", "password": "staff123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=staff_login)
    
    if response.status_code == 200:
        staff_token = response.json().get("access_token")
        staff_headers = {"Authorization": f"Bearer {staff_token}"}
        
        update_data = {"id": 1, "name": "Staff Update"}
        response = requests.put(f"{BASE_URL}/products/update", json=update_data, headers=staff_headers)
        print("Staff Access Status:", response.status_code)
        print("Staff Access Response:", response.json())

if __name__ == "__main__":
    test_update_product()
```

---

## 🐛 Error Handling

### Common Error Scenarios

1. **Missing Product ID**
   ```json
   {
     "error": "Product ID is required"
   }
   ```

2. **Product Not Found**
   ```json
   {
     "error": "Product not found"
   }
   ```

3. **Insufficient Permissions**
   ```json
   {
     "error": {
       "type": "Forbidden",
       "message": "Access forbidden: insufficient permissions.",
       "status_code": 403
     }
   }
   ```

4. **Database Constraint Violation** (if category doesn't exist)
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
| 200 | Product updated successfully |
| 400 | Bad request (missing product ID) |
| 401 | Unauthorized / Invalid token |
| 403 | Forbidden / Insufficient permissions |
| 404 | Product not found |
| 500 | Internal server error |

---

## 🔄 Related Endpoints

- **POST /products/**: Create new product
- **GET /products/**: Get all products
- **GET /products/{product_id}**: Get specific product
- **DELETE /products/delete**: Delete product
- **PATCH /products/discount**: Apply discount to product
- **GET /categories/**: Get all categories

---

## 📝 Notes

- Only admin and manager roles can update products
- Supports partial updates (only provided fields are updated)
- Product ID must be provided in request body
- Category ID must reference an existing category
- No validation for price/stock positivity during update (handled by database)
- Returns complete updated product information
- Consider implementing field validation in update operations
- No audit logging for product changes
- Database constraints prevent invalid data
- Product name uniqueness is not enforced
