import os
from typing import Optional

class Config:
    """Base configuration class."""
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///inventory.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "a1b2c3d4")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600"))
    
    # Application Configuration
    APP_NAME = os.getenv("APP_NAME", "Inventory Management API")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT = int(os.getenv("APP_PORT", "5000"))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_ENVIRONMENT = os.getenv("LOG_ENVIRONMENT", "development")
    LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/inventory_api.log")


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = "INFO"


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL", "sqlite:///test_inventory.db"
    )
    LOG_LEVEL = "DEBUG"


class Settings:
    """Settings class for environment-based configuration."""
    
    def __init__(self):
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_ENVIRONMENT = os.getenv("LOG_ENVIRONMENT", "development")
        self.LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/inventory_api.log")
        
        # Database settings
        self.DATABASE_URL = os.getenv(
            "DATABASE_URL", "sqlite:///inventory.db"
        )
        
        # JWT settings
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "a1b2c3d4")
        self.JWT_ACCESS_TOKEN_EXPIRES = int(
            os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600")
        )
        
        # Application settings
        self.APP_NAME = os.getenv("APP_NAME", "Inventory Management API")
        self.APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
        self.APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
        self.APP_PORT = int(os.getenv("APP_PORT", "5000"))
    
    @property
    def config_class(self):
        """Get the appropriate configuration class based on environment."""
        if self.ENVIRONMENT == "production":
            return ProductionConfig
        elif self.ENVIRONMENT == "testing":
            return TestingConfig
        else:
            return DevelopmentConfig


# Configuration mapping
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}