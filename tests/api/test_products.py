"""
Product Routes Tests

This module contains comprehensive tests for product endpoints
including CRUD operations and discount functionality.
"""

import pytest
import json
from src.models.models import Product, Category


class TestProductRoutes:
    """Test product endpoints."""

    def test_create_product_success(self, client, admin_headers, create_test_category, sample_product_data):
        """Test successful product creation."""
        response = client.post('/products/',
                             data=json.dumps(sample_product_data),
                             content_type='application/json',
                             headers=admin_headers)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Product added'
        assert 'product' in data
        assert data['product']['name'] == sample_product_data['name']
        assert data['product']['price'] == sample_product_data['price']

    def test_create_product_unauthorized(self, client, sample_product_data):
        """Test product creation without authentication fails."""
        response = client.post('/products/',
                             data=json.dumps(sample_product_data),
                             content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data

    def test_create_product_insufficient_permissions(self, client, staff_headers, sample_product_data):
        """Test product creation with insufficient permissions fails."""
        response = client.post('/products/',
                             data=json.dumps(sample_product_data),
                             content_type='application/json',
                             headers=staff_headers)
        
        assert response.status_code == 403
        data = json.loads(response.data)
        assert 'error' in data

    def test_create_product_invalid_data(self, client, admin_headers):
        """Test product creation with invalid data fails."""
        invalid_data = {
            'name': '',  # Empty name
            'price': -10  # Negative price
        }
        
        response = client.post('/products/',
                             data=json.dumps(invalid_data),
                             content_type='application/json',
                             headers=admin_headers)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_get_all_products_success(self, client, admin_headers, create_test_product):
        """Test getting all products succeeds."""
        response = client.get('/products/', headers=admin_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(product['name'] == create_test_product.name for product in data)

    def test_get_all_products_unauthorized(self, client):
        """Test getting products without authentication fails."""
        response = client.get('/products/')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data

    def test_get_product_by_id_success(self, client, admin_headers, create_test_product):
        """Test getting specific product by ID succeeds."""
        response = client.get(f'/products/{create_test_product.id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == create_test_product.id
        assert data['name'] == create_test_product.name

    def test_get_product_by_id_not_found(self, client, admin_headers):
        """Test getting non-existent product returns 404."""
        response = client.get('/products/999', headers=admin_headers)
        
        assert response.status_code == 404

    def test_update_product_success(self, client, admin_headers, create_test_product):
        """Test updating product succeeds."""
        update_data = {
            'name': 'Updated Product',
            'price': 149.99
        }
        
        response = client.put(f'/products/{create_test_product.id}',
                            data=json.dumps(update_data),
                            content_type='application/json',
                            headers=admin_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['product']['name'] == 'Updated Product'
        assert data['product']['price'] == 149.99

    def test_update_product_unauthorized(self, client, create_test_product):
        """Test updating product without authentication fails."""
        update_data = {'name': 'Updated Product'}
        
        response = client.put(f'/products/{create_test_product.id}',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 401

    def test_update_product_not_found(self, client, admin_headers):
        """Test updating non-existent product returns 404."""
        update_data = {'name': 'Updated Product'}
        
        response = client.put('/products/999',
                            data=json.dumps(update_data),
                            content_type='application/json',
                            headers=admin_headers)
        
        assert response.status_code == 404

    def test_delete_product_success(self, client, admin_headers, create_test_product):
        """Test deleting product succeeds."""
        response = client.delete(f'/products/{create_test_product.id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'deleted successfully' in data['message']

    def test_delete_product_unauthorized(self, client, create_test_product):
        """Test deleting product without authentication fails."""
        response = client.delete(f'/products/{create_test_product.id}')
        
        assert response.status_code == 401

    def test_delete_product_not_found(self, client, admin_headers):
        """Test deleting non-existent product returns 404."""
        response = client.delete('/products/999', headers=admin_headers)
        
        assert response.status_code == 404

    def test_apply_discount_success(self, client, admin_headers, create_test_product):
        """Test applying discount to product succeeds."""
        discount_data = {
            'discount_percentage': 20
        }
        
        response = client.post(f'/products/{create_test_product.id}/discount',
                             data=json.dumps(discount_data),
                             content_type='application/json',
                             headers=admin_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'discounted_price' in data
        assert data['original_price'] == create_test_product.price
        assert data['discount_percentage'] == 20

    def test_apply_discount_invalid_percentage(self, client, admin_headers, create_test_product):
        """Test applying invalid discount percentage fails."""
        discount_data = {
            'discount_percentage': 150  # Invalid percentage
        }
        
        response = client.post(f'/products/{create_test_product.id}/discount',
                             data=json.dumps(discount_data),
                             content_type='application/json',
                             headers=admin_headers)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_get_product_with_discount(self, client, admin_headers, create_test_product):
        """Test getting product with discount calculation."""
        # Apply discount first
        discount_data = {'discount_percentage': 10}
        client.post(f'/products/{create_test_product.id}/discount',
                   data=json.dumps(discount_data),
                   content_type='application/json',
                   headers=admin_headers)
        
        # Get product
        response = client.get(f'/products/{create_test_product.id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'discounted_price' in data or 'price' in data

    def test_product_stock_validation(self, client, admin_headers, create_test_category):
        """Test product stock quantity validation."""
        product_data = {
            'name': 'Test Product',
            'description': 'Test description',
            'price': 99.99,
            'stock_quantity': -5,  # Invalid negative stock
            'category_id': create_test_category.id
        }
        
        response = client.post('/products/',
                             data=json.dumps(product_data),
                             content_type='application/json',
                             headers=admin_headers)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_product_category_validation(self, client, admin_headers, sample_product_data):
        """Test product category validation."""
        product_data = sample_product_data.copy()
        product_data['category_id'] = 999  # Non-existent category
        
        response = client.post('/products/',
                             data=json.dumps(product_data),
                             content_type='application/json',
                             headers=admin_headers)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data


class TestProductBypass:
    """Test product bypass functionality."""

    def test_product_bypass_enabled_in_development(self, client, monkeypatch, sample_product_data, create_test_category):
        """Test that product bypass works in development environment."""
        # Enable bypass
        monkeypatch.setenv('ENVIRONMENT', 'development')
        monkeypatch.setenv('BYPASS_AUTH', 'true')
        
        response = client.post('/products/',
                             data=json.dumps(sample_product_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'auth_bypassed' in data
        assert data['auth_bypassed'] is True

    def test_product_bypass_disabled_in_production(self, client, monkeypatch, sample_product_data):
        """Test that product bypass is disabled in production."""
        # Disable bypass
        monkeypatch.setenv('ENVIRONMENT', 'production')
        monkeypatch.setenv('BYPASS_AUTH', 'false')
        
        response = client.post('/products/',
                             data=json.dumps(sample_product_data),
                             content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data


class TestProductServiceIntegration:
    """Test product service integration."""

    def test_product_service_crud(self, app, create_test_category, sample_product_data):
        """Test product service CRUD operations."""
        from src.services.service import ProductService
        
        with app.app_context():
            service = ProductService()
            
            # Create product
            product = service.create_product(sample_product_data)
            assert product.name == sample_product_data['name']
            assert product.price == sample_product_data['price']
            
            # Read product
            retrieved = service.get_product(product.id)
            assert retrieved.id == product.id
            assert retrieved.name == product.name
            
            # Update product
            update_data = {'name': 'Updated Product'}
            updated = service.update_product(product.id, update_data)
            assert updated.name == 'Updated Product'
            
            # Get all products
            all_products = service.get_all_products()
            assert len(all_products) >= 1
            
            # Delete product
            service.delete_product(product.id)
            deleted = service.get_product(product.id)
            assert deleted is None

    def test_discounted_product_service(self, app, create_test_product):
        """Test discounted product service."""
        from src.services.service import DiscountedProductService
        
        with app.app_context():
            service = DiscountedProductService()
            
            # Test discount calculation
            discounted_price = service.calculate_discounted_price(
                create_test_product.price, 20
            )
            expected_price = create_test_product.price * 0.8
            assert discounted_price == expected_price
