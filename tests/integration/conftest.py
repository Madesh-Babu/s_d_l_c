"""
Integration Test Configuration and Utilities

This module provides configuration, fixtures, and utilities for integration tests.
"""

import pytest
import json
from datetime import datetime
from src.api import create_app
from src.models.models import db, User, Product, Category
from src.core.config import settings


@pytest.fixture(scope='function')
def app():
    """Create application for testing."""
    # Configure for testing
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'ENVIRONMENT': 'testing'
    }
    
    app = create_app(test_config)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create CLI runner."""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def sample_user(app):
    """Create sample user for testing."""
    with app.app_context():
        user = User(
            username="sample_user",
            email="sample@test.com",
            role="staff"
        )
        user.set_password("SamplePassword123!")
        db.session.add(user)
        db.session.commit()
        
        return user


@pytest.fixture(scope='function')
def sample_category(app):
    """Create sample category for testing."""
    with app.app_context():
        category = Category(
            name="Sample Category",
            description="Sample category for testing"
        )
        db.session.add(category)
        db.session.commit()
        
        return category


@pytest.fixture(scope='function')
def sample_product(app, sample_category):
    """Create sample product for testing."""
    with app.app_context():
        product = Product(
            name="Sample Product",
            description="Sample product for testing",
            price=29.99,
            stock_quantity=100,
            category_id=sample_category.id
        )
        db.session.add(product)
        db.session.commit()
        
        return product


@pytest.fixture(scope='function')
def admin_user(app):
    """Create admin user for testing."""
    with app.app_context():
        admin = User(
            username="admin_user",
            email="admin@test.com",
            role="admin"
        )
        admin.set_password("AdminPassword123!")
        db.session.add(admin)
        db.session.commit()
        
        return admin


@pytest.fixture(scope='function')
def manager_user(app):
    """Create manager user for testing."""
    with app.app_context():
        manager = User(
            username="manager_user",
            email="manager@test.com",
            role="manager"
        )
        manager.set_password("ManagerPassword123!")
        db.session.add(manager)
        db.session.commit()
        
        return manager


@pytest.fixture(scope='function')
def staff_user(app):
    """Create staff user for testing."""
    with app.app_context():
        staff = User(
            username="staff_user",
            email="staff@test.com",
            role="staff"
        )
        staff.set_password("StaffPassword123!")
        db.session.add(staff)
        db.session.commit()
        
        return staff


@pytest.fixture(scope='function')
def auth_headers(client, sample_user):
    """Get authentication headers for sample user."""
    login_data = {
        "username": "sample_user",
        "password": "SamplePassword123!"
    }
    
    response = client.post('/auth/login',
                         data=json.dumps(login_data),
                         content_type='application/json')
    
    assert response.status_code == 200
    token = response.get_json()['access_token']
    
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture(scope='function')
def admin_headers(client, admin_user):
    """Get authentication headers for admin user."""
    login_data = {
        "username": "admin_user",
        "password": "AdminPassword123!"
    }
    
    response = client.post('/auth/login',
                         data=json.dumps(login_data),
                         content_type='application/json')
    
    assert response.status_code == 200
    token = response.get_json()['access_token']
    
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture(scope='function')
def manager_headers(client, manager_user):
    """Get authentication headers for manager user."""
    login_data = {
        "username": "manager_user",
        "password": "ManagerPassword123!"
    }
    
    response = client.post('/auth/login',
                         data=json.dumps(login_data),
                         content_type='application/json')
    
    assert response.status_code == 200
    token = response.get_json()['access_token']
    
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture(scope='function')
def staff_headers(client, staff_user):
    """Get authentication headers for staff user."""
    login_data = {
        "username": "staff_user",
        "password": "StaffPassword123!"
    }
    
    response = client.post('/auth/login',
                         data=json.dumps(login_data),
                         content_type='application/json')
    
    assert response.status_code == 200
    token = response.get_json()['access_token']
    
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture(scope='function')
def multiple_categories(app):
    """Create multiple categories for testing."""
    with app.app_context():
        categories = []
        category_data = [
            {"name": "Electronics", "description": "Electronic devices"},
            {"name": "Accessories", "description": "Electronic accessories"},
            {"name": "Computers", "description": "Computer equipment"},
            {"name": "Mobile", "description": "Mobile devices"}
        ]
        
        for data in category_data:
            category = Category(**data)
            db.session.add(category)
            categories.append(category)
        
        db.session.commit()
        return categories


@pytest.fixture(scope='function')
def multiple_products(app, multiple_categories):
    """Create multiple products for testing."""
    with app.app_context():
        products = []
        product_data = [
            {
                "name": "Laptop Pro",
                "description": "High-performance laptop",
                "price": 1299.99,
                "stock_quantity": 50,
                "category_id": multiple_categories[2].id  # Computers
            },
            {
                "name": "Wireless Mouse",
                "description": "Ergonomic wireless mouse",
                "price": 29.99,
                "stock_quantity": 200,
                "category_id": multiple_categories[1].id  # Accessories
            },
            {
                "name": "Smartphone X",
                "description": "Latest smartphone",
                "price": 899.99,
                "stock_quantity": 100,
                "category_id": multiple_categories[3].id  # Mobile
            },
            {
                "name": "USB-C Hub",
                "description": "Multi-port USB-C hub",
                "price": 49.99,
                "stock_quantity": 150,
                "category_id": multiple_categories[1].id  # Accessories
            },
            {
                "name": "Tablet Pro",
                "description": "Professional tablet",
                "price": 599.99,
                "stock_quantity": 75,
                "category_id": multiple_categories[3].id  # Mobile
            }
        ]
        
        for data in product_data:
            product = Product(**data)
            db.session.add(product)
            products.append(product)
        
        db.session.commit()
        return products


@pytest.fixture(scope='function')
def hierarchical_categories(app):
    """Create hierarchical category structure for testing."""
    with app.app_context():
        # Parent categories
        electronics = Category(
            name="Electronics",
            description="All electronic devices"
        )
        computers = Category(
            name="Computers",
            description="Computer equipment",
            parent_category_id=1  # Will be set after electronics is created
        )
        accessories = Category(
            name="Accessories",
            description="Electronic accessories",
            parent_category_id=1  # Will be set after electronics is created
        )
        
        db.session.add(electronics)
        db.session.commit()  # Commit to get ID
        
        computers.parent_category_id = electronics.id
        accessories.parent_category_id = electronics.id
        
        db.session.add(computers)
        db.session.add(accessories)
        db.session.commit()
        
        # Child categories
        laptops = Category(
            name="Laptops",
            description="Laptop computers",
            parent_category_id=computers.id
        )
        desktops = Category(
            name="Desktops",
            description="Desktop computers",
            parent_category_id=computers.id
        )
        
        db.session.add(laptops)
        db.session.add(desktops)
        db.session.commit()
        
        return {
            'parent': electronics,
            'children': [computers, accessories],
            'grandchildren': [laptops, desktops]
        }


class IntegrationTestHelpers:
    """Helper methods for integration tests."""
    
    @staticmethod
    def create_user_with_role(client, username, email, password, role):
        """Create a user with specific role and return auth headers."""
        user_data = {
            "username": username,
            "email": email,
            "password": password,
            "role": role
        }
        
        response = client.post('/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        login_data = {
            "username": username,
            "password": password
        }
        
        response = client.post('/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        token = response.get_json()['access_token']
        
        return {'Authorization': f'Bearer {token}'}
    
    @staticmethod
    def create_category_with_auth(client, headers, name, description, parent_id=None):
        """Create a category with authentication."""
        category_data = {
            "name": name,
            "description": description
        }
        
        if parent_id:
            category_data["parent_category_id"] = parent_id
        
        response = client.post('/categories/',
                              data=json.dumps(category_data),
                              headers=headers,
                              content_type='application/json')
        
        assert response.status_code == 201
        return response.get_json()['category']
    
    @staticmethod
    def create_product_with_auth(client, headers, name, description, price, stock, category_id):
        """Create a product with authentication."""
        product_data = {
            "name": name,
            "description": description,
            "price": price,
            "stock_quantity": stock,
            "category_id": category_id
        }
        
        response = client.post('/products/',
                              data=json.dumps(product_data),
                              headers=headers,
                              content_type='application/json')
        
        assert response.status_code == 201
        return response.get_json()['product']
    
    @staticmethod
    def assert_response_contains_keys(response, expected_keys):
        """Assert that response JSON contains expected keys."""
        data = response.get_json()
        for key in expected_keys:
            assert key in data, f"Missing key '{key}' in response"
    
    @staticmethod
    def assert_response_status_and_error(response, expected_status, expected_error_substring=None):
        """Assert response status and optionally check error message."""
        assert response.status_code == expected_status
        
        if expected_error_substring:
            data = response.get_json()
            assert 'error' in data
            assert expected_error_substring in data['error']
    
    @staticmethod
    def clean_test_data(app):
        """Clean up all test data."""
        with app.app_context():
            Product.query.filter(Product.name.like('test_%')).delete()
            Product.query.filter(Product.name.like('sample_%')).delete()
            Category.query.filter(Category.name.like('test_%')).delete()
            Category.query.filter(Category.name.like('sample_%')).delete()
            User.query.filter(User.username.like('test_%')).delete()
            User.query.filter(User.username.like('sample_%')).delete()
            User.query.filter(User.username.like('admin_%')).delete()
            User.query.filter(User.username.like('manager_%')).delete()
            User.query.filter(User.username.like('staff_%')).delete()
            db.session.commit()


# Custom markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "auth: marks tests as authentication tests"
    )
    config.addinivalue_line(
        "markers", "product: marks tests as product tests"
    )
    config.addinivalue_line(
        "markers", "category: marks tests as category tests"
    )
    config.addinivalue_line(
        "markers", "workflow: marks tests as workflow tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
