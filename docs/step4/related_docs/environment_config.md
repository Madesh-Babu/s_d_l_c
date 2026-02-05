# Environment-Based Configuration Management

## Overview

This document outlines the comprehensive environment-based configuration management system implemented throughout the application using Pydantic's BaseSettings for flexible, type-safe, and environment-aware configuration.

## Configuration Architecture

### 1. Configuration Hierarchy

#### Configuration Layers
```python
# src/core/config.py
from pydantic import BaseSettings, Field, validator
from typing import Optional, List, Dict, Any
import os

class ConfigurationHierarchy:
    """Configuration loading hierarchy"""
    
    # Priority order (highest to lowest):
    # 1. Environment variables
    # 2. .env.local file
    # 3. .env file
    # 4. Default values
    
    @staticmethod
    def load_configuration():
        """Load configuration with proper hierarchy"""
        # Load base configuration
        base_config = EnvironmentConfig()
        
        # Override with environment-specific configuration
        env_config = EnvironmentConfig.from_env()
        
        # Merge configurations
        merged_config = {**base_config.dict(), **env_config.dict()}
        
        return EnvironmentConfig(**merged_config)
```

### 2. Environment Detection

#### Environment Configuration
```python
# src/core/config.py
class EnvironmentDetector:
    """Environment detection utilities"""
    
    @staticmethod
    def get_environment() -> str:
        """Detect current environment"""
        return os.getenv('ENVIRONMENT', 'development').lower()
    
    @staticmethod
    def is_development() -> bool:
        """Check if running in development"""
        env = EnvironmentDetector.get_environment()
        return env in ['development', 'dev', 'local']
    
    @staticmethod
    def is_testing() -> bool:
        """Check if running in testing"""
        env = EnvironmentDetector.get_environment()
        return env in ['testing', 'test']
    
    @staticmethod
    def is_staging() -> bool:
        """Check if running in staging"""
        env = EnvironmentDetector.get_environment()
        return env in ['staging', 'stage']
    
    @staticmethod
    def is_production() -> bool:
        """Check if running in production"""
        env = EnvironmentDetector.get_environment()
        return env in ['production', 'prod']
    
    @staticmethod
    def get_config_file() -> str:
        """Get appropriate config file for environment"""
        env = EnvironmentDetector.get_environment()
        
        config_files = {
            'development': '.env.local',
            'testing': '.env.test',
            'staging': '.env.staging',
            'production': '.env'
        }
        
        return config_files.get(env, '.env')
```

## Configuration Models

### 1. Core Configuration

#### Main Configuration Class
```python
# src/core/config.py
class EnvironmentConfig(BaseSettings):
    """Main environment configuration"""
    
    # Basic Application Settings
    ENVIRONMENT: str = Field(default="development", description="Application environment")
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    HOST: str = Field(default="localhost", description="Application host")
    PORT: int = Field(default=5000, description="Application port")
    APP_NAME: str = Field(default="SDLC Inventory", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    
    # Security Settings
    SECRET_KEY: str = Field(default="dev-secret-key", description="Application secret key")
    JWT_SECRET_KEY: str = Field(default="jwt-secret-key", description="JWT secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="JWT token expiration")
    
    # Database Settings
    DATABASE_URL: str = Field(default="sqlite:///app.db", description="Database URL")
    DATABASE_POOL_SIZE: int = Field(default=10, description="Database pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, description="Database max overflow")
    DATABASE_POOL_TIMEOUT: int = Field(default=30, description="Database pool timeout")
    DATABASE_ECHO: bool = Field(default=False, description="Enable database query logging")
    
    # Logging Settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format")
    LOG_FILE: Optional[str] = Field(None, description="Log file path")
    LOG_ROTATION: str = Field(default="daily", description="Log rotation")
    LOG_RETENTION: int = Field(default=30, description="Log retention days")
    
    # API Settings
    API_PREFIX: str = Field(default="/api/v1", description="API prefix")
    API_TITLE: str = Field(default="SDLC Inventory API", description="API title")
    API_DESCRIPTION: str = Field(default="SDLC Inventory Management API", description="API description")
    
    # CORS Settings
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000"], description="CORS origins")
    CORS_METHODS: List[str] = Field(default=["GET", "POST", "PUT", "DELETE"], description="CORS methods")
    CORS_HEADERS: List[str] = Field(default=["Content-Type", "Authorization"], description="CORS headers")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Rate limit requests per window")
    RATE_LIMIT_WINDOW: int = Field(default=3600, description="Rate limit window in seconds")
    
    # Feature Toggles
    FEATURE_TOGGLES: Dict[str, bool] = Field(default_factory=dict, description="Feature toggles")
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True
        
    @validator('ENVIRONMENT')
    def validate_environment(cls, v):
        """Validate environment value"""
        valid_envs = ['development', 'testing', 'staging', 'production']
        if v.lower() not in valid_envs:
            raise ValueError(f"Environment must be one of: {', '.join(valid_envs)}")
        return v.lower()
    
    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v.upper()
    
    @validator('JWT_SECRET_KEY', 'SECRET_KEY')
    def validate_secret_keys(cls, v):
        """Validate secret key strength"""
        if len(v) < 32:
            raise ValueError("Secret keys must be at least 32 characters long")
        return v
    
    @validator('DATABASE_URL')
    def validate_database_url(cls, v):
        """Validate database URL format"""
        if not v.startswith(('postgresql://', 'mysql://', 'sqlite:///')):
            raise ValueError("Invalid database URL format")
        return v
```

