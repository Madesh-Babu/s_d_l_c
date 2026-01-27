"""
Global Error Handler for Flask Application

This module provides centralized error handling for the Flask application.
"""

from flask import jsonify, request, current_app
from src.core.exceptions import exception_handler
from src.core.logging import get_logger

logger = get_logger(__name__)


def register_error_handlers(app):
    """Register global error handlers for the Flask application."""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        logger.warning(f"Bad Request: {str(error)}", path=request.path, method=request.method)
        return exception_handler.handle_exception(error)
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors."""
        logger.warning(f"Unauthorized: {str(error)}", path=request.path, method=request.method)
        return exception_handler.handle_exception(error)
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors."""
        logger.warning(f"Forbidden: {str(error)}", path=request.path, method=request.method)
        return exception_handler.handle_exception(error)
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        logger.warning(f"Not Found: {str(error)}", path=request.path, method=request.method)
        return exception_handler.handle_exception(error)
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors."""
        logger.warning(f"Method Not Allowed: {str(error)}", path=request.path, method=request.method)
        return exception_handler.handle_exception(error)
    
    @app.errorhandler(409)
    def conflict(error):
        """Handle 409 Conflict errors."""
        logger.warning(f"Conflict: {str(error)}", path=request.path, method=request.method)
        return exception_handler.handle_exception(error)
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        """Handle 422 Unprocessable Entity errors."""
        logger.warning(f"Unprocessable Entity: {str(error)}", path=request.path, method=request.method)
        return exception_handler.handle_exception(error)
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handle 429 Too Many Requests errors."""
        logger.warning(f"Rate Limit Exceeded: {str(error)}", path=request.path, method=request.method)
        return exception_handler.handle_exception(error)
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error."""
        logger.error(f"Internal Server Error: {str(error)}", path=request.path, method=request.method, exc_info=True)
        return exception_handler.handle_exception(error)
    
    @app.errorhandler(502)
    def bad_gateway(error):
        """Handle 502 Bad Gateway errors."""
        logger.error(f"Bad Gateway: {str(error)}", path=request.path, method=request.method)
        return exception_handler.handle_exception(error)
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """Handle 503 Service Unavailable errors."""
        logger.error(f"Service Unavailable: {str(error)}", path=request.path, method=request.method)
        return exception_handler.handle_exception(error)
    
    @app.errorhandler(504)
    def gateway_timeout(error):
        """Handle 504 Gateway Timeout errors."""
        logger.error(f"Gateway Timeout: {str(error)}", path=request.path, method=request.method)
        return exception_handler.handle_exception(error)
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all other exceptions."""
        logger.error(f"Unhandled Exception: {str(error)}", path=request.path, method=request.method, exc_info=True)
        return exception_handler.handle_exception(error)
    
    logger.info("Global error handlers registered")
