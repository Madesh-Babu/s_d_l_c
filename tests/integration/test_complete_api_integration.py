"""
Integration Tests for Complete API Workflows

This module contains comprehensive integration tests that test complete
workflows across multiple endpoints and components of the API.
"""

import pytest
import json
from datetime import datetime
from src.models.models import db, User, Product, Category
from src.core.config import settings


class TestCompleteAPIIntegration:
    """Test complete API workflows spanning multiple endpoints."""
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self, app, client):
        """Set up clean test environment."""
        with app.app_context():
            # Clean up all test data
            Product.query.filter(Product.name.like('test_%')).delete()
            Category.query.filter(Category.name.like('test_%')).delete()
            User.query.filter(User.username.like('test_%')).delete()
            db.session.commit()
    
    def test_complete_inventory_management_workflow(self, client):
        """Test complete inventory management workflow from setup to operations."""
        
        # Step 1: Register admin user
        admin_data = {
            "username": "test_admin",
            "email": "admin@test.com",
            "password": "AdminPassword123!",
            "role": "admin"
        }
        
        response = client.post('/auth/register',
                             data=json.dumps(admin_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        admin_result = response.get_json()
        admin_id = admin_result['user_id']
        
        # Step 2: Admin login
        login_data = {
            "username": "test_admin",
            "password": "AdminPassword123!"
        }
        
        response = client.post('/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        admin_token = response.get_json()['access_token']
        admin_headers = {'Authorization': f'Bearer {admin_token}'}
        
        # Step 3: Create categories
        categories = [
            {"name": "Electronics", "description": "Electronic devices"},
            {"name": "Accessories", "description": "Electronic accessories"},
            {"name": "Computers", "description": "Computer equipment"}
        ]
        
        created_categories = []
        for category_data in categories:
            response = client.post('/categories/',
                                  data=json.dumps(category_data),
                                  headers=admin_headers,
                                  content_type='application/json')
            
            assert response.status_code == 201
            created_categories.append(response.get_json()['category'])
        
        # Step 4: Create products in categories
        products = [
            {
                "name": "Laptop Pro",
                "description": "High-performance laptop",
                "price": 1299.99,
                "stock_quantity": 50,
                "category_id": created_categories[2]['id']  # Computers
            },
            {
                "name": "Wireless Mouse",
                "description": "Ergonomic wireless mouse",
                "price": 29.99,
                "stock_quantity": 200,
                "category_id": created_categories[1]['id']  # Accessories
            },
            {
                "name": "USB-C Hub",
                "description": "Multi-port USB-C hub",
                "price": 49.99,
                "stock_quantity": 100,
                "category_id": created_categories[1]['id']  # Accessories
            }
        ]
        
        created_products = []
        for product_data in products:
            response = client.post('/products/',
                                  data=json.dumps(product_data),
                                  headers=admin_headers,
                                  content_type='application/json')
            
            assert response.status_code == 201
            created_products.append(response.get_json()['product'])
        
        # Step 5: Register staff user
        staff_data = {
            "username": "test_staff",
            "email": "staff@test.com",
            "password": "StaffPassword123!",
            "role": "staff"
        }
        
        response = client.post('/auth/register',
                             data=json.dumps(staff_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        # Step 6: Staff login
        staff_login = {
            "username": "test_staff",
            "password": "StaffPassword123!"
        }
        
        response = client.post('/auth/login',
                             data=json.dumps(staff_login),
                             content_type='application/json')
        
        assert response.status_code == 200
        staff_token = response.get_json()['access_token']
        staff_headers = {'Authorization': f'Bearer {staff_token}'}
        
        # Step 7: Staff can view products and categories
        response = client.get('/products/', headers=staff_headers)
        assert response.status_code == 200
        
        all_products = response.get_json()['products']
        assert len(all_products) >= 3
        
        response = client.get('/categories/', headers=staff_headers)
        assert response.status_code == 200
        
        all_categories = response.get_json()
        assert len(all_categories) >= 3
        
        # Step 8: Test product filtering
        response = client.get('/products/?min_price=30&max_price=100', headers=staff_headers)
        assert response.status_code == 200
        
        filtered_products = response.get_json()['products']
        for product in filtered_products:
            assert 30 <= product['price'] <= 100
        
        # Step 9: Test category-based product filtering
        computers_category = next(c for c in all_categories if c['name'] == 'Computers')
        response = client.get(f'/products/?category_id={computers_category["id"]}', headers=staff_headers)
        
        assert response.status_code == 200
        computer_products = response.get_json()['products']
        assert len(computer_products) >= 1
        
        # Step 10: Update product stock
        laptop_product = next(p for p in all_products if p['name'] == 'Laptop Pro')
        update_data = {
            "stock_quantity": 45  # Reduced from 50
        }
        
        response = client.put(f'/products/{laptop_product["id"]}',
                            data=json.dumps(update_data),
                            headers=admin_headers,
                            content_type='application/json')
        
        assert response.status_code == 200
        
        # Verify update
        response = client.get(f'/products/{laptop_product["id"]}', headers=staff_headers)
        updated_product = response.get_json()
        assert updated_product['stock_quantity'] == 45
    
    def test_multi_user_role_based_workflow(self, client):
        """Test workflow with multiple users having different roles."""
        
        # Create users with different roles
        roles_users = []
        for role in ['admin', 'manager', 'staff']:
            user_data = {
                "username": f"test_{role}_user",
                "email": f"{role}@test.com",
                "password": f"{role.title()}Password123!",
                "role": role
            }
            
            response = client.post('/auth/register',
                                 data=json.dumps(user_data),
                                 content_type='application/json')
            assert response.status_code == 201
            
            # Login and get token
            login_data = {
                "username": f"test_{role}_user",
                "password": f"{role.title()}Password123!"
            }
            
            response = client.post('/auth/login',
                                 data=json.dumps(login_data),
                                 content_type='application/json')
            assert response.status_code == 200
            
            roles_users.append({
                'role': role,
                'token': response.get_json()['access_token'],
                'headers': {'Authorization': f'Bearer {response.get_json()["access_token"]}'}
            })
        
        # Admin creates category
        admin_user = next(u for u in roles_users if u['role'] == 'admin')
        category_data = {
            "name": "Multi-user Test Category",
            "description": "Category for multi-user testing"
        }
        
        response = client.post('/categories/',
                              data=json.dumps(category_data),
                              headers=admin_user['headers'],
                              content_type='application/json')
        
        assert response.status_code == 201
        category_id = response.get_json()['category']['id']
        
        # All users should be able to view the category
        for user in roles_users:
            response = client.get('/categories/', headers=user['headers'])
            assert response.status_code == 200
            
            categories = response.get_json()
            test_category = next((c for c in categories if c['name'] == 'Multi-user Test Category'), None)
            assert test_category is not None
        
        # Manager creates product
        manager_user = next(u for u in roles_users if u['role'] == 'manager')
        product_data = {
            "name": "Multi-user Test Product",
            "description": "Product for multi-user testing",
            "price": 99.99,
            "stock_quantity": 100,
            "category_id": category_id
        }
        
        response = client.post('/products/',
                              data=json.dumps(product_data),
                              headers=manager_user['headers'],
                              content_type='application/json')
        
        assert response.status_code == 201
        product_id = response.get_json()['product']['id']
        
        # All users should be able to view the product
        for user in roles_users:
            response = client.get('/products/', headers=user['headers'])
            assert response.status_code == 200
            
            products = response.get_json()['products']
            test_product = next((p for p in products if p['name'] == 'Multi-user Test Product'), None)
            assert test_product is not None
        
        # Admin updates product
        update_data = {
            "price": 89.99,
            "stock_quantity": 80
        }
        
        response = client.put(f'/products/{product_id}',
                            data=json.dumps(update_data),
                            headers=admin_user['headers'],
                            content_type='application/json')
        
        assert response.status_code == 200
        
        # Verify all users see the updated product
        for user in roles_users:
            response = client.get(f'/products/{product_id}', headers=user['headers'])
            assert response.status_code == 200
            
            product = response.get_json()
            assert product['price'] == 89.99
            assert product['stock_quantity'] == 80
    
    def test_error_recovery_and_data_consistency(self, client):
        """Test error recovery and data consistency across operations."""
        
        # Create admin user
        admin_data = {
            "username": "test_recovery_admin",
            "email": "recovery@test.com",
            "password": "RecoveryPassword123!",
            "role": "admin"
        }
        
        response = client.post('/auth/register',
                             data=json.dumps(admin_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        # Login
        login_data = {
            "username": "test_recovery_admin",
            "password": "RecoveryPassword123!"
        }
        
        response = client.post('/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        admin_headers = {'Authorization': f'Bearer {response.get_json()["access_token"]}'}
        
        # Create valid category
        category_data = {
            "name": "Recovery Test Category",
            "description": "Category for recovery testing"
        }
        
        response = client.post('/categories/',
                              data=json.dumps(category_data),
                              headers=admin_headers,
                              content_type='application/json')
        
        assert response.status_code == 201
        category_id = response.get_json()['category']['id']
        
        # Try to create product with invalid data (should fail and rollback)
        invalid_product_data = {
            "name": "Invalid Product",
            "description": "Product with invalid data",
            "price": -10.99,  # Invalid negative price
            "stock_quantity": 100,
            "category_id": category_id
        }
        
        response = client.post('/products/',
                              data=json.dumps(invalid_product_data),
                              headers=admin_headers,
                              content_type='application/json')
        
        assert response.status_code == 400
        
        # Verify no invalid products were created
        response = client.get('/products/', headers=admin_headers)
        assert response.status_code == 200
        
        products = response.get_json()['products']
        invalid_products = [p for p in products if p['name'] == 'Invalid Product']
        assert len(invalid_products) == 0
        
        # Create valid product
        valid_product_data = {
            "name": "Valid Product",
            "description": "Valid product for recovery testing",
            "price": 29.99,
            "stock_quantity": 100,
            "category_id": category_id
        }
        
        response = client.post('/products/',
                              data=json.dumps(valid_product_data),
                              headers=admin_headers,
                              content_type='application/json')
        
        assert response.status_code == 201
        product_id = response.get_json()['product']['id']
        
        # Try to update with invalid data
        invalid_update = {
            "price": -5.99  # Invalid negative price
        }
        
        response = client.put(f'/products/{product_id}',
                            data=json.dumps(invalid_update),
                            headers=admin_headers,
                            content_type='application/json')
        
        assert response.status_code == 400
        
        # Verify product data remains unchanged
        response = client.get(f'/products/{product_id}', headers=admin_headers)
        assert response.status_code == 200
        
        product = response.get_json()
        assert product['price'] == 29.99  # Should remain unchanged
    
    def test_concurrent_operations_simulation(self, client):
        """Test simulation of concurrent operations."""
        
        # Create admin user
        admin_data = {
            "username": "test_concurrent_admin",
            "email": "concurrent@test.com",
            "password": "ConcurrentPassword123!",
            "role": "admin"
        }
        
        response = client.post('/auth/register',
                             data=json.dumps(admin_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        # Login
        login_data = {
            "username": "test_concurrent_admin",
            "password": "ConcurrentPassword123!"
        }
        
        response = client.post('/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        admin_headers = {'Authorization': f'Bearer {response.get_json()["access_token"]}'}
        
        # Create category
        category_data = {
            "name": "Concurrent Test Category",
            "description": "Category for concurrent testing"
        }
        
        response = client.post('/categories/',
                              data=json.dumps(category_data),
                              headers=admin_headers,
                              content_type='application/json')
        
        assert response.status_code == 201
        category_id = response.get_json()['category']['id']
        
        # Create multiple products rapidly (simulating concurrent creation)
        products = []
        for i in range(5):
            product_data = {
                "name": f"Concurrent Product {i}",
                "description": f"Product {i} for concurrent testing",
                "price": 10.0 + i * 5,
                "stock_quantity": 50 + i * 10,
                "category_id": category_id
            }
            
            response = client.post('/products/',
                                  data=json.dumps(product_data),
                                  headers=admin_headers,
                                  content_type='application/json')
            
            assert response.status_code == 201
            products.append(response.get_json()['product'])
        
        # Verify all products were created successfully
        response = client.get('/products/', headers=admin_headers)
        assert response.status_code == 200
        
        all_products = response.get_json()['products']
        concurrent_products = [p for p in all_products if p['name'].startswith('Concurrent Product')]
        assert len(concurrent_products) == 5
        
        # Simulate concurrent updates
        for i, product in enumerate(products):
            update_data = {
                "stock_quantity": 100 + i * 5  # Update stock
            }
            
            response = client.put(f'/products/{product["id"]}',
                                data=json.dumps(update_data),
                                headers=admin_headers,
                                content_type='application/json')
            
            assert response.status_code == 200
        
        # Verify all updates were applied
        response = client.get('/products/', headers=admin_headers)
        assert response.status_code == 200
        
        updated_products = response.get_json()['products']
        for i in range(5):
            product_name = f"Concurrent Product {i}"
            product = next(p for p in updated_products if p['name'] == product_name)
            assert product['stock_quantity'] == 100 + i * 5
    
    def test_development_vs_production_behavior(self, client):
        """Test different behavior between development and production modes."""
        
        # Test authentication bypass in development
        if settings.feature_toggles.BYPASS_AUTH and settings.is_development():
            # Should be able to access endpoints without authentication
            response = client.get('/auth/users')
            
            if response.status_code == 200:
                result = response.get_json()
                assert 'auth_bypassed' in result
                assert result['auth_bypassed'] is True
            
            response = client.get('/products/')
            if response.status_code == 200:
                result = response.get_json()
                assert isinstance(result['products'], list)
            
            response = client.get('/categories/')
            if response.status_code == 200:
                result = response.get_json()
                assert isinstance(result, list)
        else:
            # Should require authentication
            protected_endpoints = ['/auth/users', '/products/', '/categories/']
            
            for endpoint in protected_endpoints:
                response = client.get(endpoint)
                assert response.status_code == 401
        
        # Test development-specific endpoints
        response = client.post('/auth/dev-login')
        
        if settings.feature_toggles.BYPASS_AUTH and settings.is_development():
            assert response.status_code == 200
            result = response.get_json()
            assert 'access_token' in result
            assert 'bypass_enabled' in result
            assert result['bypass_enabled'] is True
        else:
            assert response.status_code == 404
    
    def test_api_health_and_monitoring(self, client):
        """Test API health check and monitoring endpoints."""
        
        # Test health endpoint
        response = client.get('/health')
        assert response.status_code in [200, 503]  # 503 if unhealthy
        
        if response.status_code == 200:
            health_data = response.get_json()
            assert 'status' in health_data
            assert 'timestamp' in health_data
            assert 'version' in health_data
            assert 'environment' in health_data
            
            # Should include system checks
            assert 'checks' in health_data
            
            # Should include feature status
            assert 'features' in health_data
            assert 'authentication_bypass' in health_data['features']
        
        # Test root endpoint
        response = client.get('/')
        assert response.status_code == 200
        
        root_data = response.get_json()
        assert 'message' in root_data
        assert 'version' in root_data
        assert 'endpoints' in root_data
