# GET /auth/{user_id}

## Overview
Retrieve specific user information by user ID. Users can access their own profile, while admins can access any user profile.

## Authentication
JWT token required. Users can access their own data; admins can access any user.

## Request Headers
| Header | Value | Description |
|--------|-------|-------------|
| Authorization | Bearer {token} | JWT access token |

## URL Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | integer | Yes | Unique identifier of the user to retrieve |

## Response Codes
| Code | Description |
|------|-------------|
| 200 | User retrieved successfully |
| 401 | Authentication token missing or invalid |
| 403 | Cannot access other users' data (non-admin) |
| 404 | User not found |
| 500 | Server error during retrieval |

## Success Response (200)
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "role": "staff",
  "created_at": "2024-01-15T10:30:00Z",
  "last_login": "2024-01-15T11:30:00Z",
  "is_active": true,
  "profile_updated_at": "2024-01-15T10:45:00Z"
}
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
  "message": "Cannot access other users' profiles",
  "status_code": 403,
  "error_code": "AUTHORIZATION_ERROR",
  "details": {
    "requesting_user_id": "2",
    "target_user_id": "1",
    "user_role": "staff"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Not Found (404)
```json
{
  "message": "User not found",
  "status_code": 404,
  "error_code": "NOT_FOUND",
  "details": {
    "user_id": 999,
    "search_criteria": "id"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Business Logic
1. **Token Validation**: Verifies JWT token is valid and not expired
2. **User Authentication**: Extracts requesting user identity from token
3. **Permission Check**: Validates access rights (self or admin)
4. **User Lookup**: Retrieves target user by ID from database
5. **Data Filtering**: Excludes sensitive information
6. **Response Formatting**: Returns user data in consistent format
7. **Audit Logging**: Logs access attempt and result

## Access Control Rules

### Self Access (All Users)
- Users can always access their own profile
- No special permissions required
- Returns full user profile data

### Admin Access
- Admin users can access any user profile
- No restrictions on target user
- Returns full user profile data

### Other Access (Denied)
- Non-admin users cannot access other users' profiles
- Returns 403 Forbidden error
- Access attempt is logged

## Security Considerations
- **Permission Enforcement**: Strict access control based on user role
- **Data Filtering**: Sensitive data excluded from response
- **Input Validation**: User ID parameter validation
- **Audit Trail**: All profile access is logged
- **Self-Service**: Users can only access their own data

## Data Filtering
The following fields are excluded from the response:
- `password_hash`
- `reset_token`
- `email_verified`
- `login_attempts`
- Other sensitive internal fields

## Logging Scenarios
- **Self Access**: User accessing own profile
- **Admin Access**: Admin accessing any user profile
- **Failed Access**: Unauthorized access attempts
- **Not Found**: Requests for non-existent users

## Rate Limiting
Recommended: 100 requests per minute per authenticated user.

## Examples

### User Accessing Own Profile
```bash
curl -H "Authorization: Bearer {user_token}" \
     http://localhost:5000/auth/1
```

### Admin Accessing User Profile
```bash
curl -H "Authorization: Bearer {admin_token}" \
     http://localhost:5000/auth/2
```

### Unauthorized Access (Non-Admin)
```bash
curl -H "Authorization: Bearer {staff_token}" \
     http://localhost:5000/auth/1
# Returns 403 Forbidden
```

### Non-Existent User
```bash
curl -H "Authorization: Bearer {admin_token}" \
     http://localhost:5000/auth/999
# Returns 404 Not Found
```

## Response Headers
```
X-User-ID: 1
X-Access-Type: self
X-Timestamp: 2024-01-15T10:30:00Z
```

## Performance Considerations
- **Database Indexing**: User ID field should be indexed
- **Caching**: Consider caching frequently accessed profiles
- **Query Optimization**: Efficient single-record queries
- **Response Size**: Minimal data transfer

## Error Handling
- **Invalid User ID**: Returns 404 for non-existent users
- **Permission Denied**: Clear 403 error for unauthorized access
- **Token Issues**: Proper 401 responses for authentication problems
- **Database Errors**: Generic 500 error for database issues

## Integration Considerations
- **User Profiles**: Integration with user profile management
- **Admin Dashboard**: Admin user management interface
- **Audit Systems**: Profile access logging
- **Security Monitoring**: Track unauthorized access attempts

## Use Cases
- **Profile Viewing**: Users viewing their own profile
- **User Management**: Admins managing user accounts
- **Account Verification**: Checking user details
- **Debugging**: Admin troubleshooting user issues

## Security Best Practices
- **Regular Audits**: Review profile access logs
- **Permission Validation**: Always validate user permissions
- **Input Sanitization**: Validate user ID parameter
- **Error Messages**: Generic error messages for security

## Testing Considerations
- **Self Access**: Test users accessing own profiles
- **Admin Access**: Test admin accessing various user profiles
- **Unauthorized Access**: Test permission enforcement
- **Edge Cases**: Test non-existent users and invalid IDs

## Deprecation Notice
None currently planned. Consider versioning for future changes.

## Alternative Endpoints
- `GET /auth/users` - List all users (admin only)
- `PUT /auth/{user_id}` - Update user information
- `DELETE /auth/{user_id}` - Delete user account
