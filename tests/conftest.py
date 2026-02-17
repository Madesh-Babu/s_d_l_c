import pytest
from src.api import create_app, db
from src.core.config import TestingConfig
from flask_jwt_extended import create_access_token


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        print("aaaa", app.config["SQLALCHEMY_DATABASE_URI"])
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_headers(app):
    """Simulate an admin user token"""
    with app.app_context():
        token = create_access_token(
            identity="1", additional_claims={"role": "admin"}  # must be string
        )
        return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def customer_headers(app):
    """Simulate a staff user token"""
    with app.app_context():
        token = create_access_token(identity="2", additional_claims={"role": "staff"})
        return {"Authorization": f"Bearer {token}"}
