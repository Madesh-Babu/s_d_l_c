"""
Authentication Routes Tests

This module contains comprehensive tests for authentication endpoints
including user registration, login, and user management operations.
"""

import pytest
import json
from src.models.models import User


class TestAuthRoutes:
    """Test authentication endpoints."""

    def test_register_user_success(self, client, sample_user_data):
        """Test successful user registration."""
        response = client.post(
            "/auth/register",
            data=json.dumps(sample_user_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["message"] == "User registered successfully"
        assert "user" in data
        assert data["user"]["username"] == sample_user_data["username"]
        assert data["user"]["email"] == sample_user_data["email"]
        assert "password" not in data["user"]  # Password should not be returned

    def test_register_user_duplicate_email(
        self, client, create_test_user, sample_user_data
    ):
        """Test registration with duplicate email fails."""
        response = client.post(
            "/auth/register",
            data=json.dumps(sample_user_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_register_user_invalid_email(self, client, sample_user_data):
        """Test registration with invalid email fails."""
        sample_user_data["email"] = "invalid-email"
        response = client.post(
            "/auth/register",
            data=json.dumps(sample_user_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_register_user_weak_password(self, client, sample_user_data):
        """Test registration with weak password fails."""
        sample_user_data["password"] = "123"
        response = client.post(
            "/auth/register",
            data=json.dumps(sample_user_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_login_success(self, client, create_test_user, sample_user_data):
        """Test successful user login."""
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"],
        }

        response = client.post(
            "/auth/login", data=json.dumps(login_data), content_type="application/json"
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "access_token" in data
        assert data["user"]["username"] == sample_user_data["username"]

    def test_login_invalid_credentials(self, client, create_test_user):
        """Test login with invalid credentials fails."""
        login_data = {"username": "wronguser", "password": "wrongpass"}

        response = client.post(
            "/auth/login", data=json.dumps(login_data), content_type="application/json"
        )

        assert response.status_code == 401
        data = json.loads(response.data)
        assert "error" in data

    def test_login_missing_fields(self, client):
        """Test login with missing fields fails."""
        login_data = {"username": "testuser"}

        response = client.post(
            "/auth/login", data=json.dumps(login_data), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_dev_login_in_development(self, client, monkeypatch):
        """Test development login endpoint in development mode."""
        # Mock development environment
        monkeypatch.setenv("ENVIRONMENT", "development")
        monkeypatch.setenv("BYPASS_AUTH", "true")

        response = client.post("/auth/dev-login")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "access_token" in data
        assert data["bypass_enabled"] is True
        assert data["environment"] == "development"

    def test_dev_login_in_production(self, client, monkeypatch):
        """Test development login endpoint fails in production."""
        # Mock production environment
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("BYPASS_AUTH", "false")

        response = client.post("/auth/dev-login")

        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data

    def test_get_users_unauthorized(self, client):
        """Test getting users without authentication fails."""
        response = client.get("/auth/users")

        assert response.status_code == 401
        data = json.loads(response.data)
        assert "error" in data

    def test_get_users_authorized(self, client, admin_headers, create_test_user):
        """Test getting users with authentication succeeds."""
        response = client.get("/auth/users", headers=admin_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list) or "users" in data
        if isinstance(data, dict) and "users" in data:
            assert len(data["users"]) >= 1

    def test_get_user_by_id_success(self, client, admin_headers, create_test_user):
        """Test getting specific user by ID succeeds."""
        response = client.get(f"/auth/{create_test_user.id}", headers=admin_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["id"] == create_test_user.id
        assert data["username"] == create_test_user.username

    def test_get_user_by_id_not_found(self, client, admin_headers):
        """Test getting non-existent user returns 404."""
        response = client.get("/auth/999", headers=admin_headers)

        assert response.status_code == 404

    def test_update_user_success(self, client, admin_headers, create_test_user):
        """Test updating user succeeds."""
        update_data = {"username": "updateduser", "email": "updated@example.com"}

        response = client.put(
            f"/auth/{create_test_user.id}",
            data=json.dumps(update_data),
            content_type="application/json",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["user"]["username"] == "updateduser"
        assert data["user"]["email"] == "updated@example.com"

    def test_update_user_unauthorized(self, client, create_test_user):
        """Test updating user without authentication fails."""
        update_data = {"username": "updateduser"}

        response = client.put(
            f"/auth/{create_test_user.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 401

    def test_delete_user_success(self, client, admin_headers, create_test_user):
        """Test deleting user succeeds."""
        response = client.delete(f"/auth/{create_test_user.id}", headers=admin_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "deleted successfully" in data["message"]

    def test_delete_user_unauthorized(self, client, create_test_user):
        """Test deleting user without authentication fails."""
        response = client.delete(f"/auth/{create_test_user.id}")

        assert response.status_code == 401

    def test_change_password_success(self, client, staff_headers, create_test_user):
        """Test changing password succeeds."""
        password_data = {
            "current_password": "TestPass123!",
            "new_password": "NewPass123!",
            "confirm_password": "NewPass123!",
        }

        response = client.post(
            "/auth/change-password",
            data=json.dumps(password_data),
            content_type="application/json",
            headers=staff_headers,
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Password changed successfully"

    def test_change_password_wrong_current(
        self, client, staff_headers, create_test_user
    ):
        """Test changing password with wrong current password fails."""
        password_data = {
            "current_password": "WrongPass123!",
            "new_password": "NewPass123!",
            "confirm_password": "NewPass123!",
        }

        response = client.post(
            "/auth/change-password",
            data=json.dumps(password_data),
            content_type="application/json",
            headers=staff_headers,
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_change_password_mismatch(self, client, staff_headers, create_test_user):
        """Test changing password with mismatched passwords fails."""
        password_data = {
            "current_password": "TestPass123!",
            "new_password": "NewPass123!",
            "confirm_password": "DifferentPass123!",
        }

        response = client.post(
            "/auth/change-password",
            data=json.dumps(password_data),
            content_type="application/json",
            headers=staff_headers,
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data


class TestAuthBypass:
    """Test authentication bypass functionality."""

    def test_bypass_enabled_in_development(self, client, monkeypatch):
        """Test that bypass works in development environment."""
        # Enable bypass
        monkeypatch.setenv("ENVIRONMENT", "development")
        monkeypatch.setenv("BYPASS_AUTH", "true")

        response = client.get("/auth/users")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "auth_bypassed" in data
        assert data["auth_bypassed"] is True

    def test_bypass_disabled_in_production(self, client, monkeypatch):
        """Test that bypass is disabled in production."""
        # Disable bypass
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("BYPASS_AUTH", "false")

        response = client.get("/auth/users")

        assert response.status_code == 401
        data = json.loads(response.data)
        assert "error" in data
