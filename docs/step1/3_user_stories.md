# User Stories

## Authentication & User Management

### As a new user, I want to register an account so that I can access the Inventory Management system.

*Acceptance Criteria:*
- Given a valid username, email, password, and role
- When I submit the registration request
- Then the system creates a new user with a hashed password
- And assigns the specified role (`staff`, `manager`, or `admin`)
- And returns 201 status with a success message
- And duplicate usernames return 400 with an error message
- And duplicate emails return 400 with an error message
- And missing required fields return 400 with validation error

---

### As a registered user, I want to log in so that I can access protected inventory features.

*Acceptance Criteria:*
- Given a valid username and password
- When I submit login credentials
- Then the system validates credentials against the hashed password
- And returns 200 status with a JWT access token
- And the token contains the user ID as identity
- And invalid credentials return 401 with an error message
- And missing credentials return 400 with validation error

---

### As an authenticated admin, I want to view all users so that I can manage system access.

*Acceptance Criteria:*
- Given a valid JWT token
- When I request the user list
- Then the system returns 200 status with all users
- And each user includes id, username, and email
- And missing or invalid token returns 401 Unauthorized

---

### As an authenticated admin, I want to update user details so that I can manage roles and credentials.

*Acceptance Criteria:*
- Given a valid JWT token
- When I provide user ID and updated fields
- Then the system updates only provided fields
- And returns 200 status with updated user details
- And invalid user ID returns 404 User not found
- And missing user ID returns 400 validation error

---

### As an authenticated admin, I want to delete a user so that I can revoke system access.

*Acceptance Criteria:*
- Given a valid JWT token
- When I request user deletion with user ID
- Then the system deletes the user permanently
- And returns 200 status with success message
- And invalid user ID returns 404 User not found

---

## Category Management

### As an admin or manager, I want to create product categories so that products can be organized.

*Acceptance Criteria:*
- Given a valid JWT token with role `admin` or `manager`
- When I provide a category name
- Then the system creates a new category
- And returns 201 status with category details
- And duplicate category names return 400
- And missing category name returns 400 validation error
- And unauthorized roles return 403 Forbidden

---

### As an authenticated user, I want to view all categories so that I can browse product classifications.

*Acceptance Criteria:*
- Given a valid JWT token
- When I request the category list
- Then the system returns 200 status with all categories
- And each category includes id and name
- And invalid token returns 401 Unauthorized

---

### As an admin or manager, I want to update a category so that category information stays accurate.

*Acceptance Criteria:*
- Given a valid JWT token with sufficient role
- When I provide category ID and updated fields
- Then the system updates the category
- And returns 200 status with updated category details
- And invalid category ID returns 404 Category not found
- And missing category ID returns 400 validation error

---

### As an admin, I want to delete a category so that obsolete categories can be removed.

*Acceptance Criteria:*
- Given a valid JWT token with role `admin`
- When I request category deletion
- Then the system deletes the category
- And associated products are also deleted
- And returns 200 status with success message
- And unauthorized roles return 403 Forbidden

---

## Product Management

### As an admin or manager, I want to add products so that inventory can be maintained.

*Acceptance Criteria:*
- Given a valid JWT token with role `admin` or `manager`
- When I provide product name, price, stock, and optional category
- Then the system creates a new product
- And returns 201 status with product details
- And missing required fields return 400 validation error
- And invalid price or stock returns 400 validation error
- And unauthorized roles return 403 Forbidden

---

### As an authenticated user, I want to view all products so that I can see available inventory.

*Acceptance Criteria:*
- Given a valid JWT token
- When I request the product list
- Then the system returns 200 status with all products
- And each product includes category name if assigned
- And invalid token returns 401 Unauthorized

---

### As an authenticated user, I want to view a specific product so that I can see its details.

*Acceptance Criteria:*
- Given a valid JWT token
- When I request a product by ID
- Then the system returns 200 status with product details
- And invalid product ID returns 404 Product not found
- And invalid token returns 401 Unauthorized

---

### As an admin or manager, I want to update product details so that inventory stays accurate.

*Acceptance Criteria:*
- Given a valid JWT token with sufficient role
- When I provide product ID and updated fields
- Then the system updates only provided fields
- And returns 200 status with updated product details
- And invalid product ID returns 404 Product not found
- And unauthorized roles return 403 Forbidden

---

### As an admin, I want to delete products so that discontinued items are removed.

*Acceptance Criteria:*
- Given a valid JWT token with role `admin`
- When I request product deletion
- Then the system deletes the product
- And returns 200 status with success message
- And invalid product ID returns 404 Product not found
- And unauthorized roles return 403 Forbidden

---

## Discount & Pricing

### As an admin or manager, I want to apply discounts and tax to products so that pricing rules can be enforced.

*Acceptance Criteria:*
- Given a valid JWT token with role `admin` or `manager`
- When I provide product ID, discount percentage, and optional tax
- Then the system applies discount first and tax next
- And updates the product price accordingly
- And returns 200 status with updated price
- And discount must be between 1 and 100
- And tax must be between 0 and 50
- And invalid product ID returns 404 Product not found