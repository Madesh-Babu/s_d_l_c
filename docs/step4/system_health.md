# Health Check Endpoint

## Overview

Provides system health information for monitoring, load balancing, and deployment verification.

## Endpoint Details

- **Method**: `GET`
- **URL**: `/health`
- **Authentication**: Not required
- **Content-Type**: `application/json`

## Response Format

### Success Response (200)
```json
{
    "status": "healthy",
    "timestamp": "2024-01-20T10:30:00Z",
    "version": "1.0.0",
    "environment": "development",
    "uptime": "2 hours, 15 minutes",
    "checks": {
        "database": {
            "status": "healthy",
            "response_time": "2ms",
            "details": "Connection successful"
        },
        "memory": {
            "status": "healthy",
            "usage": "45%",
            "available": "55%"
        },
        "api": {
            "status": "healthy",
            "endpoints_count": 12,
            "active_connections": 5
        }
    },
    "features": {
        "authentication_bypass": true,
        "debug_mode": true,
        "rate_limiting": false
    }
}
```

### Degraded Response (200)
```json
{
    "status": "degraded",
    "timestamp": "2024-01-20T10:30:00Z",
    "checks": {
        "database": {
            "status": "slow",
            "response_time": "150ms",
            "details": "Database responding slowly"
        }
    }
}
```

### Error Response (503)
```json
{
    "status": "unhealthy",
    "timestamp": "2024-01-20T10:30:00Z",
    "error": "Database connection failed"
}
```

## Implementation Pattern

### Core Logic
```python
@system_b_p.route('/health', methods=['GET'])
def health_check():
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "uptime": get_uptime(),
            "checks": {}
        }
        
        # Database health check
        db_status = check_database_health()
        health_status["checks"]["database"] = db_status
        
        # Memory health check
        memory_status = check_memory_health()
        health_status["checks"]["memory"] = memory_status
        
        # API health check
        api_status = check_api_health()
        health_status["checks"]["api"] = api_status
        
        # Feature status
        health_status["features"] = get_feature_status()
        
        # Determine overall status
        overall_status = determine_overall_status(health_status["checks"])
        health_status["status"] = overall_status
        
        # Return appropriate status code
        status_code = 200 if overall_status in ["healthy", "degraded"] else 503
        
        return jsonify(health_status), status_code
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return jsonify({
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }), 503
```

### Health Checks
1. **Database**: Connection and query performance
2. **Memory**: Usage and availability
3. **API**: Endpoint availability and response times
4. **Features**: Feature toggle status

### Status Determination
- **Healthy**: All checks passing
- **Degraded**: Some checks slow or warning
- **Unhealthy**: Critical checks failing

## Key Components

### Database Health Check
```python
def check_database_health():
    try:
        start_time = time.time()
        db.session.execute('SELECT 1')
        response_time = (time.time() - start_time) * 1000
        
        status = "healthy" if response_time < 100 else "slow"
        
        return {
            "status": status,
            "response_time": f"{response_time:.0f}ms",
            "details": "Connection successful"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "response_time": "N/A",
            "details": str(e)
        }
```

### Memory Health Check
```python
def check_memory_health():
    import psutil
    
    memory = psutil.virtual_memory()
    usage_percent = memory.percent
    
    status = "healthy" if usage_percent < 80 else "warning"
    if usage_percent > 90:
        status = "unhealthy"
    
    return {
        "status": status,
        "usage": f"{usage_percent}%",
        "available": f"{100 - usage_percent}%"
    }
```

### Feature Status
```python
def get_feature_status():
    return {
        "authentication_bypass": settings.feature_toggles.BYPASS_AUTH,
        "debug_mode": settings.FLASK_DEBUG,
        "rate_limiting": settings.feature_toggles.ENABLE_RATE_LIMITING
    }
```

## Business Logic

### Health Check Process
1. Check database connectivity and performance
2. Monitor memory usage and availability
3. Verify API endpoint availability
4. Check feature toggle status
5. Determine overall system health
6. Return appropriate response and status code

### Status Criteria
- **Database**: Response time < 100ms = healthy
- **Memory**: Usage < 80% = healthy
- **API**: All endpoints responding = healthy
- **Overall**: All checks must pass for healthy status

### Monitoring Integration
- Suitable for load balancer health checks
- Compatible with monitoring systems
- Provides detailed diagnostic information
- Supports automated alerting

## Error Scenarios

### Database Issues
- Connection failures
- Slow query performance
- Connection pool exhaustion

### System Issues
- High memory usage
- CPU exhaustion
- Disk space issues

### Application Issues
- Critical errors in health check
- Configuration problems
- Service dependencies

## Logging

### Health Check Logging
```python
logger.info("Health check completed", 
           status=health_status["status"],
           database_status=db_status["status"],
           memory_usage=memory_status["usage"])
```

### Error Logging
```python
logger.error("Health check failed", 
           error=str(e),
           component="health_check")
```

## Testing Considerations

### Test Cases
- Healthy system response
- Database connection failure
- High memory usage scenario
- Slow database response
- Feature toggle verification

### Test Data
```python
# Mock database failure
with patch('db.session.execute', side_effect=Exception("DB Error")):
    response = client.get('/health')
    assert response.json['status'] == 'unhealthy'
```

## Performance Considerations

- Fast health check execution
- Minimal resource usage
- Efficient database queries
- Quick response times

## Security Notes

- No authentication required (public endpoint)
- Limited sensitive information exposure
- Safe for external monitoring
- Rate limiting consideration

## Development Features

### Debug Information
```python
if settings.is_development():
    health_status["debug"] = {
        "database_queries": get_query_count(),
        "active_sessions": get_session_count(),
        "configuration": get_safe_config()
    }
```

### Detailed Diagnostics
- Extended error information
- Performance metrics
- Configuration details
- Debug endpoints

## Production Considerations

### Monitoring Integration
- Compatible with Prometheus
- Supports health check protocols
- Load balancer friendly
- Alert system integration

### Reliability
- Fast execution time
- Graceful degradation
- Minimal dependencies
- Robust error handling
