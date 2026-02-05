"""
Unit Tests for Authentication Service

This module contains comprehensive unit tests for authentication business logic,
testing the core authentication service functionality in isolation.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from src.core.authentication import AuthService
from src.models.models import User
from src.core.exceptions import AuthenticationError, ValidationErrorException


class TestAuthServiceComprehensive:
    """Comprehensive unit tests for authentication service business logic."""
    
    @pytest.fixture
    def auth_service(self):
        """Create auth service instance for testing."""
        return AuthService()
    
    @pytest.fixture
    def mock_user(self):
        """Create mock user for testing."""
        user = Mock(spec=User)
        user.id = 1
        user.username = "testuser"
        user.email = "test@example.com"
        user.role = "staff"
        user.password_hash = "hashed_password"
        user.check_password.return_value = True
        user.set_password = Mock()
        return user
    
    def test_user_registration_success(self, auth_service, mock_user):
        """Test successful user registration."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "role": "staff"
        }
        
        with patch.object(auth_service, 'create_user') as mock_create:
            mock_create.return_value = mock_user
            
            result = auth_service.register_user(user_data)
            
            assert result is not None
            mock_create.assert_called_once_with(user_data)
    
    def test_user_registration_duplicate_email(self, auth_service):
        """Test registration with duplicate email."""
        user_data = {
            "username": "testuser",
            "email": "existing@example.com",
            "password": "TestPassword123!",
            "role": "staff"
        }
        
        with patch.object(auth_service, 'create_user') as mock_create:
            mock_create.side_effect = ValidationErrorException("Email already exists")
            
            with pytest.raises(ValidationErrorException) as exc_info:
                auth_service.register_user(user_data)
            
            assert "Email already exists" in str(exc_info.value)
    
    def test_user_login_success(self, auth_service, mock_user):
        """Test successful user login."""
        login_data = {
            "username": "testuser",
            "password": "TestPassword123!"
        }
        
        with patch.object(auth_service, 'authenticate_user') as mock_auth:
            mock_auth.return_value = mock_user
            
            with patch.object(auth_service, 'generate_token') as mock_token:
                mock_token.return_value = "mock_jwt_token"
                
                result = auth_service.login_user(login_data)
                
                assert result['access_token'] == "mock_jwt_token"
                assert result['user']['username'] == "testuser"
                mock_auth.assert_called_once_with("testuser", "TestPassword123!")
    
    def test_user_login_invalid_credentials(self, auth_service):
        """Test login with invalid credentials."""
        login_data = {
            "username": "testuser",
            "password": "WrongPassword123!"
        }
        
        with patch.object(auth_service, 'authenticate_user') as mock_auth:
            mock_auth.side_effect = AuthenticationError("Invalid credentials")
            
            with pytest.raises(AuthenticationError) as exc_info:
                auth_service.login_user(login_data)
            
            assert "Invalid credentials" in str(exc_info.value)
    
    def test_password_validation_strong_password(self, auth_service):
        """Test strong password validation."""
        strong_password = "StrongPassword123!"
        
        result = auth_service.validate_password(strong_password)
        
        assert result['is_valid'] is True
        assert result['strength'] == 'strong'
        assert len(result['feedback']) == 0
    
    def test_password_validation_weak_password(self, auth_service):
        """Test weak password validation."""
        weak_password = "weak"
        
        result = auth_service.validate_password(weak_password)
        
        assert result['is_valid'] is False
        assert result['strength'] == 'weak'
        assert len(result['feedback']) > 0
    
    def test_password_validation_medium_password(self, auth_service):
        """Test medium strength password validation."""
        medium_password = "MediumPass123"
        
        result = auth_service.validate_password(medium_password)
        
        assert result['is_valid'] is True
        assert result['strength'] in ['medium', 'strong']
    
    def test_token_generation(self, auth_service, mock_user):
        """Test JWT token generation."""
        with patch('src.core.authentication.create_access_token') as mock_create_token:
            mock_create_token.return_value = "generated_token"
            
            token = auth_service.generate_token(mock_user)
            
            assert token == "generated_token"
            mock_create_token.assert_called_once_with(identity=str(mock_user.id))
    
    def test_token_validation_valid_token(self, auth_service, mock_user):
        """Test valid token validation."""
        valid_token = "valid_jwt_token"
        
        with patch('src.core.authentication.get_jwt_identity') as mock_identity:
            mock_identity.return_value = str(mock_user.id)
            
            with patch.object(auth_service, 'get_user_by_id') as mock_get_user:
                mock_get_user.return_value = mock_user
                
                result = auth_service.validate_token(valid_token)
                
                assert result is not None
                assert result.id == mock_user.id
                assert result.username == mock_user.username
    
    def test_token_validation_invalid_token(self, auth_service):
        """Test invalid token validation."""
        invalid_token = "invalid_token"
        
        with patch('src.core.authentication.get_jwt_identity') as mock_identity:
            mock_identity.side_effect = Exception("Invalid token")
            
            with pytest.raises(AuthenticationError) as exc_info:
                auth_service.validate_token(invalid_token)
            
            assert "Invalid token" in str(exc_info.value)
    
    def test_user_role_validation_admin(self, auth_service, mock_user):
        """Test admin role validation."""
        mock_user.role = "admin"
        
        result = auth_service.validate_user_role(mock_user, "admin")
        
        assert result is True
    
    def test_user_role_validation_insufficient_permissions(self, auth_service, mock_user):
        """Test insufficient role permissions."""
        mock_user.role = "staff"
        
        result = auth_service.validate_user_role(mock_user, "admin")
        
        assert result is False
    
    def test_user_creation_with_password_hashing(self, auth_service):
        """Test user creation with proper password hashing."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "NewPassword123!",
            "role": "staff"
        }
        
        with patch('src.models.models.User') as mock_user_class:
            mock_user_instance = Mock()
            mock_user_class.return_value = mock_user_instance
            
            with patch('src.core.models.db.session') as mock_session:
                result = auth_service.create_user(user_data)
                
                mock_user_instance.set_password.assert_called_once_with("NewPassword123!")
                mock_session.add.assert_called_once_with(mock_user_instance)
                mock_session.commit.assert_called_once()
    
    def test_user_authentication_success(self, auth_service, mock_user):
        """Test successful user authentication."""
        with patch('src.models.models.User.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_user
            
            result = auth_service.authenticate_user("testuser", "TestPassword123!")
            
            assert result is not None
            assert result.username == "testuser"
            mock_user.check_password.assert_called_once_with("TestPassword123!")
    
    def test_user_authentication_user_not_found(self, auth_service):
        """Test authentication with non-existent user."""
        with patch('src.models.models.User.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = None
            
            with pytest.raises(AuthenticationError) as exc_info:
                auth_service.authenticate_user("nonexistent", "password")
            
            assert "User not found" in str(exc_info.value)
    
    def test_user_authentication_wrong_password(self, auth_service, mock_user):
        """Test authentication with wrong password."""
        mock_user.check_password.return_value = False
        
        with patch('src.models.models.User.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_user
            
            with pytest.raises(AuthenticationError) as exc_info:
                auth_service.authenticate_user("testuser", "wrongpassword")
            
            assert "Invalid password" in str(exc_info.value)
    
    def test_email_validation_valid_format(self, auth_service):
        """Test valid email format validation."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "user123@test-domain.com"
        ]
        
        for email in valid_emails:
            result = auth_service.validate_email(email)
            assert result['is_valid'] is True
    
    def test_email_validation_invalid_format(self, auth_service):
        """Test invalid email format validation."""
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user..name@domain.com",
            "user@domain..com"
        ]
        
        for email in invalid_emails:
            result = auth_service.validate_email(email)
            assert result['is_valid'] is False
    
    def test_username_validation_valid(self, auth_service):
        """Test valid username validation."""
        valid_usernames = [
            "testuser",
            "user_123",
            "TestUser123",
            "user.name"
        ]
        
        for username in valid_usernames:
            result = auth_service.validate_username(username)
            assert result['is_valid'] is True
    
    def test_username_validation_invalid(self, auth_service):
        """Test invalid username validation."""
        invalid_usernames = [
            "a",  # Too short
            "user with spaces",
            "user@domain",
            "user#name",
            "a" * 21  # Too long
        ]
        
        for username in invalid_usernames:
            result = auth_service.validate_username(username)
            assert result['is_valid'] is False
    
    def test_session_management_create_session(self, auth_service, mock_user):
        """Test session creation."""
        with patch('src.core.authentication.redis_client') as mock_redis:
            mock_redis.setex.return_value = True
            
            session_id = auth_service.create_session(mock_user)
            
            assert session_id is not None
            assert isinstance(session_id, str)
            mock_redis.setex.assert_called_once()
    
    def test_session_management_validate_session(self, auth_service, mock_user):
        """Test session validation."""
        session_id = "valid_session_id"
        
        with patch('src.core.authentication.redis_client') as mock_redis:
            mock_redis.get.return_value = str(mock_user.id).encode()
            
            result = auth_service.validate_session(session_id)
            
            assert result is not None
            assert result.id == mock_user.id
    
    def test_session_management_expired_session(self, auth_service):
        """Test expired session validation."""
        session_id = "expired_session_id"
        
        with patch('src.core.authentication.redis_client') as mock_redis:
            mock_redis.get.return_value = None
            
            result = auth_service.validate_session(session_id)
            
            assert result is None
    
    def test_rate_limiting_check(self, auth_service):
        """Test rate limiting functionality."""
        identifier = "test_ip_address"
        
        with patch('src.core.authentication.redis_client') as mock_redis:
            mock_redis.get.return_value = None  # No existing requests
            mock_redis.setex.return_value = True
            
            result = auth_service.check_rate_limit(identifier)
            
            assert result is True  # Request allowed
            mock_redis.setex.assert_called_once()
    
    def test_rate_limiting_exceeded(self, auth_service):
        """Test rate limiting when limit is exceeded."""
        identifier = "test_ip_address"
        
        with patch('src.core.authentication.redis_client') as mock_redis:
            mock_redis.get.return_value = "10"  # Already at limit
            
            result = auth_service.check_rate_limit(identifier)
            
            assert result is False  # Request denied
    
    def test_password_reset_token_generation(self, auth_service, mock_user):
        """Test password reset token generation."""
        with patch('src.core.authentication.secrets.token_urlsafe') as mock_token:
            mock_token.return_value = "reset_token_123"
            
            with patch('src.core.authentication.redis_client') as mock_redis:
                mock_redis.setex.return_value = True
                
                token = auth_service.generate_password_reset_token(mock_user)
                
                assert token == "reset_token_123"
                mock_redis.setex.assert_called_once()
    
    def test_password_reset_token_validation(self, auth_service, mock_user):
        """Test password reset token validation."""
        token = "valid_reset_token"
        
        with patch('src.core.authentication.redis_client') as mock_redis:
            mock_redis.get.return_value = str(mock_user.id).encode()
            
            result = auth_service.validate_password_reset_token(token)
            
            assert result == str(mock_user.id)
    
    def test_password_reset_execution(self, auth_service, mock_user):
        """Test password reset execution."""
        token = "valid_reset_token"
        new_password = "NewPassword123!"
        
        with patch.object(auth_service, 'validate_password_reset_token') as mock_validate:
            mock_validate.return_value = str(mock_user.id)
            
            with patch.object(auth_service, 'get_user_by_id') as mock_get_user:
                mock_get_user.return_value = mock_user
                
                with patch('src.core.models.db.session') as mock_session:
                    auth_service.reset_password(token, new_password)
                    
                    mock_user.set_password.assert_called_once_with(new_password)
                    mock_session.commit.assert_called_once()
    
    def test_account_lockout_after_failed_attempts(self, auth_service, mock_user):
        """Test account lockout after multiple failed attempts."""
        with patch('src.core.authentication.redis_client') as mock_redis:
            mock_redis.get.return_value = "5"  # 5 failed attempts
            mock_redis.setex.return_value = True
            
            result = auth_service.is_account_locked("testuser")
            
            assert result is True
            mock_redis.setex.assert_called_once()
    
    def test_account_unlock_after_timeout(self, auth_service):
        """Test account unlock after lockout timeout."""
        with patch('src.core.authentication.redis_client') as mock_redis:
            mock_redis.get.return_value = None  # Lock expired
            
            result = auth_service.is_account_locked("testuser")
            
            assert result is False