### 2. Feature Toggles

#### Feature Toggle Configuration
```python
# src/core/config.py
class FeatureToggles(BaseSettings):
    """Feature toggle configuration"""
    
    # Authentication Features
    BYPASS_AUTH: bool = Field(default=False, description="Bypass authentication in development")
    ENABLE_JWT_AUTH: bool = Field(default=True, description="Enable JWT authentication")
    ENABLE_OAUTH: bool = Field(default=False, description="Enable OAuth authentication")
    ENABLE_TWO_FACTOR: bool = Field(default=False, description="Enable two-factor authentication")
    
    # API Features
    ENABLE_API_DOCS: bool = Field(default=True, description="Enable API documentation")
    ENABLE_SWAGGER_UI: bool = Field(default=True, description="Enable Swagger UI")
    ENABLE_REDOC: bool = Field(default=True, description="Enable ReDoc")
    
    # Security Features
    ENABLE_RATE_LIMITING: bool = Field(default=True, description="Enable rate limiting")
    ENABLE_CORS: bool = Field(default=True, description="Enable CORS")
    ENABLE_SECURITY_HEADERS: bool = Field(default=True, description="Enable security headers")
    ENABLE_REQUEST_LOGGING: bool = Field(default=True, description="Enable request logging")
    
    # Performance Features
    ENABLE_CACHING: bool = Field(default=False, description="Enable caching")
    ENABLE_COMPRESSION: bool = Field(default=True, description="Enable response compression")
    ENABLE_METRICS: bool = Field(default=False, description="Enable metrics collection")
    
    # Development Features
    ENABLE_DEBUG_TOOLBAR: bool = Field(default=False, description="Enable debug toolbar")
    ENABLE_PROFILING: bool = Field(default=False, description="Enable profiling")
    ENABLE_HOT_RELOAD: bool = Field(default=False, description="Enable hot reload")
    
    class Config:
        env_prefix = "FEATURE_"
        case_sensitive = True
    
    @validator('BYPASS_AUTH')
    def validate_bypass_auth(cls, v, info):
        """Ensure auth bypass is only enabled in development"""
        env = None
        if hasattr(info, 'context') and info.context:
            env = info.context.get('ENVIRONMENT')
        if not env:
            env = os.getenv('ENVIRONMENT', 'development')
        
        if v and env not in ['development', 'local', 'dev']:
            raise ValueError("Authentication bypass can only be enabled in development")
        return v
```

### 3. Environment-Specific Configurations

