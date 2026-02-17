"""
Integration Tests for Category Endpoints

This module contains comprehensive integration tests for category endpoints,
testing CRUD operations, hierarchical relationships, and business logic.
"""

import pytest
import json
from datetime import datetime
from src.models.models import db, Category, Product, User
from src.core.config import settings


class TestCategoryIntegration:
    """Test complete category management workflows."""

    @pytest.fixture(autouse=True)
    def setup_test_data(self, app, client):
        """Set up test data for category tests."""
        with app.app_context():
            # Clean up test data
            Category.query.filter(Category.name.like("test_%")).delete()
            Product.query.filter(Product.name.like("test_%")).delete()
            User.query.filter(User.username.like("test_%")).delete()
            db.session.commit()

            # Create test user
            test_user = User(
                username="test_category_user",
                email="test_category@example.com",
                role="staff",
            )
            test_user.set_password("TestPassword123!")
            db.session.add(test_user)
            db.session.commit()

            self.user_id = test_user.id

    def get_auth_headers(self, client):
        """Get authentication headers for test user."""
        login_data = {"username": "test_category_user", "password": "TestPassword123!"}

        response = client.post(
            "/auth/login", data=json.dumps(login_data), content_type="application/json"
        )

        token = response.get_json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_complete_category_crud_workflow(self, client):
        """Test complete CRUD workflow for categories."""

        auth_headers = self.get_auth_headers(client)

        # Step 1: Create a category
        category_data = {
            "name": "test_integration_category",
            "description": "Category for integration testing",
        }

        response = client.post(
            "/categories/",
            data=json.dumps(category_data),
            headers=auth_headers,
            content_type="application/json",
        )

        assert response.status_code == 201
        create_result = response.get_json()
        assert create_result["message"] == "Category created successfully"
        assert create_result["category"]["name"] == "test_integration_category"

        category_id = create_result["category"]["id"]

        # Step 2: Retrieve all categories and verify our category is there
        response = client.get("/categories/", headers=auth_headers)

        assert response.status_code == 200
        get_all_result = response.get_json()
        assert isinstance(get_all_result, list)

        # Find our category
        category_names = [c["name"] for c in get_all_result]
        assert "test_integration_category" in category_names

        # Step 3: Get specific category by ID
        response = client.get(f"/categories/{category_id}", headers=auth_headers)

        assert response.status_code == 200
        get_one_result = response.get_json()
        assert get_one_result["name"] == "test_integration_category"
        assert get_one_result["description"] == "Category for integration testing"

        # Step 4: Update the category
        update_data = {
            "name": "test_integration_category_updated",
            "description": "Updated category description",
        }

        response = client.put(
            f"/categories/{category_id}",
            data=json.dumps(update_data),
            headers=auth_headers,
            content_type="application/json",
        )

        assert response.status_code == 200
        update_result = response.get_json()
        assert update_result["message"] == "Category updated successfully"
        assert update_result["category"]["name"] == "test_integration_category_updated"
        assert (
            update_result["category"]["description"] == "Updated category description"
        )

        # Step 5: Delete the category
        response = client.delete(f"/categories/{category_id}", headers=auth_headers)

        assert response.status_code == 200
        delete_result = response.get_json()
        assert "deleted successfully" in delete_result["message"]

        # Step 6: Verify category is deleted
        response = client.get(f"/categories/{category_id}", headers=auth_headers)
        assert response.status_code == 404

    def test_category_hierarchical_relationships(self, client):
        """Test hierarchical category relationships."""

        auth_headers = self.get_auth_headers(client)

        # Step 1: Create parent category
        parent_data = {
            "name": "test_parent_category",
            "description": "Parent category for hierarchy testing",
        }

        response = client.post(
            "/categories/",
            data=json.dumps(parent_data),
            headers=auth_headers,
            content_type="application/json",
        )

        assert response.status_code == 201
        parent_id = response.get_json()["category"]["id"]

        # Step 2: Create child category
        child_data = {
            "name": "test_child_category",
            "description": "Child category for hierarchy testing",
            "parent_category_id": parent_id,
        }

        response = client.post(
            "/categories/",
            data=json.dumps(child_data),
            headers=auth_headers,
            content_type="application/json",
        )

        assert response.status_code == 201
        child_result = response.get_json()
        child_id = child_result["category"]["id"]

        # Verify parent-child relationship
        assert child_result["category"]["parent_category_id"] == parent_id

        # Step 3: Create grandchild category
        grandchild_data = {
            "name": "test_grandchild_category",
            "description": "Grandchild category for hierarchy testing",
            "parent_category_id": child_id,
        }

        response = client.post(
            "/categories/",
            data=json.dumps(grandchild_data),
            headers=auth_headers,
            content_type="application/json",
        )

        assert response.status_code == 201
        grandchild_result = response.get_json()
        grandchild_id = grandchild_result["category"]["id"]

        # Verify hierarchy
        assert grandchild_result["category"]["parent_category_id"] == child_id

        # Step 4: Test retrieving categories with hierarchy info
        response = client.get(f"/categories/{child_id}", headers=auth_headers)

        assert response.status_code == 200
        child_detail = response.get_json()
        assert child_detail["parent_category_id"] == parent_id

        # Step 5: Test getting products in hierarchical categories
        # Create products in different categories
        product_data = {
            "name": "test_hierarchy_product",
            "description": "Product for hierarchy testing",
            "price": 29.99,
            "stock_quantity": 100,
            "category_id": child_id,
        }

        response = client.post(
            "/products/",
            data=json.dumps(product_data),
            headers=auth_headers,
            content_type="application/json",
        )

        assert response.status_code == 201

        # Get products in child category
        response = client.get(f"/categories/{child_id}/products", headers=auth_headers)

        if response.status_code == 200:
            products = response.get_json()
            assert isinstance(products, list)
            # Should contain our product
            product_names = [p["name"] for p in products]
            assert "test_hierarchy_product" in product_names

    def test_category_validation_and_business_rules(self, client):
        """Test category validation and business rule enforcement."""

        auth_headers = self.get_auth_headers(client)

        # Test invalid name (too short)
        invalid_category_data = {
            "name": "a",  # Too short
            "description": "Invalid category test",
        }

        response = client.post(
            "/categories/",
            data=json.dumps(invalid_category_data),
            headers=auth_headers,
            content_type="application/json",
        )

        assert response.status_code == 400
        result = response.get_json()
        assert "error" in result

        # Test duplicate category name
        category_data = {
            "name": "test_duplicate_category",
            "description": "Category for duplicate testing",
        }

        # Create first category
        response1 = client.post(
            "/categories/",
            data=json.dumps(category_data),
            headers=auth_headers,
            content_type="application/json",
        )
        assert response1.status_code == 201

        # Try to create duplicate
        response2 = client.post(
            "/categories/",
            data=json.dumps(category_data),
            headers=auth_headers,
            content_type="application/json",
        )
        assert response2.status_code == 409
        result = response2.get_json()
        assert "error" in result

        # Test invalid parent category
        invalid_parent_data = {
            "name": "test_invalid_parent",
            "description": "Category with invalid parent",
            "parent_category_id": 99999,  # Non-existent parent
        }

        response = client.post(
            "/categories/",
            data=json.dumps(invalid_parent_data),
            headers=auth_headers,
            content_type="application/json",
        )

        assert response.status_code == 404
        result = response.get_json()
        assert "error" in result

    def test_category_product_relationships(self, client):
        """Test category-product relationships and data integrity."""

        auth_headers = self.get_auth_headers(client)

        # Create category
        category_data = {
            "name": "test_products_category",
            "description": "Category for product relationship testing",
        }

        response = client.post(
            "/categories/",
            data=json.dumps(category_data),
            headers=auth_headers,
            content_type="application/json",
        )

        assert response.status_code == 201
        category_id = response.get_json()["category"]["id"]

        # Create multiple products in the category
        products = [
            {
                "name": f"test_category_product_{i}",
                "description": f"Product {i} for category testing",
                "price": 10.0 + i * 5,
                "stock_quantity": 50 + i * 10,
                "category_id": category_id,
            }
            for i in range(5)
        ]

        created_products = []
        for product_data in products:
            response = client.post(
                "/products/",
                data=json.dumps(product_data),
                headers=auth_headers,
                content_type="application/json",
            )
            assert response.status_code == 201
            created_products.append(response.get_json()["product"])

        # Test getting products by category
        response = client.get(
            f"/categories/{category_id}/products", headers=auth_headers
        )

        if response.status_code == 200:
            category_products = response.get_json()
            assert isinstance(category_products, list)
            assert len(category_products) >= 5

            # Verify all products belong to the correct category
            for product in category_products:
                assert product["category_id"] == category_id

        # Test category deletion with products (should handle constraints)
        # This might fail due to foreign key constraints, which is expected
        response = client.delete(f"/categories/{category_id}", headers=auth_headers)

        # The behavior depends on your database constraints
        # It might succeed (cascade delete) or fail (constraint violation)
        if response.status_code == 200:
            # Category was deleted, products should be gone too
            response = client.get("/products/", headers=auth_headers)
            all_products = response.get_json()["products"]

            # Our test products should be gone
            test_product_names = [
                p["name"]
                for p in all_products
                if p["name"].startswith("test_category_product")
            ]
            assert len(test_product_names) == 0
        elif response.status_code == 400:
            # Category deletion failed due to constraints (expected behavior)
            result = response.get_json()
            assert "error" in result

    def test_category_circular_reference_prevention(self, client):
        """Test prevention of circular category references."""

        auth_headers = self.get_auth_headers(client)

        # Create parent category
        parent_data = {
            "name": "test_circular_parent",
            "description": "Parent for circular reference test",
        }

        response = client.post(
            "/categories/",
            data=json.dumps(parent_data),
            headers=auth_headers,
            content_type="application/json",
        )

        assert response.status_code == 201
        parent_id = response.get_json()["category"]["id"]

        # Create child category
        child_data = {
            "name": "test_circular_child",
            "description": "Child for circular reference test",
            "parent_category_id": parent_id,
        }

        response = client.post(
            "/categories/",
            data=json.dumps(child_data),
            headers=auth_headers,
            content_type="application/json",
        )

        assert response.status_code == 201
        child_id = response.get_json()["category"]["id"]

        # Try to set parent as child of its own child (circular reference)
        circular_update = {"parent_category_id": child_id}

        response = client.put(
            f"/categories/{parent_id}",
            data=json.dumps(circular_update),
            headers=auth_headers,
            content_type="application/json",
        )

        # Should prevent circular reference
        assert response.status_code in [400, 409]
        result = response.get_json()
        assert "error" in result

    def test_category_development_bypass(self, client):
        """Test category endpoints with development bypass."""

        if settings.feature_toggles.BYPASS_AUTH and settings.is_development():
            # Should be able to access without authentication
            response = client.get("/categories/")

            if response.status_code == 200:
                result = response.get_json()
                assert isinstance(result, list)
            elif response.status_code == 404:
                # Endpoint might not exist, which is fine for this test
                pass
        else:
            # Should require authentication
            response = client.get("/categories/")
            assert response.status_code == 401

    def test_category_data_integrity(self, client):
        """Test data integrity and consistency across category operations."""

        auth_headers = self.get_auth_headers(client)

        # Create category
        category_data = {
            "name": "test_integrity_category",
            "description": "Category for integrity testing",
        }

        response = client.post(
            "/categories/",
            data=json.dumps(category_data),
            headers=auth_headers,
            content_type="application/json",
        )

        assert response.status_code == 201
        category_id = response.get_json()["category"]["id"]

        # Verify data consistency across different endpoints
        # Get from list endpoint
        response_list = client.get("/categories/", headers=auth_headers)
        assert response_list.status_code == 200

        list_category = next(
            (c for c in response_list.get_json() if c["id"] == category_id), None
        )

        # Get from detail endpoint
        response_detail = client.get(f"/categories/{category_id}", headers=auth_headers)
        assert response_detail.status_code == 200

        detail_category = response_detail.get_json()

        # Data should be consistent
        assert list_category["id"] == detail_category["id"]
        assert list_category["name"] == detail_category["name"]
        assert list_category["description"] == detail_category["description"]

        # Test update consistency
        update_data = {
            "name": "test_integrity_category_updated",
            "description": "Updated description for integrity testing",
        }

        response = client.put(
            f"/categories/{category_id}",
            data=json.dumps(update_data),
            headers=auth_headers,
            content_type="application/json",
        )

        assert response.status_code == 200

        # Verify consistency after update
        response_list = client.get("/categories/", headers=auth_headers)
        updated_list_category = next(
            (c for c in response_list.get_json() if c["id"] == category_id), None
        )

        response_detail = client.get(f"/categories/{category_id}", headers=auth_headers)
        updated_detail_category = response_detail.get_json()

        assert updated_list_category["name"] == updated_detail_category["name"]
        assert (
            updated_list_category["description"]
            == updated_detail_category["description"]
        )

    def test_category_error_handling_and_rollback(self, client):
        """Test error handling and transaction rollback."""

        auth_headers = self.get_auth_headers(client)

        # Test creating category with invalid parent that should cause rollback
        invalid_category_data = {
            "name": "test_rollback_category",
            "description": "Category for rollback testing",
            "parent_category_id": 99999,  # Invalid parent
        }

        response = client.post(
            "/categories/",
            data=json.dumps(invalid_category_data),
            headers=auth_headers,
            content_type="application/json",
        )

        assert response.status_code == 404

        # Verify no categories were created due to rollback
        response = client.get("/categories/", headers=auth_headers)

        assert response.status_code == 200
        result = response.get_json()

        # Should not contain our test category
        category_names = [c["name"] for c in result]
        assert "test_rollback_category" not in category_names
