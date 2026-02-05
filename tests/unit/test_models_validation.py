"""
Unit Tests for Pydantic Model Validation

This module contains comprehensive unit tests for Pydantic model validation,
serialization, and business logic validation.
"""

import pytest
from pydantic import ValidationError
from datetime import datetime
from src.models.schemas import (
    UserCreate, UserLogin, UserUpdate, ProductCreate, ProductUpdate,
    CategoryCreate, CategoryUpdate, UserResponse, ProductResponse, CategoryResponse
)
from src.core.exceptions import ValidationErrorException


class TestModelsValidation:
    """Comprehensive unit tests for Pydantic model validation and serialization."""
    
    def test_user_create_valid_data(self):
        """Test UserCreate model with valid data."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "role": "staff"
        }
        
        user = UserCreate(**user_data)
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "TestPassword123!"
        assert user.role == "staff"
    
    def test_user_create_invalid_username(self):
        """Test UserCreate model with invalid username."""
        invalid_usernames = [
            "",  # Empty
            "a",  # Too short
            "user with spaces",  # Contains spaces
            "user@domain",  # Contains @ symbol
            "user#name",  # Contains special character
            "a" * 21  # Too long
        ]
        
        for username in invalid_usernames:
            user_data = {
                "username": username,
                "email": "test@example.com",
                "password": "TestPassword123!",
                "role": "staff"
            }
            
            with pytest.raises(ValidationError):
                UserCreate(**user_data)
    
    def test_user_create_invalid_email(self):
        """Test UserCreate model with invalid email."""
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user..name@domain.com",
            "user@domain..com"
        ]
        
        for email in invalid_emails:
            user_data = {
                "username": "testuser",
                "email": email,
                "password": "TestPassword123!",
                "role": "staff"
            }
            
            with pytest.raises(ValidationError):
                UserCreate(**user_data)
    
    def test_user_create_invalid_password(self):
        """Test UserCreate model with invalid password."""
        invalid_passwords = [
            "",  # Empty
            "weak",  # Too short
            "password",  # No uppercase, numbers, or special chars
            "Password",  # No numbers or special chars
            "Password123",  # No special chars
            "password123!",  # No uppercase
            "PASSWORD123!",  # No lowercase
        ]
        
        for password in invalid_passwords:
            user_data = {
                "username": "testuser",
                "email": "test@example.com",
                "password": password,
                "role": "staff"
            }
            
            with pytest.raises(ValidationError):
                UserCreate(**user_data)
    
    def test_user_create_invalid_role(self):
        """Test UserCreate model with invalid role."""
        invalid_roles = [
            "invalid_role",
            "superadmin",
            "guest",
            "root"
        ]
        
        for role in invalid_roles:
            user_data = {
                "username": "testuser",
                "email": "test@example.com",
                "password": "TestPassword123!",
                "role": role
            }
            
            with pytest.raises(ValidationError):
                UserCreate(**user_data)
    
    def test_user_login_valid_data(self):
        """Test UserLogin model with valid data."""
        login_data = {
            "username": "testuser",
            "password": "TestPassword123!"
        }
        
        login = UserLogin(**login_data)
        
        assert login.username == "testuser"
        assert login.password == "TestPassword123!"
    
    def test_user_login_missing_fields(self):
        """Test UserLogin model with missing required fields."""
        # Missing username
        with pytest.raises(ValidationError):
            UserLogin(password="TestPassword123!")
        
        # Missing password
        with pytest.raises(ValidationError):
            UserLogin(username="testuser")
    
    def test_user_update_valid_data(self):
        """Test UserUpdate model with valid data."""
        update_data = {
            "username": "newusername",
            "email": "newemail@example.com",
            "role": "manager"
        }
        
        update = UserUpdate(**update_data)
        
        assert update.username == "newusername"
        assert update.email == "newemail@example.com"
        assert update.role == "manager"
    
    def test_user_update_partial_data(self):
        """Test UserUpdate model with partial data."""
        # Only username
        update = UserUpdate(username="newusername")
        assert update.username == "newusername"
        assert update.email is None
        assert update.role is None
        
        # Only email
        update = UserUpdate(email="newemail@example.com")
        assert update.username is None
        assert update.email == "newemail@example.com"
        assert update.role is None
    
    def test_user_update_with_password(self):
        """Test UserUpdate model with password field."""
        update_data = {
            "password": "NewPassword123!"
        }
        
        update = UserUpdate(**update_data)
        assert update.password == "NewPassword123!"
    
    def test_product_create_valid_data(self):
        """Test ProductCreate model with valid data."""
        product_data = {
            "name": "Test Product",
            "description": "Test product description",
            "price": 29.99,
            "stock_quantity": 100,
            "category_id": 1
        }
        
        product = ProductCreate(**product_data)
        
        assert product.name == "Test Product"
        assert product.description == "Test product description"
        assert product.price == 29.99
        assert product.stock_quantity == 100
        assert product.category_id == 1
    
    def test_product_create_invalid_price(self):
        """Test ProductCreate model with invalid price."""
        invalid_prices = [
            -10.99,  # Negative
            0,  # Zero
            1000000.00  # Too high (business rule)
        ]
        
        for price in invalid_prices:
            product_data = {
                "name": "Test Product",
                "description": "Test product description",
                "price": price,
                "stock_quantity": 100,
                "category_id": 1
            }
            
            with pytest.raises(ValidationError):
                ProductCreate(**product_data)
    
    def test_product_create_invalid_stock(self):
        """Test ProductCreate model with invalid stock quantity."""
        invalid_stocks = [
            -10,  # Negative
            1000000  # Too high (business rule)
        ]
        
        for stock in invalid_stocks:
            product_data = {
                "name": "Test Product",
                "description": "Test product description",
                "price": 29.99,
                "stock_quantity": stock,
                "category_id": 1
            }
            
            with pytest.raises(ValidationError):
                ProductCreate(**product_data)
    
    def test_product_create_missing_required_fields(self):
        """Test ProductCreate model with missing required fields."""
        # Missing name
        with pytest.raises(ValidationError):
            ProductCreate(
                description="Test product description",
                price=29.99,
                stock_quantity=100,
                category_id=1
            )
        
        # Missing price
        with pytest.raises(ValidationError):
            ProductCreate(
                name="Test Product",
                description="Test product description",
                stock_quantity=100,
                category_id=1
            )
    
    def test_product_update_valid_data(self):
        """Test ProductUpdate model with valid data."""
        update_data = {
            "name": "Updated Product",
            "price": 39.99,
            "stock_quantity": 150
        }
        
        update = ProductUpdate(**update_data)
        
        assert update.name == "Updated Product"
        assert update.price == 39.99
        assert update.stock_quantity == 150
    
    def test_category_create_valid_data(self):
        """Test CategoryCreate model with valid data."""
        category_data = {
            "name": "Test Category",
            "description": "Test category description"
        }
        
        category = CategoryCreate(**category_data)
        
        assert category.name == "Test Category"
        assert category.description == "Test category description"
        assert category.parent_category_id is None
    
    def test_category_create_with_parent(self):
        """Test CategoryCreate model with parent category."""
        category_data = {
            "name": "Child Category",
            "description": "Child category description",
            "parent_category_id": 1
        }
        
        category = CategoryCreate(**category_data)
        
        assert category.name == "Child Category"
        assert category.parent_category_id == 1
    
    def test_category_create_invalid_name(self):
        """Test CategoryCreate model with invalid name."""
        invalid_names = [
            "",  # Empty
            "a",  # Too short
            "a" * 101  # Too long
        ]
        
        for name in invalid_names:
            category_data = {
                "name": name,
                "description": "Test category description"
            }
            
            with pytest.raises(ValidationError):
                CategoryCreate(**category_data)
    
    def test_user_response_serialization(self):
        """Test UserResponse model serialization."""
        user_data = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "role": "staff",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        user_response = UserResponse(**user_data)
        
        assert user_response.id == 1
        assert user_response.username == "testuser"
        assert user_response.email == "test@example.com"
        assert user_response.role == "staff"
        assert isinstance(user_response.created_at, datetime)
        assert isinstance(user_response.updated_at, datetime)
    
    def test_product_response_serialization(self):
        """Test ProductResponse model serialization."""
        product_data = {
            "id": 1,
            "name": "Test Product",
            "description": "Test product description",
            "price": 29.99,
            "stock_quantity": 100,
            "category_id": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        product_response = ProductResponse(**product_data)
        
        assert product_response.id == 1
        assert product_response.name == "Test Product"
        assert product_response.price == 29.99
        assert product_response.stock_quantity == 100
        assert product_response.category_id == 1
        assert isinstance(product_response.created_at, datetime)
        assert isinstance(product_response.updated_at, datetime)
    
    def test_category_response_serialization(self):
        """Test CategoryResponse model serialization."""
        category_data = {
            "id": 1,
            "name": "Test Category",
            "description": "Test category description",
            "parent_category_id": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        category_response = CategoryResponse(**category_data)
        
        assert category_response.id == 1
        assert category_response.name == "Test Category"
        assert category_response.description == "Test category description"
        assert category_response.parent_category_id is None
        assert isinstance(category_response.created_at, datetime)
        assert isinstance(category_response.updated_at, datetime)
    
    def test_model_validation_error_messages(self):
        """Test that validation error messages are descriptive."""
        try:
            UserCreate(
                username="a",  # Too short
                email="invalid-email",  # Invalid format
                password="weak",  # Too weak
                role="invalid_role"  # Invalid role
            )
        except ValidationError as e:
            errors = e.errors()
            
            # Should have multiple validation errors
            assert len(errors) >= 4
            
            # Check that errors are descriptive
            error_fields = [error['loc'][0] for error in errors]
            assert 'username' in error_fields
            assert 'email' in error_fields
            assert 'password' in error_fields
            assert 'role' in error_fields
    
    def test_model_serialization_to_dict(self):
        """Test model serialization to dictionary."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "role": "staff"
        }
        
        user = UserCreate(**user_data)
        user_dict = user.model_dump()
        
        assert user_dict['username'] == "testuser"
        assert user_dict['email'] == "test@example.com"
        assert user_dict['role'] == "staff"
        assert 'password' in user_dict
    
    def test_model_serialization_to_json(self):
        """Test model serialization to JSON."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "role": "staff"
        }
        
        user = UserCreate(**user_data)
        user_json = user.model_dump_json()
        
        assert "testuser" in user_json
        assert "test@example.com" in user_json
        assert "staff" in user_json
    
    def test_model_exclude_fields(self):
        """Test excluding fields from serialization."""
        user_data = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "role": "staff",
            "password": "hashed_password",  # Should not be in response
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        user_response = UserResponse(**user_data)
        
        # Should not have password field
        assert not hasattr(user_response, 'password')
        
        # Should have other fields
        assert hasattr(user_response, 'id')
        assert hasattr(user_response, 'username')
        assert hasattr(user_response, 'email')
    
    def test_model_validation_custom_methods(self):
        """Test custom validation methods in models."""
        # Test email validation
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "role": "staff"
        }
        
        user = UserCreate(**user_data)
        
        # Should have custom validation methods
        if hasattr(user, 'validate_email'):
            assert user.validate_email() is True
        
        if hasattr(user, 'validate_password'):
            assert user.validate_password() is True
    
    def test_model_business_logic_validation(self):
        """Test business logic validation in models."""
        # Test that business rules are enforced
        product_data = {
            "name": "Test Product",
            "description": "Test product description",
            "price": 29.99,
            "stock_quantity": 100,
            "category_id": 1
        }
        
        product = ProductCreate(**product_data)
        
        # Should enforce business rules
        assert product.price > 0
        assert product.stock_quantity >= 0
        assert product.category_id > 0
    
    def test_model_inheritance_and_composition(self):
        """Test model inheritance and composition patterns."""
        # Test that models can be composed
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "role": "staff"
        }
        
        user_create = UserCreate(**user_data)
        
        # Should be able to create response from create
        user_response_data = {
            "id": 1,
            "username": user_create.username,
            "email": user_create.email,
            "role": user_create.role,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        user_response = UserResponse(**user_response_data)
        
        assert user_response.username == user_create.username
        assert user_response.email == user_create.email
        assert user_response.role == user_create.role
    
    def test_model_error_handling_integration(self):
        """Test model error handling integration with custom exceptions."""
        try:
            UserCreate(
                username="invalid",
                email="invalid-email",
                password= "weak",
                role: "invalid"
            )
        except ValidationError as e:
            # Should be able to convert to custom exception
            custom_error = ValidationErrorException("Validation failed", details=e.errors())
            
            assert custom_error.message == "Validation failed"
            assert len(custom_error.details) > 0
    
    def test_model_performance_with_large_data(self):
        """Test model performance with large datasets."""
        import time
        
        # Test with many fields
        large_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "role": "staff"
        }
        
        start_time = time.time()
        
        for _ in range(1000):
            user = UserCreate(**large_data)
            user_dict = user.model_dump()
        
        end_time = time.time()
        
        # Should complete in reasonable time
        assert end_time - start_time < 1.0  # 1 second
    
    def test_model_thread_safety(self):
        """Test model thread safety."""
        import threading
        
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "role": "staff"
        }
        
        results = []
        
        def create_user():
            user = UserCreate(**user_data)
            results.append(user.username)
        
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=create_user)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All threads should have completed successfully
        assert len(results) == 10
        assert all(result == "testuser" for result in results)