#### Development Configuration
```python
# src/core/config.py
class DevelopmentConfig(EnvironmentConfig):
    """Development environment configuration"""
    
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    DATABASE_ECHO: bool = True
    ENABLE_DEBUG_TOOLBAR: bool = True
    ENABLE_PROFILING: bool = True
    
    class Config:
        env_file = '.env.local'
        env_file_encoding = 'utf-8'

class TestingConfig(EnvironmentConfig):
    """Testing environment configuration"""
    
    TESTING: bool = True
    DATABASE_URL: str = "sqlite:///:memory:"
    LOG_LEVEL: str = "WARNING"
    RATE_LIMIT_ENABLED: bool = False
    ENABLE_REQUEST_LOGGING: bool = False
    
    class Config:
        env_file = '.env.test'
        env_file_encoding = 'utf-8'

class StagingConfig(EnvironmentConfig):
    """Staging environment configuration"""
    
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    ENABLE_DEBUG_TOOLBAR: bool = False
    ENABLE_PROFILING: bool = False
    ENABLE_METRICS: bool = True
    
    class Config:
        env_file = '.env.staging'
        env_file_encoding = 'utf-8'

class ProductionConfig(EnvironmentConfig):
    """Production environment configuration"""
    
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"
    ENABLE_DEBUG_TOOLBAR: bool = False
    ENABLE_PROFILING: bool = False
    ENABLE_METRICS: bool = True
    DATABASE_ECHO: bool = False
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
```

## Configuration Management

### 1. Configuration Factory

#### Configuration Factory Pattern
```python
# src/core/config_factory.py
from typing import Type
from src.core.config import (
    EnvironmentConfig, 
    DevelopmentConfig, 
    TestingConfig, 
    StagingConfig, 
    ProductionConfig,
    EnvironmentDetector
)

class ConfigurationFactory:
    """Factory for creating environment-specific configurations"""
    
    _config_map = {
        'development': DevelopmentConfig,
        'dev': DevelopmentConfig,
        'local': DevelopmentConfig,
        'testing': TestingConfig,
        'test': TestingConfig,
        'staging': StagingConfig,
        'stage': StagingConfig,
        'production': ProductionConfig,
        'prod': ProductionConfig
    }
    
    @classmethod
    def create_configuration(cls, environment: str = None) -> EnvironmentConfig:
        """Create configuration for specified environment"""
        if environment is None:
            environment = EnvironmentDetector.get_environment()
        
        config_class = cls._config_map.get(environment, EnvironmentConfig)
        return config_class()
    
    @classmethod
    def get_available_environments(cls) -> List[str]:
        """Get list of available environments"""
        return list(cls._config_map.keys())
    
    @classmethod
    def register_configuration(cls, environment: str, config_class: Type[EnvironmentConfig]):
        """Register new environment configuration"""
        cls._config_map[environment] = config_class
```

### 2. Configuration Manager

#### Configuration Manager
```python
# src/core/config_manager.py
from typing import Any, Dict, Optional
from src.core.config import EnvironmentConfig
from src.core.config_factory import ConfigurationFactory

class ConfigurationManager:
    """Configuration management utilities"""
    
    def __init__(self):
        self._config: Optional[EnvironmentConfig] = None
        self._config_cache: Dict[str, Any] = {}
    
    @property
    def config(self) -> EnvironmentConfig:
        """Get current configuration"""
        if self._config is None:
            self._config = ConfigurationFactory.create_configuration()
        return self._config
    
    def reload_configuration(self, environment: str = None) -> EnvironmentConfig:
        """Reload configuration"""
        self._config = ConfigurationFactory.create_configuration(environment)
        self._config_cache.clear()
        return self._config
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get configuration setting with caching"""
        if key in self._config_cache:
            return self._config_cache[key]
        
        value = getattr(self.config, key, default)
        self._config_cache[key] = value
        return value
    
    def get_database_url(self) -> str:
        """Get database URL"""
        return self.config.DATABASE_URL
    
    def get_jwt_settings(self) -> Dict[str, Any]:
        """Get JWT settings"""
        return {
            'secret_key': self.config.JWT_SECRET_KEY,
            'algorithm': self.config.JWT_ALGORITHM,
            'expire_minutes': self.config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            'level': self.config.LOG_LEVEL,
            'format': self.config.LOG_FORMAT,
            'file': self.config.LOG_FILE,
            'rotation': self.config.LOG_ROTATION,
            'retention': self.config.LOG_RETENTION
        }
    
    def get_cors_config(self) -> Dict[str, Any]:
        """Get CORS configuration"""
        return {
            'origins': self.config.CORS_ORIGINS,
            'methods': self.config.CORS_METHODS,
            'headers': self.config.CORS_HEADERS
        }
    
    def get_rate_limit_config(self) -> Dict[str, Any]:
        """Get rate limiting configuration"""
        return {
            'enabled': self.config.RATE_LIMIT_ENABLED,
            'requests': self.config.RATE_LIMIT_REQUESTS,
            'window': self.config.RATE_LIMIT_WINDOW
        }
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if feature is enabled"""
        feature_toggles = self.config.FEATURE_TOGGLES
        return feature_toggles.get(feature, False)
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all configuration settings"""
        return self.config.dict()
```

