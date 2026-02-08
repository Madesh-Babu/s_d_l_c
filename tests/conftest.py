import pytest
import os
import sys

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.api import create_app, db
from src.core.config import config
from flask_jwt_extended import create_access_token


@pytest.fixture
def app():
    # Set environment to testing for pytest
    os.environ['ENVIRONMENT'] = 'testing'
    
    app = create_app('testing')
    with app.app_context():
        print("Database URI:", app.config.get("SQLALCHEMY_DATABASE_URI"))
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
            identity="1",  # must be string
            additional_claims={"role": "admin"}
        )
        return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def customer_headers(app):
    """Simulate a staff user token"""
    with app.app_context():
        token = create_access_token(
            identity="2",
            additional_claims={"role": "staff"}
        )
        return {"Authorization": f"Bearer {token}"}
