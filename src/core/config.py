import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv('.env.local')

def get_database_uri():
    """Get PostgreSQL database URI from environment variables with validation."""
    
    # PostgreSQL Configuration - Environment variables required (no defaults for security)
    PG_USER = os.getenv("PG_USER")
    PG_PASSWORD = os.getenv("PG_PASSWORD")
    PG_HOST = os.getenv("PG_HOST")
    PG_PORT = os.getenv("PG_PORT")
    PG_DB = os.getenv("PG_DB")
    
    # Validate required environment variables
    required_vars = {
        'PG_USER': PG_USER,
        'PG_PASSWORD': PG_PASSWORD,
        'PG_HOST': PG_HOST,
        'PG_PORT': PG_PORT,
        'PG_DB': PG_DB
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        raise ValueError(
            f"Missing required PostgreSQL environment variables: {', '.join(missing_vars)}. "
            "Please set these in your .env.local file."
        )
    
    # Database URI constructed from individual variables
    return (
        f"postgresql://{PG_USER}:{PG_PASSWORD}"
        f"@{PG_HOST}:{PG_PORT}/{PG_DB}"
    )

class Config:
    """Base configuration class."""
    
    # Database configuration using function
    SQLALCHEMY_DATABASE_URI = get_database_uri()
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
    # LOG_LEVEL inherited from environment variable


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # LOG_LEVEL inherited from environment variable


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL", "sqlite:///test_inventory.db"
    )
    # LOG_LEVEL inherited from environment variable


class Settings:
    """Settings class for environment-based configuration."""
    
    def __init__(self):
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_ENVIRONMENT = os.getenv("LOG_ENVIRONMENT", "development")
        self.LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/inventory_api.log")
        
        # PostgreSQL settings from individual environment variables (required - no defaults)
        self.PG_USER = os.getenv("PG_USER")
        self.PG_PASSWORD = os.getenv("PG_PASSWORD")
        self.PG_HOST = os.getenv("PG_HOST")
        self.PG_PORT = os.getenv("PG_PORT")
        self.PG_DB = os.getenv("PG_DB")
        
        # Validate required PostgreSQL environment variables
        self._validate_postgres_config()
        
        # Database URI constructed from individual variables
        self.PG_URI = (
            f"postgresql://{self.PG_USER}:{self.PG_PASSWORD}"
            f"@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"
        )
        
        self.DATABASE_URL = self.PG_URI
        
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
    
    def _validate_postgres_config(self):
        """Validate that all required PostgreSQL environment variables are set."""
        required_vars = {
            'PG_USER': self.PG_USER,
            'PG_PASSWORD': self.PG_PASSWORD,
            'PG_HOST': self.PG_HOST,
            'PG_PORT': self.PG_PORT,
            'PG_DB': self.PG_DB
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        if missing_vars:
            raise ValueError(
                f"Missing required PostgreSQL environment variables: {', '.join(missing_vars)}. "
                "Please set these in your .env.local file."
            )
    
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