## Environment Files

### 1. Environment File Templates

#### .env.example
```bash
# Environment Configuration
ENVIRONMENT=development
DEBUG=True
HOST=localhost
PORT=5000
APP_NAME=SDLC Inventory
APP_VERSION=1.0.0

# Security
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/sdlc_inventory
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30
DATABASE_ECHO=False

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=logs/app.log
LOG_ROTATION=daily
LOG_RETENTION=30

# API
API_PREFIX=/api/v1
API_TITLE=SDLC Inventory API
API_DESCRIPTION=SDLC Inventory Management API

# CORS
CORS_ORIGINS=["http://localhost:3000"]
CORS_METHODS=["GET", "POST", "PUT", "DELETE"]
CORS_HEADERS=["Content-Type", "Authorization"]

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Feature Toggles
FEATURE_BYPASS_AUTH=False
FEATURE_ENABLE_JWT_AUTH=True
FEATURE_ENABLE_OAUTH=False
FEATURE_ENABLE_TWO_FACTOR=False
FEATURE_ENABLE_API_DOCS=True
FEATURE_ENABLE_SWAGGER_UI=True
FEATURE_ENABLE_REDOC=True
FEATURE_ENABLE_RATE_LIMITING=True
FEATURE_ENABLE_CORS=True
FEATURE_ENABLE_SECURITY_HEADERS=True
FEATURE_ENABLE_REQUEST_LOGGING=True
FEATURE_ENABLE_CACHING=False
FEATURE_ENABLE_COMPRESSION=True
FEATURE_ENABLE_METRICS=False
FEATURE_ENABLE_DEBUG_TOOLBAR=False
FEATURE_ENABLE_PROFILING=False
FEATURE_ENABLE_HOT_RELOAD=False
```

#### .env.local (Development)
```bash
# Development Environment
ENVIRONMENT=development
DEBUG=True
HOST=localhost
PORT=5000

# Development Database
DATABASE_URL=postgresql://dev_user:dev_pass@localhost:5432/sdlc_inventory_dev
DATABASE_ECHO=True

# Development Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=console

# Development Features
FEATURE_BYPASS_AUTH=True
FEATURE_ENABLE_DEBUG_TOOLBAR=True
FEATURE_ENABLE_PROFILING=True
FEATURE_ENABLE_HOT_RELOAD=True
```

#### .env.test (Testing)
```bash
# Testing Environment
ENVIRONMENT=testing
TESTING=True
DATABASE_URL=sqlite:///:memory:
LOG_LEVEL=WARNING
RATE_LIMIT_ENABLED=False
FEATURE_ENABLE_REQUEST_LOGGING=False
```

#### .env.staging (Staging)
```bash
# Staging Environment
ENVIRONMENT=staging
DEBUG=False
HOST=0.0.0.0
PORT=5000

# Staging Database
DATABASE_URL=postgresql://stage_user:stage_pass@db-staging:5432/sdlc_inventory_stage

# Staging Features
FEATURE_ENABLE_METRICS=True
FEATURE_ENABLE_CACHING=True
```

#### .env (Production)
```bash
# Production Environment
ENVIRONMENT=production
DEBUG=False
HOST=0.0.0.0
PORT=5000

# Production Database
DATABASE_URL=postgresql://prod_user:prod_pass@db-prod:5432/sdlc_inventory_prod

# Production Features
FEATURE_ENABLE_METRICS=True
FEATURE_ENABLE_CACHING=True
```

## Configuration Validation

### 1. Configuration Validators

