import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgresql@127.0.0.1:5432/Inventory_Management_API"
    )

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://postgres:postgresql@127.0.0.1:5432/Inventory_Management_test"
    )
    