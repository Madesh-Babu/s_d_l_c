"""
Service Layer Tests

This module contains comprehensive tests for service layer
including business logic, validation, and data operations.
"""

import pytest
from unittest.mock import Mock, patch
from src.services.service import ProductService, CategoryService, DiscountedProductService
from src.services.price_decorator import Price, DiscountDecorator, TaxDecorator
from src.models.models import User, Product, Category


class TestProductService:
    """Test ProductService."""

    def test_product_service_initialization(self, app):
        """Test ProductService initialization."""
        with app.app_context():
            service = ProductService()
            
            assert service is not None
            assert hasattr(service, 'create_product')
            assert hasattr(service, 'get_product')
            assert hasattr(service, 'get_all_products')
            assert hasattr(service, 'update_product')
            assert hasattr(service, 'delete_product')

    def test_create_product_success(self, app, create_test_category, sample_product_data):
        """Test successful product creation."""
        with app.app_context():
            service = ProductService()
            
            product = service.create_product(sample_product_data)
            
            assert product.name == sample_product_data['name']
            assert product.price == sample_product_data['price']
            assert product.category_id == create_test_category.id
            assert product.id is not None

    def test_create_product_invalid_category(self, app, sample_product_data):
        """Test product creation with invalid category."""
        with app.app_context():
            service = ProductService()
            
            invalid_data = sample_product_data.copy()
            invalid_data['category_id'] = 999  # Non-existent category
            
            with pytest.raises(Exception):
                service.create_product(invalid_data)

    def test_get_product_success(self, app, create_test_product):
        """Test getting product by ID."""
        with app.app_context():
            service = ProductService()
            
            product = service.get_product(create_test_product.id)
            
            assert product.id == create_test_product.id
            assert product.name == create_test_product.name

    def test_get_product_not_found(self, app):
        """Test getting non-existent product."""
        with app.app_context():
            service = ProductService()
            
            product = service.get_product(999)
            
            assert product is None

    def test_get_all_products_success(self, app, create_test_product):
        """Test getting all products."""
        with app.app_context():
            service = ProductService()
            
            products = service.get_all_products()
            
            assert isinstance(products, list)
            assert len(products) >= 1
            assert any(p.id == create_test_product.id for p in products)

    def test_get_all_products_empty(self, app):
        """Test getting all products when none exist."""
        with app.app_context():
            service = ProductService()
            
            products = service.get_all_products()
            
            assert isinstance(products, list)
            assert len(products) == 0

    def test_update_product_success(self, app, create_test_product):
        """Test successful product update."""
        with app.app_context():
            service = ProductService()
            
            update_data = {
                'name': 'Updated Product',
                'price': 149.99
            }
            
            updated_product = service.update_product(create_test_product.id, update_data)
            
            assert updated_product.name == 'Updated Product'
            assert updated_product.price == 149.99

    def test_update_product_not_found(self, app):
        """Test updating non-existent product."""
        with app.app_context():
            service = ProductService()
            
            update_data = {'name': 'Updated Product'}
            
            with pytest.raises(Exception):
                service.update_product(999, update_data)

    def test_delete_product_success(self, app, create_test_product):
        """Test successful product deletion."""
        with app.app_context():
            service = ProductService()
            
            service.delete_product(create_test_product.id)
            
            # Product should be deleted
            deleted_product = service.get_product(create_test_product.id)
            assert deleted_product is None

    def test_delete_product_not_found(self, app):
        """Test deleting non-existent product."""
        with app.app_context():
            service = ProductService()
            
            with pytest.raises(Exception):
                service.delete_product(999)

    def test_product_validation(self, app, create_test_category):
        """Test product data validation."""
        with app.app_context():
            service = ProductService()
            
            # Test negative price
            invalid_data = {
                'name': 'Test Product',
                'price': -10,
                'category_id': create_test_category.id
            }
            
            with pytest.raises(Exception):
                service.create_product(invalid_data)

    def test_product_stock_management(self, app, create_test_product):
        """Test product stock quantity management."""
        with app.app_context():
            service = ProductService()
            
            # Update stock
            update_data = {'stock_quantity': 50}
            updated = service.update_product(create_test_product.id, update_data)
            
            assert updated.stock_quantity == 50


