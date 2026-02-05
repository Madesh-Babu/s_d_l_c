"""
Unit Tests for Custom Validation Functions

This module contains comprehensive unit tests for custom validation functions and rules.
"""

import pytest
from src.core.validation import (
    EmailValidator, PasswordValidator, UsernameValidator,
    PhoneNumberValidator, URLValidator, DateValidator,
    BusinessValidator, SecurityValidator
)
from src.core.exceptions import ValidationErrorException


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
            "admin@mailserver1",
            "example@s.example",
            "mailhost!username@example.org",
            "user%example.com@example.org"
        ]
        
        for email in valid_emails:
            validator = EmailValidator(email)
            assert validator.is_valid() is True
            assert len(validator.get_errors()) == 0
    
    def test_invalid_emails(self):
        """Test validation of invalid email addresses."""
        invalid_emails = [
            "Abc.example.com",  # No @ symbol
            "A@b@c@example.com",  # Multiple @ symbols
            "a\"b(c)d,e:f;g<h>i[j\\k]l@example.com",  # Invalid characters
            "just\"not\"right@example.com",  # Quoted strings
            "this is\"not\\allowed@example.com",  # Spaces
            "this\\ still\\\"not\\\\allowed@example.com",  # Backslashes
            "i_like_underscore@but_its_not_allowed_in_this_part.com",  # Invalid local part
            "test@.com",  # Starts with dot
            "test@domain.",  # Ends with dot
            "test@domain..com",  # Double dots
            "@test.com",  # No local part
            "test@",  # No domain part
            "test@test",  # No TLD
            "test@-domain.com",  # Domain starts with hyphen
            "test@domain-.com"  # Domain ends with hyphen
        ]
        
        for email in invalid_emails:
            validator = EmailValidator(email)
            assert validator.is_valid() is False
            assert len(validator.get_errors()) > 0
    
    def test_email_case_sensitivity(self):
        """Test email case sensitivity handling."""
        email = "Test@Example.COM"
        validator = EmailValidator(email)
        
        # Should be valid but normalized
        assert validator.is_valid() is True
        assert validator.get_normalized_email() == "test@example.com"
    
    def test_email_length_validation(self):
        """Test email length validation."""
        # Very long email (should be invalid)
        long_email = "a" * 245 + "@example.com"
        validator = EmailValidator(long_email)
        
        assert validator.is_valid() is False
        assert any("too long" in error.lower() for error in validator.get_errors())


class TestPasswordValidator:
    """Test password validation functionality."""
    
    def test_strong_passwords(self):
        """Test validation of strong passwords."""
        strong_passwords = [
            "StrongPassword123!",
            "MySecureP@ssw0rd",
            "C0mpl3x!P@ssword",
            "R@nd0m#Ch@rs$123",
            "VerySecurePassword2024!"
        ]
        
        for password in strong_passwords:
            validator = PasswordValidator(password)
            assert validator.is_valid() is True
            assert validator.get_strength() in ["strong", "very_strong"]
            assert len(validator.get_errors()) == 0
    
    def test_weak_passwords(self):
        """Test validation of weak passwords."""
        weak_passwords = [
            "weak",
            "password",
            "123456",
            "abc123",
            "password123",
            "qwerty",
            "letmein",
            "admin",
            "user"
        ]
        
        for password in weak_passwords:
            validator = PasswordValidator(password)
            assert validator.is_valid() is False
            assert validator.get_strength() == "weak"
            assert len(validator.get_errors()) > 0
    
    def test_password_requirements(self):
        """Test specific password requirements."""
        # Test minimum length
        validator = PasswordValidator("Short1!")
        assert not validator.is_valid()
        assert any("short" in error.lower() for error in validator.get_errors())
        
        # Test uppercase requirement
        validator = PasswordValidator("nouppercase123!")
        assert not validator.is_valid()
        assert any("uppercase" in error.lower() for error in validator.get_errors())
        
        # Test lowercase requirement
        validator = PasswordValidator("NOLOWERCASE123!")
        assert not validator.is_valid()
        assert any("lowercase" in error.lower() for error in validator.get_errors())
        
        # Test number requirement
        validator = PasswordValidator("NoNumbers!")
        assert not validator.is_valid()
        assert any("number" in error.lower() for error in validator.get_errors())
        
        # Test special character requirement
        validator = PasswordValidator("NoSpecialChars123")
        assert not validator.is_valid()
        assert any("special" in error.lower() for error in validator.get_errors())
    
    def test_password_common_patterns(self):
        """Test detection of common password patterns."""
        common_patterns = [
            "password123!",
            "admin123!",
            "qwerty123!",
            "letmein123!",
            "welcome123!",
            "monkey123!"
        ]
        
        for password in common_patterns:
            validator = PasswordValidator(password)
            assert not validator.is_valid()
            assert any("common" in error.lower() for error in validator.get_errors())
    
    def test_password_personal_info(self):
        """Test detection of personal information in passwords."""
        username = "testuser"
        email = "test@example.com"
        
        # Password containing username
        validator = PasswordValidator("testuser123!", username=username)
        assert not validator.is_valid()
        assert any("username" in error.lower() for error in validator.get_errors())
        
        # Password containing email parts
        validator = PasswordValidator("test123!", email=email)
        assert not validator.is_valid()
        assert any("email" in error.lower() for error in validator.get_errors())
    
    def test_password_strength_scoring(self):
        """Test password strength scoring."""
        test_cases = [
            ("", 0),
            ("a", 1),
            ("abc", 2),
            ("password", 3),
            ("Password123", 5),
            ("Password123!", 7),
            ("StrongPassword123!", 9)
        ]
        
        for password, expected_min_score in test_cases:
            validator = PasswordValidator(password)
            assert validator.get_score() >= expected_min_score