#### Validation Utilities
```python
# src/core/config_validators.py
from typing import Any, List, Dict
from urllib.parse import urlparse
import re

class ConfigurationValidator:
    """Configuration validation utilities"""
    
    @staticmethod
    def validate_database_url(url: str) -> bool:
        """Validate database URL format"""
        try:
            parsed = urlparse(url)
            return parsed.scheme in ['postgresql', 'mysql', 'sqlite']
        except Exception:
            return False
    
    @staticmethod
    def validate_jwt_secret(secret: str) -> bool:
        """Validate JWT secret strength"""
        return len(secret) >= 32
    
    @staticmethod
    def validate_log_level(level: str) -> bool:
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        return level.upper() in valid_levels
    
    @staticmethod
    def validate_cors_origins(origins: List[str]) -> bool:
        """Validate CORS origins"""
        for origin in origins:
            if not origin.startswith(('http://', 'https://')):
                return False
        return True
    
    @staticmethod
    def validate_rate_limit_settings(requests: int, window: int) -> bool:
        """Validate rate limiting settings"""
        return requests > 0 and window > 0
    
    @staticmethod
    def validate_environment(env: str) -> bool:
        """Validate environment name"""
        valid_envs = ['development', 'testing', 'staging', 'production']
        return env.lower() in valid_envs
    
    @staticmethod
    def validate_feature_toggles(toggles: Dict[str, bool]) -> Dict[str, str]:
        """Validate feature toggles and return errors"""
        errors = {}
        
        # Check bypass auth in production
        if toggles.get('BYPASS_AUTH', False):
            env = os.getenv('ENVIRONMENT', 'development')
            if env not in ['development', 'local', 'dev']:
                errors['BYPASS_AUTH'] = "Cannot enable auth bypass in production"
        
        return errors
```

### 2. Configuration Testing

#### Configuration Tests
```python
# tests/unit/test_config_comprehensive.py
import pytest
import os
from unittest.mock import patch
from src.core.config import EnvironmentConfig, FeatureToggles
from src.core.config_factory import ConfigurationFactory
from src.core.config_manager import ConfigurationManager

class TestEnvironmentConfig:
    """Test environment configuration"""
    
    def test_default_configuration(self):
        """Test default configuration values"""
        config = EnvironmentConfig()
        
        assert config.ENVIRONMENT == "development"
        assert config.DEBUG is False
        assert config.HOST == "localhost"
        assert config.PORT == 5000
        assert config.LOG_LEVEL == "INFO"
    
    def test_environment_variable_override(self):
        """Test environment variable override"""
        with patch.dict(os.environ, {
            'ENVIRONMENT': 'production',
            'DEBUG': 'True',
            'PORT': '8000'
        }):
            config = EnvironmentConfig()
            assert config.ENVIRONMENT == "production"
            assert config.DEBUG is True
            assert config.PORT == 8000
    
    def test_invalid_environment(self):
        """Test invalid environment validation"""
        with pytest.raises(ValueError) as exc_info:
            EnvironmentConfig(ENVIRONMENT="invalid")
        
        assert "Environment must be one of" in str(exc_info.value)
    
    def test_invalid_log_level(self):
        """Test invalid log level validation"""
        with pytest.raises(ValueError) as exc_info:
            EnvironmentConfig(LOG_LEVEL="invalid")
        
        assert "Log level must be one of" in str(exc_info.value)
    
    def test_weak_secret_key(self):
        """Test weak secret key validation"""
        with pytest.raises(ValueError) as exc_info:
            EnvironmentConfig(JWT_SECRET_KEY="weak")
        
        assert "Secret keys must be at least 32 characters" in str(exc_info.value)

class TestFeatureToggles:
    """Test feature toggle configuration"""
    
    def test_default_feature_toggles(self):
        """Test default feature toggle values"""
        toggles = FeatureToggles()
        
        assert toggles.BYPASS_AUTH is False
        assert toggles.ENABLE_JWT_AUTH is True
        assert toggles.ENABLE_API_DOCS is True
    
    def test_feature_toggle_override(self):
        """Test feature toggle override"""
        with patch.dict(os.environ, {
            'FEATURE_BYPASS_AUTH': 'True',
            'FEATURE_ENABLE_JWT_AUTH': 'False'
        }):
            toggles = FeatureToggles()
            assert toggles.BYPASS_AUTH is True
            assert toggles.ENABLE_JWT_AUTH is False
    
    def test_bypass_auth_in_production(self):
        """Test bypass auth validation in production"""
        with patch.dict(os.environ, {
            'ENVIRONMENT': 'production',
            'FEATURE_BYPASS_AUTH': 'True'
        }):
            with pytest.raises(ValueError) as exc_info:
                FeatureToggles()
            
            assert "Authentication bypass can only be enabled in development" in str(exc_info.value)

class TestConfigurationFactory:
    """Test configuration factory"""
    
    def test_development_configuration(self):
        """Test development configuration creation"""
        config = ConfigurationFactory.create_configuration('development')
        assert config.DEBUG is True
        assert config.LOG_LEVEL == "DEBUG"
    
    def test_production_configuration(self):
        """Test production configuration creation"""
        config = ConfigurationFactory.create_configuration('production')
        assert config.DEBUG is False
        assert config.LOG_LEVEL == "WARNING"
    
    def test_unknown_environment(self):
        """Test unknown environment falls back to default"""
        config = ConfigurationFactory.create_configuration('unknown')
        assert isinstance(config, EnvironmentConfig)

class TestConfigurationManager:
    """Test configuration manager"""
    
    def test_configuration_singleton(self):
        """Test configuration manager singleton behavior"""
        manager1 = ConfigurationManager()
        manager2 = ConfigurationManager()
        
        assert manager1.config is manager2.config
    
    def test_setting_caching(self):
        """Test setting caching"""
        manager = ConfigurationManager()
        
        # First call should cache
        value1 = manager.get_setting('ENVIRONMENT')
        
        # Second call should use cache
        value2 = manager.get_setting('ENVIRONMENT')
        
        assert value1 == value2
    
    def test_configuration_reload(self):
        """Test configuration reload"""
        manager = ConfigurationManager()
        original_config = manager.config
        
        # Reload configuration
        new_config = manager.reload_configuration()
        
        assert new_config is not None
        assert manager.config is new_config
```

