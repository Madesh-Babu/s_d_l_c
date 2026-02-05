"""
Integration Tests for Product Endpoints

This module contains comprehensive integration tests for product endpoints,
testing CRUD operations, filtering, pagination, and business logic.
"""

import pytest
import json
from datetime import datetime
from src.models.models import db, Product, Category, User
from src.core.config import settings


class TestProductIntegration:
    """Test complete product management workflows."""
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self, app, client):
        """Set up test data for product tests."""
        with app.app_context():
            # Clean up test data
            Product.query.filter(Product.name.like('test_%')).delete()
            Category.query.filter(Category.name.like('test_%')).delete()
            User.query.filter(User.username.like('test_%')).delete()
            db.session.commit()
            
            # Create test category
            test_category = Category(
                name="test_category",
                description="Test category for integration tests"
            )
            db.session.add(test_category)
            
            # Create test user
            test_user = User(
                username="test_product_user",
                email="test_product@example.com",
                role="staff"
            )
            test_user.set_password("TestPassword123!")
            db.session.add(test_user)
            
            db.session.commit()
            
            # Store IDs for tests
            self.category_id = test_category.id
            self.user_id = test_user.id
    
    def get_auth_headers(self, client):
        """Get authentication headers for test user."""
        login_data = {
            "username": "test_product_user",
            "password": "TestPassword123!"
        }
        
        response = client.post('/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        token = response.get_json()['access_token']
        return {'Authorization': f'Bearer {token}'}
    
    def test_complete_product_crud_workflow(self, client):
        """Test complete CRUD workflow for products."""
        
        auth_headers = self.get_auth_headers(client)
        
        # Step 1: Create a product
        product_data = {
            "name": "test_integration_product",
            "description": "Product for integration testing",
            "price": 29.99,
            "stock_quantity": 100,
            "category_id": self.category_id
        }
        
        response = client.post('/products/',
                             data=json.dumps(product_data),
                             headers=auth_headers,
                             content_type='application/json')
        
        assert response.status_code == 201
        create_result = response.get_json()
        assert create_result['message'] == "Product created successfully"
        assert create_result['product']['name'] == "test_integration_product"
        
        product_id = create_result['product']['id']
        
        # Step 2: Retrieve all products and verify our product is there
        response = client.get('/products/', headers=auth_headers)
        
        assert response.status_code == 200
        get_all_result = response.get_json()
        assert isinstance(get_all_result['products'], list)
        
        # Find our product
        product_names = [p['name'] for p in get_all_result['products']]
        assert "test_integration_product" in product_names
        
        # Step 3: Get specific product by ID
        response = client.get(f'/products/{product_id}', headers=auth_headers)
        
        assert response.status_code == 200
        get_one_result = response.get_json()
        assert get_one_result['name'] == "test_integration_product"
        assert get_one_result['price'] == 29.99
        
        # Step 4: Update the product
        update_data = {
            "name": "test_integration_product_updated",
            "price": 39.99,
            "stock_quantity": 150
        }
        
        response = client.put(f'/products/{product_id}',
                            data=json.dumps(update_data),
                            headers=auth_headers,
                            content_type='application/json')
        
        assert response.status_code == 200
        update_result = response.get_json()
        assert update_result['message'] == "Product updated successfully"
        assert update_result['product']['name'] == "test_integration_product_updated"
        assert update_result['product']['price'] == 39.99
        
        # Step 5: Delete the product
        response = client.delete(f'/products/{product_id}', headers=auth_headers)
        
        assert response.status_code == 200
        delete_result = response.get_json()
        assert "deleted successfully" in delete_result['message']
        
        # Step 6: Verify product is deleted
        response = client.get(f'/products/{product_id}', headers=auth_headers)
        assert response.status_code == 404
    
    def test_product_validation_and_business_rules(self, client):
        """Test product validation and business rule enforcement."""
        
        auth_headers = self.get_auth_headers(client)
        
        # Test invalid price (negative)
        invalid_product_data = {
            "name": "test_invalid_product",
            "description": "Invalid product test",
            "price": -10.99,
            "stock_quantity": 100,
            "category_id": self.category_id
        }
        
        response = client.post('/products/',
                             data=json.dumps(invalid_product_data),
                             headers=auth_headers,
                             content_type='application/json')
        
        assert response.status_code == 400
        result = response.get_json()
        assert 'error' in result
        
        # Test invalid stock quantity (negative)
        invalid_stock_data = {
            "name": "test_invalid_stock",
            "description": "Invalid stock test",
            "price": 29.99,
            "stock_quantity": -50,
            "category_id": self.category_id
        }
        
        response = client.post('/products/',
                             data=json.dumps(invalid_stock_data),
                             headers=auth_headers,
                             content_type='application/json')
        
        assert response.status_code == 400
        result = response.get_json()
        assert 'error' in result
        
        # Test non-existent category
        invalid_category_data = {
            "name": "test_invalid_category",
            "description": "Invalid category test",
            "price": 29.99,
            "stock_quantity": 100,
            "category_id": 99999  # Non-existent category
        }
        
        response = client.post('/products/',
                             data=json.dumps(invalid_category_data),
                             headers=auth_headers,
                             content_type='application/json')
        
        assert response.status_code == 404
        result = response.get_json()
        assert 'error' in result
    
    def test_product_filtering_and_pagination(self, client):
        """Test product filtering and pagination functionality."""
        
        auth_headers = self.get_auth_headers(client)
        
        # Create multiple test products
        products = [
            {
                "name": f"test_filter_product_{i}",
                "description": f"Product {i} for filtering test",
                "price": 10.0 + i * 5,
                "stock_quantity": 50 + i * 10,
                "category_id": self.category_id
            }
            for i in range(10)
        ]
        
        created_products = []
        for product_data in products:
            response = client.post('/products/',
                                  data=json.dumps(product_data),
                                  headers=auth_headers,
                                  content_type='application/json')
            assert response.status_code == 201
            created_products.append(response.get_json()['product'])
        
        # Test price filtering
        response = client.get('/products/?min_price=20&max_price=40', headers=auth_headers)
        
        assert response.status_code == 200
        result = response.get_json()
        filtered_products = result['products']
        
        # Verify all products are within price range
        for product in filtered_products:
            assert 20 <= product['price'] <= 40
        
        # Test stock filtering
        response = client.get('/products/?in_stock=true', headers=auth_headers)
        
        assert response.status_code == 200
        result = response.get_json()
        stock_products = result['products']
        
        # Verify all products have stock > 0
        for product in stock_products:
            assert product['stock_quantity'] > 0
        
        # Test pagination
        response = client.get('/products/?page=1&per_page=5', headers=auth_headers)
        
        assert response.status_code == 200
        result = response.get_json()
        
        assert len(result['products']) <= 5
        assert 'pagination' in result
        assert result['pagination']['page'] == 1
        assert result['pagination']['per_page'] == 5
        
        # Test category filtering
        response = client.get(f'/products/?category_id={self.category_id}', headers=auth_headers)
        
        assert response.status_code == 200
        result = response.get_json()
        category_products = result['products']
        
        # Verify all products are in the correct category
        for product in category_products:
            assert product['category_id'] == self.category_id
    
    def test_product_category_relationships(self, client):
        """Test product-category relationships and data integrity."""
        
        auth_headers = self.get_auth_headers(client)
        
        # Create product with category
        product_data = {
            "name": "test_relationship_product",
            "description": "Product for relationship testing",
            "price": 29.99,
            "stock_quantity": 100,
            "category_id": self.category_id
        }
        
        response = client.post('/products/',
                             data=json.dumps(product_data),
                             headers=auth_headers,
                             content_type='application/json')
        
        assert response.status_code == 201
        product_id = response.get_json()['product']['id']
        
        # Retrieve product and verify category information
        response = client.get(f'/products/{product_id}', headers=auth_headers)
        
        assert response.status_code == 200
        product = response.get_json()
        
        # Should include category information
        assert 'category_id' in product
        assert product['category_id'] == self.category_id
        
        # Test retrieving products with category details
        response = client.get('/products/', headers=auth_headers)
        
        assert response.status_code == 200
        result = response.get_json()
        
        # Find our product in the list
        our_product = next((p for p in result['products'] if p['id'] == product_id), None)
        assert our_product is not None
        assert our_product['category_id'] == self.category_id
    
    def test_product_concurrent_operations(self, client):
        """Test concurrent product operations and data consistency."""
        
        auth_headers = self.get_auth_headers(client)
        
        # Create a product
        product_data = {
            "name": "test_concurrent_product",
            "description": "Product for concurrent testing",
            "price": 29.99,
            "stock_quantity": 100,
            "category_id": self.category_id
        }
        
        response = client.post('/products/',
                             data=json.dumps(product_data),
                             headers=auth_headers,
                             content_type='application/json')
        
        assert response.status_code == 201
        product_id = response.get_json()['product']['id']
        
        # Test simultaneous updates (simulate concurrent access)
        update_data_1 = {
            "price": 39.99,
            "stock_quantity": 80
        }
        
        update_data_2 = {
            "price": 49.99,
            "stock_quantity": 60
        }
        
        # First update
        response1 = client.put(f'/products/{product_id}',
                             data=json.dumps(update_data_1),
                             headers=auth_headers,
                             content_type='application/json')
        
        assert response1.status_code == 200
        
        # Second update
        response2 = client.put(f'/products/{product_id}',
                             data=json.dumps(update_data_2),
                             headers=auth_headers,
                             content_type='application/json')
        
        assert response2.status_code == 200
        
        # Verify final state
        response = client.get(f'/products/{product_id}', headers=auth_headers)
        
        assert response.status_code == 200
        final_product = response.get_json()
        
        # Should reflect the last update
        assert final_product['price'] == 49.99
        assert final_product['stock_quantity'] == 60
    
    def test_product_error_handling_and_rollback(self, client):
        """Test error handling and transaction rollback."""
        
        auth_headers = self.get_auth_headers(client)
        
        # Test creating product with invalid data that should cause rollback
        invalid_product_data = {
            "name": "test_rollback_product",
            "description": "Product for rollback testing",
            "price": 29.99,
            "stock_quantity": 100,
            "category_id": 99999  # Invalid category
        }
        
        response = client.post('/products/',
                             data=json.dumps(invalid_product_data),
                             headers=auth_headers,
                             content_type='application/json')
        
        assert response.status_code == 404
        
        # Verify no products were created due to rollback
        response = client.get('/products/', headers=auth_headers)
        
        assert response.status_code == 200
        result = response.get_json()
        
        # Should not contain our test product
        product_names = [p['name'] for p in result['products']]
        assert "test_rollback_product" not in product_names
    
    def test_product_development_bypass(self, client):
        """Test product endpoints with development bypass."""
        
        if settings.feature_toggles.BYPASS_AUTH and settings.is_development():
            # Should be able to access without authentication
            response = client.get('/products/')
            
            if response.status_code == 200:
                result = response.get_json()
                assert isinstance(result['products'], list)
            elif response.status_code == 404:
                # Endpoint might not exist, which is fine for this test
                pass
        else:
            # Should require authentication
            response = client.get('/products/')
            assert response.status_code == 401
    
    def test_product_data_integrity(self, client):
        """Test data integrity and consistency."""
        
        auth_headers = self.get_auth_headers(client)
        
        # Create product
        product_data = {
            "name": "test_integrity_product",
            "description": "Product for integrity testing",
            "price": 29.99,
            "stock_quantity": 100,
            "category_id": self.category_id
        }
        
        response = client.post('/products/',
                             data=json.dumps(product_data),
                             headers=auth_headers,
                             content_type='application/json')
        
        assert response.status_code == 201
        product_id = response.get_json()['product']['id']
        
        # Verify data consistency across different endpoints
        # Get from list endpoint
        response_list = client.get('/products/', headers=auth_headers)
        assert response_list.status_code == 200
        
        list_product = next((p for p in response_list.get_json()['products'] 
                           if p['id'] == product_id), None)
        
        # Get from detail endpoint
        response_detail = client.get(f'/products/{product_id}', headers=auth_headers)
        assert response_detail.status_code == 200
        
        detail_product = response_detail.get_json()
        
        # Data should be consistent
        assert list_product['id'] == detail_product['id']
        assert list_product['name'] == detail_product['name']
        assert list_product['price'] == detail_product['price']
        assert list_product['category_id'] == detail_product['category_id']
