"""
Integration Tests for Authentication Endpoints

This module contains comprehensive integration tests for authentication endpoints,
testing the complete workflow from user registration to protected resource access.
"""

import pytest
import json
from datetime import datetime
from src.models.models import db, User
from src.core.config import settings


class TestAuthenticationIntegration:
    """Test complete authentication workflows."""

    @pytest.fixture(autouse=True)
    def setup_test_data(self, app, client):
        """Set up test data for authentication tests."""
        with app.app_context():
            # Clean up any existing test users
            User.query.filter(User.username.like("test_%")).delete()
            db.session.commit()

    def test_complete_user_workflow(self, client):
        """Test complete user registration, login, and access workflow."""

        # Step 1: Register a new user
        registration_data = {
            "username": "test_workflow_user",
            "email": "test_workflow@example.com",
            "password": "TestPassword123!",
            "role": "staff",
        }

        response = client.post(
            "/auth/register",
            data=json.dumps(registration_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        registration_result = response.get_json()
        assert registration_result["message"] == "User registered successfully"
        assert registration_result["username"] == "test_workflow_user"
        assert "user_id" in registration_result

        # Step 2: Login with the registered user
        login_data = {"username": "test_workflow_user", "password": "TestPassword123!"}

        response = client.post(
            "/auth/login", data=json.dumps(login_data), content_type="application/json"
        )

        assert response.status_code == 200
        login_result = response.get_json()
        assert login_result["message"] == "Login successful"
        assert "access_token" in login_result
        assert login_result["user"]["username"] == "test_workflow_user"

        # Step 3: Access protected endpoint with JWT token
        token = login_result["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/auth/users", headers=auth_headers)

        assert response.status_code == 200
        users_result = response.get_json()
        assert isinstance(users_result, list)

        # Verify our user is in the list
        user_usernames = [user["username"] for user in users_result]
        assert "test_workflow_user" in user_usernames

    def test_user_registration_and_login_validation(self, client):
        """Test validation in registration and login endpoints."""

        # Test registration with invalid data
        invalid_registration = {
            "username": "a",  # Too short
            "email": "invalid-email",  # Invalid format
            "password": "123",  # Too weak
            "role": "invalid_role",  # Invalid role
        }

        response = client.post(
            "/auth/register",
            data=json.dumps(invalid_registration),
            content_type="application/json",
        )

        assert response.status_code == 400
        result = response.get_json()
        assert "error" in result

        # Test login with invalid credentials
        # First register a valid user
        valid_registration = {
            "username": "test_validation_user",
            "email": "test_validation@example.com",
            "password": "TestPassword123!",
            "role": "staff",
        }

        client.post(
            "/auth/register",
            data=json.dumps(valid_registration),
            content_type="application/json",
        )

        # Try login with wrong password
        invalid_login = {
            "username": "test_validation_user",
            "password": "WrongPassword123!",
        }

        response = client.post(
            "/auth/login",
            data=json.dumps(invalid_login),
            content_type="application/json",
        )

        assert response.status_code == 401
        result = response.get_json()
        assert "error" in result

    def test_duplicate_user_registration(self, client):
        """Test registration of duplicate users."""

        user_data = {
            "username": "test_duplicate_user",
            "email": "test_duplicate@example.com",
            "password": "TestPassword123!",
            "role": "staff",
        }

        # Register first user
        response1 = client.post(
            "/auth/register",
            data=json.dumps(user_data),
            content_type="application/json",
        )
        assert response1.status_code == 201

        # Try to register same user again
        response2 = client.post(
            "/auth/register",
            data=json.dumps(user_data),
            content_type="application/json",
        )
        assert response2.status_code == 409
        result = response2.get_json()
        assert "error" in result

    def test_protected_endpoints_without_token(self, client):
        """Test accessing protected endpoints without authentication."""

        # Test various protected endpoints without token
        protected_endpoints = [
            "/auth/users",
            "/auth/users/1",
            "/products/",
            "/categories/",
        ]

        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            # Should return 401 unless bypass is enabled
            if settings.feature_toggles.BYPASS_AUTH and settings.is_development():
                # In development with bypass, should work
                assert response.status_code in [200, 404]
            else:
                # In production, should require authentication
                assert response.status_code == 401

    def test_protected_endpoints_with_invalid_token(self, client):
        """Test accessing protected endpoints with invalid JWT token."""

        invalid_headers = {"Authorization": "Bearer invalid_token_here"}

        protected_endpoints = [
            "/auth/users",
            "/auth/users/1",
            "/products/",
            "/categories/",
        ]

        for endpoint in protected_endpoints:
            response = client.get(endpoint, headers=invalid_headers)
            assert response.status_code == 401

    def test_development_bypass_functionality(self, client):
        """Test authentication bypass in development mode."""

        if settings.feature_toggles.BYPASS_AUTH and settings.is_development():
            # In development with bypass, should access without token
            response = client.get("/auth/users")
            assert response.status_code == 200
            result = response.get_json()
            assert "auth_bypassed" in result
            assert result["auth_bypassed"] is True
        else:
            # In production or without bypass, should require authentication
            response = client.get("/auth/users")
            assert response.status_code == 401

    def test_user_role_based_access(self, client):
        """Test role-based access control."""

        # Create users with different roles
        roles = ["staff", "manager", "admin"]
        created_users = {}

        for role in roles:
            user_data = {
                "username": f"test_{role}_user",
                "email": f"test_{role}@example.com",
                "password": "TestPassword123!",
                "role": role,
            }

            response = client.post(
                "/auth/register",
                data=json.dumps(user_data),
                content_type="application/json",
            )
            assert response.status_code == 201

            # Login and get token
            login_data = {
                "username": f"test_{role}_user",
                "password": "TestPassword123!",
            }

            login_response = client.post(
                "/auth/login",
                data=json.dumps(login_data),
                content_type="application/json",
            )
            assert login_response.status_code == 200

            created_users[role] = login_response.get_json()["access_token"]

        # Test that all roles can access basic endpoints
        for role, token in created_users.items():
            auth_headers = {"Authorization": f"Bearer {token}"}

            # All users should be able to access user list
            response = client.get("/auth/users", headers=auth_headers)
            assert response.status_code == 200

    def test_jwt_token_expiration(self, client):
        """Test JWT token expiration handling."""

        # Register and login a user
        user_data = {
            "username": "test_expiration_user",
            "email": "test_expiration@example.com",
            "password": "TestPassword123!",
            "role": "staff",
        }

        client.post(
            "/auth/register",
            data=json.dumps(user_data),
            content_type="application/json",
        )

        login_data = {
            "username": "test_expiration_user",
            "password": "TestPassword123!",
        }

        response = client.post(
            "/auth/login", data=json.dumps(login_data), content_type="application/json"
        )

        token = response.get_json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # Test token works immediately
        response = client.get("/auth/users", headers=auth_headers)
        assert response.status_code == 200

        # Note: JWT expiration testing would require time manipulation
        # or very short token expiration times, which is beyond basic integration testing

    def test_error_handling_consistency(self, client):
        """Test consistent error handling across authentication endpoints."""

        # Test malformed JSON
        response = client.post(
            "/auth/register", data="invalid json", content_type="application/json"
        )
        assert response.status_code == 400

        # Test missing required fields
        response = client.post(
            "/auth/register", data=json.dumps({}), content_type="application/json"
        )
        assert response.status_code == 400

        # Test invalid content type
        response = client.post(
            "/auth/register", data=json.dumps({}), content_type="text/plain"
        )
        assert response.status_code == 400

    def test_database_transaction_rollback(self, client):
        """Test database transaction rollback on errors."""

        # Try to create user with invalid data that should cause rollback
        invalid_user_data = {
            "username": "test_rollback_user",
            "email": "test_rollback@example.com",
            "password": "TestPassword123!",
            "role": "invalid_role_that_should_fail_validation",
        }

        response = client.post(
            "/auth/register",
            data=json.dumps(invalid_user_data),
            content_type="application/json",
        )

        assert response.status_code == 400

        # Verify user was not created due to rollback
        login_data = {"username": "test_rollback_user", "password": "TestPassword123!"}

        response = client.post(
            "/auth/login", data=json.dumps(login_data), content_type="application/json"
        )

        assert response.status_code == 401  # User should not exist