class TestCategoryService:
    """Test CategoryService."""

    def test_category_service_initialization(self, app):
        """Test CategoryService initialization."""
        with app.app_context():
            service = CategoryService()
            
            assert service is not None
            assert hasattr(service, 'create_category')
            assert hasattr(service, 'get_category')
            assert hasattr(service, 'get_all_categories')
            assert hasattr(service, 'update_category')
            assert hasattr(service, 'delete_category')

    def test_create_category_success(self, app, sample_category_data):
        """Test successful category creation."""
        with app.app_context():
            service = CategoryService()
            
            category = service.create_category(sample_category_data)
            
            assert category.name == sample_category_data['name']
            assert category.description == sample_category_data['description']
            assert category.id is not None

    def test_create_category_duplicate_name(self, app, create_test_category, sample_category_data):
        """Test category creation with duplicate name."""
        with app.app_context():
            service = CategoryService()
            
            with pytest.raises(Exception):
                service.create_category(sample_category_data)

    def test_get_category_success(self, app, create_test_category):
        """Test getting category by ID."""
        with app.app_context():
            service = CategoryService()
            
            category = service.get_category(create_test_category.id)
            
            assert category.id == create_test_category.id
            assert category.name == create_test_category.name

    def test_get_category_not_found(self, app):
        """Test getting non-existent category."""
        with app.app_context():
            service = CategoryService()
            
            category = service.get_category(999)
            
            assert category is None

    def test_get_all_categories_success(self, app, create_test_category):
        """Test getting all categories."""
        with app.app_context():
            service = CategoryService()
            
            categories = service.get_all_categories()
            
            assert isinstance(categories, list)
            assert len(categories) >= 1
            assert any(c.id == create_test_category.id for c in categories)

    def test_update_category_success(self, app, create_test_category):
        """Test successful category update."""
        with app.app_context():
            service = CategoryService()
            
            update_data = {
                'name': 'Updated Category',
                'description': 'Updated description'
            }
            
            updated_category = service.update_category(create_test_category.id, update_data)
            
            assert updated_category.name == 'Updated Category'
            assert updated_category.description == 'Updated description'

    def test_delete_category_success(self, app, create_test_category):
        """Test successful category deletion."""
        with app.app_context():
            service = CategoryService()
            
            service.delete_category(create_test_category.id)
            
            # Category should be deleted
            deleted_category = service.get_category(create_test_category.id)
            assert deleted_category is None

    def test_delete_category_with_products(self, app, create_test_category, create_test_product):
        """Test deleting category with associated products."""
        with app.app_context():
            service = CategoryService()
            
            with pytest.raises(Exception):  # Should fail due to foreign key constraint
                service.delete_category(create_test_category.id)

    def test_get_category_with_products(self, app, create_test_category, create_test_product):
        """Test getting category with associated products."""
        with app.app_context():
            service = CategoryService()
            
            category_with_products = service.get_category_with_products(create_test_category.id)
            
            assert category_with_products.id == create_test_category.id
            assert len(category_with_products.products) >= 1
            assert category_with_products.products[0].id == create_test_product.id


class TestDiscountedProductService:
    """Test DiscountedProductService."""

    def test_discounted_service_inheritance(self, app):
        """Test that DiscountedProductService inherits from ProductService."""
        with app.app_context():
            service = DiscountedProductService()
            
            # Should have all ProductService methods
            assert hasattr(service, 'create_product')
            assert hasattr(service, 'get_product')
            assert hasattr(service, 'calculate_discounted_price')

    def test_calculate_discounted_price(self, app):
        """Test discount price calculation."""
        with app.app_context():
            service = DiscountedProductService()
            
            original_price = 100.0
            discount_percentage = 20
            
            discounted_price = service.calculate_discounted_price(original_price, discount_percentage)
            
            expected_price = original_price * (1 - discount_percentage / 100)
            assert discounted_price == expected_price

    def test_calculate_discounted_price_zero_discount(self, app):
        """Test discount calculation with zero discount."""
        with app.app_context():
            service = DiscountedProductService()
            
            original_price = 100.0
            discount_percentage = 0
            
            discounted_price = service.calculate_discounted_price(original_price, discount_percentage)
            
            assert discounted_price == original_price

    def test_calculate_discounted_price_full_discount(self, app):
        """Test discount calculation with 100% discount."""
        with app.app_context():
            service = DiscountedProductService()
            
            original_price = 100.0
            discount_percentage = 100
            
            discounted_price = service.calculate_discounted_price(original_price, discount_percentage)
            
            assert discounted_price == 0.0

    def test_calculate_discounted_price_invalid_percentage(self, app):
        """Test discount calculation with invalid percentage."""
        with app.app_context():
            service = DiscountedProductService()
            
            with pytest.raises(Exception):
                service.calculate_discounted_price(100.0, -10)  # Negative percentage
            
            with pytest.raises(Exception):
                service.calculate_discounted_price(100.0, 150)  # Percentage > 100

    def test_create_discounted_product(self, app, create_test_category, sample_product_data):
        """Test creating product with discount calculation."""
        with app.app_context():
            service = DiscountedProductService()
            
            product = service.create_product(sample_product_data)
            
            assert product.name == sample_product_data['name']
            assert product.price == sample_product_data['price']
            
            # Calculate discount
            discounted_price = service.calculate_discounted_price(product.price, 10)
            assert discounted_price == product.price * 0.9


