from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from error_handlers import register_error_handlers

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_class=Config):
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgresql@127.0.0.1:5432/Inventory_Management_API'
    app.config['JWT_SECRET_KEY'] = 'a1b2c3d4'
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app,db)
    jwt.init_app(app)
    register_error_handlers(app)
    
    from app.products.routes import products_b_p
    from app.authentication.routes import auth_b_p
    from app.categories.routes import categories_b_p

    app.register_blueprint(products_b_p, url_prefix="/products")
    app.register_blueprint(auth_b_p,url_prefix='/auth')
    app.register_blueprint(categories_b_p,url_prefix="/categories")


    
    @app.route('/')
    def home():
        return {'message':"Inventory Management API Running"}
    
    return app
