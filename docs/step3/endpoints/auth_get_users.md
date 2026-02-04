# GET /auth/users

## Overview
Retrieve a list of all users registered in the system. Admin-only endpoint for user management.

## Authentication
JWT token required with admin role privileges.

## Request Headers
| Header | Value | Description |
|--------|-------|-------------|
| Authorization | Bearer {token} | JWT access token with admin role |

## Query Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page | integer | No | 1 | Page number for pagination |
| per_page | integer | No | 20 | Items per page (max 100) |
| role | string | No | - | Filter by user role |
| search | string | No | - | Search by username or email |

## Response Codes
| Code | Description |
|------|-------------|
| 200 | Users retrieved successfully |
| 401 | Authentication token missing or invalid |
| 403 | User lacks admin privileges |
| 500 | Server error during retrieval |

## Success Response (200)
```json
[
  {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "admin",
    "created_at": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-15T11:30:00Z"
  },
  {
    "id": 2,
    "username": "jane_smith",
    "email": "jane@example.com",
    "role": "manager",
    "created_at": "2024-01-14T09:15:00Z",
    "last_login": "2024-01-15T10:45:00Z"
  }
]
```

## Error Responses

### Unauthorized (401)
```json
{
  "message": "Authentication token is required",
  "status_code": 401,
  "error_code": "AUTHENTICATION_ERROR",
  "details": {
    "reason": "token_missing"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Forbidden (403)
```json
{
  "message": "Admin access required",
  "status_code": 403,
  "error_code": "AUTHORIZATION_ERROR",
  "details": {
    "user_role": "staff",
    "required_role": "admin"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Business Logic
1. **Token Validation**: Verifies JWT token is valid and not expired
2. **User Authentication**: Extracts user identity from token
3. **Role Authorization**: Checks if user has admin role
4. **Query Building**: Applies filters and pagination parameters
5. **Database Query**: Retrieves users from database
6. **Data Filtering**: Excludes sensitive information (passwords)
7. **Response Formatting**: Returns consistent user data format
8. **Audit Logging**: Logs access attempt and result

## Security Considerations
- **Admin Only**: Only admin users can access this endpoint
- **Data Filtering**: Sensitive data is excluded from response
- **Input Validation**: All query parameters are validated
- **Audit Trail**: All access attempts are logged
- **Pagination**: Prevents large response sizes

## Data Filtering
The following fields are excluded from the response:
- `password_hash`
- `reset_token`
- `email_verified`
- Other sensitive internal fields

## Query Parameter Examples

### Pagination
```
GET /auth/users?page=2&per_page=10
```

### Role Filtering
```
GET /auth/users?role=staff
```

### Search
```
GET /auth/users?search=john
```

### Combined Filters
```
GET /auth/users?role=manager&page=1&per_page=5
```

## Rate Limiting
Recommended: 100 requests per minute per authenticated user.

## Logging
- **Success**: User list retrieval with requesting admin ID
- **Failure**: Access attempts with user roles and reasons
- **Security**: Unauthorized access attempts and patterns

## Performance Considerations
- **Database Indexing**: Username and email fields should be indexed
- **Pagination**: Essential for large user databases
- **Caching**: Consider caching frequent queries
- **Query Optimization**: Efficient database queries

## Response Headers
```
X-Total-Count: 150
X-Page: 1
X-Per-Page: 20
X-Total-Pages: 8
```

## Examples

### Basic Request
```bash
curl -H "Authorization: Bearer {token}" \
     http://localhost:5000/auth/users
```

### With Pagination
```bash
curl -H "Authorization: Bearer {token}" \
     "http://localhost:5000/auth/users?page=2&per_page=10"
```

### With Role Filter
```bash
curl -H "Authorization: Bearer {token}" \
     "http://localhost:5000/auth/users?role=staff"
```

### With Search
```bash
curl -H "Authorization: Bearer {token}" \
     "http://localhost:5000/auth/users?search=john"
```

## Error Handling
- **Token Validation**: Clear error messages for invalid tokens
- **Role Checking**: Specific error for insufficient permissions
- **Database Errors**: Generic error for database issues
- **Input Validation**: Validation errors for bad parameters

## Integration Considerations
- **User Management**: Integrate with admin dashboard
- **Audit Systems**: Feed data to audit logging systems
- **Monitoring**: Track access patterns and usage
- **Security**: Monitor for unauthorized access attempts

## Deprecation Notice
None currently planned. Consider versioning for future changes.

## Alternative Endpoints
- `GET /auth/{user_id}` - Get specific user by ID
- `PUT /auth/{user_id}` - Update specific user
- `DELETE /auth/{user_id}` - Delete specific user

## Security Best Practices
- **Regular Audits**: Review admin access logs regularly
- **Token Validation**: Always validate token expiration
- **Input Sanitization**: Sanitize all query parameters
- **Error Messages**: Generic error messages for security

## Testing Considerations
- **Mock Data**: Use test data for development
- **Role Testing**: Test with different user roles
- **Pagination Testing**: Test pagination edge cases
- **Search Testing**: Test search functionality thoroughly
