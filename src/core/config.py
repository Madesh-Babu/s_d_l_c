"""
Environment-based Configuration Management with Feature Toggles

This module provides robust configuration management using Pydantic BaseSettings
with environment-specific settings and feature toggle support.
"""

import os
from typing import Optional, Dict, Any, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class FeatureToggles(BaseSettings):
    """Feature toggle configuration for different environments."""
    
    model_config = SettingsConfigDict(
        env_file='.env.local',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )
    
    # Authentication Features
    BYPASS_AUTH: bool = Field(False, description="Bypass authentication in local development")
    ENABLE_JWT: bool = Field(True, description="Enable JWT authentication")
    ENABLE_ROLE_BASED_ACCESS: bool = Field(True, description="Enable role-based access control")
    
    # API Features
    ENABLE_RATE_LIMITING: bool = Field(True, description="Enable API rate limiting")
    ENABLE_CORS: bool = Field(True, description="Enable CORS headers")
    ENABLE_REQUEST_LOGGING: bool = Field(True, description="Enable detailed request logging")
    
    # Development Features
    ENABLE_SWAGGER_DOCS: bool = Field(True, description="Enable Swagger documentation")
    
    # Security Features
    ENABLE_SECURITY_HEADERS: bool = Field(True, description="Enable security headers")
    ENABLE_INPUT_VALIDATION: bool = Field(True, description="Enable strict input validation")
    
    # Monitoring Features
    ENABLE_HEALTH_CHECKS: bool = Field(True, description="Enable health check endpoints")
    
    @field_validator("BYPASS_AUTH")
    @classmethod
    def validate_bypass_auth(cls, v, info):
        """Ensure auth bypass is only enabled in development."""
        # Get environment from context or fallback to os.getenv
        env = None
        if hasattr(info, 'context') and info.context:
            env = info.context.get('ENVIRONMENT')
        if not env:
            env = os.getenv('ENVIRONMENT', 'development')
        
        if v and env not in ['development', 'local', 'dev']:
            raise ValueError("Authentication bypass can only be enabled in development environment")
        return v
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled."""
        return getattr(self, feature_name.upper(), False)
    
    def get_enabled_features(self) -> List[str]:
        """Get list of all enabled features."""
        enabled = []
        for field_name, field_value in self.__dict__.items():
            if field_value is True:
                enabled.append(field_name)
        return enabled


class EnvironmentConfig(BaseSettings):
    """Base environment configuration."""
    
    model_config = SettingsConfigDict(
        env_file='.env.local',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )
    
    # Environment Settings
    ENVIRONMENT: str = Field('development', description="Application environment")
    FLASK_ENV: str = Field('development', description="Flask environment")
    FLASK_DEBUG: bool = Field(False, description="Flask debug mode")
    
    # Database Configuration
    PG_USER: str = Field(..., description="PostgreSQL username")
    PG_PASSWORD: str = Field(..., description="PostgreSQL password")
    PG_HOST: str = Field(..., description="PostgreSQL host")
    PG_PORT: int = Field(5432, description="PostgreSQL port")
    PG_DB: str = Field(..., description="PostgreSQL database name")
    
    # JWT Configuration
    JWT_SECRET_KEY: str = Field(..., description="JWT secret key")
    JWT_ACCESS_TOKEN_EXPIRES: int = Field(3600, description="JWT access token expiration in seconds")
    JWT_ALGORITHM: str = Field("HS256", description="JWT algorithm")
    
    # Logging Configuration
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    LOG_ENVIRONMENT: str = Field("development", description="Logging environment")
    LOG_FILE_PATH: str = Field("logs/inventory_api.log", description="Log file path")
    
    # Feature Toggles
    feature_toggles: FeatureToggles = Field(default_factory=FeatureToggles)
    
    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v):
        """Validate JWT secret key length."""
        if len(v) < 8:
            raise ValueError("JWT secret key must be at least 8 characters long")
        return v
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v.upper()
    
    def get_database_uri(self) -> str:
        """Get database connection URI."""
        return f"postgresql://{self.PG_USER}:{self.PG_PASSWORD}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() in ['development', 'local', 'dev']
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() in ['production', 'prod']
    
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.ENVIRONMENT.lower() in ['testing', 'test']
    
    def get_environment_config(self) -> Dict[str, Any]:
        """Get environment-specific configuration."""
        base_config = {
            "ENVIRONMENT": self.ENVIRONMENT,
            "DEBUG": self.FLASK_DEBUG,
            "DATABASE_URI": self.get_database_uri(),
            "JWT_SECRET_KEY": self.JWT_SECRET_KEY,
            "JWT_ACCESS_TOKEN_EXPIRES": self.JWT_ACCESS_TOKEN_EXPIRES,
            "LOG_LEVEL": self.LOG_LEVEL,
            "LOG_FILE_PATH": self.LOG_FILE_PATH,
        }
        
        # Add environment-specific configurations
        if self.is_development():
            base_config.update({
                "SQLALCHEMY_DATABASE_URI": self.get_database_uri(),
                "SQLALCHEMY_TRACK_MODIFICATIONS": True,
                "SQLALCHEMY_ECHO": True,  # Show SQL queries in development
                "TESTING": True,
                "WTF_CSRF_ENABLED": False,  # Disable CSRF in development
            })
        elif self.is_production():
            base_config.update({
                "SQLALCHEMY_DATABASE_URI": self.get_database_uri(),
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
                "SQLALCHEMY_ECHO": False,
                "TESTING": False,
                "WTF_CSRF_ENABLED": True,
            })
        elif self.is_testing():
            base_config.update({
                "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # In-memory DB for testing
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
                "SQLALCHEMY_ECHO": False,
                "TESTING": True,
                "WTF_CSRF_ENABLED": False,
            })
        
        return base_config


class DevelopmentConfig(EnvironmentConfig):
    """Development environment configuration."""
    
    FLASK_DEBUG: bool = Field(True, description="Flask debug mode in development")
    LOG_LEVEL: str = Field("DEBUG", description="Debug logging in development")
    
    # Development-specific feature toggles
    feature_toggles: FeatureToggles = Field(default_factory=lambda: FeatureToggles(
        BYPASS_AUTH=True,  # Enable auth bypass in development
        ENABLE_RATE_LIMITING=False,  # Disable rate limiting in dev
    ))


class ProductionConfig(EnvironmentConfig):
    """Production environment configuration."""
    
    FLASK_DEBUG: bool = Field(False, description="Flask debug mode disabled in production")
    LOG_LEVEL: str = Field("WARNING", description="Warning level logging in production")
    
    # Production-specific feature toggles
    feature_toggles: FeatureToggles = Field(default_factory=lambda: FeatureToggles(
        ENABLE_RATE_LIMITING=True,  # Enable rate limiting in production
    ))


class TestingConfig(EnvironmentConfig):
    """Testing environment configuration."""
    
    FLASK_DEBUG: bool = Field(False, description="Flask debug mode disabled in testing")
    LOG_LEVEL: str = Field("ERROR", description="Error logging in testing")
    
    # Testing-specific feature toggles
    feature_toggles: FeatureToggles = Field(default_factory=lambda: FeatureToggles(
        ENABLE_RATE_LIMITING=False,  # Disable rate limiting in tests
    ))


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'dev': DevelopmentConfig,
    'local': DevelopmentConfig,
    'production': ProductionConfig,
    'prod': ProductionConfig,
    'testing': TestingConfig,
    'test': TestingConfig,
}

# Global settings instance
settings = EnvironmentConfig()

# Legacy compatibility classes
class Config:
    """Legacy Config class for backward compatibility."""
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = "dev-key"
    
    # Logging Configuration
    LOG_LEVEL = settings.LOG_LEVEL
    LOG_ENVIRONMENT = settings.LOG_ENVIRONMENT
    LOG_FILE_PATH = settings.LOG_FILE_PATH


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL", "sqlite:///test_inventory.db"
    )


# Configuration mapping
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}


if __name__ == "__main__":
    # Test configuration
    print("🔧 Testing Pydantic Configuration")
    print("=" * 50)
    
    try:
        print(f"✅ Configuration loaded successfully")
        print(f"🗄️ Database: {settings.PG_HOST}:{settings.PG_PORT}/{settings.PG_DB}")
        print(f"🔐 JWT Algorithm: {settings.JWT_ALGORITHM}")
        print(f"📝 Log Level: {settings.LOG_LEVEL}")
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        raise