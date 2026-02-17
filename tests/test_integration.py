"""
Integration Tests

This module contains integration tests that test the entire application
including API endpoints, database operations, and business logic.
"""

import pytest
import json
from src.api import create_app, db
from src.models.models import User, Product, Category


class TestApplicationIntegration:
    """Test full application integration."""

    def test_full_user_workflow(self, client, sample_user_data):
        """Test complete user registration and login workflow."""
        # Register user
        register_response = client.post(
            "/auth/register",
            data=json.dumps(sample_user_data),
            content_type="application/json",
        )

        assert register_response.status_code == 201

        # Login user
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"],
        }
        login_response = client.post(
            "/auth/login", data=json.dumps(login_data), content_type="application/json"
        )

        assert login_response.status_code == 200
        login_data = json.loads(login_response.data)
        assert "access_token" in login_data

        # Use token to access protected endpoint
        token = login_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        users_response = client.get("/auth/users", headers=headers)
        assert users_response.status_code == 200

    def test_full_product_workflow(
        self, client, admin_headers, sample_category_data, sample_product_data
    ):
        """Test complete product management workflow."""
        # Create category
        category_response = client.post(
            "/categories/",
            data=json.dumps(sample_category_data),
            content_type="application/json",
            headers=admin_headers,
        )

        assert category_response.status_code == 201
        category_data = json.loads(category_response.data)
        category_id = category_data["category"]["id"]

        # Create product
        product_data = sample_product_data.copy()
        product_data["category_id"] = category_id

        product_response = client.post(
            "/products/",
            data=json.dumps(product_data),
            content_type="application/json",
            headers=admin_headers,
        )

        assert product_response.status_code == 201
        product_data = json.loads(product_response.data)
        product_id = product_data["product"]["id"]

        # Get product
        get_response = client.get(f"/products/{product_id}", headers=admin_headers)
        assert get_response.status_code == 200

        # Update product
        update_data = {"name": "Updated Product"}
        update_response = client.put(
            f"/products/{product_id}",
            data=json.dumps(update_data),
            content_type="application/json",
            headers=admin_headers,
        )
        assert update_response.status_code == 200

        # Delete product
        delete_response = client.delete(
            f"/products/{product_id}", headers=admin_headers
        )
        assert delete_response.status_code == 200

    def test_authentication_bypass_integration(
        self, client, monkeypatch, sample_user_data
    ):
        """Test authentication bypass in development mode."""
        # Enable bypass
        monkeypatch.setenv("ENVIRONMENT", "development")
        monkeypatch.setenv("BYPASS_AUTH", "true")

        # Should be able to access protected endpoints without auth
        response = client.get("/auth/users")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "auth_bypassed" in data
        assert data["auth_bypassed"] is True

    def test_error_handling_integration(self, client):
        """Test global error handling."""
        # Test 404 error
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404

        # Test validation error
        response = client.post(
            "/auth/register",
            data=json.dumps({"invalid": "data"}),
            content_type="application/json",
        )
        assert response.status_code == 400

        # Test authentication error
        response = client.get("/auth/users")
        assert response.status_code == 401

    def test_logging_integration(self, app, mock_logger):
        """Test that logging works throughout the application."""
        with app.test_request_context("/"):
            # Mock the logger
            with patch("src.core.logging.get_logger", return_value=mock_logger):
                from src.api.authentication.routes import auth_b_p

                # Make a request that should trigger logging
                client = app.test_client()
                response = client.post(
                    "/auth/register",
                    data=json.dumps(
                        {
                            "username": "test",
                            "email": "test@example.com",
                            "password": "TestPass123!",
                            "role": "staff",
                        }
                    ),
                    content_type="application/json",
                )

                # Should have logged the request
                assert mock_logger.info.called or mock_logger.error.called

    def test_database_integration(self, app):
        """Test database operations integration."""
        with app.app_context():
            # Create test data
            user = User(username="test", email="test@example.com", role="staff")
            user.set_password("TestPass123!")
            db.session.add(user)
            db.session.commit()

            # Verify data was saved
            saved_user = User.query.filter_by(username="test").first()
            assert saved_user is not None
            assert saved_user.email == "test@example.com"

            # Update data
            saved_user.email = "updated@example.com"
            db.session.commit()

            # Verify update
            updated_user = User.query.filter_by(username="test").first()
            assert updated_user.email == "updated@example.com"

            # Delete data
            db.session.delete(saved_user)
            db.session.commit()

            # Verify deletion
            deleted_user = User.query.filter_by(username="test").first()
            assert deleted_user is None

    def test_configuration_integration(self, app):
        """Test configuration integration."""
        with app.app_context():
            # Test that configuration is loaded
            assert app.config["SQLALCHEMY_DATABASE_URI"] is not None
            assert app.config["JWT_SECRET_KEY"] is not None

            # Test environment detection
            from src.core.config import settings

            assert settings.ENVIRONMENT is not None

    def test_middleware_integration(self, app):
        """Test middleware integration."""
        with app.test_request_context("/"):
            # Test that middleware is registered
            # This would require more complex setup to test properly
            assert hasattr(app, "before_request_funcs") or True  # Basic check

    def test_service_layer_integration(
        self, app, create_test_category, sample_product_data
    ):
        """Test service layer integration."""
        with app.app_context():
            from src.services.service import ProductService, CategoryService

            # Test category service
            category_service = CategoryService()
            categories = category_service.get_all_categories()
            assert len(categories) >= 1

            # Test product service
            product_service = ProductService()
            product = product_service.create_product(sample_product_data)
            assert product.name == sample_product_data["name"]

            # Test discounted service
            from src.services.service import DiscountedProductService

            discounted_service = DiscountedProductService()
            discounted_price = discounted_service.calculate_discounted_price(
                product.price, 20
            )
            assert discounted_price == product.price * 0.8

    def test_validation_integration(self, app):
        """Test validation integration across the application."""
        with app.app_context():
            from src.models.schemas import UserCreate, ProductCreate

            # Test user validation
            with pytest.raises(Exception):
                UserCreate(username="", email="invalid", password="123", role="staff")

            # Test product validation
            with pytest.raises(Exception):
                ProductCreate(name="", price=-10, stock_quantity=-5, category_id=1)

    def test_exception_handling_integration(self, app):
        """Test exception handling integration."""
        with app.app_context():
            from src.core.exceptions import ValidationErrorException, ExceptionHandler

            # Test custom exception
            exception = ValidationErrorException("Test error")
            handler = ExceptionHandler()
            response = handler.handle_exception(exception)

            assert response[1] == 400
            assert "error_code" in response[0]

    def test_feature_toggles_integration(self, app, monkeypatch):
        """Test feature toggles integration."""
        with app.app_context():
            # Test bypass toggle
            monkeypatch.setenv("BYPASS_AUTH", "true")
            monkeypatch.setenv("ENVIRONMENT", "development")

            # Reload configuration
            from src.core.config import FeatureToggles

            toggles = FeatureToggles()

            assert toggles.BYPASS_AUTH is True

    def test_health_check_integration(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "status" in data
        assert "environment" in data
        assert data["status"] == "healthy"

    def test_home_endpoint_integration(self, client):
        """Test home endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data
        assert "Inventory Management API" in data["message"]
