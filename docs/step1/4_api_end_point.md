# API Endpoints Overview

## Base URL
url = `http://127.0.0.1:5000`


## Authentication
This API uses JWT Bearer token authentication.
```
Authorization: Bearer <your_jwt_token>
```
## 1. Authentication API (/auth)

### 1.1 User Registration
 - **Endpoint** : `POST {{url}}/auth/register`
 - **Description** : Register a new user account

 *Request Body:*

 ```json
 {
    "username" : "string",
    "email" : "string",
    "role" : "string (admin, manager, staff)",
    "password":"string"
 }
 ```

 *Success Response:*
 - **201 Created**
 ```json
{
  "message": "User registered successfully"
}
```

*Error Responses:*
- **400 Bad Request** - Missing Required Fields
- **400 Bad Request** - Email already exists
- **500 Internal Server Error** - Internal server error

### 1.2 User Login
- **Endpoint**: `POST {{url}}/auth/login`
- **Description**: Authenticate user and get JWT access token

*Request Body (Form Data):*
```json
{
   "username":"string",
   "password":"string"
}

*Success Response:*
- **200 OK**
```json
{
  "access_token": "string",
  "message": "Login Successful"
}
```

*Error Response:*
- **401 Unauthorized** - Incorrect username or password


## 2. Inventory Products API

### 2.1 Create Product (/products)
- **Endpoint**: `POST {{url}}/products`
- **Description**: Create a new product for the authenticated user

*Headers Required:*
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

*Request Body:*
```json
{
    "name":"string",
    "description":"String",
    "price":"Integer",
    "stock":"Integer",
    "category_id":"Integer"
}
```

*Success Response:*
- **201 Created**
```json
{
"message": "Product added",
  "product": {
    "category": "string",
    "description": "String",
    "id":"Integer" ,
    "name": "String",
    "price": "Integer",
    "stock": "Integer"
  }
}
```

*Error Response*
- **401 Unauthorized** - Not authenticated
- **401 Unauthorized** - Invalid authentication credentials
- **400 Bad Request** - "Missing field: stock is required"
- **500 Internal Server Error** - Internal server error

### 2.2 Get All Products (/products)

*Headers Requuired*
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

*Success Response*
- **200 OK**
```json
{
   "id": 1,
   "name": "string",
   "price": "Integer",
   "stock": "Integer",
   "category": "string"
}
```
*Error response*
- **401 Unauthorized** - Not authenticated

### 2.3 Get Product by ID (/products)

*Headers Requuired*
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

*Success Response*
- **200 OK**
```json
{
   "id": 1,
   "name": "string",
   "price": "Integer",
   "stock": "Integer",
   "category": "string"
}
```
*Error response*
- **401 Unauthorized** - Not authenticated
- **404 Not Found** - Product Not Found

### 2.4 Update Product (/products/update)

- **Endpoint**: `PUT {{url}}/products/update`
- **Description**: Update an existing product
- **Access**: admin, manager

*Headers Required*
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

*Request Body*
```json
{
   "id": 1,
  "name": "string",
  "description": "string",
  "price": 900,
  "stock": 8,
  "category_id": 1
}
```

*Success Response*
- **200 OK**
```json
{
   "message": "Product updated",
  "product": {
    "id": "Integer",
    "name": "string",
    "description": "string",
    "price": "Integer",
    "stock": "Integer",
    "category": "string"
  }
}
```

*Error Response*
- **401 Unauthorized** - Not authenticated
- **403 Forbidden** - Insufficient permissions
- **400 Bad Request** - Product ID is required
- **404 Not Found** - Product not found

### 2.5 Delete Product (/products/delete)

- **Endpoint**: `DELETE {{url}}/products/delete`
- **Description**: Delete an existing product
- **Access**: admin only

*Headers Required*
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

*Request Body*
```json
{
   "id": 1
}
```

*Success Response*
- **200 OK**
```json
{
   "message": "Product deleted"
}
```

*Error Response*
- **401 Unauthorized** - Not authenticated
- **403 Forbidden** - Insufficient permissions
- **400 Bad Request** - Product ID is required
- **404 Not Found** - Product not found

### 2.6 Apply Discount to Product (/products/discount)

- **Endpoint**: `PATCH {{url}}/products/discount`
- **Description**: Apply discount and tax to a product
- **Access**: admin, manager

*Headers Required*
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

*Request Body*
```json
{
   "id": 1,
   "discount": 10,
   "tax": 5
}
```

*Success Response*
- **200 OK**
```json
{
   "message": "Applied 10% discount and 5% tax",
   "new_price": 855.0
}
```

*Error Response*
- **401 Unauthorized** - Not authenticated
- **403 Forbidden** - Insufficient permissions
- **400 Bad Request** - Product ID and discount percentage are required
- **400 Bad Request** - Discount must be a number between 1 and 100
- **400 Bad Request** - Tax must be between 0 and 50
- **404 Not Found** - Product not found

## 3. Categories API (/categories)

### 3.1 Create Category (/categories)

- **Endpoint**: `POST {{url}}/categories`
- **Description**: Create a new category
- **Access**: admin, manager

*Headers Required*
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

*Request Body*
```json
{
   "name": "Electronics",
   "description": "Electronic devices and accessories"
}
```

*Success Response*
- **201 Created**
```json
{
   "message": "Category created successfully",
   "category": {
      "id": 1,
      "name": "Electronics"
   }
}
```

*Error Response*
- **401 Unauthorized** - Not authenticated
- **403 Forbidden** - Insufficient permissions
- **400 Bad Request** - Category name is required

### 3.2 Get All Categories (/categories)

- **Endpoint**: `GET {{url}}/categories`
- **Description**: Get all categories

*Headers Required*
```
Authorization: Bearer <jwt_token>
```

*Success Response*
- **200 OK**
```json
[
   {
      "id": 1,
      "name": "Electronics"
   },
   {
      "id": 2,
      "name": "Clothing"
   }
]
```

*Error Response*
- **401 Unauthorized** - Not authenticated

### 3.3 Get Category by ID (/categories)

- **Endpoint**: `GET {{url}}/categories/<category_id>`
- **Description**: Get a specific category by ID

*Headers Required*
```
Authorization: Bearer <jwt_token>
```

*Success Response*
- **200 OK**
```json
{
   "id": 1,
   "name": "Electronics"
}
```

*Error Response*
- **401 Unauthorized** - Not authenticated
- **404 Not Found** - Category not found

### 3.4 Update Category (/categories/update)

- **Endpoint**: `PUT {{url}}/categories/update`
- **Description**: Update an existing category
- **Access**: admin, manager

*Headers Required*
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

*Request Body*
```json
{
   "id": 1,
   "name": "Updated Category Name",
   "description": "Updated description"
}
```

*Success Response*
- **200 OK**
```json
{
   "message": "Category updated successfully",
   "category": {
      "id": 1,
      "name": "Updated Category Name",
      "description": "Updated description"
   }
}
```

*Error Response*
- **401 Unauthorized** - Not authenticated
- **403 Forbidden** - Insufficient permissions
- **400 Bad Request** - Category ID is required
- **404 Not Found** - Category not found

### 3.5 Delete Category (/categories/<category_id>)

- **Endpoint**: `DELETE {{url}}/categories/<category_id>`
- **Description**: Delete a category (will also delete associated products)
- **Access**: admin only

*Headers Required*
```
Authorization: Bearer <jwt_token>
```

*Success Response*
- **200 OK**
```json
{
   "message": "Category deleted successfully"
}
```

*Error Response*
- **401 Unauthorized** - Not authenticated
- **403 Forbidden** - Insufficient permissions
- **404 Not Found** - Category not found

## 4. User Management API (/auth)

### 4.1 Get All Users (/auth/users)

- **Endpoint**: `GET {{url}}/auth/users`
- **Description**: Get all users

*Headers Required*
```
Authorization: Bearer <jwt_token>
```

*Success Response*
- **200 OK**
```json
[
   {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com"
   },
   {
      "id": 2,
      "username": "manager",
      "email": "manager@example.com"
   }
]
```

*Error Response*
- **401 Unauthorized** - Not authenticated

### 4.2 Get User by ID (/auth/<user_id>)

- **Endpoint**: `GET {{url}}/auth/<user_id>`
- **Description**: Get a specific user by ID

*Headers Required*
```
Authorization: Bearer <jwt_token>
```

*Success Response*
- **200 OK**
```json
{
   "id": 1,
   "username": "admin",
   "email": "admin@example.com"
}
```

*Error Response*
- **401 Unauthorized** - Not authenticated
- **404 Not Found** - User not found

### 4.3 Update User (/auth/update)

- **Endpoint**: `PUT {{url}}/auth/update`
- **Description**: Update user information

*Headers Required*
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

*Request Body*
```json
{
   "id": 1,
   "username": "new_username",
   "email": "new_email@example.com",
   "password": "new_password",
   "role": "admin"
}
```

*Success Response*
- **200 OK**
```json
{
   "message": "User updated",
   "user": {
      "id": 1,
      "username": "new_username",
      "email": "new_email@example.com",
      "role": "admin"
   }
}
```

*Error Response*
- **401 Unauthorized** - Not authenticated
- **400 Bad Request** - User ID is required
- **404 Not Found** - User not found

### 4.4 Delete User (/auth/delete)

- **Endpoint**: `DELETE {{url}}/auth/delete`
- **Description**: Delete a user

*Headers Required*
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

*Request Body*
```json
{
   "id": 1
}
```

*Success Response*
- **200 OK**
```json
{
   "message": "User username deleted successfully"
}
```

*Error Response*
- **401 Unauthorized** - Not authenticated
- **400 Bad Request** - User ID is required
- **404 Not Found** - User not found

## 5. Role-Based Access Control

The API implements role-based access control with the following roles:

- **admin**: Full access to all endpoints including delete operations
- **manager**: Can create, read, update products and categories, apply discounts
- **staff**: Can read products and categories

## 6. Data Models

### Product Model
```json
{
   "id": "Integer (Primary Key)",
   "name": "String (100 chars, required)",
   "description": "String (255 chars, optional)",
   "price": "Float (required)",
   "stock": "Integer (default: 0)",
   "category_id": "Integer (Foreign Key to categories.id, optional)"
}
```

### Category Model
```json
{
   "id": "Integer (Primary Key)",
   "name": "String (100 chars, unique, required)",
   "description": "String (255 chars, optional)"
}
```

### User Model
```json
{
   "id": "Integer (Primary Key)",
   "username": "String (80 chars, unique, required)",
   "email": "String (120 chars, unique, required)",
   "password_hash": "String (200 chars, required)",
   "role": "String (20 chars, required) - admin/manager/staff"
}
```

## 7. Error Handling

All endpoints return consistent error responses:

```json
{
   "error": "Error message description"
}
```

Common HTTP Status Codes:
- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required or invalid
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

