# Delete Product API Documentation

## 📋 Overview

The Delete Product API provides functionality for authenticated users with admin privileges to permanently remove products from the inventory system. This endpoint deletes product records and the action is irreversible.

**Endpoint:** `DELETE /products/delete`  
**Base URL:** `http://127.0.0.1:5000`  
**Authentication:** Required (JWT Bearer Token)  
**Required Role:** `admin`

---

## 🔐 API Endpoint

### DELETE /products/delete

Delete a product from the inventory.

**URL:** `DELETE /products/delete`  
**Content-Type:** `application/json`  
**Authentication:** `Bearer {JWT_TOKEN}`  
**Required Role:** `admin`

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | Yes | Product ID to delete |

#### Request Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| Authorization | string | Yes | Bearer token for authentication |
| Content-Type | string | Yes | Request content type |

#### Request Examples

**Delete product with admin token:**
```bash
curl -X DELETE "http://127.0.0.1:5000/products/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN_HERE" \
  -d '{
    "id": 3
  }'
```

**Delete multiple products (separate requests):**
```bash
curl -X DELETE "http://127.0.0.1:5000/products/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN_HERE" \
  -d '{
    "id": 1
  }'

curl -X DELETE "http://127.0.0.1:5000/products/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN_HERE" \
  -d '{
    "id": 2
  }'
```

#### Response

**Success Response (200 OK)**
```json
{
  "message": "Product deleted"
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
| error | string | Error description (for error responses) |

---

## 🚀 Usage Examples

### 1. Delete Product (Admin)

**Request:**
```bash
curl -X DELETE "http://127.0.0.1:5000/products/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "id": 3
  }'
```

**Response:**
```json
{
  "message": "Product deleted"
}
```

### 2. Delete High-Value Product

**Request:**
```bash
curl -X DELETE "http://127.0.0.1:5000/products/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "id": 1
  }'
```

**Response:**
```json
{
  "message": "Product deleted"
}
```

### 3. Delete Non-Existent Product

**Request:**
```bash
curl -X DELETE "http://127.0.0.1:5000/products/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "id": 999
  }'
```

**Response:**
```json
{
  "error": "Product not found"
}
```

### 4. Missing Product ID

**Request:**
```bash
curl -X DELETE "http://127.0.0.1:5000/products/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "name": "test"
  }'
```

**Response:**
```json
{
  "error": "Product ID is required"
}
```

### 5. Manager User Access Denied

**Request:**
```bash
curl -X DELETE "http://127.0.0.1:5000/products/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_MANAGER_JWT_TOKEN_HERE" \
  -d '{
    "id": 2
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

### 6. Staff User Access Denied

**Request:**
```bash
curl -X DELETE "http://127.0.0.1:5000/products/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_STAFF_JWT_TOKEN_HERE" \
  -d '{
    "id": 2
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

### Deletion Process

1. **Token Validation**: JWT token is validated using `@jwt_required()` decorator
2. **Role Authorization**: User role is checked using `@role_required("admin")`
3. **Input Validation**: Product ID is validated in request body
4. **Product Lookup**: Product is queried from database using service layer
5. **Database Deletion**: Product record is removed from database
6. **Database Commit**: Deletion is permanently saved
7. **Response**: Returns success message

### Security Features

- **Admin-Only Access**: Only admin role can delete products
- **Permanent Deletion**: Action is irreversible
- **Database Constraints**: Referential integrity handled by database
- **Input Validation**: Validates product ID is provided

### Endpoint Implementation

```python
@products_b_p.route("/delete", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete_product():
    data = request.get_json()
    if "id" not in data:
        return jsonify({"error": "Product ID is required"}), 400

    success = product_service.delete_product(data["id"])
    if not success:
        return jsonify({"error": "Product not found"}), 404

    return jsonify({"message": "Product deleted"}), 200
```

### Service Layer Method

```python
def delete_product(self, product_id):
    """Delete a product by ID"""
    product = Product.query.get(product_id)
    if not product:
        return False
    
    db.session.delete(product)
    db.session.commit()
    return True
```

### Database Considerations

- **Cascade Deletes**: Related data may be affected by database constraints
- **Foreign Keys**: Other tables referencing products may have cascade rules
- **Transaction Safety**: Deletion is wrapped in database transaction
- **Irreversible Action**: Cannot undo deletion once committed

---

## 🧪 Testing

### Manual Testing with cURL

```bash
# First, get authentication token for admin
ADMIN_TOKEN=$(curl -s -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | jq -r '.access_token')

# Create a test product first
curl -X POST "http://127.0.0.1:5000/products/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "name": "Test Product for Deletion",
    "price": 99.99,
    "stock": 10
  }'

# Test successful deletion
curl -X DELETE "http://127.0.0.1:5000/products/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "id": 1
  }'