class TestUsernameValidator:
    """Test username validation functionality."""
    
    def test_valid_usernames(self):
        """Test validation of valid usernames."""
        valid_usernames = [
            "testuser",
            "user123",
            "test_user",
            "user.name",
            "TestUser123",
            "user_123_name",
            "a1b2c3",
            "username"
        ]
        
        for username in valid_usernames:
            validator = UsernameValidator(username)
            assert validator.is_valid() is True
            assert len(validator.get_errors()) == 0
    
    def test_invalid_usernames(self):
        """Test validation of invalid usernames."""
        invalid_usernames = [
            "",  # Empty
            "a",  # Too short
            "user with spaces",  # Contains spaces
            "user@domain",  # Contains @ symbol
            "user#name",  # Contains special character
            "user$name",  # Contains dollar sign
            "user%name",  # Contains percent sign
            "a" * 21,  # Too long
            "123user",  # Starts with number
            "-user",  # Starts with hyphen
            "user-",  # Ends with hyphen
            "_user",  # Starts with underscore (depends on policy)
            "user_",  # Ends with underscore (depends on policy)
        ]
        
        for username in invalid_usernames:
            validator = UsernameValidator(username)
            assert validator.is_valid() is False
            assert len(validator.get_errors()) > 0
    
    def test_username_length_validation(self):
        """Test username length validation."""
        # Test minimum length
        validator = UsernameValidator("ab")
        assert not validator.is_valid()
        assert any("short" in error.lower() for error in validator.get_errors())
        
        # Test maximum length
        validator = UsernameValidator("a" * 21)
        assert not validator.is_valid()
        assert any("long" in error.lower() for error in validator.get_errors())
    
    def test_username_case_sensitivity(self):
        """Test username case sensitivity."""
        username = "TestUser"
        validator = UsernameValidator(username)
        
        # Should be valid
        assert validator.is_valid() is True
        
        # Should normalize to lowercase (depending on policy)
        normalized = validator.get_normalized_username()
        assert normalized == "testuser"


class TestPhoneNumberValidator:
    """Test phone number validation functionality."""
    
    def test_valid_phone_numbers(self):
        """Test validation of valid phone numbers."""
        valid_numbers = [
            "+1234567890",
            "+1 (123) 456-7890",
            "123-456-7890",
            "(123) 456-7890",
            "123.456.7890",
            "1234567890",
            "+44 20 7946 0958",  # UK format
            "+49 30 12345678",  # German format
            "+33 1 42 86 83 26"  # French format
        ]
        
        for number in valid_numbers:
            validator = PhoneNumberValidator(number)
            assert validator.is_valid() is True
            assert len(validator.get_errors()) == 0
    
    def test_invalid_phone_numbers(self):
        """Test validation of invalid phone numbers."""
        invalid_numbers = [
            "",  # Empty
            "abc",  # Letters only
            "123",  # Too short
            "1234567890123456",  # Too long
            "+1abc",  # Contains letters
            "1-800-INVALID",  # Contains letters
            "phone",  # Word
            "+",  # Just plus sign
        ]
        
        for number in invalid_numbers:
            validator = PhoneNumberValidator(number)
            assert validator.is_valid() is False
            assert len(validator.get_errors()) > 0
    
    def test_phone_number_formatting(self):
        """Test phone number formatting."""
        number = "+1234567890"
        validator = PhoneNumberValidator(number)
        
        # Should be able to format to different styles
        formatted = validator.format_number("international")
        assert formatted == "+1 234-567-890"
        
        formatted = validator.format_number("national")
        assert formatted == "(234) 567-890"


