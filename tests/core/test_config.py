"""
Configuration Tests

This module contains comprehensive tests for configuration management
including environment settings, feature toggles, and validation.
"""

import pytest
import os
from unittest.mock import patch
from src.core.config import settings, FeatureToggles, EnvironmentConfig, DevelopmentConfig, ProductionConfig, TestingConfig


class TestFeatureToggles:
    """Test feature toggles configuration."""

    def test_feature_toggles_default_values(self):
        """Test feature toggles have correct default values."""
        toggles = FeatureToggles()
        
        assert toggles.BYPASS_AUTH is False
        assert toggles.ENABLE_JWT is True
        assert toggles.ENABLE_ROLE_BASED_ACCESS is True
        assert toggles.ENABLE_RATE_LIMITING is True
        assert toggles.ENABLE_CORS is True
        assert toggles.ENABLE_REQUEST_LOGGING is True
        assert toggles.ENABLE_SWAGGER_DOCS is True

    def test_feature_toggles_from_environment(self, monkeypatch):
        """Test feature toggles load from environment variables."""
        monkeypatch.setenv('BYPASS_AUTH', 'true')
        monkeypatch.setenv('ENABLE_RATE_LIMITING', 'false')
        
        toggles = FeatureToggles()
        
        assert toggles.BYPASS_AUTH is True
        assert toggles.ENABLE_RATE_LIMITING is False

    def test_bypass_auth_validation_in_production(self, monkeypatch):
        """Test that BYPASS_AUTH cannot be enabled in production."""
        monkeypatch.setenv('BYPASS_AUTH', 'true')
        monkeypatch.setenv('ENVIRONMENT', 'production')
        
        with pytest.raises(ValueError, match="Authentication bypass can only be enabled in development"):
            FeatureToggles()

    def test_bypass_auth_validation_in_development(self, monkeypatch):
        """Test that BYPASS_AUTH can be enabled in development."""
        monkeypatch.setenv('BYPASS_AUTH', 'true')
        monkeypatch.setenv('ENVIRONMENT', 'development')
        
        toggles = FeatureToggles()
        assert toggles.BYPASS_AUTH is True

    def test_is_feature_enabled(self):
        """Test is_feature_enabled method."""
        toggles = FeatureToggles()
        
        assert toggles.is_feature_enabled('ENABLE_JWT') is True
        assert toggles.is_feature_enabled('BYPASS_AUTH') is False

    def test_get_enabled_features(self):
        """Test get_enabled_features method."""
        toggles = FeatureToggles()
        enabled = toggles.get_enabled_features()
        
        assert isinstance(enabled, list)
        assert 'ENABLE_JWT' in enabled
        assert 'ENABLE_ROLE_BASED_ACCESS' in enabled


class TestEnvironmentConfig:
    """Test environment configuration."""

    def test_environment_config_default_values(self):
        """Test environment config has correct default values."""
        config = EnvironmentConfig()
        
        assert config.ENVIRONMENT == 'development'
        assert config.FLASK_ENV == 'development'
        assert config.FLASK_DEBUG is False
        assert config.PG_USER is not None
        assert config.PG_PASSWORD is not None
        assert config.PG_HOST is not None
        assert config.PG_DB is not None
        assert config.JWT_SECRET_KEY is not None

    def test_environment_config_from_env_file(self, monkeypatch):
        """Test environment config loads from .env file."""
        monkeypatch.setenv('PG_USER', 'testuser')
        monkeypatch.setenv('PG_PASSWORD', 'testpass')
        monkeypatch.setenv('JWT_SECRET_KEY', 'test-secret')
        
        config = EnvironmentConfig()
        
        assert config.PG_USER == 'testuser'
        assert config.PG_PASSWORD == 'testpass'
        assert config.JWT_SECRET_KEY == 'test-secret'

    def test_get_environment_config(self):
        """Test get_environment_config method."""
        config = EnvironmentConfig()
        flask_config = config.get_environment_config()
        
        assert isinstance(flask_config, dict)
        assert 'SQLALCHEMY_DATABASE_URI' in flask_config
        assert 'JWT_SECRET_KEY' in flask_config
        assert 'DEBUG' in flask_config

    def test_is_development(self):
        """Test is_development method."""
        config = EnvironmentConfig()
        config.ENVIRONMENT = 'development'
        
        assert config.is_development() is True

    def test_is_production(self):
        """Test is_production method."""
        config = EnvironmentConfig()
        config.ENVIRONMENT = 'production'
        
        assert config.is_production() is True

    def test_is_testing(self):
        """Test is_testing method."""
        config = EnvironmentConfig()
        config.ENVIRONMENT = 'testing'
        
        assert config.is_testing() is True


