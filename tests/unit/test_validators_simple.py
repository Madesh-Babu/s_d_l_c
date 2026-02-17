"""
Simple Unit Tests for Validation Functions

This module contains basic unit tests for available validation functions.
"""

import pytest
from src.core.validation import EmailValidator, PasswordValidator, UserValidator


class TestEmailValidator:
    """Test email validation functionality."""

    def test_valid_emails(self):
        """Test validation of valid email addresses."""
        valid_emails = [
            "simple@example.com",
            "very.common@example.com",
            "disposable.style.email.with+symbol@example.com",
            "user.name+tag+sorting@example.com",
            "x@example.com",
            "example-indeed@strange-example.com",
            "example@s.example",
            "user%example.com@example.org",
        ]

        for email in valid_emails:
            validator = EmailValidator(email=email)
            assert validator.email == email.lower()

    def test_invalid_emails(self):
        """Test validation of invalid email addresses."""
        invalid_emails = [
            "Abc.example.com",  # No @ symbol
            "A@b@c@example.com",  # Multiple @ symbols
            "test@.com",  # Starts with dot
            "test@domain.",  # Ends with dot
            "@test.com",  # No local part
            "test@",  # No domain part
            "test@test",  # No TLD
        ]

        for email in invalid_emails:
            with pytest.raises(ValueError):
                EmailValidator(email=email)


class TestPasswordValidator:
    """Test password validation functionality."""

    def test_strong_passwords(self):
        """Test validation of strong passwords."""
        strong_passwords = [
            "StrongPass123!",
            "MySecure@Password2024",
            "Complex#Passw0rd",
            "Valid$Password99",
        ]

        for password in strong_passwords:
            validator = PasswordValidator(password=password)
            assert validator.password == password

    def test_weak_passwords(self):
        """Test validation of weak passwords."""
        weak_passwords = [
            "weak",  # Too short
            "nouppercase123!",  # No uppercase
            "NOLOWERCASE123!",  # No lowercase
            "NoNumbers!",  # No digits
            "NoSpecialChars123",  # No special chars
            "White Space 123!",  # Contains whitespace
        ]

        for password in weak_passwords:
            with pytest.raises(ValueError):
                PasswordValidator(password=password)

    def test_password_strength_scoring(self):
        """Test password strength scoring."""
        # Test weak password
        strength = PasswordValidator.get_password_strength("weak123")
        assert strength["strength"] == "Weak"
        assert strength["score"] <= 2

        # Test strong password
        strength = PasswordValidator.get_password_strength("StrongPass123!")
        assert strength["strength"] in ["Fair", "Strong"]
        assert strength["score"] >= 4


class TestUserValidator:
    """Test user validation functionality."""

    def test_valid_user_data(self):
        """Test validation of valid user data."""
        user_data = {
            "email": "test@example.com",
            "password": "StrongPass123!",
            "username": "testuser",
        }

        validator = UserValidator(**user_data)
        assert validator.email == "test@example.com"
        assert validator.username == "testuser"
        assert validator.password == "StrongPass123!"

    def test_invalid_email(self):
        """Test validation of invalid email."""
        user_data = {
            "email": "invalid-email",
            "password": "StrongPass123!",
            "username": "testuser",
        }

        with pytest.raises(ValueError):
            UserValidator(**user_data)

    def test_invalid_password(self):
        """Test validation of invalid password."""
        user_data = {
            "email": "test@example.com",
            "password": "weak",
            "username": "testuser",
        }

        with pytest.raises(ValueError):
            UserValidator(**user_data)

    def test_invalid_username(self):
        """Test validation of invalid username."""
        user_data = {
            "email": "test@example.com",
            "password": "StrongPass123!",
            "username": "ab",  # Too short
        }

        with pytest.raises(
            ValueError, match="Username must be at least 3 characters long"
        ):
            UserValidator(**user_data)
