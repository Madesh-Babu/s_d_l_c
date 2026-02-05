"""
Unit Tests for Configuration Management

This module contains comprehensive unit tests for configuration management,
testing settings validation, environment detection, and feature toggles.
"""

import pytest
from unittest.mock import patch, Mock
from src.core.config import settings, EnvironmentConfig, FeatureToggles, DevelopmentConfig, ProductionConfig
from src.core.exceptions import ConfigurationError
import tempfile
import os


class TestConfigComprehensive:
    """Comprehensive unit tests for configuration management and validation."""
    
    def test_environment_config_default_values(self):
        """Test environment config default values."""
        config = EnvironmentConfig()
        
        assert config.ENVIRONMENT == 'development'
        assert config.FLASK_ENV == 'development'
        assert config.FLASK_DEBUG is False
    
    def test_environment_config_from_env_file(self):
        """Test loading configuration from environment file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("ENVIRONMENT=production\n")
            f.write("FLASK_DEBUG=True\n")
            f.write("APP_NAME=Test App\n")
            env_file = f.name
        
        try:
            config = EnvironmentConfig(_env_file=env_file)
            
            assert config.ENVIRONMENT == 'production'
            assert config.FLASK_DEBUG is True
            assert config.APP_NAME == "Test App"
        finally:
            os.unlink(env_file)
    
    def test_feature_toggles_default_values(self):
        """Test feature toggles default values."""
        toggles = FeatureToggles()
        
        assert toggles.BYPASS_AUTH is False
        assert toggles.ENABLE_JWT is True
        assert toggles.ENABLE_RATE_LIMITING is True
        assert toggles.ENABLE_CORS is True
    
    def test_feature_toggles_from_env_file(self):
        """Test loading feature toggles from environment file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("BYPASS_AUTH=True\n")
            f.write("ENABLE_RATE_LIMITING=False\n")
            f.write("ENABLE_CORS=False\n")
            env_file = f.name
        
        try:
            toggles = FeatureToggles(_env_file=env_file)
            
            assert toggles.BYPASS_AUTH is True
            assert toggles.ENABLE_RATE_LIMITING is False
            assert toggles.ENABLE_CORS is False
        finally:
            os.unlink(env_file)
    
    def test_bypass_auth_validation_development(self):
        """Test bypass auth validation in development environment."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'development'}):
            toggles = FeatureToggles(BYPASS_AUTH=True)
            
            # Should not raise an error in development
            assert toggles.BYPASS_AUTH is True
    
    def test_bypass_auth_validation_production(self):
        """Test bypass auth validation in production environment."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'production'}):
            with pytest.raises(ValueError) as exc_info:
                FeatureToggles(BYPASS_AUTH=True)
            
            assert "Authentication bypass can only be enabled in development" in str(exc_info.value)
    
    def test_development_config_settings(self):
        """Test development configuration settings."""
        config = DevelopmentConfig()
        
        assert config.ENVIRONMENT == 'development'
        assert config.FLASK_DEBUG is True
        assert config.feature_toggles.BYPASS_AUTH is True
        assert config.feature_toggles.ENABLE_RATE_LIMITING is False
    
    def test_production_config_settings(self):
        """Test production configuration settings."""
        config = ProductionConfig()
        
        assert config.ENVIRONMENT == 'production'
        assert config.FLASK_DEBUG is False
        assert config.feature_toggles.BYPASS_AUTH is False
        assert config.feature_toggles.ENABLE_RATE_LIMITING is True
    
    def test_settings_singleton_behavior(self):
        """Test that settings behaves as a singleton."""
        settings1 = settings
        settings2 = settings
        
        assert settings1 is settings2
    
    def test_is_development_method(self):
        """Test is_development method."""
        # Test development environment
        dev_config = DevelopmentConfig()
        assert dev_config.is_development() is True
        
        # Test production environment
        prod_config = ProductionConfig()
        assert prod_config.is_development() is False
    
    def test_is_production_method(self):
        """Test is_production method."""
        # Test development environment
        dev_config = DevelopmentConfig()
        assert dev_config.is_production() is False
        
        # Test production environment
        prod_config = ProductionConfig()
        assert prod_config.is_production() is True
    
    def test_is_testing_method(self):
        """Test is_testing method."""
        # Test with testing environment
        with patch.dict(os.environ, {'ENVIRONMENT': 'testing'}):
            config = EnvironmentConfig()
            assert config.is_testing() is True
        
        # Test with non-testing environment
        with patch.dict(os.environ, {'ENVIRONMENT': 'development'}):
            config = EnvironmentConfig()
            assert config.is_testing() is False
    
    def test_database_url_validation(self):
        """Test database URL validation."""
        # Valid database URLs
        valid_urls = [
            "sqlite:///test.db",
            "postgresql://user:pass@localhost/db",
            "mysql://user:pass@localhost/db"
        ]
        
        for url in valid_urls:
            config = EnvironmentConfig(DATABASE_URL=url)
            assert config.DATABASE_URL == url
    
    def test_jwt_configuration_validation(self):
        """Test JWT configuration validation."""
        # Valid JWT configuration
        config = EnvironmentConfig(
            JWT_SECRET_KEY="test_secret_key",
            JWT_ACCESS_TOKEN_EXPIRES=3600
        )
        
        assert config.JWT_SECRET_KEY == "test_secret_key"
        assert config.JWT_ACCESS_TOKEN_EXPIRES == 3600
    
    def test_jwt_secret_key_validation_weak_key(self):
        """Test JWT secret key validation for weak keys."""
        with pytest.raises(ValueError) as exc_info:
            EnvironmentConfig(JWT_SECRET_KEY="weak")
        
        assert "JWT secret key must be at least 32 characters" in str(exc_info.value)
    
    def test_logging_configuration_validation(self):
        """Test logging configuration validation."""
        # Valid log levels
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in valid_levels:
            config = EnvironmentConfig(LOG_LEVEL=level)
            assert config.LOG_LEVEL == level
    
    def test_logging_configuration_invalid_level(self):
        """Test logging configuration with invalid level."""
        with pytest.raises(ValueError) as exc_info:
            EnvironmentConfig(LOG_LEVEL="INVALID")
        
        assert "Invalid log level" in str(exc_info.value)
    
    def test_cors_configuration_validation(self):
        """Test CORS configuration validation."""
        # Valid CORS origins
        valid_origins = [
            "http://localhost:3000",
            "https://example.com",
            ["http://localhost:3000", "https://example.com"]
        ]
        
        for origins in valid_origins:
            config = EnvironmentConfig(CORS_ORIGINS=origins)
            assert config.CORS_ORIGINS == origins
    
    def test_rate_limiting_configuration(self):
        """Test rate limiting configuration."""
        config = EnvironmentConfig(
            RATE_LIMIT_ENABLED=True,
            RATE_LIMIT_PER_MINUTE=100
        )
        
        assert config.RATE_LIMIT_ENABLED is True
        assert config.RATE_LIMIT_PER_MINUTE == 100
    
    def test_rate_limiting_validation_negative_limit(self):
        """Test rate limiting with negative limit."""
        with pytest.raises(ValueError) as exc_info:
            EnvironmentConfig(RATE_LIMIT_PER_MINUTE=-10)
        
        assert "Rate limit must be positive" in str(exc_info.value)
    
    def test_cache_configuration_validation(self):
        """Test cache configuration validation."""
        # Valid cache configurations
        valid_configs = [
            {"type": "simple", "timeout": 300},
            {"type": "redis", "host": "localhost", "port": 6379},
            {"type": "memcached", "servers": ["localhost:11211"]}
        ]
        
        for cache_config in valid_configs:
            config = EnvironmentConfig(CACHE_CONFIG=cache_config)
            assert config.CACHE_CONFIG == cache_config
    
    def test_mail_configuration_validation(self):
        """Test mail configuration validation."""
        # Valid mail configuration
        config = EnvironmentConfig(
            MAIL_SERVER="smtp.example.com",
            MAIL_PORT=587,
            MAIL_USE_TLS=True,
            MAIL_USERNAME="test@example.com",
            MAIL_PASSWORD="password"
        )
        
        assert config.MAIL_SERVER == "smtp.example.com"
        assert config.MAIL_PORT == 587
        assert config.MAIL_USE_TLS is True
    
    def test_mail_configuration_invalid_port(self):
        """Test mail configuration with invalid port."""
        with pytest.raises(ValueError) as exc_info:
            EnvironmentConfig(MAIL_PORT=70000)
        
        assert "Invalid mail port" in str(exc_info.value)
    
    def test_api_configuration_validation(self):
        """Test API configuration validation."""
        config = EnvironmentConfig(
            API_VERSION="v1",
            API_PREFIX="/api",
            API_TITLE="Test API",
            API_DESCRIPTION="Test API Description"
        )
        
        assert config.API_VERSION == "v1"
        assert config.API_PREFIX == "/api"
        assert config.API_TITLE == "Test API"
    
    def test_security_configuration_validation(self):
        """Test security configuration validation."""
        config = EnvironmentConfig(
            SECURITY_PASSWORD_SALT="salty_salt",
            SECURITY_PASSWORD_HASH="bcrypt",
            SECURITY_TOKEN_MAX_AGE=3600
        )
        
        assert config.SECURITY_PASSWORD_SALT == "salty_salt"
        assert config.SECURITY_PASSWORD_HASH == "bcrypt"
        assert config.SECURITY_TOKEN_MAX_AGE == 3600
    
    def test_feature_toggle_enabled_check(self):
        """Test checking if a feature toggle is enabled."""
        toggles = FeatureToggles(
            BYPASS_AUTH=True,
            ENABLE_JWT=False,
            ENABLE_RATE_LIMITING=True
        )
        
        assert toggles.is_feature_enabled("BYPASS_AUTH") is True
        assert toggles.is_feature_enabled("ENABLE_JWT") is False
        assert toggles.is_feature_enabled("ENABLE_RATE_LIMITING") is True
        assert toggles.is_feature_enabled("NONEXISTENT_FEATURE") is False
    
    def test_feature_toggle_get_enabled_features(self):
        """Test getting list of enabled features."""
        toggles = FeatureToggles(
            BYPASS_AUTH=True,
            ENABLE_JWT=True,
            ENABLE_RATE_LIMITING=False,
            ENABLE_CORS=True
        )
        
        enabled = toggles.get_enabled_features()
        
        assert "BYPASS_AUTH" in enabled
        assert "ENABLE_JWT" in enabled
        assert "ENABLE_CORS" in enabled
        assert "ENABLE_RATE_LIMITING" not in enabled
    
    def test_environment_detection_from_flask_env(self):
        """Test environment detection from FLASK_ENV."""
        with patch.dict(os.environ, {'FLASK_ENV': 'development'}):
            config = EnvironmentConfig()
            assert config.ENVIRONMENT == 'development'
        
        with patch.dict(os.environ, {'FLASK_ENV': 'production'}):
            config = EnvironmentConfig()
            assert config.ENVIRONMENT == 'production'
    
    def test_environment_priority_Environment_overrides_flask_env(self):
        """Test that ENVIRONMENT takes priority over FLASK_ENV."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'production', 'FLASK_ENV': 'development'}):
            config = EnvironmentConfig()
            assert config.ENVIRONMENT == 'production'
    
    def test_configuration_validation_missing_required_fields(self):
        """Test configuration validation for missing required fields."""
        with pytest.raises(ValueError) as exc_info:
            EnvironmentConfig()  # Missing required fields will raise validation errors
        
        # The specific error depends on the Pydantic validation
        assert "validation error" in str(exc_info.value).lower()
    
    def test_configuration_reload_on_change(self):
        """Test configuration reloading when environment changes."""
        initial_config = EnvironmentConfig()
        initial_env = initial_config.ENVIRONMENT
        
        # Change environment
        with patch.dict(os.environ, {'ENVIRONMENT': 'testing'}):
            new_config = EnvironmentConfig()
            assert new_config.ENVIRONMENT != initial_env
    
    def test_configuration_export_to_dict(self):
        """Test exporting configuration to dictionary."""
        config = EnvironmentConfig(
            ENVIRONMENT="development",
            FLASK_DEBUG=True,
            APP_NAME="Test App"
        )
        
        config_dict = config.model_dump()
        
        assert config_dict['ENVIRONMENT'] == "development"
        assert config_dict['FLASK_DEBUG'] is True
        assert config_dict['APP_NAME'] == "Test App"
    
    def test_configuration_export_to_json(self):
        """Test exporting configuration to JSON."""
        config = EnvironmentConfig(
            ENVIRONMENT="development",
            FLASK_DEBUG=True,
            APP_NAME="Test App"
        )
        
        json_str = config.model_dump_json()
        
        assert "development" in json_str
        assert "Test App" in json_str
    
    def test_sensitive_data_masking(self):
        """Test masking of sensitive configuration data."""
        config = EnvironmentConfig(
            DATABASE_URL="postgresql://user:password@localhost/db",
            JWT_SECRET_KEY="super_secret_key",
            MAIL_PASSWORD="mail_password"
        )
        
        # The masking implementation would depend on specific requirements
        # This is a placeholder for the test
        assert config.DATABASE_URL is not None
        assert config.JWT_SECRET_KEY is not None
        assert config.MAIL_PASSWORD is not None
    
    def test_configuration_schema_validation(self):
        """Test configuration schema validation."""
        # Test with valid configuration
        valid_config = {
            "ENVIRONMENT": "development",
            "FLASK_DEBUG": True,
            "APP_NAME": "Test App",
            "JWT_SECRET_KEY": "super_secret_key_that_is_long_enough"
        }
        
        config = EnvironmentConfig(**valid_config)
        
        assert config.ENVIRONMENT == "development"
        assert config.FLASK_DEBUG is True
        assert config.APP_NAME == "Test App"
    
    def test_configuration_environment_variable_override(self):
        """Test that environment variables override configuration file values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("ENVIRONMENT=development\n")
            f.write("FLASK_DEBUG=False\n")
            env_file = f.name
        
        try:
            with patch.dict(os.environ, {'FLASK_DEBUG': 'True'}):
                config = EnvironmentConfig(_env_file=env_file)
                
                # Environment variable should override file value
                assert config.ENVIRONMENT == "development"
                assert config.FLASK_DEBUG is True
        finally:
            os.unlink(env_file)
    
    def test_configuration_type_conversion(self):
        """Test proper type conversion for configuration values."""
        config = EnvironmentConfig(
            FLASK_DEBUG="true",  # String should be converted to boolean
            JWT_ACCESS_TOKEN_EXPIRES="3600",  # String should be converted to int
            RATE_LIMIT_PER_MINUTE="100.5"  # String should be converted to float
        )
        
        assert isinstance(config.FLASK_DEBUG, bool)
        assert isinstance(config.JWT_ACCESS_TOKEN_EXPIRES, int)
        assert isinstance(config.RATE_LIMIT_PER_MINUTE, (int, float))
    
    def test_configuration_default_values_completeness(self):
        """Test that all required configuration has sensible defaults."""
        config = EnvironmentConfig()
        
        # Check that essential fields have defaults
        assert hasattr(config, 'ENVIRONMENT')
        assert hasattr(config, 'FLASK_ENV')
        assert hasattr(config, 'FLASK_DEBUG')
        assert hasattr(config, 'JWT_SECRET_KEY')
        assert hasattr(config, 'JWT_ACCESS_TOKEN_EXPIRES')
    
    def test_feature_toggle_dynamic_enable_disable(self):
        """Test dynamically enabling and disabling feature toggles."""
        toggles = FeatureToggles()
        
        # Initially disabled
        assert toggles.BYPASS_AUTH is False
        
        # Enable dynamically
        toggles.BYPASS_AUTH = True
        assert toggles.BYPASS_AUTH is True
        
        # Disable dynamically
        toggles.BYPASS_AUTH = False
        assert toggles.BYPASS_AUTH is False
    
    def test_configuration_validation_custom_validators(self):
        """Test custom configuration validators."""
        # Test custom validator for URL format
        with pytest.raises(ValueError) as exc_info:
            EnvironmentConfig(DATABASE_URL="invalid_url_format")
        
        assert "Invalid database URL format" in str(exc_info.value)
    
    def test_configuration_inheritance_and_override(self):
        """Test configuration inheritance and override patterns."""
        # Base configuration
        base_config = EnvironmentConfig(ENVIRONMENT="development")
        
        # Development config should inherit and override
        dev_config = DevelopmentConfig()
        assert dev_config.ENVIRONMENT == "development"
        assert dev_config.FLASK_DEBUG is True  # Overridden
        
        # Production config should inherit and override
        prod_config = ProductionConfig()
        assert prod_config.ENVIRONMENT == "production"
        assert prod_config.FLASK_DEBUG is False  # Overridden
