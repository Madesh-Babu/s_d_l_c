# Apply Product Discount API Documentation

## 📋 Overview

The Apply Product Discount API provides functionality for authenticated users with appropriate permissions to apply discounts and taxes to products. This endpoint uses a decorator pattern for flexible price calculations and updates product prices permanently.

**Endpoint:** `PATCH /products/discount`  
**Base URL:** `http://127.0.0.1:5000`  
**Authentication:** Required (JWT Bearer Token)  
**Required Role:** `admin`, `manager`

---

## 🔐 API Endpoint

### PATCH /products/discount

Apply discount and tax to a product.

**URL:** `PATCH /products/discount`  
**Content-Type:** `application/json`  
**Authentication:** `Bearer {JWT_TOKEN}`  
**Required Role:** `admin`, `manager`

#### Request Body

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| id | integer | Yes | Product ID to apply discount | Must be valid product ID |
| discount | number | Yes | Discount percentage | 1-100 |
| tax | number | No | Tax percentage | 0-50 |

#### Request Headers

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| Authorization | string | Yes | Bearer token for authentication |
| Content-Type | string | Yes | Request content type |

#### Request Examples

**Apply 10% discount:**
```bash
curl -X PATCH "http://127.0.0.1:5000/products/discount" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "id": 1,
    "discount": 10
  }'
```

**Apply 15% discount with 5% tax:**
```bash
curl -X PATCH "http://127.0.0.1:5000/products/discount" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "id": 2,
    "discount": 15,
    "tax": 5
  }'
```

**Apply 20% discount with 8% tax:**
```bash
curl -X PATCH "http://127.0.0.1:5000/products/discount" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "id": 3,
    "discount": 20,
    "tax": 8
  }'
```

#### Response

**Success Response (200 OK)**
```json
{
  "message": "Applied 10% discount and 0% tax",
  "new_price": 899.99
}
```

**Success Response (200 OK) - With Tax**
```json
{
  "message": "Applied 15% discount and 5% tax",
  "new_price": 1274.96
}
```

**Error Responses**

**Missing Required Fields (400 Bad Request)**
```json
{
  "error": "Product ID and discount percentage are required"
}
```

**Invalid Discount (400 Bad Request)**
```json
{
  "error": "Discount must be a number between 1 and 100"
}
```

**Invalid Tax (400 Bad Request)**
```json
{
  "error": "Tax must be between 0 and 50"
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
| message | string | Success message with applied percentages |
| new_price | number | Updated product price after discount and tax |
| error | string | Error description (for error responses) |

---

## 🚀 Usage Examples

### 1. Apply 10% Discount Only

**Request:**
```bash
curl -X PATCH "http://127.0.0.1:5000/products/discount" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "id": 1,
    "discount": 10
  }'
```

**Response:**
```json
{
  "message": "Applied 10% discount and 0% tax",
  "new_price": 899.99
}
```

### 2. Apply Discount with Tax

**Request:**
```bash
curl -X PATCH "http://127.0.0.1:5000/products/discount" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "id": 2,
    "discount": 15,
    "tax": 5
  }'
```

**Response:**
```json
{
  "message": "Applied 15% discount and 5% tax",
  "new_price": 1274.96
}
```

### 3. Apply Maximum Discount

**Request:**
```bash
curl -X PATCH "http://127.0.0.1:5000/products/discount" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "id": 3,
    "discount": 50,
    "tax": 10
  }'
```

**Response:**
```json
{
  "message": "Applied 50% discount and 10% tax",
  "new_price": 549.95
}
```

### 4. Invalid Discount Percentage

**Request:**
```bash
curl -X PATCH "http://127.0.0.1:5000/products/discount" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "id": 1,
    "discount": 150
  }'
```

**Response:**
```json
{
  "error": "Discount must be a number between 1 and 100"
}
```

### 5. Invalid Tax Percentage

**Request:**
```bash
curl -X PATCH "http://127.0.0.1:5000/products/discount" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "id": 1,
    "discount": 10,
    "tax": 75
  }'
