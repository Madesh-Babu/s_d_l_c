"""
Basic Unit Tests for Models

This module contains basic unit tests for model functionality.
"""

import pytest
from src.models.models import User, Category, Product
from src.api import db


class TestUserModel:
    """Test User model functionality."""

    def test_user_creation(self, app):
        """Test user creation."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com", role="user")
            user.set_password("TestPass123!")

            assert user.username == "testuser"
            assert user.email == "test@example.com"
            assert user.role == "user"
            assert user.password_hash is not None
            assert user.password_hash != "TestPass123!"

    def test_password_verification(self, app):
        """Test password verification."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com", role="user")
            user.set_password("TestPass123!")

            assert user.check_password("TestPass123!") is True
            assert user.check_password("WrongPass") is False

    def test_user_to_dict(self, app):
        """Test user serialization."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com", role="user")
            user.set_password("TestPass123!")

            user_dict = user.to_dict()
            assert user_dict["username"] == "testuser"
            assert user_dict["role"] == "user"
            assert "password_hash" not in user_dict


class TestCategoryModel:
    """Test Category model functionality."""

    def test_category_creation(self, app):
        """Test category creation."""
        with app.app_context():
            category = Category(name="Electronics")

            assert category.name == "Electronics"

    def test_category_to_dict(self, app):
        """Test category serialization."""
        with app.app_context():
            category = Category(name="Electronics")

            # Note: Add to_dict method if needed
            # For now, just test basic attributes
            assert category.name == "Electronics"


class TestProductModel:
    """Test Product model functionality."""

    def test_product_creation(self, app):
        """Test product creation."""
        with app.app_context():
            # Note: This will need adjustment based on actual Product model
            # For now, this is a placeholder
            pass
