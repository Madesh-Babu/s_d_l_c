"""
Category Routes Tests

This module contains comprehensive tests for category endpoints
including CRUD operations and product relationships.
"""

import pytest
import json
from src.models.models import Category, Product


class TestCategoryRoutes:
    """Test category endpoints."""

    def test_create_category_success(self, client, admin_headers, sample_category_data):
        """Test successful category creation."""
        response = client.post(
            "/categories/",
            data=json.dumps(sample_category_data),
            content_type="application/json",
            headers=admin_headers,
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["message"] == "Category created successfully"
        assert "category" in data
        assert data["category"]["name"] == sample_category_data["name"]
        assert data["category"]["description"] == sample_category_data["description"]

    def test_create_category_unauthorized(self, client, sample_category_data):
        """Test category creation without authentication fails."""
        response = client.post(
            "/categories/",
            data=json.dumps(sample_category_data),
            content_type="application/json",
        )

        assert response.status_code == 401
        data = json.loads(response.data)
        assert "error" in data

    def test_create_category_insufficient_permissions(
        self, client, staff_headers, sample_category_data
    ):
        """Test category creation with insufficient permissions fails."""
        response = client.post(
            "/categories/",
            data=json.dumps(sample_category_data),
            content_type="application/json",
            headers=staff_headers,
        )

        assert response.status_code == 403
        data = json.loads(response.data)
        assert "error" in data

    def test_create_category_invalid_data(self, client, admin_headers):
        """Test category creation with invalid data fails."""
        invalid_data = {"name": "", "description": "Valid description"}  # Empty name

        response = client.post(
            "/categories/",
            data=json.dumps(invalid_data),
            content_type="application/json",
            headers=admin_headers,
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_create_category_duplicate_name(
        self, client, admin_headers, create_test_category, sample_category_data
    ):
        """Test category creation with duplicate name fails."""
        response = client.post(
            "/categories/",
            data=json.dumps(sample_category_data),
            content_type="application/json",
            headers=admin_headers,
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_get_all_categories_success(
        self, client, admin_headers, create_test_category
    ):
        """Test getting all categories succeeds."""
        response = client.get("/categories/", headers=admin_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(category["name"] == create_test_category.name for category in data)

    def test_get_all_categories_unauthorized(self, client):
        """Test getting categories without authentication fails."""
        response = client.get("/categories/")

        assert response.status_code == 401
        data = json.loads(response.data)
        assert "error" in data

    def test_get_category_by_id_success(
        self, client, admin_headers, create_test_category
    ):
        """Test getting specific category by ID succeeds."""
        response = client.get(
            f"/categories/{create_test_category.id}", headers=admin_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["id"] == create_test_category.id
        assert data["name"] == create_test_category.name

    def test_get_category_by_id_not_found(self, client, admin_headers):
        """Test getting non-existent category returns 404."""
        response = client.get("/categories/999", headers=admin_headers)

        assert response.status_code == 404

    def test_update_category_success(self, client, admin_headers, create_test_category):
        """Test updating category succeeds."""
        update_data = {"name": "Updated Category", "description": "Updated description"}

        response = client.put(
            f"/categories/{create_test_category.id}",
            data=json.dumps(update_data),
            content_type="application/json",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["category"]["name"] == "Updated Category"
        assert data["category"]["description"] == "Updated description"

    def test_update_category_unauthorized(self, client, create_test_category):
        """Test updating category without authentication fails."""
        update_data = {"name": "Updated Category"}

        response = client.put(
            f"/categories/{create_test_category.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 401

    def test_update_category_not_found(self, client, admin_headers):
        """Test updating non-existent category returns 404."""
        update_data = {"name": "Updated Category"}

        response = client.put(
            "/categories/999",
            data=json.dumps(update_data),
            content_type="application/json",
            headers=admin_headers,
        )

        assert response.status_code == 404

    def test_delete_category_success(self, client, admin_headers, create_test_category):
        """Test deleting category succeeds."""
        response = client.delete(
            f"/categories/{create_test_category.id}", headers=admin_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "deleted successfully" in data["message"]

    def test_delete_category_unauthorized(self, client, create_test_category):
        """Test deleting category without authentication fails."""
        response = client.delete(f"/categories/{create_test_category.id}")

        assert response.status_code == 401

    def test_delete_category_not_found(self, client, admin_headers):
        """Test deleting non-existent category returns 404."""
        response = client.delete("/categories/999", headers=admin_headers)

        assert response.status_code == 404

    def test_delete_category_with_products(
        self, client, admin_headers, create_test_category, create_test_product
    ):
        """Test deleting category with associated products fails."""
        response = client.delete(
            f"/categories/{create_test_category.id}", headers=admin_headers
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "products" in data["error"].lower()

    def test_get_category_products_success(
        self, client, admin_headers, create_test_category, create_test_product
    ):
        """Test getting products in a category succeeds."""
        response = client.get(
            f"/categories/{create_test_category.id}/products", headers=admin_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert all(
            product["category_id"] == create_test_category.id for product in data
        )

    def test_get_category_products_empty(
        self, client, admin_headers, create_test_category
    ):
        """Test getting products from empty category succeeds."""
        response = client.get(
            f"/categories/{create_test_category.id}/products", headers=admin_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_category_products_not_found(self, client, admin_headers):
        """Test getting products from non-existent category returns 404."""
        response = client.get("/categories/999/products", headers=admin_headers)

        assert response.status_code == 404


class TestCategoryBypass:
    """Test category bypass functionality."""

    def test_category_bypass_enabled_in_development(
        self, client, monkeypatch, sample_category_data
    ):
        """Test that category bypass works in development environment."""
        # Enable bypass
        monkeypatch.setenv("ENVIRONMENT", "development")
        monkeypatch.setenv("BYPASS_AUTH", "true")

        response = client.post(
            "/categories/",
            data=json.dumps(sample_category_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert "auth_bypassed" in data
        assert data["auth_bypassed"] is True

    def test_category_bypass_disabled_in_production(
        self, client, monkeypatch, sample_category_data
    ):
        """Test that category bypass is disabled in production."""
        # Disable bypass
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("BYPASS_AUTH", "false")

        response = client.post(
            "/categories/",
            data=json.dumps(sample_category_data),
            content_type="application/json",
        )

        assert response.status_code == 401
        data = json.loads(response.data)
        assert "error" in data


class TestCategoryServiceIntegration:
    """Test category service integration."""

    def test_category_service_crud(self, app, sample_category_data):
        """Test category service CRUD operations."""
        from src.services.service import CategoryService

        with app.app_context():
            service = CategoryService()

            # Create category
            category = service.create_category(sample_category_data)
            assert category.name == sample_category_data["name"]
            assert category.description == sample_category_data["description"]

            # Read category
            retrieved = service.get_category(category.id)
            assert retrieved.id == category.id
            assert retrieved.name == category.name

            # Update category
            update_data = {"name": "Updated Category"}
            updated = service.update_category(category.id, update_data)
            assert updated.name == "Updated Category"

            # Get all categories
            all_categories = service.get_all_categories()
            assert len(all_categories) >= 1

            # Delete category
            service.delete_category(category.id)
            deleted = service.get_category(category.id)
            assert deleted is None

    def test_category_product_relationships(
        self, app, create_test_category, sample_product_data
    ):
        """Test category-product relationships."""
        from src.services.service import CategoryService, ProductService

        with app.app_context():
            category_service = CategoryService()
            product_service = ProductService()

            # Create product in category
            product_data = sample_product_data.copy()
            product_data["category_id"] = create_test_category.id
            product = product_service.create_product(product_data)

            # Get category with products
            category_with_products = category_service.get_category_with_products(
                create_test_category.id
            )
            assert len(category_with_products.products) >= 1
            assert category_with_products.products[0].id == product.id