```

**Response:**
```json
{
  "error": "Tax must be between 0 and 50"
}
```

### 6. Staff User Access Denied

**Request:**
```bash
curl -X PATCH "http://127.0.0.1:5000/products/discount" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer STAFF_JWT_TOKEN" \
  -d '{
    "id": 1,
    "discount": 10
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

### Discount Calculation Process

1. **Token Validation**: JWT token is validated using `@jwt_required()` decorator
2. **Role Authorization**: User role is checked using `@role_required("admin", "manager")`
3. **Input Validation**: Validates required fields and parameter ranges
4. **Product Lookup**: Product is queried from database
5. **Price Calculation**: Applies discount first, then tax using decorator pattern
6. **Price Update**: Updates product price in database
7. **Response**: Returns new price and applied percentages

### Price Calculation Logic

The discount system uses a decorator pattern:

```python
# Apply discount first
base_price = Price(product.price)
discounted = DiscountDecorator(base_price, discount_percentage)

# Then apply tax if specified
if tax_percentage > 0:
    final_price = TaxDecorator(discounted, tax_percentage).get_price()
else:
    final_price = discounted.get_price()

# Round to 2 decimal places
product.price = round(final_price, 2)
```

### Decorator Pattern Implementation

```python
class Price(IPrice):
    """Base class representing the original price"""
    def __init__(self, base_price: float):
        self._base_price = base_price
    
    def get_price(self):
        return self._base_price

class DiscountDecorator(PriceDecorator):
    """Applies discount to the base price"""
    def get_price(self):
        base = self._price_component.get_price()
        return base - (base * (self.discount_percent / 100))

class TaxDecorator(PriceDecorator):
    """Adds tax to the price after discount"""
    def get_price(self):
        base = self._price_component.get_price()
        return base + (base * (self.tax_percent / 100))
```

### Endpoint Implementation

```python
@products_b_p.route("/discount", methods=["PATCH"])
@jwt_required()
@role_required("admin", "manager")
def discount_product():
    data = request.get_json()

    if not data or "id" not in data or "discount" not in data:
        return jsonify({"error": "Product ID and discount percentage are required"}), 400
    
    product_id = data["id"]
    discount = data["discount"]
    tax = data.get("tax", 0)

    # Validate discount range
    if not isinstance(discount, (int, float)) or discount <= 0 or discount > 100:
        return jsonify({"error": "Discount must be a number between 1 and 100"}), 400
    
    # Validate tax range
    if not isinstance(tax, (int, float)) or tax < 0 or tax > 50:
        return jsonify({"error": "Tax must be between 0 and 50"}), 400
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    updated = DiscountedProductService.apply_discount(product, discount, tax)
    return jsonify({
        "message": f"Applied {discount}% discount and {tax}% tax",
        "new_price": updated.price
    }), 200
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

# Create a test product first
curl -X POST "http://127.0.0.1:5000/products/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "name": "Test Product for Discount",
    "price": 1000.00,
    "stock": 10
  }'

# Test applying 10% discount
curl -X PATCH "http://127.0.0.1:5000/products/discount" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "id": 1,
    "discount": 10
  }'

# Test applying discount with tax
curl -X PATCH "http://127.0.0.1:5000/products/discount" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "id": 1,
    "discount": 15,
    "tax": 5
  }'

# Test invalid discount
curl -X PATCH "http://127.0.0.1:5000/products/discount" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "id": 1,
    "discount": 150
  }'

# Test invalid tax
curl -X PATCH "http://127.0.0.1:5000/products/discount" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "id": 1,
    "discount": 10,
    "tax": 75
  }'

# Test missing fields
curl -X PATCH "http://127.0.0.1:5000/products/discount" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "id": 1
  }'

# Test staff access (should fail)
STAFF_TOKEN=$(curl -s -X POST "http://127.0.0.1:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "staff_user", "password": "staff123"}' \
  | jq -r '.access_token')

curl -X PATCH "http://127.0.0.1:5000/products/discount" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -d '{
    "id": 1,
    "discount": 10
  }'
```

### Python Testing Example

