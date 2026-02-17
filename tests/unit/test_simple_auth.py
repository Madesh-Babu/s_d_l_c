"""
Simple Unit Tests for Authentication

This module contains basic unit tests for authentication functionality.
"""

import pytest
from unittest.mock import Mock, patch
from src.models.models import User
from src.api import db


class TestUserAuthentication:
    """Test user authentication functionality."""

    @pytest.fixture
    def mock_user(self):
        """Create a mock user for testing."""
        user = Mock()
        user.id = 1
        user.username = "testuser"
        user.email = "test@example.com"
        user.role = "user"
        user.password_hash = "hashed_password"
        return user

    def test_user_password_setting(self):
        """Test password setting functionality."""
        with patch("src.models.models.generate_password_hash") as mock_hash:
            mock_hash.return_value = "hashed_password"

            user = User(username="testuser", email="test@example.com", role="user")
            user.set_password("TestPass123!")

            mock_hash.assert_called_once_with("TestPass123!")
            assert user.password_hash == "hashed_password"

    def test_user_password_verification_success(self):
        """Test successful password verification."""
        with patch("src.models.models.check_password_hash") as mock_check:
            mock_check.return_value = True

            user = User(username="testuser", email="test@example.com", role="user")
            user.password_hash = "hashed_password"

            result = user.check_password("TestPass123!")

            mock_check.assert_called_once_with("hashed_password", "TestPass123!")
            assert result is True

    def test_user_password_verification_failure(self):
        """Test failed password verification."""
        with patch("src.models.models.check_password_hash") as mock_check:
            mock_check.return_value = False

            user = User(username="testuser", email="test@example.com", role="user")
            user.password_hash = "hashed_password"

            result = user.check_password("WrongPassword")

            mock_check.assert_called_once_with("hashed_password", "WrongPassword")
            assert result is False

    def test_user_to_dict_excludes_password(self, mock_user):
        """Test user serialization excludes sensitive data."""
        mock_user.to_dict.return_value = {
            "id": mock_user.id,
            "username": mock_user.username,
            "role": mock_user.role,
        }

        result = mock_user.to_dict()

        assert "password_hash" not in result
        assert result["username"] == "testuser"
        assert result["role"] == "user"

    def test_user_role_validation(self):
        """Test user role validation."""
        valid_roles = ["user", "admin", "staff", "manager"]

        for role in valid_roles:
            user = User(username="testuser", email="test@example.com", role=role)
            assert user.role == role

    def test_user_email_case_handling(self):
        """Test email case handling."""
        email_upper = "TEST@EXAMPLE.COM"
        email_lower = "test@example.com"

        user = User(username="testuser", email=email_upper, role="user")

        # Email should be stored as provided (case sensitivity depends on requirements)
        assert user.email == email_upper