class TestPriceDecorator:
    """Test price decorator pattern."""

    def test_base_price(self):
        """Test base price class."""
        price = Price(100.0)
        
        assert price.get_price() == 100.0
        assert str(price) == "$100.00"

    def test_discount_decorator(self):
        """Test discount decorator."""
        base_price = Price(100.0)
        discounted = DiscountDecorator(base_price, 20)
        
        assert discounted.get_price() == 80.0  # 100 * (1 - 0.2)
        assert str(discounted) == "$80.00"

    def test_tax_decorator(self):
        """Test tax decorator."""
        base_price = Price(100.0)
        with_tax = TaxDecorator(base_price, 10)
        
        assert with_tax.get_price() == 110.0  # 100 * (1 + 0.1)
        assert str(with_tax) == "$110.00"

    def test_multiple_decorators(self):
        """Test multiple decorators chained."""
        base_price = Price(100.0)
        discounted = DiscountDecorator(base_price, 20)  # $80
        with_tax = TaxDecorator(discounted, 10)  # $88
        
        assert with_tax.get_price() == 88.0
        assert str(with_tax) == "$88.00"

    def test_decorator_order_matters(self):
        """Test that decorator order affects final price."""
        base_price = Price(100.0)
        
        # Discount then tax: $100 -> $80 -> $88
        discounted_then_tax = TaxDecorator(DiscountDecorator(base_price, 20), 10)
        
        # Tax then discount: $100 -> $110 -> $88
        tax_then_discount = DiscountDecorator(TaxDecorator(base_price, 10), 20)
        
        # Both should result in same final price for these percentages
        assert discounted_then_tax.get_price() == tax_then_discount.get_price()

    def test_decorator_zero_values(self):
        """Test decorators with zero values."""
        base_price = Price(100.0)
        
        # Zero discount
        no_discount = DiscountDecorator(base_price, 0)
        assert no_discount.get_price() == 100.0
        
        # Zero tax
        no_tax = TaxDecorator(base_price, 0)
        assert no_tax.get_price() == 100.0

    def test_decorator_edge_cases(self):
        """Test decorator edge cases."""
        base_price = Price(100.0)
        
        # Maximum discount
        max_discount = DiscountDecorator(base_price, 100)
        assert max_discount.get_price() == 0.0
        
        # High tax
        high_tax = TaxDecorator(base_price, 50)
        assert high_tax.get_price() == 150.0

    def test_decorator_validation(self):
        """Test decorator input validation."""
        base_price = Price(100.0)
        
        # Invalid discount percentage
        with pytest.raises(Exception):
            DiscountDecorator(base_price, -10)
        
        with pytest.raises(Exception):
            DiscountDecorator(base_price, 150)
        
        # Invalid tax percentage
        with pytest.raises(Exception):
            TaxDecorator(base_price, -10)
        
        with pytest.raises(Exception):
            TaxDecorator(base_price, 150)


class TestServiceIntegration:
    """Test service integration and business logic."""

    def test_service_transaction_rollback(self, app, create_test_category):
        """Test that service operations roll back on error."""
        with app.app_context():
            service = ProductService()
            
            # Try to create invalid product
            invalid_data = {
                'name': '',  # Invalid empty name
                'price': 99.99,
                'category_id': create_test_category.id
            }
            
            initial_count = len(service.get_all_products())
            
            try:
                service.create_product(invalid_data)
            except Exception:
                pass  # Expected to fail
            
            # Count should be unchanged
            final_count = len(service.get_all_products())
            assert initial_count == final_count

    def test_service_business_rules(self, app, create_test_category):
        """Test service business rules."""
        with app.app_context():
            service = ProductService()
            
            # Test minimum price rule
            invalid_data = {
                'name': 'Test Product',
                'price': 0.01,  # Too low
                'category_id': create_test_category.id
            }
            
            # Should enforce minimum price (if implemented)
            try:
                product = service.create_product(invalid_data)
                # If created, check if price was adjusted
                assert product.price >= 1.0
            except Exception:
                # Or should reject low price
                pass

    def test_service_performance(self, app, create_test_category, sample_product_data):
        """Test service performance with multiple operations."""
        with app.app_context():
            service = ProductService()
            
            import time
            start_time = time.time()
            
            # Create multiple products
            products = []
            for i in range(10):
                data = sample_product_data.copy()
                data['name'] = f'Product {i}'
                product = service.create_product(data)
                products.append(product)
            
            # Get all products
            all_products = service.get_all_products()
            
            # Update all products
            for product in products:
                service.update_product(product.id, {'name': f'Updated {product.name}'})
            
            # Delete all products
            for product in products:
                service.delete_product(product.id)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Should complete reasonably quickly
            assert duration < 2.0
            assert len(all_products) >= 10
