# PUT /auth/{user_id}

## Overview
Update user information. Users can update their own profile, while admins can update any user profile including role changes.

## Authentication
JWT token required. Users can update their own data; admins can update any user.

## Request Headers
| Header | Value | Description |
|--------|-------|-------------|
| Authorization | Bearer {token} | JWT access token |
| Content-Type | application/json | Request content type |

## URL Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | integer | Yes | Unique identifier of the user to update |

## Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | string | No | New username (min 3 characters) |
| email | string | No | New email address |
| role | string | No | New role (admin only) |

## Response Codes
| Code | Description |
|------|-------------|
| 200 | User updated successfully |
| 401 | Authentication token missing or invalid |
| 403 | Cannot update other users (non-admin) |
| 403 | Role changes restricted to admin |
| 404 | User not found |
| 400 | Validation errors for input data |
| 409 | Username or email already exists |
| 500 | Server error during update |

## Success Response (200)
```json
{
  "message": "User updated successfully",
  "user": {
    "id": 1,
    "username": "john_doe_updated",
    "email": "john.updated@example.com",
    "role": "staff",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:30:00Z"
  },
  "updated_fields": ["username", "email"]
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
  "message": "Cannot update other users' profiles",
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

### Validation Error (400)
```json
{
  "message": "Validation failed",
  "status_code": 400,
  "error_code": "VALIDATION_ERROR",
  "details": {
    "username": "Username must be at least 3 characters",
    "email": "Invalid email format"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Conflict Error (409)
```json
{
  "message": "Username already taken",
  "status_code": 409,
  "error_code": "CONFLICT",
  "details": {
    "field": "username",
    "value": "jane_smith",
    "existing_user_id": 3
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Business Logic
1. **Token Validation**: Verifies JWT token is valid and not expired
2. **User Authentication**: Extracts requesting user identity from token
3. **Permission Check**: Validates update rights (self or admin)
4. **Input Validation**: Validates all provided fields
5. **Conflict Checking**: Checks for username/email conflicts
6. **User Update**: Updates user record in database
7. **Audit Logging**: Logs update attempt and changes
8. **Response Formatting**: Returns updated user data

## Access Control Rules

### Self Updates (All Users)
- Users can update their own username and email
- Cannot change their own role
- All fields are optional (partial updates)

### Admin Updates
- Admins can update any user's username, email, and role
- Full access to all user fields
- Can perform role changes

### Role Changes
- Only admin users can change user roles
- Users cannot change their own role
- Role changes require admin privileges

## Validation Rules
- **Username**: Minimum 3 characters, alphanumeric + underscores
- **Email**: Must match standard email regex pattern
- **Role**: Must be one of: admin, manager, staff (admin only)

## Conflict Checking
- **Username**: Checks for existing usernames (excluding current user)
- **Email**: Checks for existing emails (excluding current user)
- **Role**: No conflicts (admin privilege required)

## Security Considerations
- **Permission Enforcement**: Strict access control based on user role
- **Input Validation**: All input data is validated and sanitized
- **Conflict Prevention**: Prevents duplicate usernames and emails
- **Audit Trail**: All updates are logged with change details
- **Role Security**: Role changes restricted to admins

## Logging Scenarios
- **Self Updates**: Users updating their own profiles
- **Admin Updates**: Admins updating user profiles
- **Role Changes**: Admins changing user roles
- **Failed Updates**: Validation errors and conflicts
- **Unauthorized Attempts**: Non-admin users trying to access others

## Rate Limiting
Recommended: 50 requests per minute per authenticated user.

## Examples

### User Updating Own Profile
```bash
curl -X PUT \
     -H "Authorization: Bearer {user_token}" \
     -H "Content-Type: application/json" \
     -d '{"username": "john_doe_updated", "email": "john.updated@example.com"}' \
     http://localhost:5000/auth/1
```

### Admin Updating User Role
```bash
curl -X PUT \
     -H "Authorization: Bearer {admin_token}" \
     -H "Content-Type: application/json" \
     -d '{"role": "manager"}' \
     http://localhost:5000/auth/2
```

### Admin Updating Multiple Fields
```bash
curl -X PUT \
     -H "Authorization: Bearer {admin_token}" \
     -H "Content-Type: application/json" \
     -d '{"username": "jane_smith", "email": "jane.smith@example.com", "role": "staff"}' \
     http://localhost:5000/auth/2
```

### Unauthorized Update (Non-Admin)
```bash
curl -X PUT \
     -H "Authorization: Bearer {staff_token}" \
     -H "Content-Type: application/json" \
     -d '{"role": "admin"}' \
     http://localhost:5000/auth/1
# Returns 403 Forbidden
```

## Response Headers
```
X-User-ID: 1
X-Updated-Fields: username,email
X-Access-Type: self
X-Timestamp: 2024-01-15T11:30:00Z
```

## Performance Considerations
- **Database Indexing**: Username and email fields should be indexed
- **Transaction Management**: Updates should be atomic
- **Conflict Checking**: Efficient queries for duplicate detection
- **Audit Logging**: Asynchronous logging to prevent delays

## Error Handling
- **Invalid User ID**: Returns 404 for non-existent users
- **Permission Denied**: Clear 403 error for unauthorized updates
- **Validation Errors**: Detailed validation error messages
- **Conflict Errors**: Specific conflict information
- **Database Errors**: Generic 500 error for database issues

## Integration Considerations
- **User Profiles**: Integration with user profile management
- **Admin Dashboard**: Admin user management interface
- **Audit Systems**: Update logging and change tracking
- **Security Monitoring**: Track unauthorized update attempts

## Use Cases
- **Profile Updates**: Users updating their personal information
- **User Management**: Admins managing user accounts
- **Role Management**: Admins changing user roles
- **Account Maintenance**: Routine user account updates

## Security Best Practices
- **Regular Audits**: Review update logs for suspicious activity
- **Permission Validation**: Always validate user permissions
- **Input Sanitization**: Validate and sanitize all input data
- **Role Security**: Strict control over role changes
- **Change Tracking**: Maintain audit trail of all changes

## Testing Considerations
- **Self Updates**: Test users updating their own profiles
- **Admin Updates**: Test admin updating various user profiles
- **Role Changes**: Test admin role change functionality
- **Validation Testing**: Test all validation rules
- **Conflict Testing**: Test duplicate prevention

## Deprecation Notice
None currently planned. Consider versioning for future changes.

## Alternative Endpoints
- `GET /auth/{user_id}` - Get user information
- `DELETE /auth/{user_id}` - Delete user account
- `POST /auth/change-password` - Change user password
