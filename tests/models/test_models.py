"""
Model Tests

This module contains comprehensive tests for database models
including User, Product, and Category models.
"""

import pytest
from src.models.models import User, Product, Category
from src.models.schemas import (
    UserCreate,
    UserUpdate,
    ProductCreate,
    ProductUpdate,
    CategoryCreate,
    CategoryUpdate,
)
from datetime import datetime


class TestUserModel:
    """Test User model."""

    def test_user_creation(self, app):
        """Test user model creation."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com", role="staff")
            user.set_password("TestPass123!")

            assert user.username == "testuser"
            assert user.email == "test@example.com"
            assert user.role == "staff"
            assert user.id is None  # Not saved yet

    def test_user_password_hashing(self, app):
        """Test password hashing functionality."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("TestPass123!")

            # Password should be hashed, not stored as plain text
            assert user.password_hash != "TestPass123!"
            assert len(user.password_hash) > 50  # Hash should be longer

    def test_user_password_verification(self, app):
        """Test password verification."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("TestPass123!")

            # Correct password should verify
            assert user.check_password("TestPass123!") is True

            # Wrong password should not verify
            assert user.check_password("WrongPass123!") is False

    def test_user_to_dict(self, app):
        """Test user to_dict method."""
        with app.app_context():
            user = User(
                id=1,
                username="testuser",
                email="test@example.com",
                role="staff",
                created_at=datetime.utcnow(),
            )

            user_dict = user.to_dict()

            assert user_dict["id"] == 1
            assert user_dict["username"] == "testuser"
            assert user_dict["email"] == "test@example.com"
            assert user_dict["role"] == "staff"
            assert "password_hash" not in user_dict  # Password should not be included
            assert "created_at" in user_dict

    def test_user_repr(self, app):
        """Test user string representation."""
        with app.app_context():
            user = User(id=1, username="testuser", email="test@example.com")

            repr_str = repr(user)
            assert "testuser" in repr_str
            assert "test@example.com" in repr_str

    def test_user_role_validation(self, app):
        """Test user role validation."""
        with app.app_context():
            # Valid roles
            valid_roles = ["admin", "manager", "staff"]
            for role in valid_roles:
                user = User(username="test", email="test@example.com", role=role)
                assert user.role == role

    def test_user_email_uniqueness(self, app, db):
        """Test email uniqueness constraint."""
        with app.app_context():
            # Create first user
            user1 = User(username="user1", email="test@example.com")
            user1.set_password("TestPass123!")
            db.session.add(user1)
            db.session.commit()

            # Try to create second user with same email
            user2 = User(username="user2", email="test@example.com")
            user2.set_password("TestPass123!")
            db.session.add(user2)

            with pytest.raises(Exception):  # Should raise integrity error
                db.session.commit()


class TestProductModel:
    """Test Product model."""

    def test_product_creation(self, app, create_test_category):
        """Test product model creation."""
        with app.app_context():
            product = Product(
                name="Test Product",
                description="Test description",
                price=99.99,
                stock_quantity=100,
                category_id=create_test_category.id,
            )

            assert product.name == "Test Product"
            assert product.description == "Test description"
            assert product.price == 99.99
            assert product.stock_quantity == 100
            assert product.category_id == create_test_category.id

    def test_product_to_dict(self, app, create_test_category):
        """Test product to_dict method."""
        with app.app_context():
            product = Product(
                id=1,
                name="Test Product",
                description="Test description",
                price=99.99,
                stock_quantity=100,
                category_id=create_test_category.id,
                created_at=datetime.utcnow(),
            )

            product_dict = product.to_dict()

            assert product_dict["id"] == 1
            assert product_dict["name"] == "Test Product"
            assert product_dict["price"] == 99.99
            assert product_dict["stock_quantity"] == 100
            assert product_dict["category_id"] == create_test_category.id
            assert "created_at" in product_dict

    def test_product_repr(self, app, create_test_category):
        """Test product string representation."""
        with app.app_context():
            product = Product(
                id=1,
                name="Test Product",
                price=99.99,
                category_id=create_test_category.id,
            )

            repr_str = repr(product)
            assert "Test Product" in repr_str
            assert "99.99" in repr_str

    def test_product_category_relationship(self, app, create_test_category):
        """Test product-category relationship."""
        with app.app_context():
            product = Product(
                name="Test Product", price=99.99, category_id=create_test_category.id
            )

            # Should be able to access category
            assert product.category_id == create_test_category.id

    def test_product_price_validation(self, app, create_test_category):
        """Test product price validation."""
        with app.app_context():
            # Valid prices
            valid_prices = [0, 0.01, 99.99, 1000.00]
            for price in valid_prices:
                product = Product(
                    name="Test", price=price, category_id=create_test_category.id
                )
                assert product.price == price

    def test_product_stock_validation(self, app, create_test_category):
        """Test product stock quantity validation."""
        with app.app_context():
            # Valid stock quantities
            valid_stocks = [0, 1, 100, 1000]
            for stock in valid_stocks:
                product = Product(
                    name="Test",
                    price=99.99,
                    stock_quantity=stock,
                    category_id=create_test_category.id,
                )
                assert product.stock_quantity == stock

    def test_product_category_foreign_key(self, app, db):
        """Test product category foreign key constraint."""
        with app.app_context():
            # Try to create product with non-existent category
            product = Product(
                name="Test Product",
                price=99.99,
                category_id=999,  # Non-existent category
            )
            db.session.add(product)

            with pytest.raises(Exception):  # Should raise foreign key error
                db.session.commit()


class TestCategoryModel:
    """Test Category model."""

    def test_category_creation(self, app):
        """Test category model creation."""
        with app.app_context():
            category = Category(name="Test Category", description="Test description")

            assert category.name == "Test Category"
            assert category.description == "Test description"

    def test_category_to_dict(self, app):
        """Test category to_dict method."""
        with app.app_context():
            category = Category(
                id=1,
                name="Test Category",
                description="Test description",
                created_at=datetime.utcnow(),
            )

            category_dict = category.to_dict()

            assert category_dict["id"] == 1
            assert category_dict["name"] == "Test Category"
            assert category_dict["description"] == "Test description"
            assert "created_at" in category_dict

    def test_category_repr(self, app):
        """Test category string representation."""
        with app.app_context():
            category = Category(id=1, name="Test Category")

            repr_str = repr(category)
            assert "Test Category" in repr_str

    def test_category_product_relationship(
        self, app, create_test_category, create_test_product
    ):
        """Test category-product relationship."""
        with app.app_context():
            category = create_test_category
            product = create_test_product

            # Product should be associated with category
            assert product.category_id == category.id

    def test_category_name_uniqueness(self, app, db):
        """Test category name uniqueness constraint."""
        with app.app_context():
            # Create first category
            category1 = Category(name="Test Category", description="First")
            db.session.add(category1)
            db.session.commit()

            # Try to create second category with same name
            category2 = Category(name="Test Category", description="Second")
            db.session.add(category2)

            with pytest.raises(Exception):  # Should raise integrity error
                db.session.commit()


class TestModelSchemas:
    """Test Pydantic schemas for model validation."""

    def test_user_create_schema(self):
        """Test UserCreate schema validation."""
        # Valid data
        valid_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!",
            "role": "staff",
        }

        user = UserCreate(**valid_data)
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == "staff"

    def test_user_create_schema_invalid_email(self):
        """Test UserCreate schema with invalid email."""
        invalid_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "TestPass123!",
            "role": "staff",
        }

        with pytest.raises(Exception):  # Should raise validation error
            UserCreate(**invalid_data)

    def test_user_create_schema_weak_password(self):
        """Test UserCreate schema with weak password."""
        invalid_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123",
            "role": "staff",
        }

        with pytest.raises(Exception):  # Should raise validation error
            UserCreate(**invalid_data)

    def test_product_create_schema(self):
        """Test ProductCreate schema validation."""
        valid_data = {
            "name": "Test Product",
            "description": "Test description",
            "price": 99.99,
            "stock_quantity": 100,
            "category_id": 1,
        }

        product = ProductCreate(**valid_data)
        assert product.name == "Test Product"
        assert product.price == 99.99
        assert product.category_id == 1

    def test_product_create_schema_invalid_price(self):
        """Test ProductCreate schema with invalid price."""
        invalid_data = {
            "name": "Test Product",
            "description": "Test description",
            "price": -10,  # Negative price
            "stock_quantity": 100,
            "category_id": 1,
        }

        with pytest.raises(Exception):  # Should raise validation error
            ProductCreate(**invalid_data)

    def test_category_create_schema(self):
        """Test CategoryCreate schema validation."""
        valid_data = {"name": "Test Category", "description": "Test description"}

        category = CategoryCreate(**valid_data)
        assert category.name == "Test Category"
        assert category.description == "Test description"

    def test_category_create_schema_empty_name(self):
        """Test CategoryCreate schema with empty name."""
        invalid_data = {"name": "", "description": "Test description"}  # Empty name

        with pytest.raises(Exception):  # Should raise validation error
            CategoryCreate(**invalid_data)


class TestModelIntegration:
    """Test model integration and relationships."""

    def test_category_product_cascade_delete(
        self, app, db, create_test_category, create_test_product
    ):
        """Test that deleting category with products fails (protect)."""
        with app.app_context():
            category = create_test_category
            product = create_test_product

            # Try to delete category (should fail due to foreign key constraint)
            db.session.delete(category)

            with pytest.raises(Exception):  # Should raise integrity error
                db.session.commit()

    def test_model_timestamps(self, app, db, sample_user_data):
        """Test that models have proper timestamps."""
        with app.app_context():
            user = User(
                username=sample_user_data["username"],
                email=sample_user_data["email"],
                role=sample_user_data["role"],
            )
            user.set_password(sample_user_data["password"])
            db.session.add(user)
            db.session.commit()

            # Should have created_at timestamp
            assert user.created_at is not None
            assert isinstance(user.created_at, datetime)

    def test_model_string_conversions(
        self, app, create_test_user, create_test_product, create_test_category
    ):
        """Test model string conversions and representations."""
        with app.app_context():
            # User string conversion
            user_str = str(create_test_user)
            assert create_test_user.username in user_str

            # Product string conversion
            product_str = str(create_test_product)
            assert create_test_product.name in product_str

            # Category string conversion
            category_str = str(create_test_category)
            assert create_test_category.name in category_str