```python
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_product_discount():
    # Login as admin
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        admin_token = response.json().get("access_token")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create a test product
        product_data = {
            "name": "Test Product for Discount",
            "description": "Product to test discount functionality",
            "price": 1000.00,
            "stock": 10
        }
        
        create_response = requests.post(f"{BASE_URL}/products/", json=product_data, headers=admin_headers)
        print("Create Product Status:", create_response.status_code)
        
        if create_response.status_code == 201:
            # Get the product ID
            products_response = requests.get(f"{BASE_URL}/products/", headers=admin_headers)
            if products_response.status_code == 200:
                products = products_response.json()
                test_product_id = max([product["id"] for product in products]) if products else None
                
                if test_product_id:
                    # Test applying 10% discount
                    discount_data = {"id": test_product_id, "discount": 10}
                    discount_response = requests.patch(f"{BASE_URL}/products/discount", 
                                                     json=discount_data, headers=admin_headers)
                    print("10% Discount Status:", discount_response.status_code)
                    print("10% Discount Response:", discount_response.json())
                    
                    # Test applying discount with tax
                    tax_data = {"id": test_product_id, "discount": 15, "tax": 5}
                    tax_response = requests.patch(f"{BASE_URL}/products/discount", 
                                               json=tax_data, headers=admin_headers)
                    print("Discount + Tax Status:", tax_response.status_code)
                    print("Discount + Tax Response:", tax_response.json())
        
        # Test validation errors
        invalid_discount = {"id": 1, "discount": 150}
        response = requests.patch(f"{BASE_URL}/products/discount", 
                                  json=invalid_discount, headers=admin_headers)
        print("Invalid Discount Status:", response.status_code)
        print("Invalid Discount Response:", response.json())
        
        invalid_tax = {"id": 1, "discount": 10, "tax": 75}
        response = requests.patch(f"{BASE_URL}/products/discount", 
                                  json=invalid_tax, headers=admin_headers)
        print("Invalid Tax Status:", response.status_code)
        print("Invalid Tax Response:", response.json())
        
        # Test missing fields
        missing_data = {"id": 1}
        response = requests.patch(f"{BASE_URL}/products/discount", 
                                  json=missing_data, headers=admin_headers)
        print("Missing Fields Status:", response.status_code)
        print("Missing Fields Response:", response.json())
    
    # Test staff access (should fail)
    staff_login = {"username": "staff_user", "password": "staff123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=staff_login)
    
    if response.status_code == 200:
        staff_token = response.json().get("access_token")
        staff_headers = {"Authorization": f"Bearer {staff_token}"}
        
        discount_data = {"id": 1, "discount": 10}
        staff_response = requests.patch(f"{BASE_URL}/products/discount", 
                                       json=discount_data, headers=staff_headers)
        print("Staff Access Status:", staff_response.status_code)
        print("Staff Access Response:", staff_response.json())

if __name__ == "__main__":
    test_product_discount()
```

---

## 🐛 Error Handling

### Common Error Scenarios

1. **Missing Required Fields**
   ```json
   {
     "error": "Product ID and discount percentage are required"
   }
   ```

2. **Invalid Discount Range**
   ```json
   {
     "error": "Discount must be a number between 1 and 100"
   }
   ```

3. **Invalid Tax Range**
   ```json
   {
     "error": "Tax must be between 0 and 50"
   }
   ```

4. **Product Not Found**
   ```json
   {
     "error": "Product not found"
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
| 200 | Discount applied successfully |
| 400 | Bad request (validation errors) |
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
- **DELETE /products/delete**: Delete product
- **GET /categories/**: Get all categories

---

## 📝 Notes

- Only admin and manager roles can apply discounts
- Discount is applied first, then tax (if specified)
- Price changes are permanent and update the database
- Uses decorator pattern for flexible price calculations
- Discount must be between 1 and 100 percent
- Tax must be between 0 and 50 percent
- Tax is optional (defaults to 0 if not specified)
- New price is rounded to 2 decimal places
- No rollback mechanism for price changes
- Consider implementing audit logging for price changes
- Multiple discounts can be applied cumulatively
- Original price is not preserved after discount application