class TestURLValidator:
    """Test URL validation functionality."""
    
    def test_valid_urls(self):
        """Test validation of valid URLs."""
        valid_urls = [
            "https://www.example.com",
            "http://example.com",
            "https://subdomain.example.com/path",
            "https://example.com/path/to/resource",
            "https://example.com/path?query=value",
            "https://example.com/path#fragment",
            "ftp://example.com/file.txt",
            "http://localhost:3000",
            "https://192.168.1.1:8080"
        ]
        
        for url in valid_urls:
            validator = URLValidator(url)
            assert validator.is_valid() is True
            assert len(validator.get_errors()) == 0
    
    def test_invalid_urls(self):
        """Test validation of invalid URLs."""
        invalid_urls = [
            "",  # Empty
            "not-a-url",  # No protocol
            "http://",  # No domain
            "https://",  # No domain
            "://example.com",  # Invalid protocol
            "http://invalid domain",  # Space in domain
            "http://.example.com",  # Starts with dot
            "http://example.com.",  # Ends with dot
            "http://example..com"  # Double dots
        ]
        
        for url in invalid_urls:
            validator = URLValidator(url)
            assert validator.is_valid() is False
            assert len(validator.get_errors()) > 0
    
    def test_url_components_validation(self):
        """Test validation of URL components."""
        url = "https://user:pass@example.com:8080/path?query=value#fragment"
        validator = URLValidator(url)
        
        assert validator.is_valid() is True
        
        components = validator.get_components()
        assert components['scheme'] == 'https'
        assert components['netloc'] == 'user:pass@example.com:8080'
        assert components['path'] == '/path'
        assert components['query'] == 'query=value'
        assert components['fragment'] == 'fragment'


class TestDateValidator:
    """Test date validation functionality."""
    
    def test_valid_dates(self):
        """Test validation of valid dates."""
        valid_dates = [
            "2024-01-01",
            "01/01/2024",
            "2024-01-01T12:00:00Z",
            "2024-01-01 12:00:00",
            "Jan 1, 2024",
            "1 January 2024"
        ]
        
        for date_str in valid_dates:
            validator = DateValidator(date_str)
            assert validator.is_valid() is True
            assert len(validator.get_errors()) == 0
    
    def test_invalid_dates(self):
        """Test validation of invalid dates."""
        invalid_dates = [
            "",  # Empty
            "not-a-date",  # Invalid format
            "2024-13-01",  # Invalid month
            "2024-02-30",  # Invalid day
            "2024-01-32",  # Invalid day
            "2024-00-01",  # Invalid month
            "2024-01-00",  # Invalid day
            "2024-02-29",  # Not a leap year
        ]
        
        for date_str in invalid_dates:
            validator = DateValidator(date_str)
            assert validator.is_valid() is False
            assert len(validator.get_errors()) > 0
    
    def test_date_range_validation(self):
        """Test date range validation."""
        # Test future date
        future_date = "2050-01-01"
        validator = DateValidator(future_date, max_future_years=10)
        assert not validator.is_valid()
        assert any("future" in error.lower() for error in validator.get_errors())
        
        # Test past date
        past_date = "1900-01-01"
        validator = DateValidator(past_date, min_year=2000)
        assert not validator.is_valid()
        assert any("past" in error.lower() for error in validator.get_errors())