class TestDevelopmentConfig:
    """Test development configuration."""

    def test_development_config_values(self):
        """Test development config has correct values."""
        config = DevelopmentConfig()
        
        assert config.ENVIRONMENT == 'development'
        assert config.FLASK_DEBUG is True
        assert config.feature_toggles.BYPASS_AUTH is True
        assert config.feature_toggles.ENABLE_RATE_LIMITING is False

    def test_development_config_database_uri(self):
        """Test development config database URI."""
        config = DevelopmentConfig()
        flask_config = config.get_environment_config()
        
        assert 'postgresql://' in flask_config['SQLALCHEMY_DATABASE_URI']


class TestProductionConfig:
    """Test production configuration."""

    def test_production_config_values(self):
        """Test production config has correct values."""
        config = ProductionConfig()
        
        assert config.ENVIRONMENT == 'production'
        assert config.FLASK_DEBUG is False
        assert config.feature_toggles.BYPASS_AUTH is False
        assert config.feature_toggles.ENABLE_RATE_LIMITING is True

    def test_production_config_security_settings(self):
        """Test production config security settings."""
        config = ProductionConfig()
        flask_config = config.get_environment_config()
        
        assert flask_config['DEBUG'] is False


class TestTestingConfig:
    """Test testing configuration."""

    def test_testing_config_values(self):
        """Test testing config has correct values."""
        config = TestingConfig()
        
        assert config.ENVIRONMENT == 'testing'
        assert config.FLASK_DEBUG is False
        assert config.feature_toggles.BYPASS_AUTH is False

    def test_testing_config_database_uri(self):
        """Test testing config uses in-memory database."""
        config = TestingConfig()
        flask_config = config.get_environment_config()
        
        # Should use SQLite for testing
        assert 'sqlite:' in flask_config['SQLALCHEMY_DATABASE_URI'] or 'test' in flask_config['SQLALCHEMY_DATABASE_URI']


class TestConfigIntegration:
    """Test configuration integration."""

    def test_settings_instance(self):
        """Test that settings is properly instantiated."""
        assert settings is not None
        assert isinstance(settings, EnvironmentConfig)

    def test_config_loading_order(self, monkeypatch):
        """Test configuration loading priority."""
        # Environment variables should override .env file
        monkeypatch.setenv('PG_USER', 'env_user')
        
        config = EnvironmentConfig()
        assert config.PG_USER == 'env_user'

    def test_missing_required_fields(self, monkeypatch):
        """Test behavior when required fields are missing."""
        # Clear required environment variables
        monkeypatch.delenv('PG_USER', raising=False)
        monkeypatch.delenv('PG_PASSWORD', raising=False)
        monkeypatch.delenv('JWT_SECRET_KEY', raising=False)
        
        with pytest.raises(Exception):  # Should raise validation error
            EnvironmentConfig()

    def test_database_uri_construction(self, monkeypatch):
        """Test database URI is constructed correctly."""
        monkeypatch.setenv('PG_USER', 'testuser')
        monkeypatch.setenv('PG_PASSWORD', 'testpass')
        monkeypatch.setenv('PG_HOST', 'localhost')
        monkeypatch.setenv('PG_PORT', '5432')
        monkeypatch.setenv('PG_DB', 'testdb')
        
        config = EnvironmentConfig()
        flask_config = config.get_environment_config()
        
        expected_uri = 'postgresql://testuser:testpass@localhost:5432/testdb'
        assert flask_config['SQLALCHEMY_DATABASE_URI'] == expected_uri

    def test_feature_toggle_inheritance(self):
        """Test that environment configs inherit feature toggles correctly."""
        dev_config = DevelopmentConfig()
        prod_config = ProductionConfig()
        
        assert dev_config.feature_toggles.BYPASS_AUTH is True
        assert prod_config.feature_toggles.BYPASS_AUTH is False