# Test deleting non-existent product
curl -X DELETE "http://127.0.0.1:5000/products/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "id": 999
  }'

# Test missing product ID
curl -X DELETE "http://127.0.0.1:5000/products/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "name": "test"
  }'

# Test manager access (should fail)
MANAGER_TOKEN=$(curl -s -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "manager_user", "password": "manager123"}' \
  | jq -r '.access_token')

curl -X DELETE "http://127.0.0.1:5000/products/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MANAGER_TOKEN" \
  -d '{
    "id": 2
  }'

# Test staff access (should fail)
STAFF_TOKEN=$(curl -s -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "staff_user", "password": "staff123"}' \
  | jq -r '.access_token')

curl -X DELETE "http://127.0.0.1:5000/products/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -d '{
    "id": 2
  }'
```

### Python Testing Example

```python
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_delete_product():
    # Login as admin
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        admin_token = response.json().get("access_token")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # First, create a test product to delete
        product_data = {
            "name": "Test Product for Deletion",
            "description": "This product will be deleted",
            "price": 99.99,
            "stock": 10
        }
        
        create_response = requests.post(f"{BASE_URL}/products/", json=product_data, headers=admin_headers)
        print("Create Product Status:", create_response.status_code)
        
        if create_response.status_code == 201:
            # Get the product ID (assuming it's the last created product)
            products_response = requests.get(f"{BASE_URL}/products/", headers=admin_headers)
            if products_response.status_code == 200:
                products = products_response.json()
                test_product_id = max([product["id"] for product in products]) if products else None
                
                if test_product_id:
                    # Test deleting the product
                    delete_data = {"id": test_product_id}
                    delete_response = requests.delete(f"{BASE_URL}/products/delete", 
                                                    json=delete_data, headers=admin_headers)
                    print("Delete Status:", delete_response.status_code)
                    print("Delete Response:", delete_response.json())
        
        # Test deleting non-existent product
        non_existent_data = {"id": 999}
        non_existent_response = requests.delete(f"{BASE_URL}/products/delete", 
                                                json=non_existent_data, headers=admin_headers)
        print("Non-existent Delete Status:", non_existent_response.status_code)
        print("Non-existent Delete Response:", non_existent_response.json())
        
        # Test missing product ID
        missing_data = {"name": "test"}
        missing_response = requests.delete(f"{BASE_URL}/products/delete", 
                                          json=missing_data, headers=admin_headers)
        print("Missing ID Status:", missing_response.status_code)
        print("Missing ID Response:", missing_response.json())
    
    # Test manager access (should fail)
    manager_login = {"username": "manager_user", "password": "manager123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=manager_login)
    
    if response.status_code == 200:
        manager_token = response.json().get("access_token")
        manager_headers = {"Authorization": f"Bearer {manager_token}"}
        
        delete_data = {"id": 1}
        manager_response = requests.delete(f"{BASE_URL}/products/delete", 
                                         json=delete_data, headers=manager_headers)
        print("Manager Access Status:", manager_response.status_code)
        print("Manager Access Response:", manager_response.json())
    
    # Test staff access (should fail)
    staff_login = {"username": "staff_user", "password": "staff123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=staff_login)
    
    if response.status_code == 200:
        staff_token = response.json().get("access_token")
        staff_headers = {"Authorization": f"Bearer {staff_token}"}
        
        delete_data = {"id": 1}
        staff_response = requests.delete(f"{BASE_URL}/products/delete", 
                                       json=delete_data, headers=staff_headers)
        print("Staff Access Status:", staff_response.status_code)
        print("Staff Access Response:", staff_response.json())

if __name__ == "__main__":
    test_delete_product()
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

3. **Insufficient Permissions (Manager)**
   ```json
   {
     "error": {
       "type": "Forbidden",
       "message": "Access forbidden: insufficient permissions.",
       "status_code": 403
     }
   }
   ```

4. **Insufficient Permissions (Staff)**
   ```json
   {
     "error": {
       "type": "Forbidden",
       "message": "Access forbidden: insufficient permissions.",
       "status_code": 403
     }
   }
   ```

5. **Database Constraint Violation** (if product has related data)
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
| 200 | Product deleted successfully |
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
- **PUT /products/update**: Update product
- **PATCH /products/discount**: Apply discount to product
- **GET /categories/**: Get all categories

---

## 📝 Notes

- Only admin role can delete products (most restrictive permission)
- Deletion is permanent and cannot be undone
- No soft delete implementation - records are permanently removed
- Database constraints may prevent deletion if product has related data
- Simple success message without product details
- No confirmation step required - deletion is immediate
- Consider implementing soft delete or audit logging in production
- No return of deleted product information
- Product ID must be provided in request body (not URL parameter)
- All other roles (manager, staff) are explicitly denied access