class TestBusinessValidator:
    """Test business logic validation functionality."""
    
    def test_product_price_validation(self):
        """Test product price validation."""
        # Valid prices
        valid_prices = [0.01, 10.99, 100.00, 9999.99]
        for price in valid_prices:
            assert BusinessValidator.validate_price(price) is True
        
        # Invalid prices
        invalid_prices = [-10.99, 0, 10000.00]
        for price in invalid_prices:
            assert BusinessValidator.validate_price(price) is False
    
    def test_stock_quantity_validation(self):
        """Test stock quantity validation."""
        # Valid quantities
        valid_quantities = [0, 1, 100, 9999]
        for quantity in valid_quantities:
            assert BusinessValidator.validate_stock_quantity(quantity) is True
        
        # Invalid quantities
        invalid_quantities = [-1, -100, 10000]
        for quantity in invalid_quantities:
            assert BusinessValidator.validate_stock_quantity(quantity) is False
    
    def test_category_name_validation(self):
        """Test category name validation."""
        # Valid names
        valid_names = ["Electronics", "Books", "Clothing", "Home & Garden"]
        for name in valid_names:
            assert BusinessValidator.validate_category_name(name) is True
        
        # Invalid names
        invalid_names = ["", "a", "a" * 101, "Category123!", "Category with special chars!"]
        for name in invalid_names:
            assert BusinessValidator.validate_category_name(name) is False
    
    def test_user_role_validation(self):
        """Test user role validation."""
        valid_roles = ["admin", "manager", "staff"]
        for role in valid_roles:
            assert BusinessValidator.validate_user_role(role) is True
        
        invalid_roles = ["superadmin", "guest", "root", "invalid_role"]
        for role in invalid_roles:
            assert BusinessValidator.validate_user_role(role) is False


class TestSecurityValidator:
    """Test security validation functionality."""
    
    def test_sql_injection_detection(self):
        """Test SQL injection detection."""
        injection_attempts = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES('hacker','pass'); --",
            "UNION SELECT * FROM users",
            "' OR 1=1 --"
        ]
        
        for injection in injection_attempts:
            assert SecurityValidator.contains_sql_injection(injection) is True
    
    def test_xss_detection(self):
        """Test XSS detection."""
        xss_attempts = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
            "';alert('xss');//"
        ]
        
        for xss in xss_attempts:
            assert SecurityValidator.contains_xss(xss) is True
    
    def test_file_upload_validation(self):
        """Test file upload validation."""
        # Valid files
        valid_files = [
            ("document.pdf", "application/pdf"),
            ("image.jpg", "image/jpeg"),
            ("text.txt", "text/plain")
        ]
        
        for filename, content_type in valid_files:
            assert SecurityValidator.validate_file_upload(filename, content_type) is True
        
        # Invalid files
        invalid_files = [
            ("script.exe", "application/octet-stream"),
            ("virus.bat", "application/x-msdownload"),
            ("shell.php", "application/x-php")
        ]
        
        for filename, content_type in invalid_files:
            assert SecurityValidator.validate_file_upload(filename, content_type) is False
    
    def test_input_sanitization(self):
        """Test input sanitization."""
        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>"
        ]
        
        for dangerous_input in dangerous_inputs:
            sanitized = SecurityValidator.sanitize_input(dangerous_input)
            assert "<script>" not in sanitized
            assert "javascript:" not in sanitized
            assert "onerror=" not in sanitized


class TestValidatorIntegration:
    """Test validator integration scenarios."""
    
    def test_user_registration_validation(self):
        """Test complete user registration validation."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPassword123!",
            "role": "staff"
        }
        
        # All validations should pass
        username_validator = UsernameValidator(user_data["username"])
        email_validator = EmailValidator(user_data["email"])
        password_validator = PasswordValidator(user_data["password"])
        role_validator = BusinessValidator.validate_user_role(user_data["role"])
        
        assert username_validator.is_valid() is True
        assert email_validator.is_valid() is True
        assert password_validator.is_valid() is True
        assert role_validator is True
    
    def test_product_creation_validation(self):
        """Test complete product creation validation."""
        product_data = {
            "name": "Test Product",
            "price": 29.99,
            "stock_quantity": 100,
            "category_id": 1
        }
        
        # All validations should pass
        price_valid = BusinessValidator.validate_price(product_data["price"])
        stock_valid = BusinessValidator.validate_stock_quantity(product_data["stock_quantity"])
        category_valid = product_data["category_id"] > 0
        
        assert price_valid is True
        assert stock_valid is True
        assert category_valid is True
    
    def test_validation_error_aggregation(self):
        """Test aggregation of validation errors."""
        validators = [
            UsernameValidator("ab"),  # Too short
            EmailValidator("invalid-email"),  # Invalid format
            PasswordValidator("weak")  # Too weak
        ]
        
        all_errors = []
        for validator in validators:
            if not validator.is_valid():
                all_errors.extend(validator.get_errors())
        
        assert len(all_errors) > 0
        assert any("username" in error.lower() for error in all_errors)
        assert any("email" in error.lower() for error in all_errors)
        assert any("password" in error.lower() for error in all_errors)
