import pytest


def test_unauthenticated_request_rejected(client):
    """No token should result in 401 Unauthorized"""
    res = client.get("/products/")
    assert res.status_code == 401
    assert "Missing Authorization Header" in res.get_json()["msg"]


def test_unauthorized_role_cannot_add_product(client, customer_headers):
    """Customer (staff) role should not add products (403 Forbidden)"""
    res = client.post(
        "/products/",
        json={"name": "Unauthorized Item", "price": 99, "stock": 5},
        headers=customer_headers
    )
    assert res.status_code in (401, 403), f"Unexpected status {res.status_code}: {res.get_json()}"


def test_admin_can_add_product(client, admin_headers):
    """Admin role should successfully add a product"""
    res = client.post(
        "/products/",
        json={"name": "Authorized Product", "price": 150, "stock": 3},
        headers=admin_headers
    )
    print("Admin add response:", res.get_json())  # Debug output
    assert res.status_code == 201, f"Unexpected status {res.status_code}: {res.get_json()}"
    data = res.get_json()
    assert data["product"]["name"] == "Authorized Product"


def test_unauthorized_delete_rejected(client, customer_headers):
    """Customer should not delete product"""
    res = client.delete("/products/delete", json={"id": 1}, headers=customer_headers)
    assert res.status_code in (401, 403), f"Unexpected status {res.status_code}: {res.get_json()}"


def test_no_token_delete_rejected(client):
    """Missing token should reject delete request"""
    res = client.delete("/products/delete", json={"id": 1})
    assert res.status_code == 401

