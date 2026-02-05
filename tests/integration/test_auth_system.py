"""
Integration Tests for Authentication System

This module contains end-to-end authentication system integration tests.
"""

import pytest
import json
from datetime import datetime, timedelta
from src.models.models import User, db
from src.core.config import settings


class TestAuthSystem:
    """End-to-end authentication system integration tests."""
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self, app, client):
        """Set up clean test environment."""
        with app.app_context():
            # Clean up test data
            User.query.filter(User.username.like('test_%')).delete()
            db.session.commit()
    
    def test_complete_authentication_flow(self, client):
        """Test complete authentication flow from registration to protected access."""
        
        # Step 1: Register user
        user_data = {
            "username": "test_auth_user",
            "email": "test_auth@example.com",
            "password": "TestPassword123!",
            "role": "staff"
        }
        
        response = client.post('/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        registration_result = response.get_json()
        assert registration_result['message'] == "User registered successfully"
        assert registration_result['username'] == "test_auth_user"
        
        # Step 2: Login user
        login_data = {
            "username": "test_auth_user",
            "password": "TestPassword123!"
        }
        
        response = client.post('/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        login_result = response.get_json()
        assert login_result['message'] == "Login successful"
        assert 'access_token' in login_result
        
        # Step 3: Access protected endpoint
        token = login_result['access_token']
        auth_headers = {'Authorization': f'Bearer {token}'}
        
        response = client.get('/auth/users', headers=auth_headers)
        
        assert response.status_code == 200
        users_result = response.get_json()
        assert isinstance(users_result, list)
        
        # Step 4: Verify user is in the list
        user_usernames = [user['username'] for user in users_result]
        assert "test_auth_user" in user_usernames
    
    def test_authentication_with_different_roles(self, client):
        """Test authentication with different user roles."""
        
        # Create users with different roles
        roles = ['admin', 'manager', 'staff']
        created_users = {}
        
        for role in roles:
            user_data = {
                "username": f"test_{role}_user",
                "email": f"test_{role}@example.com",
                "password": "TestPassword123!",
                "role": role
            }
            
            # Register user
            response = client.post('/auth/register',
                                 data=json.dumps(user_data),
                                 content_type='application/json')
            assert response.status_code == 201
            
            # Login user
            login_data = {
                "username": f"test_{role}_user",
                "password": "TestPassword123!"
            }
            
            response = client.post('/auth/login',
                                 data=json.dumps(login_data),
                                 content_type='application/json')
            assert response.status_code == 200
            
            created_users[role] = response.get_json()['access_token']
        
        # Test that all roles can access basic endpoints
        for role, token in created_users.items():
            auth_headers = {'Authorization': f'Bearer {token}'}
            
            response = client.get('/auth/users', headers=auth_headers)
            assert response.status_code == 200
    
    def test_authentication_token_expiration(self, client):
        """Test authentication token expiration."""
        
        # Register and login user
        user_data = {
            "username": "test_token_user",
            "email": "test_token@example.com",
            "password": "TestPassword123!",
            "role": "staff"
        }
        
        client.post('/auth/register',
                   data=json.dumps(user_data),
                   content_type='application/json')
        
        login_data = {
            "username": "test_token_user",
            "password": "TestPassword123!"
        }
        
        response = client.post('/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        token = response.get_json()['access_token']
        auth_headers = {'Authorization': f'Bearer {token}'}
        
        # Test token works immediately
        response = client.get('/auth/users', headers=auth_headers)
        assert response.status_code == 200
        
        # Note: JWT expiration testing would require time manipulation
        # or very short token expiration times, which is beyond basic integration testing
    
    def test_authentication_error_handling(self, client):
        """Test authentication error handling."""
        
        # Test registration with invalid data
        invalid_data = {
            "username": "a",  # Too short
            "email": "invalid-email",  # Invalid format
            "password": "weak",  # Too weak
            "role": "invalid_role"  # Invalid role
        }
        
        response = client.post('/auth/register',
                             data=json.dumps(invalid_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        result = response.get_json()
        assert 'error' in result
        
        # Test login with invalid credentials
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        
        response = client.post('/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 401
        result = response.get_json()
        assert 'error' in result
        
        # Test access without authentication
        response = client.get('/auth/users')
        
        if settings.feature_toggles.BYPASS_AUTH and settings.is_development():
            # In development with bypass, should work
            assert response.status_code == 200
        else:
            # In production, should require authentication
            assert response.status_code == 401
    
    def test_authentication_concurrent_access(self, client):
        """Test concurrent authentication access."""
        
        import threading
        import time
        
        results = []
        errors = []
        
        def authenticate_user(user_id):
            try:
                user_data = {
                    "username": f"concurrent_user_{user_id}",
                    "email": f"concurrent_{user_id}@example.com",
                    "password": "TestPassword123!",
                    "role": "staff"
                }
                
                # Register
                response = client.post('/auth/register',
                                     data=json.dumps(user_data),
                                     content_type='application/json')
                
                if response.status_code == 201:
                    # Login
                    login_data = {
                        "username": f"concurrent_user_{user_id}",
                        "password": "TestPassword123!"
                    }
                    
                    response = client.post('/auth/login',
                                         data=json.dumps(login_data),
                                         content_type='application/json')
                    
                    if response.status_code == 200:
                        token = response.get_json()['access_token']
                        auth_headers = {'Authorization': f'Bearer {token}'}
                        
                        # Access protected endpoint
                        response = client.get('/auth/users', headers=auth_headers)
                        
                        results.append({
                            'user_id': user_id,
                            'status': response.status_code
                        })
                    else:
                        errors.append(f"Login failed for user {user_id}")
                else:
                    errors.append(f"Registration failed for user {user_id}")
                    
            except Exception as e:
                errors.append(f"Exception for user {user_id}: {str(e)}")
        
        # Create multiple threads for concurrent authentication
        threads = []
        for i in range(5):
            thread = threading.Thread(target=authenticate_user, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5
        
        for result in results:
            assert result['status'] == 200
    
    def test_authentication_database_integrity(self, client):
        """Test authentication database integrity."""
        
        # Register user
        user_data = {
            "username": "test_integrity_user",
            "email": "test_integrity@example.com",
            "password": "TestPassword123!",
            "role": "staff"
        }
        
        response = client.post('/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        # Verify user exists in database
        with client.application.app_context():
            user = User.query.filter_by(username="test_integrity_user").first()
            assert user is not None
            assert user.email == "test_integrity@example.com"
            assert user.role == "staff"
            assert user.check_password("TestPassword123!")
        
        # Login and get token
        login_data = {
            "username": "test_integrity_user",
            "password": "TestPassword123!"
        }
        
        response = client.post('/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        token = response.get_json()['access_token']
        
        # Update user
        update_data = {
            "email": "updated_integrity@example.com"
        }
        
        auth_headers = {'Authorization': f'Bearer {token}'}
        response = client.put('/auth/users/1',
                            data=json.dumps(update_data),
                            headers=auth_headers,
                            content_type='application/json')
        
        assert response.status_code == 200
        
        # Verify update in database
        with client.application.app_context():
            user = User.query.filter_by(username="test_integrity_user").first()
            assert user.email == "updated_integrity@example.com"
    
    def test_authentication_security_features(self, client):
        """Test authentication security features."""
        
        # Test password hashing
        user_data = {
            "username": "test_security_user",
            "email": "test_security@example.com",
            "password": "TestPassword123!",
            "role": "staff"
        }
        
        response = client.post('/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        # Verify password is hashed in database
        with client.application.app_context():
            user = User.query.filter_by(username="test_security_user").first()
            assert user.password_hash is not None
            assert user.password_hash != "TestPassword123!"
            assert user.check_password("TestPassword123!")
            assert not user.check_password("WrongPassword123!")
        
        # Test JWT token structure
        login_data = {
            "username": "test_security_user",
            "password": "TestPassword123!"
        }
        
        response = client.post('/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        token = response.get_json()['access_token']
        
        # Token should be properly formatted
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are typically long
        
        # Test malformed token
        malformed_headers = {'Authorization': 'Bearer malformed_token'}
        response = client.get('/auth/users', headers=malformed_headers)
        
        if not (settings.feature_toggles.BYPASS_AUTH and settings.is_development()):
            assert response.status_code == 401
    
    def test_authentication_performance(self, client):
        """Test authentication performance."""
        
        import time
        
        # Measure registration time
        start_time = time.time()
        
        user_data = {
            "username": "test_perf_user",
            "email": "test_perf@example.com",
            "password": "TestPassword123!",
            "role": "staff"
        }
        
        response = client.post('/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        registration_time = time.time() - start_time
        assert response.status_code == 201
        assert registration_time < 2.0  # Should complete within 2 seconds
        
        # Measure login time
        start_time = time.time()
        
        login_data = {
            "username": "test_perf_user",
            "password": "TestPassword123!"
        }
        
        response = client.post('/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        login_time = time.time() - start_time
        assert response.status_code == 200
        assert login_time < 1.0  # Should complete within 1 second
        
        # Measure protected endpoint access time
        token = response.get_json()['access_token']
        auth_headers = {'Authorization': f'Bearer {token}'}
        
        start_time = time.time()
        response = client.get('/auth/users', headers=auth_headers)
        access_time = time.time() - start_time
        
        assert response.status_code == 200
        assert access_time < 0.5  # Should complete within 0.5 seconds
    
    def test_authentication_development_bypass(self, client):
        """Test authentication development bypass functionality."""
        
        if settings.feature_toggles.BYPASS_AUTH and settings.is_development():
            # Test dev-login endpoint
            response = client.post('/auth/dev-login',
                                 data=json.dumps({}),
                                 content_type='application/json')
            
            assert response.status_code == 200
            result = response.get_json()
            assert 'access_token' in result
            assert result['bypass_enabled'] is True
            
            # Test bypass access to protected endpoints
            response = client.get('/auth/users')
            assert response.status_code == 200
            result = response.get_json()
            assert 'auth_bypassed' in result
            assert result['auth_bypassed'] is True
        else:
            # Dev-login should not be available
            response = client.post('/auth/dev-login',
                                 data=json.dumps({}),
                                 content_type='application/json')
            
            assert response.status_code == 404
    
    def test_authentication_error_recovery(self, client):
        """Test authentication error recovery."""
        
        # Test database connection error recovery
        with patch('src.models.models.User.query') as mock_query:
            mock_query.side_effect = Exception("Database connection failed")
            
            response = client.post('/auth/login',
                                 data=json.dumps({
                                     "username": "test_user",
                                     "password": "test_password"
                                 }),
                                 content_type='application/json')
            
            assert response.status_code == 500
            result = response.get_json()
            assert 'error' in result
        
        # Test that system recovers for next request
        response = client.post('/auth/login',
                             data=json.dumps({
                                 "username": "nonexistent",
                                 "password": "wrongpassword"
                             }),
                             content_type='application/json')
        
        assert response.status_code == 401
        result = response.get_json()
        assert 'error' in result
    
    def test_authentication_logging(self, client):
        """Test authentication logging functionality."""
        
        # Test successful registration logging
        with patch('src.core.logging.logger') as mock_logger:
            mock_logger.info = Mock()
            
            user_data = {
                "username": "test_logging_user",
                "email": "test_logging@example.com",
                "password": "TestPassword123!",
                "role": "staff"
            }
            
            response = client.post('/auth/register',
                                 data=json.dumps(user_data),
                                 content_type='application/json')
            
            assert response.status_code == 201
            # Verify logging was called
            assert mock_logger.info.called
        
        # Test failed login logging
        with patch('src.core.logging.logger') as mock_logger:
            mock_logger.warning = Mock()
            
            response = client.post('/auth/login',
                                 data=json.dumps({
                                     "username": "nonexistent",
                                     "password": "wrongpassword"
                                 }),
                                 content_type='application/json')
            
            assert response.status_code == 401
            # Verify warning logging was called
            assert mock_logger.warning.called
    
    def test_authentication_configuration_integration(self, client):
        """Test authentication integration with configuration."""
        
        # Test that configuration affects authentication behavior
        if settings.feature_toggles.BYPASS_AUTH and settings.is_development():
            # Bypass should work
            response = client.get('/auth/users')
            assert response.status_code == 200
        else:
            # Bypass should not work
            response = client.get('/auth/users')
            assert response.status_code == 401
        
        # Test JWT configuration
        user_data = {
            "username": "test_config_user",
            "email": "test_config@example.com",
            "password": "TestPassword123!",
            "role": "staff"
        }
        
        response = client.post('/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        login_data = {
            "username": "test_config_user",
            "password": "TestPassword123!"
        }
        
        response = client.post('/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        token = response.get_json()['access_token']
        
        # Token should work with current configuration
        auth_headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/auth/users', headers=auth_headers)
        assert response.status_code == 200
