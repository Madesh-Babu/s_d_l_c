# DELETE /auth/{user_id}

## Overview
Delete a user account from the system. Admin-only endpoint for user account management.

## Authentication
JWT token required with admin role privileges.

## Request Headers
| Header | Value | Description |
|--------|-------|-------------|
| Authorization | Bearer {token} | JWT access token with admin role |

## URL Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | integer | Yes | Unique identifier of the user to delete |

## Response Codes
| Code | Description |
|------|-------------|
| 200 | User deleted successfully |
| 401 | Authentication token missing or invalid |
| 403 | User lacks admin privileges |
| 400 | Cannot delete own account |
| 404 | User not found |
| 500 | Server error during deletion |

## Success Response (200)
```json
{
  "message": "User 'john_doe' deleted successfully",
  "deleted_user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "staff"
  },
  "deleted_at": "2024-01-15T11:30:00Z",
  "deleted_by": {
    "id": 2,
    "username": "admin_user",
    "role": "admin"
  }
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

### Self-Deletion (400)
```json
{
  "message": "Cannot delete your own account",
  "status_code": 400,
  "error_code": "VALIDATION_ERROR",
  "details": {
    "user_id": 1,
    "reason": "self_deletion_prevented"
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
3. **Role Authorization**: Checks if user has admin role
4. **Self-Deletion Check**: Prevents users from deleting their own account
5. **User Lookup**: Retrieves target user by ID from database
6. **Data Cleanup**: Handles related data cleanup if needed
7. **User Deletion**: Removes user record from database
8. **Audit Logging**: Logs deletion with complete details

## Access Control Rules

### Admin Access Only
- Only admin users can delete user accounts
- No exceptions for self-deletion
- Strict role enforcement

### Self-Deletion Prevention
- Users cannot delete their own accounts
- Prevents system lockout scenarios
- Maintains system integrity

### Cascade Considerations
- User-related data may need cleanup
- Product associations handled appropriately
- Audit trail preservation

## Security Considerations
- **Admin Only**: Strict admin-only access control
- **Self-Deletion Prevention**: Prevents account lockout
- **Data Integrity**: Proper cleanup of related data
- **Audit Trail**: Complete deletion logging
- **Irreversible Action**: Deletion cannot be undone

## Data Cleanup Considerations
- **User Products**: Handle or reassign user's products
- **Audit Logs**: Preserve audit trail for deleted user
- **Sessions**: Invalidate user sessions
- **Dependencies**: Handle any dependent records

## Logging Scenarios
- **Successful Deletion**: Complete deletion details
- **Failed Deletion**: Reasons for failure
- **Unauthorized Attempts**: Non-admin deletion attempts
- **Self-Deletion Attempts**: Users trying to delete own accounts
- **System Integrity**: Data cleanup and system impact

## Rate Limiting
Recommended: 20 requests per minute per authenticated admin user.

## Examples

### Admin Deleting User
```bash
curl -X DELETE \
     -H "Authorization: Bearer {admin_token}" \
     http://localhost:5000/auth/1
```

### Unauthorized Deletion (Non-Admin)
```bash
curl -X DELETE \
     -H "Authorization: Bearer {staff_token}" \
     http://localhost:5000/auth/1
# Returns 403 Forbidden
```

### Self-Deletion Attempt
```bash
curl -X DELETE \
     -H "Authorization: Bearer {user_token}" \
     http://localhost:5000/auth/1
# Returns 400 Cannot delete own account
```

### Non-Existent User
```bash
curl -X DELETE \
     -H "Authorization: Bearer {admin_token}" \
     http://localhost:5000/auth/999
# Returns 404 Not Found
```

## Response Headers
```
X-Deleted-User-ID: 1
X-Deleted-By: 2
X-Deletion-Timestamp: 2024-01-15T11:30:00Z
X-System-Impact: user_data_cleanup
```

## Performance Considerations
- **Database Transactions**: Use transactions for data integrity
- **Cascade Operations**: Efficient cleanup of related data
- **Audit Logging**: Asynchronous logging to prevent delays
- **Index Maintenance**: Update database indexes after deletion

## Error Handling
- **Invalid User ID**: Returns 404 for non-existent users
- **Permission Denied**: Clear 403 error for non-admin users
- **Self-Deletion**: Specific 400 error for self-deletion attempts
- **Database Errors**: Generic 500 error for database issues
- **Constraint Violations**: Handle foreign key constraints appropriately

## Integration Considerations
- **User Management**: Integration with admin user management interface
- **Audit Systems**: Feed deletion events to audit logging
- **Data Retention**: Consider data retention policies
- **Backup Systems**: Ensure proper backup before deletion

## Use Cases
- **Account Termination**: Removing terminated employee accounts
- **User Cleanup**: Cleaning up inactive or test accounts
- **Security Response**: Removing compromised accounts
- **System Maintenance**: Routine user account management

## Security Best Practices
- **Regular Audits**: Review deletion logs for suspicious activity
- **Permission Validation**: Always validate admin permissions
- **Data Backup**: Ensure critical data is backed up
- **Documentation**: Maintain deletion policies and procedures
- **Recovery Planning**: Have account recovery procedures if needed

## Compliance Considerations
- **Data Retention**: Follow data retention regulations
- **Privacy Laws**: Comply with privacy protection laws
- **Audit Requirements**: Maintain audit trail for compliance
- **Right to Erasure**: Consider GDPR/privacy law requirements

## Testing Considerations
- **Admin Deletion**: Test admin deleting various user accounts
- **Unauthorized Access**: Test non-admin deletion attempts
- **Self-Deletion**: Test self-deletion prevention
- **Data Cleanup**: Test related data cleanup
- **Edge Cases**: Test non-existent users and invalid IDs

## Deprecation Notice
None currently planned. Consider versioning for future changes.

## Alternative Endpoints
- `PUT /auth/{user_id}` - Update user information (less destructive)
- `POST /auth/deactivate/{user_id}` - Deactivate user (reversible)
- `GET /auth/{user_id}` - Get user information before deletion

## Recovery Considerations
- **Backup Strategy**: Regular database backups
- **Recovery Process**: Documented recovery procedures
- **Data Restoration**: Ability to restore deleted accounts
- **Emergency Access**: Emergency account recovery procedures
