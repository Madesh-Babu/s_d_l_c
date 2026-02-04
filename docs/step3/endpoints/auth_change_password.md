# POST /auth/change-password

## Overview
Change user password with current password verification and security validation.

## Authentication
JWT token required for the user whose password is being changed.

## Request Headers
| Header | Value | Description |
|--------|-------|-------------|
| Authorization | Bearer {token} | JWT access token |
| Content-Type | application/json | Request content type |

## Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| current_password | string | Yes | User's current password |
| new_password | string | Yes | New password (strong password required) |
| confirm_password | string | Yes | Confirmation of new password |

## Response Codes
| Code | Description |
|------|-------------|
| 200 | Password changed successfully |
| 401 | Authentication token missing or invalid |
| 400 | Missing required fields or validation errors |
| 400 | Current password incorrect |
| 400 | Passwords do not match |
| 404 | User not found |
| 500 | Server error during update |

## Success Response (200)
```json
{
  "message": "Password changed successfully",
  "password_strength": "strong",
  "changed_at": "2024-01-15T11:30:00Z",
  "user_id": 1,
  "password_complexity": {
    "length": 12,
    "has_uppercase": true,
    "has_lowercase": true,
    "has_numbers": true,
    "has_special_chars": true
  }
}
```

## Error Responses

### Missing Fields (400)
```json
{
  "message": "All password fields are required",
  "status_code": 400,
  "error_code": "VALIDATION_ERROR",
  "details": {
    "missing_fields": ["confirm_password"],
    "provided_fields": ["current_password", "new_password"]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Current Password Incorrect (400)
```json
{
  "message": "Current password is incorrect",
  "status_code": 400,
  "error_code": "VALIDATION_ERROR",
  "details": {
    "reason": "current_password_invalid",
    "attempt_time": "2024-01-15T10:30:00Z"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Passwords Do Not Match (400)
```json
{
  "message": "New passwords do not match",
  "status_code": 400,
  "error_code": "VALIDATION_ERROR",
  "details": {
    "new_password": "SecurePass123!",
    "confirm_password": "DifferentPass123!"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Weak Password (400)
```json
{
  "message": "Password validation failed",
  "status_code": 400,
  "error_code": "VALIDATION_ERROR",
  "details": {
    "password_issues": [
      "Password must be at least 8 characters",
      "Password must contain at least one uppercase letter",
      "Password must contain at least one number"
    ]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Business Logic
1. **Token Validation**: Verifies JWT token is valid and not expired
2. **User Authentication**: Extracts user identity from token
3. **Input Validation**: Validates all required fields are present
4. **Current Password Verification**: Confirms current password is correct
5. **Password Strength Validation**: Validates new password meets requirements
6. **Password Confirmation**: Ensures new passwords match
7. **Password Update**: Updates password hash in database
8. **Session Invalidation**: Invalidates existing user sessions
9. **Audit Logging**: Logs password change for security

## Password Strength Requirements
- **Minimum Length**: 8 characters
- **Uppercase Letters**: At least 1 (A-Z)
- **Lowercase Letters**: At least 1 (a-z)
- **Numbers**: At least 1 (0-9)
- **Special Characters**: Optional but recommended (!@#$%^&*)

## Security Considerations
- **Current Password Verification**: Prevents unauthorized password changes
- **Strong Password Requirements**: Enforces password security standards
- **Password Hashing**: Uses secure hashing algorithm (bcrypt)
- **Session Invalidation**: Invalidates existing sessions after change
- **Audit Logging**: All password changes are logged for security
- **Rate Limiting**: Prevents brute force password change attempts

## Logging Scenarios
- **Success**: Successful password changes with user ID
- **Failure**: Failed attempts with reasons (wrong current password, weak password)
- **Security**: Suspicious patterns (multiple failed attempts)
- **Audit**: Complete audit trail for compliance

## Session Management
- **Current Sessions**: All existing sessions are invalidated
- **Token Revocation**: Current JWT tokens become invalid
- **Re-authentication**: User must login with new password
- **Security**: Prevents session hijacking after password change

## Rate Limiting
Recommended: 5 requests per minute per authenticated user to prevent abuse.

## Examples

### Successful Password Change
```bash
curl -X POST \
     -H "Authorization: Bearer {user_token}" \
     -H "Content-Type: application/json" \
     -d '{
       "current_password": "OldPass123!",
       "new_password": "NewSecurePass456!",
       "confirm_password": "NewSecurePass456!"
     }' \
     http://localhost:5000/auth/change-password
```

### Missing Current Password
```bash
curl -X POST \
     -H "Authorization: Bearer {user_token}" \
     -H "Content-Type: application/json" \
     -d '{
       "new_password": "NewSecurePass456!",
       "confirm_password": "NewSecurePass456!"
     }' \
     http://localhost:5000/auth/change-password
# Returns 400 - Missing current password
```

### Wrong Current Password
```bash
curl -X POST \
     -H "Authorization: Bearer {user_token}" \
     -H "Content-Type: application/json" \
     -d '{
       "current_password": "WrongPass123!",
       "new_password": "NewSecurePass456!",
       "confirm_password": "NewSecurePass456!"
     }' \
     http://localhost:5000/auth/change-password
# Returns 400 - Current password incorrect
```

### Passwords Do Not Match
```bash
curl -X POST \
     -H "Authorization: Bearer {user_token}" \
     -H "Content-Type: application/json" \
     -d '{
       "current_password": "OldPass123!",
       "new_password": "NewSecurePass456!",
       "confirm_password": "DifferentPass789!"
     }' \
     http://localhost:5000/auth/change-password
# Returns 400 - Passwords do not match
```

### Weak Password
```bash
curl -X POST \
     -H "Authorization: Bearer {user_token}" \
     -H "Content-Type: application/json" \
     -d '{
       "current_password": "OldPass123!",
       "new_password": "weak",
       "confirm_password": "weak"
     }' \
     http://localhost:5000/auth/change-password
# Returns 400 - Password validation failed
```

## Response Headers
```
X-Password-Changed: true
X-Password-Strength: strong
X-Session-Invalidated: true
X-Timestamp: 2024-01-15T11:30:00Z
```

## Performance Considerations
- **Password Hashing**: Use efficient hashing algorithms
- **Database Updates**: Optimize password update queries
- **Session Cleanup**: Efficient session invalidation
- **Logging**: Asynchronous logging to prevent delays

## Error Handling
- **Input Validation**: Clear error messages for missing fields
- **Password Verification**: Generic error for wrong current password
- **Strength Validation**: Detailed feedback for weak passwords
- **Database Errors**: Generic error for database issues
- **Security**: No sensitive information in error messages

## Integration Considerations
- **User Interface**: Integration with user profile management
- **Security Systems**: Feed events to security monitoring
- **Session Management**: Integration with session management systems
- **Compliance**: Meet compliance requirements for password changes

## Use Cases
- **Regular Password Changes**: Users updating their passwords
- **Security Response**: Forced password changes after security incidents
- **Account Recovery**: Part of account recovery processes
- **Policy Compliance**: Meeting password policy requirements

## Security Best Practices
- **Regular Changes**: Encourage regular password changes
- **Strong Requirements**: Enforce strong password policies
- **Monitoring**: Monitor password change patterns
- **Audit Trail**: Maintain complete audit trail
- **Session Security**: Invalidate sessions after password change

## Compliance Considerations
- **Password Policies**: Meet industry password requirements
- **Audit Requirements**: Maintain audit trail for compliance
- **Data Protection**: Protect password change data
- **Security Standards**: Meet security framework requirements

## Testing Considerations
- **Valid Changes**: Test successful password changes
- **Invalid Current Password**: Test wrong current password scenarios
- **Weak Passwords**: Test password strength validation
- **Mismatched Passwords**: Test password confirmation
- **Session Invalidation**: Test session cleanup after change

## Deprecation Notice
None currently planned. Consider versioning for future changes.

## Alternative Endpoints
- `POST /auth/reset-password` - Password reset (forgot password)
- `POST /auth/force-change-password` - Admin forced password change
- `GET /auth/password-policy` - Get password requirements
