# POST /auth/login

## Overview
Authenticate user credentials and generate JWT access token for API access.

## Authentication
None required - this is a public endpoint for user authentication.

## Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | string | Yes | User's registered username |
| password | string | Yes | User's password |

## Response Codes
| Code | Description |
|------|-------------|
| 200 | Authentication successful |
| 400 | Missing required fields |
| 401 | Invalid username or password |
| 500 | Server error during authentication |

## Success Response (200)
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "staff"
  }
}
```

## Error Responses

### Missing Fields (400)
```json
{
  "message": "Username and password are required",
  "status_code": 400,
  "error_code": "VALIDATION_ERROR",
  "details": {
    "missing_fields": ["username", "password"]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Invalid Credentials (401)
```json
{
  "message": "Invalid username or password",
  "status_code": 401,
  "error_code": "AUTHENTICATION_ERROR",
  "details": {
    "reason": "credentials_invalid"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Business Logic
1. **Input Validation**: Validates both username and password are provided
2. **User Lookup**: Retrieves user by username from database
3. **Password Verification**: Uses secure timing-safe comparison
4. **Token Generation**: Creates JWT token with user claims
5. **Token Claims**: Includes user ID, role, username, and expiration
6. **Response Format**: Returns token and user information
7. **Audit Logging**: Logs login attempt and result

## Security Considerations
- **Password Verification**: Uses timing-safe comparison to prevent timing attacks
- **Failed Login Logging**: All failed attempts are logged with IP addresses
- **JWT Security**: Tokens include expiration and user claims
- **Rate Limiting**: Recommended to prevent brute force attacks
- **Account Locking**: Consider implementing after failed attempts

## JWT Token Structure
```json
{
  "sub": "1",
  "role": "staff",
  "username": "john_doe",
  "iat": 1642248600,
  "exp": 1642252200,
  "jti": "unique-token-id"
}
```

## Rate Limiting
Recommended: 5 requests per minute per IP address to prevent brute force attacks.

## Logging
- **Success**: Successful login with user ID and IP address
- **Failure**: Failed login attempts with username and IP
- **Security**: Suspicious login patterns and multiple failures

## Token Usage
Include the access token in the Authorization header for subsequent requests:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Token Expiration
- **Default**: 1 hour (3600 seconds)
- **Refresh**: User must re-authenticate after expiration
- **Configuration**: Expiration time can be configured

## Examples

### Valid Request
```json
{
  "username": "john_doe",
  "password": "SecurePass123!"
}
```

### Invalid Request (Missing Password)
```json
{
  "username": "john_doe"
}
```

### Invalid Request (Wrong Credentials)
```json
{
  "username": "john_doe",
  "password": "wrongpassword"
}
```

## Security Headers
Response includes security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`

## Error Handling
- **Generic Error**: Returns generic "Invalid credentials" message
- **Server Errors**: Logged but not exposed to client
- **Account Status**: Differentiates between non-existent and locked accounts

## Performance Considerations
- **Database Indexing**: Username field should be indexed
- **Token Generation**: Efficient JWT generation process
- **Logging**: Asynchronous logging to prevent delays
