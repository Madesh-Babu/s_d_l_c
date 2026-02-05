# Integration Tests

This directory contains comprehensive integration tests for the Inventory Management API.

## Overview

Integration tests verify that multiple components work together correctly. They test complete workflows, API endpoints, database operations, and business logic across the entire application.

## Test Structure

### Test Files

- **`test_authentication_integration.py`** - Complete authentication workflows
- **`test_product_integration.py`** - Product management workflows
- **`test_category_integration.py`** - Category management workflows  
- **`test_complete_api_integration.py`** - End-to-end API workflows
- **`conftest.py`** - Test configuration and fixtures
- **`run_tests.py`** - Test runner utilities

### Test Categories

#### Authentication Integration Tests
- Complete user registration → login → protected resource access
- Role-based access control
- JWT token validation and expiration
- Development bypass functionality
- Error handling and rollback scenarios

#### Product Integration Tests
- Complete CRUD workflows for products
- Product filtering and pagination
- Category-product relationships
- Business rule validation
- Concurrent operations and data consistency

#### Category Integration Tests
- Category CRUD operations
- Hierarchical category relationships
- Parent-child category validation
- Circular reference prevention
- Category-product relationships

#### Complete API Integration Tests
- Multi-user role-based workflows
- Error recovery and data consistency
- Concurrent operations simulation
- Development vs production behavior
- API health and monitoring

## Running Tests

### Run All Integration Tests
```bash
python tests/integration/run_tests.py
```

### Run Specific Test File
```bash
python tests/integration/run_tests.py --file test_authentication_integration.py
```

### Run with Coverage
```bash
python tests/integration/run_tests.py --coverage
```

### Using Pytest Directly
```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific test file
pytest tests/integration/test_authentication_integration.py -v

# Run with coverage
pytest tests/integration/ --cov=src --cov-report=html

# Run specific test markers
pytest tests/integration/ -m "integration and auth" -v
```

## Test Fixtures

### User Fixtures
- `sample_user` - Basic test user
- `admin_user` - Admin role user
- `manager_user` - Manager role user
- `staff_user` - Staff role user

### Authentication Fixtures
- `auth_headers` - Headers for sample user
- `admin_headers` - Headers for admin user
- `manager_headers` - Headers for manager user
- `staff_headers` - Headers for staff user

### Data Fixtures
- `sample_category` - Single test category
- `sample_product` - Single test product
- `multiple_categories` - Multiple test categories
- `multiple_products` - Multiple test products
- `hierarchical_categories` - Parent-child category structure

## Test Features

### Environment Detection
Tests automatically adapt to development vs production environments:
- Authentication bypass testing in development
- Production authentication requirements
- Feature toggle validation

### Database Transactions
All tests use in-memory SQLite database with proper transaction handling:
- Automatic rollback on test failure
- Clean data isolation between tests
- Proper setup and teardown

### Error Scenarios
Comprehensive error testing includes:
- Validation errors with detailed messages
- Database constraint violations
- Authentication and authorization failures
- Network and system errors

### Performance Testing
- Concurrent operation simulation
- Database query optimization verification
- Response time validation
- Memory usage monitoring

## Test Data Management

### Automatic Cleanup
Test fixtures automatically clean up data:
- Prefix-based filtering (test_, sample_)
- Role-based filtering (admin_, manager_, staff_)
- Complete database reset between tests

### Data Consistency
Tests verify data consistency across:
- Multiple endpoint calls
- Different user roles
- Concurrent operations
- Error recovery scenarios

## Development vs Production

### Development Mode Tests
- Authentication bypass functionality
- Debug information validation
- Development-specific endpoints
- Verbose error messages

### Production Mode Tests
- Strict authentication requirements
- Minimal error messages
- Security-focused responses
- Rate limiting validation

## Best Practices

### Test Organization
- Group related tests in logical classes
- Use descriptive test method names
- Provide clear test documentation
- Follow consistent naming conventions

### Test Isolation
- Each test should be independent
- Use fixtures for shared setup
- Clean up data after each test
- Avoid test dependencies

### Error Testing
- Test both success and failure scenarios
- Validate error messages and codes
- Test edge cases and boundary conditions
- Verify rollback behavior

### Performance Testing
- Include timing assertions where appropriate
- Test with realistic data volumes
- Verify database query efficiency
- Monitor memory usage

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Check if bypass is enabled in development
   - Verify user creation and login flow
   - Ensure JWT tokens are properly generated

2. **Database Errors**
   - Verify in-memory database setup
   - Check foreign key constraints
   - Ensure proper transaction handling

3. **Test Isolation**
   - Verify fixture cleanup
   - Check for data leakage between tests
   - Ensure proper teardown

4. **Environment Issues**
   - Verify configuration loading
   - Check feature toggle settings
   - Ensure proper environment detection

### Debug Tips

1. **Use Verbose Output**
   ```bash
   pytest tests/integration/ -v -s
   ```

2. **Run Single Test**
   ```bash
   pytest tests/integration/test_authentication_integration.py::TestAuthenticationIntegration::test_complete_user_workflow -v -s
   ```

3. **Enable Debug Logging**
   ```bash
   pytest tests/integration/ --log-cli-level=DEBUG
   ```

4. **Stop on First Failure**
   ```bash
   pytest tests/integration/ -x --tb=long
   ```

## Coverage Requirements

Integration tests should maintain at least 80% code coverage for:
- API endpoint handlers
- Business logic functions
- Database models and relationships
- Authentication and authorization

## Continuous Integration

Integration tests are designed to run in CI/CD environments:
- No external dependencies required
- Self-contained test database
- Environment-agnostic configuration
- Fast execution times

## Future Enhancements

Planned improvements to integration testing:

1. **API Contract Testing**
   - OpenAPI specification validation
   - Response schema verification
   - Backward compatibility testing

2. **Load Testing**
   - Concurrent user simulation
   - Stress testing scenarios
   - Performance benchmarking

3. **Security Testing**
   - Input validation testing
   - SQL injection prevention
   - XSS protection verification

4. **Cross-Service Testing**
   - Microservice integration
   - External API dependencies
   - Network failure simulation
