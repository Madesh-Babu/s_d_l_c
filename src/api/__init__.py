import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from src.core.config import config, settings
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from src.core.error_handlers import register_error_handlers
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
    
    # Load environment-based configuration
    try:
        # Use the new configuration system
        config_class = config.get(config_name, config['development'])
        
        # Instantiate the configuration class with environment variables
        env_config = config_class()
        
        # Get environment-specific configuration
        flask_config = env_config.get_environment_config()
        
        # Update Flask app config
        app.config.update(flask_config)
        
        logger = get_logger(__name__)
        logger.info("Application configured with new system", 
                   config_name=config_name,
                   environment=env_config.ENVIRONMENT,
                   debug=env_config.FLASK_DEBUG)
        
    except Exception as e:
        # Fallback to legacy config if new system fails
        import traceback
        print(f"Config error: {e}")
        print(traceback.format_exc())
        
        # Use simple configuration as fallback
        app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('PG_USER', 'postgres')}:{os.getenv('PG_PASSWORD', 'postgresql')}@{os.getenv('PG_HOST', '127.0.0.1')}:{os.getenv('PG_PORT', '5432')}/{os.getenv('PG_DB', 'Inventory_Management_API')}"
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
        app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        
        logger = get_logger(__name__)
        logger.warning("Using fallback configuration", error=str(e))
    
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
    
    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return {
            'status': 'healthy',
            'environment': app.config.get('ENVIRONMENT', 'unknown'),
            'debug': app.config.get('DEBUG', False)
        }
    
    logger.info("Application initialized successfully")
    return app