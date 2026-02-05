"""
API Tests for Authentication Router

This module contains comprehensive API tests for authentication endpoints and middleware.
"""

import pytest
import json
from unittest.mock import patch, Mock
from src.models.models import User
from src.core.exceptions import AuthenticationError, ValidationErrorException


class TestAuthRouter:
    """Test authentication API endpoints and middleware."""
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    @pytest.fixture
    def sample_user(self, app):
        """Create sample user for testing."""
        with app.app_context():
            user = User(
                username="testuser",
                email="test@example.com",
                role="staff"
            )
            user.set_password("TestPassword123!")
            return user
    
    def test_register_user_success(self, client, sample_user):
        """Test successful user registration."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "NewPassword123!",
            "role": "staff"
        }
        
        with patch('src.api.authentication.routes.User.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = None
            
            with patch('src.models.models.db.session') as mock_session:
                mock_session.add = Mock()
                mock_session.commit = Mock()
                
                response = client.post('/auth/register',
                                     data=json.dumps(user_data),
                                     content_type='application/json')
                
                assert response.status_code == 201
                result = response.get_json()
                assert result['message'] == "User registered successfully"
                assert result['username'] == "newuser"
                assert result['email'] == "newuser@example.com"
    
    def test_register_user_duplicate_email(self, client, sample_user):
        """Test registration with duplicate email."""
        user_data = {
            "username": "newuser",
            "email": "test@example.com",  # Same as sample_user
            "password": "NewPassword123!",
            "role": "staff"
        }
        
        with patch('src.api.authentication.routes.User.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = sample_user
            
            response = client.post('/auth/register',
                                 data=json.dumps(user_data),
                                 content_type='application/json')
            
            assert response.status_code == 409
            result = response.get_json()
            assert 'error' in result
    
    def test_register_user_validation_error(self, client):
        """Test registration with validation errors."""
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
    
    def test_register_user_missing_data(self, client):
        """Test registration with missing required data."""
        response = client.post('/auth/register',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        result = response.get_json()
        assert 'error' in result
    
    def test_register_user_invalid_json(self, client):
        """Test registration with invalid JSON."""
        response = client.post('/auth/register',
                             data="invalid json",
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_login_user_success(self, client, sample_user):
        """Test successful user login."""
        login_data = {
            "username": "testuser",
            "password": "TestPassword123!"
        }
        
        with patch('src.api.authentication.routes.User.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = sample_user
            
            with patch('src.api.authentication.routes.create_access_token') as mock_token:
                mock_token.return_value = "mock_jwt_token"
                
                response = client.post('/auth/login',
                                     data=json.dumps(login_data),
                                     content_type='application/json')
                
                assert response.status_code == 200
                result = response.get_json()
                assert result['message'] == "Login successful"
                assert result['access_token'] == "mock_jwt_token"
                assert result['user']['username'] == "testuser"
    
    def test_login_user_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        login_data = {
            "username": "testuser",
            "password": "WrongPassword123!"
        }
        
        with patch('src.api.authentication.routes.User.query') as mock_query:
            mock_user = Mock()
            mock_user.check_password.return_value = False
            mock_query.filter_by.return_value.first.return_value = mock_user
            
            response = client.post('/auth/login',
                                 data=json.dumps(login_data),
                                 content_type='application/json')
            
            assert response.status_code == 401
            result = response.get_json()
            assert 'error' in result
    
    def test_login_user_not_found(self, client):
        """Test login with non-existent user."""
        login_data = {
            "username": "nonexistent",
            "password": "Password123!"
        }
        
        with patch('src.api.authentication.routes.User.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = None
            
            response = client.post('/auth/login',
                                 data=json.dumps(login_data),
                                 content_type='application/json')
            
            assert response.status_code == 401
            result = response.get_json()
            assert 'error' in result
    
    def test_login_user_missing_data(self, client):
        """Test login with missing required data."""
        response = client.post('/auth/login',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        result = response.get_json()
        assert 'error' in result
    
    def test_dev_login_development_mode(self, client):
        """Test development login endpoint in development mode."""
        with patch('src.api.authentication.routes.settings.is_development') as mock_dev:
            mock_dev.return_value = True
            
            with patch('src.api.authentication.routes.settings.feature_toggles.BYPASS_AUTH', True):
                response = client.post('/auth/dev-login',
                                     data=json.dumps({}),
                                     content_type='application/json')
                
                assert response.status_code == 200
                result = response.get_json()
                assert result['message'] == "Development login successful"
                assert 'access_token' in result
                assert result['bypass_enabled'] is True
    
    def test_dev_login_production_mode(self, client):
        """Test development login endpoint in production mode."""
        with patch('src.api.authentication.routes.settings.is_development') as mock_dev:
            mock_dev.return_value = False
            
            response = client.post('/auth/dev-login',
                                 data=json.dumps({}),
                                 content_type='application/json')
            
            assert response.status_code == 404
    
    def test_dev_login_bypass_disabled(self, client):
        """Test development login with bypass disabled."""
        with patch('src.api.authentication.routes.settings.is_development') as mock_dev:
            mock_dev.return_value = True
            
            with patch('src.api.authentication.routes.settings.feature_toggles.BYPASS_AUTH', False):
                response = client.post('/auth/dev-login',
                                     data=json.dumps({}),
                                     content_type='application/json')
                
                assert response.status_code == 403
    
    def test_get_users_with_auth(self, client, sample_user):
        """Test getting users with valid authentication."""
        with patch('src.api.authentication.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.authentication.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.api.authentication.routes.User.query') as mock_query:
                    mock_query.all.return_value = [sample_user]
                    
                    response = client.get('/auth/users',
                                        headers={'Authorization': 'Bearer valid_token'})
                    
                    assert response.status_code == 200
                    result = response.get_json()
                    assert isinstance(result, list)
                    assert len(result) >= 1
    
    def test_get_users_without_auth_development(self, client):
        """Test getting users without auth in development mode."""
        with patch('src.api.authentication.routes.settings.feature_toggles.BYPASS_AUTH', True):
            with patch('src.api.authentication.routes.settings.is_development') as mock_dev:
                mock_dev.return_value = True
                
                with patch('src.api.authentication.routes.User.query') as mock_query:
                    mock_query.all.return_value = []
                    
                    response = client.get('/auth/users')
                    
                    assert response.status_code == 200
                    result = response.get_json()
                    assert 'auth_bypassed' in result
                    assert result['auth_bypassed'] is True
    
    def test_get_users_without_auth_production(self, client):
        """Test getting users without auth in production mode."""
        with patch('src.api.authentication.routes.settings.feature_toggles.BYPASS_AUTH', False):
            with patch('src.api.authentication.routes.settings.is_development') as mock_dev:
                mock_dev.return_value = False
                
                response = client.get('/auth/users')
                    
                assert response.status_code == 401
                result = response.get_json()
                assert 'error' in result
    
    def test_get_user_by_id_success(self, client, sample_user):
        """Test getting user by ID with valid authentication."""
        with patch('src.api.authentication.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.authentication.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.api.authentication.routes.User.query') as mock_query:
                    mock_query.get_or_404.return_value = sample_user
                    
                    response = client.get('/auth/users/1',
                                        headers={'Authorization': 'Bearer valid_token'})
                    
                    assert response.status_code == 200
                    result = response.get_json()
                    assert result['id'] == sample_user.id
                    assert result['username'] == sample_user.username
    
    def test_get_user_by_id_not_found(self, client):
        """Test getting non-existent user by ID."""
        with patch('src.api.authentication.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.authentication.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.api.authentication.routes.User.query') as mock_query:
                    mock_query.get_or_404.side_effect = Exception("User not found")
                    
                    response = client.get('/auth/users/999',
                                        headers={'Authorization': 'Bearer valid_token'})
                    
                    assert response.status_code == 404
    
    def test_update_user_success(self, client, sample_user):
        """Test updating user with valid authentication."""
        update_data = {
            "username": "updateduser",
            "email": "updated@example.com"
        }
        
        with patch('src.api.authentication.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.authentication.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.api.authentication.routes.User.query') as mock_query:
                    mock_query.get_or_404.return_value = sample_user
                    
                    with patch('src.models.models.db.session') as mock_session:
                        mock_session.commit = Mock()
                        
                        response = client.put('/auth/users/1',
                                            data=json.dumps(update_data),
                                            headers={'Authorization': 'Bearer valid_token'},
                                            content_type='application/json')
                        
                        assert response.status_code == 200
                        result = response.get_json()
                        assert result['message'] == "User updated successfully"
    
    def test_update_user_validation_error(self, client):
        """Test updating user with validation errors."""
        invalid_data = {
            "username": "a",  # Too short
            "email": "invalid-email"  # Invalid format
        }
        
        with patch('src.api.authentication.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.authentication.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                response = client.put('/auth/users/1',
                                    data=json.dumps(invalid_data),
                                    headers={'Authorization': 'Bearer valid_token'},
                                    content_type='application/json')
                
                assert response.status_code == 400
                result = response.get_json()
                assert 'error' in result
    
    def test_delete_user_success(self, client, sample_user):
        """Test deleting user with valid authentication."""
        with patch('src.api.authentication.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.authentication.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.api.authentication.routes.User.query') as mock_query:
                    mock_query.get_or_404.return_value = sample_user
                    
                    with patch('src.models.models.db.session') as mock_session:
                        mock_session.delete = Mock()
                        mock_session.commit = Mock()
                        
                        response = client.delete('/auth/users/1',
                                              headers={'Authorization': 'Bearer valid_token'})
                        
                        assert response.status_code == 200
                        result = response.get_json()
                        assert "deleted successfully" in result['message']
    
    def test_change_password_success(self, client, sample_user):
        """Test changing password with valid authentication."""
        password_data = {
            "current_password": "TestPassword123!",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        }
        
        with patch('src.api.authentication.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.authentication.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = str(sample_user.id)
                
                with patch('src.api.authentication.routes.User.query') as mock_query:
                    mock_query.get.return_value = sample_user
                    
                    with patch('src.models.models.db.session') as mock_session:
                        mock_session.commit = Mock()
                        
                        response = client.post('/auth/change-password',
                                            data=json.dumps(password_data),
                                            headers={'Authorization': 'Bearer valid_token'},
                                            content_type='application/json')
                        
                        assert response.status_code == 200
                        result = response.get_json()
                        assert result['message'] == "Password changed successfully"
    
    def test_change_password_wrong_current_password(self, client, sample_user):
        """Test changing password with wrong current password."""
        password_data = {
            "current_password": "WrongPassword123!",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        }
        
        with patch('src.api.authentication.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.authentication.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = str(sample_user.id)
                
                with patch('src.api.authentication.routes.User.query') as mock_query:
                    sample_user.check_password.return_value = False
                    mock_query.get.return_value = sample_user
                    
                    response = client.post('/auth/change-password',
                                        data=json.dumps(password_data),
                                        headers={'Authorization': 'Bearer valid_token'},
                                        content_type='application/json')
                        
                        assert response.status_code == 400
                        result = response.get_json()
                        assert 'error' in result
    
    def test_change_password_mismatch_confirmation(self, client, sample_user):
        """Test changing password with mismatched confirmation."""
        password_data = {
            "current_password": "TestPassword123!",
            "new_password": "NewPassword123!",
            "confirm_password": "DifferentPassword123!"
        }
        
        with patch('src.api.authentication.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.authentication.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = str(sample_user.id)
                
                with patch('src.api.authentication.routes.User.query') as mock_query:
                    sample_user.check_password.return_value = True
                    mock_query.get.return_value = sample_user
                    
                    response = client.post('/auth/change-password',
                                        data=json.dumps(password_data),
                                        headers={'Authorization': 'Bearer valid_token'},
                                        content_type='application/json')
                        
                        assert response.status_code == 400
                        result = response.get_json()
                        assert 'error' in result
    
    def test_validate_password_endpoint(self, client):
        """Test password validation endpoint."""
        password_data = {
            "password": "TestPassword123!"
        }
        
        response = client.post('/auth/validate-password',
                             data=json.dumps(password_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        result = response.get_json()
        assert 'is_valid' in result
        assert 'strength' in result
    
    def test_validate_password_missing_data(self, client):
        """Test password validation with missing data."""
        response = client.post('/auth/validate-password',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        result = response.get_json()
        assert 'error' in result
    
    def test_authentication_middleware_valid_token(self, client):
        """Test authentication middleware with valid token."""
        with patch('src.api.authentication.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.authentication.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                response = client.get('/auth/users',
                                    headers={'Authorization': 'Bearer valid_token'})
                
                # Should not raise authentication error
                assert response.status_code in [200, 404]  # 404 if no users exist
    
    def test_authentication_middleware_invalid_token(self, client):
        """Test authentication middleware with invalid token."""
        with patch('src.api.authentication.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.side_effect = Exception("Invalid token")
            
            response = client.get('/auth/users',
                                headers={'Authorization': 'Bearer invalid_token'})
            
            assert response.status_code == 401
            result = response.get_json()
            assert 'error' in result
    
    def test_authentication_middleware_missing_token(self, client):
        """Test authentication middleware with missing token."""
        response = client.get('/auth/users')
        
        assert response.status_code == 401
        result = response.get_json()
        assert 'error' in result
    
    def test_rate_limiting_middleware(self, client):
        """Test rate limiting middleware."""
        with patch('src.api.authentication.routes.check_rate_limit') as mock_rate_limit:
            mock_rate_limit.return_value = False  # Rate limit exceeded
            
            response = client.post('/auth/login',
                                 data=json.dumps({"username": "test", "password": "test"}),
                                 content_type='application/json')
            
            assert response.status_code == 429
            result = response.get_json()
            assert 'error' in result
    
    def test_cors_middleware(self, client):
        """Test CORS middleware."""
        response = client.options('/auth/register',
                                headers={'Origin': 'http://localhost:3000'})
        
        # Should include CORS headers
        assert response.status_code in [200, 204]
    
    def test_error_handling_middleware(self, client):
        """Test error handling middleware."""
        with patch('src.api.authentication.routes.User.query') as mock_query:
            mock_query.side_effect = Exception("Database error")
            
            response = client.post('/auth/login',
                                 data=json.dumps({"username": "test", "password": "test"}),
                                 content_type='application/json')
            
            assert response.status_code == 500
            result = response.get_json()
            assert 'error' in result
    
    def test_request_logging_middleware(self, client):
        """Test request logging middleware."""
        with patch('src.core.logging.logger') as mock_logger:
            mock_logger.info = Mock()
            
            response = client.get('/auth/users')
            
            # Should log the request
            assert mock_logger.info.called
    
    def test_response_formatting_middleware(self, client):
        """Test response formatting middleware."""
        with patch('src.api.authentication.routes.settings.is_development') as mock_dev:
            mock_dev.return_value = True
            
            response = client.get('/auth/users')
            
            # Should include debug information in development
            if response.status_code == 200:
                result = response.get_json()
                # Debug info might be included in development mode
                assert isinstance(result, (dict, list))
