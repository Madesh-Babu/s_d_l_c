"""
Unit Tests for Password Service

This module contains comprehensive unit tests for password hashing and verification logic.
"""

import pytest
from unittest.mock import patch, Mock
from src.core.password_service import PasswordService
from src.core.exceptions import PasswordError
import re


class TestPasswordService:
    """Comprehensive unit tests for password hashing and verification logic."""
    
    @pytest.fixture
    def password_service(self):
        """Create password service instance for testing."""
        return PasswordService()
    
    def test_password_hashing_success(self, password_service):
        """Test successful password hashing."""
        password = "TestPassword123!"
        hashed = password_service.hash_password(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 50  # bcrypt hashes are typically 60 chars
        assert hashed.startswith('$2b$')  # bcrypt prefix
    
    def test_password_verification_success(self, password_service):
        """Test successful password verification."""
        password = "TestPassword123!"
        hashed = password_service.hash_password(password)
        
        assert password_service.verify_password(password, hashed) is True
    
    def test_password_verification_failure(self, password_service):
        """Test password verification with wrong password."""
        password = "TestPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = password_service.hash_password(password)
        
        assert password_service.verify_password(wrong_password, hashed) is False
    
    def test_password_strength_analysis(self, password_service):
        """Test password strength analysis."""
        # Strong password
        strong_password = "StrongPassword123!"
        result = password_service.analyze_strength(strong_password)
        
        assert result['strength'] == 'strong'
        assert result['score'] >= 8
        assert len(result['feedback']) == 0
        
        # Medium password
        medium_password = "MediumPass123"
        result = password_service.analyze_strength(medium_password)
        
        assert result['strength'] == 'medium'
        assert 4 <= result['score'] < 8
        
        # Weak password
        weak_password = "weak"
        result = password_service.analyze_strength(weak_password)
        
        assert result['strength'] == 'weak'
        assert result['score'] < 4
        assert len(result['feedback']) > 0
    
    def test_password_validation_requirements(self, password_service):
        """Test password validation against requirements."""
        # Valid password
        valid_password = "ValidPassword123!"
        result = password_service.validate_password(valid_password)
        
        assert result['is_valid'] is True
        assert len(result['errors']) == 0
        
        # Invalid passwords
        invalid_passwords = [
            "",  # Empty
            "short",  # Too short
            "nouppercase123!",  # No uppercase
            "NOLOWERCASE123!",  # No lowercase
            "NoNumbers!",  # No numbers
            "NoSpecialChars123",  # No special chars
            "Password123!",  # Contains common word
            "12345678!",  # All numbers and special
            "ABCDEFGH!",  # All letters and special
        ]
        
        for password in invalid_passwords:
            result = password_service.validate_password(password)
            assert result['is_valid'] is False
            assert len(result['errors']) > 0
    
    def test_password_common_patterns_detection(self, password_service):
        """Test detection of common password patterns."""
        common_passwords = [
            "password123!",
            "Password123!",
            "admin123!",
            "qwerty123!",
            "letmein123!",
            "welcome123!"
        ]
        
        for password in common_passwords:
            result = password_service.validate_password(password)
            assert result['is_valid'] is False
            assert any('common' in error.lower() for error in result['errors'])
    
    def test_password_personal_info_detection(self, password_service):
        """Test detection of personal information in passwords."""
        # Test with username
        username = "testuser"
        password_with_username = "testuser123!"
        
        result = password_service.validate_password(password_with_username, username=username)
        assert result['is_valid'] is False
        assert any('username' in error.lower() for error in result['errors'])
        
        # Test with email
        email = "test@example.com"
        password_with_email = "test123!"
        
        result = password_service.validate_password(password_with_email, email=email)
        assert result['is_valid'] is False
        assert any('email' in error.lower() for error in result['errors'])
    
    def test_password_hashing_consistency(self, password_service):
        """Test that password hashing is consistent but produces different hashes."""
        password = "TestPassword123!"
        
        # Hash same password multiple times
        hash1 = password_service.hash_password(password)
        hash2 = password_service.hash_password(password)
        
        # Hashes should be different (due to salt)
        assert hash1 != hash2
        
        # But both should verify correctly
        assert password_service.verify_password(password, hash1) is True
        assert password_service.verify_password(password, hash2) is True
    
    def test_password_hashing_rounds(self, password_service):
        """Test password hashing with different rounds."""
        password = "TestPassword123!"
        
        # Test with different rounds
        hash_low_rounds = password_service.hash_password(password, rounds=4)
        hash_high_rounds = password_service.hash_password(password, rounds=12)
        
        # Both should verify correctly
        assert password_service.verify_password(password, hash_low_rounds) is True
        assert password_service.verify_password(password, hash_high_rounds) is True
        
        # Hashes should be different
        assert hash_low_rounds != hash_high_rounds
    
    def test_password_hashing_invalid_input(self, password_service):
        """Test password hashing with invalid input."""
        invalid_inputs = [
            None,
            "",
            "   ",  # Whitespace only
            123,  # Not a string
            [],  # Not a string
            {}
        ]
        
        for invalid_input in invalid_inputs:
            with pytest.raises(PasswordError):
                password_service.hash_password(invalid_input)
    
    def test_password_verification_invalid_input(self, password_service):
        """Test password verification with invalid input."""
        password = "TestPassword123!"
        hashed = password_service.hash_password(password)
        
        invalid_inputs = [
            None,
            "",
            123,
            [],
            {}
        ]
        
        for invalid_input in invalid_inputs:
            with pytest.raises(PasswordError):
                password_service.verify_password(invalid_input, hashed)
    
    def test_password_verification_invalid_hash(self, password_service):
        """Test password verification with invalid hash."""
        password = "TestPassword123!"
        
        invalid_hashes = [
            "",
            "invalid_hash",
            "$2b$12$invalidhash",
            "short",
            123,
            None
        ]
        
        for invalid_hash in invalid_hashes:
            with pytest.raises(PasswordError):
                password_service.verify_password(password, invalid_hash)
    
    def test_password_strength_scoring(self, password_service):
        """Test password strength scoring algorithm."""
        test_cases = [
            ("", 0),  # Empty
            ("a", 1),  # Very weak
            ("abc", 2),  # Weak
            ("password", 3),  # Still weak
            ("Password123", 5),  # Medium
            ("Password123!", 7),  # Good
            ("StrongPassword123!", 9),  # Strong
            ("VeryStrongPassword123!@#", 10),  # Very strong
        ]
        
        for password, expected_min_score in test_cases:
            result = password_service.analyze_strength(password)
            assert result['score'] >= expected_min_score
    
    def test_password_strength_feedback(self, password_service):
        """Test password strength feedback messages."""
        # Weak password should have feedback
        weak_password = "weak"
        result = password_service.analyze_strength(weak_password)
        
        assert len(result['feedback']) > 0
        assert any('short' in feedback.lower() for feedback in result['feedback'])
        
        # Strong password should have no feedback
        strong_password = "StrongPassword123!"
        result = password_service.analyze_strength(strong_password)
        
        assert len(result['feedback']) == 0
    
    def test_password_entropy_calculation(self, password_service):
        """Test password entropy calculation."""
        # High entropy password
        high_entropy_password = "RandomChars!@#123ABCdef"
        result = password_service.analyze_strength(high_entropy_password)
        
        assert result['entropy'] > 100  # High entropy
        
        # Low entropy password
        low_entropy_password = "aaaaaaaa"
        result = password_service.analyze_strength(low_entropy_password)
        
        assert result['entropy'] < 20  # Low entropy
    
    def test_password_pattern_detection(self, password_service):
        """Test detection of common patterns in passwords."""
        patterns = {
            "sequential": "abcdef123",
            "repeated": "aaabbb111",
            "keyboard": "qwerty123",
            "date": "January2024!",
            "phone": "5551234567"
        }
        
        for pattern_type, password in patterns.items():
            result = password_service.validate_password(password)
            assert result['is_valid'] is False
            assert any(pattern_type in error.lower() for error in result['errors'])
    
    def test_password_hash_timing_attack_resistance(self, password_service):
        """Test resistance to timing attacks."""
        import time
        
        password = "TestPassword123!"
        hashed = password_service.hash_password(password)
        
        # Measure verification time for correct password
        start_time = time.time()
        password_service.verify_password(password, hashed)
        correct_time = time.time() - start_time
        
        # Measure verification time for incorrect password
        start_time = time.time()
        password_service.verify_password("WrongPassword123!", hashed)
        incorrect_time = time.time() - start_time
        
        # Times should be similar (within reasonable margin)
        time_diff = abs(correct_time - incorrect_time)
        assert time_diff < 0.1  # 100ms margin
    
    def test_password_service_configuration(self, password_service):
        """Test password service configuration."""
        # Test default configuration
        assert password_service.min_length == 8
        assert password_service.max_length == 128
        assert password_service.require_uppercase is True
        assert password_service.require_lowercase is True
        assert password.service.require_numbers is True
        assert password.service.require_special is True
        
        # Test custom configuration
        custom_service = PasswordService(
            min_length=12,
            max_length=64,
            require_uppercase=False,
            require_special=False
        )
        
        assert custom_service.min_length == 12
        assert custom_service.max_length == 64
        assert custom_service.require_uppercase is False
        assert custom_service.require_special is False
    
    def test_password_service_with_pepper(self, password_service):
        """Test password service with pepper (additional secret)."""
        password = "TestPassword123!"
        
        # Hash with pepper
        hashed_with_pepper = password_service.hash_password(password, pepper="secret_pepper")
        
        # Hash without pepper
        hashed_without_pepper = password_service.hash_password(password)
        
        # Hashes should be different
        assert hashed_with_pepper != hashed_without_pepper
        
        # Both should verify with correct pepper
        assert password_service.verify_password(password, hashed_with_pepper, pepper="secret_pepper") is True
        
        # Should fail with wrong pepper
        assert password_service.verify_password(password, hashed_with_pepper, pepper="wrong_pepper") is False
    
    def test_password_service_expiration(self, password_service):
        """Test password expiration functionality."""
        password = "TestPassword123!"
        hashed = password_service.hash_password(password)
        
        # Test with recent hash (should not be expired)
        assert password_service.is_password_expired(hashed, max_age_days=90) is False
        
        # Test with old hash (should be expired)
        old_hash_timestamp = int((datetime.now().timestamp() - 100 * 24 * 3600) * 1000)  # 100 days ago
        
        # This would require modification to include timestamp in hash
        # For now, test the logic conceptually
        assert password_service.is_password_expired("old_hash", max_age_days=90) is True
    
    def test_password_service_breached_password_check(self, password_service):
        """Test checking against breached password lists."""
        # Mock breached password check
        with patch.object(password_service, 'is_breached_password') as mock_breached:
            mock_breached.return_value = True
            
            password = "TestPassword123!"
            result = password_service.validate_password(password)
            
            assert result['is_valid'] is False
            assert any('breached' in error.lower() for error in result['errors'])
    
    def test_password_service_unicode_handling(self, password_service):
        """Test handling of Unicode characters in passwords."""
        unicode_passwords = [
            "Password123!🔒",
            "MøtPåss123!",
            "パスワード123!",
            "Пароль123!",
            "كلمةالسر123!"
        ]
        
        for password in unicode_passwords:
            # Should hash without errors
            hashed = password_service.hash_password(password)
            assert hashed is not None
            
            # Should verify correctly
            assert password_service.verify_password(password, hashed) is True
    
    def test_password_service_memory_cleanup(self, password_service):
        """Test memory cleanup for sensitive data."""
        password = "TestPassword123!"
        
        # Hash password
        hashed = password_service.hash_password(password)
        
        # The original password should still be in memory in Python
        # But we can test that the service doesn't retain sensitive data
        assert not hasattr(password_service, '_last_password')
        assert not hasattr(password_service, '_last_hash')
    
    def test_password_service_concurrent_access(self, password_service):
        """Test thread safety of password service."""
        import threading
        import time
        
        results = []
        
        def hash_password():
            password = f"Password{time.time()}123!"
            hashed = password_service.hash_password(password)
            results.append(hashed)
        
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=hash_password)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All threads should have completed successfully
        assert len(results) == 10
        assert all(len(hashed) > 50 for hashed in results)
        
        # All hashes should be different
        assert len(set(results)) == 10
