# POST /auth/dev-login

## Overview
Development-only authentication bypass endpoint for testing and development purposes.

## Authentication
None required - this is a public endpoint for development use only.

## Request Body
No request body required.

## Response Codes
| Code | Description |
|------|-------------|
| 200 | Development login successful |
| 404 | Not available in production environment |
| 404 | Bypass feature disabled |

## Success Response (200)
```json
{
  "access_token": "dev_token_1642248600",
  "token_type": "Bearer",
  "bypass_enabled": true,
  "environment": "development",
  "message": "Development login successful - authentication bypassed",
  "user": {
    "id": "dev_user",
    "username": "dev_user",
    "email": "dev@example.com",
    "role": "admin"
  }
}
```

## Error Responses

### Production Environment (404)
```json
{
  "message": "Development login only available in development environment",
  "status_code": 404,
  "error_code": "NOT_FOUND",
  "details": {
    "environment": "production",
    "feature": "development_login"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Bypass Disabled (404)
```json
{
  "message": "Authentication bypass is disabled",
  "status_code": 404,
  "error_code": "NOT_FOUND",
  "details": {
    "feature": "BYPASS_AUTH",
    "status": "disabled"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Business Logic
1. **Environment Validation**: Checks if current environment is development
2. **Feature Toggle Validation**: Verifies BYPASS_AUTH is enabled
3. **Development User**: Creates mock development user with admin privileges
4. **Token Generation**: Creates JWT token with bypass metadata
5. **Token Claims**: Includes bypass information and environment
6. **Response Format**: Returns token with bypass confirmation
7. **Audit Logging**: Logs development login for debugging

## Security Considerations
- **Environment Restriction**: Only available in development environment
- **Feature Toggle**: Controlled by BYPASS_AUTH configuration
- **Production Protection**: Completely disabled in production
- **Audit Trail**: All bypass usage is logged
- **Token Metadata**: Bypass information included in token claims

## Environment Validation
The endpoint only works in these environments:
- `development`
- `local`
- `dev`

Any other environment will return a 404 error.

## Feature Toggle Configuration
Must have these environment variables:
```bash
ENVIRONMENT=development
BYPASS_AUTH=true
```

## JWT Token Structure (Development)
```json
{
  "sub": "dev_user",
  "role": "admin",
  "username": "dev_user",
  "bypass_enabled": true,
  "environment": "development",
  "dev_mode": true,
  "iat": 1642248600,
  "exp": 1642252200,
  "jti": "dev-token-id"
}
```

## Bypass Metadata
The development token includes special metadata:
- `bypass_enabled`: true
- `environment`: current environment
- `dev_mode`: true
- `bypass_reason`: "development_testing"

## Logging
- **Success**: Development login with environment and bypass status
- **Failure**: Failed bypass attempts with reasons
- **Security**: All bypass usage tracked for audit

## Usage Examples

### Development Environment
```bash
curl -X POST http://localhost:5000/auth/dev-login
```

### Production Environment (Will Fail)
```bash
curl -X POST https://api.example.com/auth/dev-login
# Returns 404 - Not available in production
```

## Integration with Other Endpoints
When bypass is enabled, all other endpoints will accept requests without authentication:
- All endpoints check for bypass status
- Bypass responses include metadata
- Normal authentication flow is skipped
- Bypass status is logged for each request

## Development Workflow
1. Enable bypass in environment configuration
2. Use dev-login to get bypass token
3. Use token for testing all endpoints
4. Monitor bypass usage in logs
5. Disable bypass before production deployment

## Testing Benefits
- **Quick Setup**: No need to create test users
- **Full Access**: Admin privileges for testing all features
- **Consistent Testing**: Same token for all test scenarios
- **Debugging Support**: Bypass metadata in logs
- **Rapid Development**: Skip authentication during development

## Security Best Practices
- **Never Enable in Production**: Always verify environment
- **Use Feature Flags**: Control bypass with configuration
- **Monitor Usage**: Track bypass usage in development
- **Disable Before Deploy**: Ensure bypass is disabled in production
- **Document Usage**: Clear documentation for development team

## Rate Limiting
Not applicable - development endpoint with controlled access.

## Error Handling
- **Environment Check**: Clear error messages for wrong environment
- **Feature Toggle**: Specific error when bypass is disabled
- **Server Errors**: Logged but not exposed to maintain security

## Performance Considerations
- **Minimal Overhead**: Simple validation and token generation
- **No Database**: Doesn't require database queries
- **Fast Response**: Immediate token generation
- **Lightweight**: Minimal processing requirements

## Troubleshooting

### Bypass Not Working
1. Check `ENVIRONMENT` variable is set to `development`
2. Verify `BYPASS_AUTH` is set to `true`
3. Confirm application is restarted after configuration changes
4. Check logs for bypass validation errors

### Production Access
1. Verify environment is not set to `production`
2. Check feature toggle configuration
3. Review deployment configuration
4. Ensure environment variables are properly set

## Deprecation Notice
This endpoint is intended for development only and may be removed in production builds.
