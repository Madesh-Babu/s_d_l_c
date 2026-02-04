# POST /auth/register

## Overview
Register a new user account in the system with validation and security checks.

## Authentication
None required - this is a public endpoint for user registration.

## Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | string | Yes | Unique username for the account (min 3 characters) |
| email | string | Yes | Valid email address for user identification |
| password | string | Yes | Strong password meeting security requirements |
| role | string | Yes | User role (admin, manager, staff) |

## Response Codes
| Code | Description |
|------|-------------|
| 201 | User registration successful |
| 400 | Validation errors for invalid input |
| 409 | Conflict if username or email already exists |
| 500 | Server error during registration |

## Success Response (201)
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "staff",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

## Error Responses

### Validation Error (400)
```json
{
  "message": "Validation failed",
  "status_code": 400,
  "error_code": "VALIDATION_ERROR",
  "details": {
    "email": "Invalid email format",
    "password": "Password must be at least 8 characters"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Conflict Error (409)
```json
{
  "message": "User with this email already exists",
  "status_code": 409,
  "error_code": "CONFLICT",
  "details": {
    "field": "email",
    "value": "john@example.com"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Business Logic
1. **Input Validation**: Validates all required fields are present
2. **Email Validation**: Uses regex pattern to verify email format
3. **Password Strength**: Enforces minimum 8 characters, uppercase, lowercase, numbers
4. **Duplicate Checking**: Checks for existing usernames and emails
5. **Password Hashing**: Uses secure hashing algorithm (bcrypt)
6. **User Creation**: Creates user record in database
7. **Audit Logging**: Logs registration attempt and result

## Security Considerations
- **Password Security**: Password is never stored in plain text
- **Input Validation**: Prevents injection attacks and malicious data
- **Rate Limiting**: Recommended to prevent spam registration
- **Audit Trail**: All registration attempts are logged
- **Data Sanitization**: Input data is properly sanitized

## Validation Rules
- **Username**: Minimum 3 characters, alphanumeric + underscores
- **Email**: Must match standard email regex pattern
- **Password**: Minimum 8 characters, at least 1 uppercase, 1 lowercase, 1 number
- **Role**: Must be one of: admin, manager, staff

## Rate Limiting
Recommended: 5 requests per minute per IP address to prevent spam registration.

## Logging
- **Success**: User registration with user ID and username
- **Failure**: Registration failures with reasons
- **Security**: Suspicious registration attempts

## Examples

### Valid Request
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "role": "staff"
}
```

### Invalid Request (Weak Password)
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "123",
  "role": "staff"
}
```

### Invalid Request (Bad Email)
```json
{
  "username": "john_doe",
  "email": "invalid-email",
  "password": "SecurePass123!",
  "role": "staff"
}
```
