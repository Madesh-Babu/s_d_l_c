import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from src.core.config import Config, config
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from error_handlers import register_error_handlers
from src.core.logging import setup_logging, LoggingMiddleware, get_logger

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_name=None):
    """Create and configure Flask application."""
    
    # Determine configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Setup structured logging
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    log_environment = app.config.get('LOG_ENVIRONMENT', 'development')
    setup_logging(log_level=log_level, environment=log_environment)
    
    # Initialize logger
    logger = get_logger(__name__)
    logger.info("Application starting", config_name=config_name, log_level=log_level)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Add logging middleware
    LoggingMiddleware(app)
    
    # Register blueprints
    from src.api.products.routes import products_b_p
    from src.api.authentication.routes import auth_b_p
    from src.api.categories.routes import categories_b_p

    app.register_blueprint(products_b_p, url_prefix="/products")
    app.register_blueprint(auth_b_p, url_prefix='/auth')
    app.register_blueprint(categories_b_p, url_prefix="/categories")
    
    @app.route('/')
    def home():
        logger.info("Home endpoint accessed")
        return {'message': "Inventory Management API Running"}
    
    logger.info("Application initialized successfully")
    return app
