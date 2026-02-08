# Environment Configuration

> **🎯 Learning Objective:** Understand how to implement flexible, type-safe, and environment-aware configuration management using Pydantic's BaseSettings.

This document outlines the comprehensive environment-based configuration management system implemented throughout the application using Pydantic's BaseSettings for flexible, type-safe, and environment-aware configuration.

---

## 📚 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Configuration Types](#configuration-types)
- [Environment Variables](#environment-variables)
- [Validation](#validation)
- [Best Practices](#best-practices)

---

## 🎯 Overview

Environment configuration provides:
- **🔧 Flexibility** - Environment-specific settings
- **🔒 Type Safety** - Automatic type validation
- **📁 File Support** - .env file integration
- **⚡ Performance** - Fast configuration loading
- **🛡️ Security** - Sensitive data protection

---

## 🏗️ Architecture

### Configuration Hierarchy
1. **Environment Variables** - Highest priority
2. **.env.local** - Local overrides
3. **.env** - Environment-specific settings
4. **Default Values** - Fallback values

### Configuration Components
- **Base Settings** - Core configuration class
- **Feature Toggles** - Feature flag management
- **Database Config** - Database connection settings
- **Security Config** - Authentication and security settings
- **Logging Config** - Logging configuration

---

## ⚙️ Configuration Types

### Core Configuration
- **Environment** - Application environment (dev/test/prod)
- **Debug Mode** - Development debugging settings
- **Secret Key** - Application security key
- **Database URL** - Database connection string

### Feature Toggles
- **Bypass Auth** - Development authentication bypass
- **Enable Logging** - Structured logging control
- **Enable Metrics** - Performance monitoring
- **Rate Limiting** - API rate limiting control

### Security Settings
- **JWT Settings** - Token configuration
- **Password Policy** - Password requirements
- **Session Settings** - Session management
- **CORS Settings** - Cross-origin resource sharing

---

## 🌍 Environment Variables

### Development Environment
```bash
# .env file for development
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=sqlite:///dev.db
SECRET_KEY=dev-secret-key
BYPASS_AUTH=true
```

### Production Environment
```bash
# Production environment variables
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=super-secure-production-key
BYPASS_AUTH=false
```

### Testing Environment
```bash
# Testing configuration
ENVIRONMENT=testing
DEBUG=true
DATABASE_URL=sqlite:///test.db
SECRET_KEY=test-secret-key
BYPASS_AUTH=true
```

---

## ✅ Validation

### Type Validation
- **Automatic validation** - Pydantic type checking
- **Custom validators** - Business logic validation
- **Environment validation** - Environment-specific checks
- **Security validation** - Sensitive data validation

### Validation Examples
```python
# Environment validation
@validator('ENVIRONMENT')
def validate_environment(cls, v):
    valid_envs = ['development', 'testing', 'production']
    if v not in valid_envs:
        raise ValueError(f'Invalid environment: {v}')
    return v

# Secret key validation
@validator('SECRET_KEY')
def validate_secret_key(cls, v):
    if len(v) < 32:
        raise ValueError('Secret key must be at least 32 characters')
    return v
```

---

## 🔧 Implementation

### Configuration Class
```python
# Main configuration setup
class EnvironmentConfig(BaseSettings):
    """Environment-aware configuration"""
    
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    DATABASE_URL: str
    SECRET_KEY: str
    
    class Config:
        env_file = '.env'
        case_sensitive = True
```

### Feature Toggles
```python
# Feature toggle management
class FeatureToggles(BaseSettings):
    """Feature flag configuration"""
    
    BYPASS_AUTH: bool = False
    ENABLE_LOGGING: bool = True
    ENABLE_METRICS: bool = False
    
    @validator('BYPASS_AUTH')
    def validate_bypass_auth(cls, v, info):
        env = info.context.get('ENVIRONMENT', 'development')
        if v and env == 'production':
            raise ValueError('Cannot bypass auth in production')
        return v
```

---

## 🛡️ Security Considerations

### Sensitive Data Protection
- **Environment variables** - Never store secrets in code
- **File permissions** - Secure .env file access
- **Audit logging** - Track configuration changes
- **Encryption** - Encrypt sensitive configuration values

### Production Safety
- **Environment validation** - Prevent production misconfiguration
- **Default security** - Secure default values
- **Validation checks** - Runtime configuration validation
- **Monitoring** - Configuration change monitoring

---

## ✅ Best Practices

### Configuration Management
- **Environment separation** - Different configs per environment
- **Version control** - Exclude sensitive files from VCS
- **Documentation** - Document all configuration options
- **Validation** - Validate all configuration values

### Security Practices
- **Use secrets management** - Store secrets securely
- **Rotate keys** - Regular key rotation
- **Least privilege** - Minimal required permissions
- **Audit trails** - Track configuration access

### Development Practices
- **Local development** - Use .env.local for personal settings
- **Team collaboration** - Share base .env template
- **Testing** - Test configuration validation
- **Documentation** - Keep configuration docs updated

---

## 🚀 Advanced Features

### Dynamic Configuration
- **Runtime updates** - Hot configuration reloading
- **Feature flags** - Dynamic feature control
- **A/B testing** - Configuration-based experiments
- **Canary deployments** - Gradual configuration changes

### Configuration Sources
- **Environment variables** - System environment
- **Configuration files** - JSON, YAML, TOML support
- **Remote config** - External configuration services
- **Database config** - Database-stored settings

---

## 🔍 Troubleshooting

### Common Issues
- **Missing variables** - Check environment setup
- **Type errors** - Verify variable formats
- **File permissions** - Check .env file access
- **Validation failures** - Review validation rules

### Debug Steps
1. **Check environment** - Verify ENVIRONMENT setting
2. **Validate files** - Ensure .env files exist and are readable
3. **Review variables** - Check variable names and values
4. **Test validation** - Run configuration validation

---

## 📋 Configuration Checklist

### Development Setup
- [ ] Create .env file with development settings
- [ ] Set ENVIRONMENT=development
- [ ] Configure database URL for development
- [ ] Set development secret key
- [ ] Enable debug mode
- [ ] Configure feature toggles

### Production Deployment
- [ ] Set production environment variables
- [ ] Configure production database
- [ ] Set secure secret key
- [ ] Disable debug mode
- [ ] Configure security settings
- [ ] Set up monitoring and logging

### Security Review
- [ ] Validate all environment variables
- [ ] Check secret key strength
- [ ] Verify database security
- [ ] Review feature toggle settings
- [ ] Audit configuration access
- [ ] Test configuration validation