## Configuration Usage

### 1. Application Initialization

#### Flask Application Configuration
```python
# src/app.py
from flask import Flask
from src.core.config_manager import ConfigurationManager
from src.core.logging import setup_logging

def create_app():
    """Create Flask application with configuration"""
    app = Flask(__name__)
    
    # Load configuration
    config_manager = ConfigurationManager()
    config = config_manager.config
    
    # Configure Flask app
    app.config['DEBUG'] = config.DEBUG
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['DATABASE_URL'] = config.DATABASE_URL
    
    # Setup logging
    setup_logging(config_manager.get_logging_config())
    
    # Configure extensions based on environment
    if config.DEBUG:
        # Development extensions
        from flask_debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension(app)
    
    return app
```

### 2. Service Configuration

#### Service Configuration Usage
```python
# src/services/auth_service.py
from src.core.config_manager import ConfigurationManager

class AuthService:
    """Authentication service with configuration"""
    
    def __init__(self):
        self.config_manager = ConfigurationManager()
        self.jwt_settings = self.config_manager.get_jwt_settings()
    
    def generate_token(self, user):
        """Generate JWT token using configuration"""
        import jwt
        import datetime
        
        payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.datetime.utcnow() + 
                   datetime.timedelta(minutes=self.jwt_settings['expire_minutes'])
        }
        
        return jwt.encode(
            payload,
            self.jwt_settings['secret_key'],
            algorithm=self.jwt_settings['algorithm']
        )
```

## Benefits of Environment-Based Configuration

### 1. Flexibility
- **Environment-specific settings** for different deployment targets
- **Feature toggles** for enabling/disabling functionality
- **Easy configuration changes** without code deployment
- **Consistent configuration** across environments

### 2. Security
- **Sensitive data separation** from code
- **Environment-specific secrets** management
- **Production safeguards** for dangerous settings
- **Configuration validation** for security

### 3. Maintainability
- **Centralized configuration** management
- **Type-safe configuration** with Pydantic
- **Configuration validation** at startup
- **Clear documentation** of settings

### 4. Scalability
- **Easy environment setup** for new deployments
- **Configuration inheritance** between environments
- **Feature flag management** for gradual rollouts
- **Environment-specific optimizations**

## Conclusion

The environment-based configuration management system provides:
- **Flexible configuration** for different environments
- **Type-safe settings** with validation
- **Feature toggle support** for dynamic functionality
- **Security safeguards** for production deployments
- **Comprehensive testing** of configuration logic
- **Easy maintenance** and scalability

This implementation serves as a robust foundation for managing application configuration across all environments.
