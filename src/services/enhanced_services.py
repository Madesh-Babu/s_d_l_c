"""
Enhanced Service Layer with Design Patterns Integration

This module integrates the Singleton, Factory Method, and Abstract Method patterns
into the existing service architecture.
"""

from src.core.design_patterns import (
    DatabaseConnectionManager, 
    ServiceFactory, 
    NotificationManager
)
from src.models.models import db, Category, Product, User
from src.models.schemas import (
    CategoryCreate, CategoryUpdate, ProductCreate, ProductUpdate,
    DiscountRequest, UserCreate, UserUpdate
)
from pydantic import ValidationError
from typing import Dict, Any, Optional, List
import logging


# ==============================
# ENHANCED SERVICES WITH DESIGN PATTERNS
# ==============================

class EnhancedProductService:
    """
    Enhanced Product Service using Singleton and Factory Method patterns.
    """
    
    def __init__(self):
        # Use Singleton pattern for database connection
        self.db_manager = DatabaseConnectionManager()
        self.logger = logging.getLogger(__name__)
        self.notification_manager = NotificationManager()
    
    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new product with enhanced logging and notifications."""
        try:
            # Validate product data
            validated_data = ProductCreate(**product_data)
            
            # Use singleton database connection
            connection = self.db_manager.get_connection()
            self.logger.info(f"🗄️ Using database connection: {connection}")
            
            # Check for duplicate product
            existing_product = Product.query.filter_by(name=validated_data.name).first()
            if existing_product:
                return {"success": False, "message": f"Product '{validated_data.name}' already exists"}
            
            # Create new product
            new_product = Product(
                name=validated_data.name,
                description=validated_data.description,
                price=validated_data.price,
                stock=validated_data.stock,
                category_id=validated_data.category_id
            )
            
            db.session.add(new_product)
            db.session.commit()
            
            # Send notification using Abstract Method pattern
            self.notification_manager.send_notification(
                "email", 
                "admin@inventory.com", 
                f"New product created: {new_product.name}",
                subject="Product Creation Notification"
            )
            
            self.logger.info(f"✅ Product created successfully: {new_product.name}")
            
            return {
                "success": True,
                "product": {
                    "id": new_product.id,
                    "name": new_product.name,
                    "price": float(new_product.price),
                    "stock": new_product.stock
                }
            }
            
        except ValidationError as e:
            self.logger.error(f"❌ Validation error: {str(e)}")
            return {"success": False, "message": f"Validation error: {str(e)}"}
        except Exception as e:
            self.logger.error(f"❌ Error creating product: {str(e)}")
            return {"success": False, "message": f"Error creating product: {str(e)}"}
    
    def get_product(self, product_id: int) -> Dict[str, Any]:
        """Get product by ID using Factory Method pattern."""
        try:
            # Use Factory Method pattern to create service
            service = ServiceFactory.create_service("product")
            result = service.execute(product_id, "get")
            
            # Enhance with database query
            product = Product.query.get(product_id)
            if not product:
                return {"success": False, "message": "Product not found"}
            
            self.logger.info(f"📦 Retrieved product: {product.name}")
            
            return {
                "success": True,
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": float(product.price),
                    "stock": product.stock,
                    "category_id": product.category_id
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting product: {str(e)}")
            return {"success": False, "message": f"Error getting product: {str(e)}"}
    
    def update_product(self, product_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update product with notifications."""
        try:
            product = Product.query.get(product_id)
            if not product:
                return {"success": False, "message": "Product not found"}
            
            # Validate update data
            validated_data = ProductUpdate(**update_data)
            
            # Update product fields
            for field, value in validated_data.dict(exclude_unset=True).items():
                setattr(product, field, value)
            
            db.session.commit()
            
            # Send notification
            self.notification_manager.send_notification(
                "email",
                "admin@inventory.com",
                f"Product updated: {product.name}",
                subject="Product Update Notification"
            )
            
            self.logger.info(f"✅ Product updated successfully: {product.name}")
            
            return {
                "success": True,
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "price": float(product.price),
                    "stock": product.stock
                }
            }
            
        except ValidationError as e:
            return {"success": False, "message": f"Validation error: {str(e)}"}
        except Exception as e:
            return {"success": False, "message": f"Error updating product: {str(e)}"}
    
    def delete_product(self, product_id: int) -> Dict[str, Any]:
        """Delete product with notifications."""
        try:
            product = Product.query.get(product_id)
            if not product:
                return {"success": False, "message": "Product not found"}
            
            product_name = product.name
            db.session.delete(product)
            db.session.commit()
            
            # Send notification
            self.notification_manager.send_notification(
                "email",
                "admin@inventory.com",
                f"Product deleted: {product_name}",
                subject="Product Deletion Notification"
            )
            
            self.logger.info(f"🗑️ Product deleted successfully: {product_name}")
            
            return {"success": True, "message": f"Product '{product_name}' deleted successfully"}
            
        except Exception as e:
            return {"success": False, "message": f"Error deleting product: {str(e)}"}


class EnhancedUserService:
    """
    Enhanced User Service using all three design patterns.
    """
    
    def __init__(self):
        # Singleton pattern for database connection
        self.db_manager = DatabaseConnectionManager()
        self.logger = logging.getLogger(__name__)
        
        # Factory Method pattern for service creation
        self.service_factory = ServiceFactory()
        
        # Abstract Method pattern for notifications
        self.notification_manager = NotificationManager()
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user with all design patterns in action."""
        try:
            # Validate user data
            validated_data = UserCreate(**user_data)
            
            # Use singleton database connection
            connection = self.db_manager.get_connection()
            self.logger.info(f"🗄️ Using database connection: {connection}")
            
            # Check for duplicate user
            existing_user = User.query.filter_by(username=validated_data.username).first()
            if existing_user:
                return {"success": False, "message": f"User '{validated_data.username}' already exists"}
            
            # Create new user
            new_user = User(
                username=validated_data.username,
                email=validated_data.email,
                role=validated_data.role
            )
            new_user.set_password(validated_data.password)
            
            db.session.add(new_user)
            db.session.commit()
            
            # Use Factory Method pattern to create user service
            user_service = self.service_factory.create_service("user")
            service_result = user_service.execute(new_user.id, "get")
            
            # Send notifications using different methods (Abstract Method pattern)
            notifications = [
                ("email", validated_data.email, "Welcome to Inventory Management System!", 
                 {"subject": "Welcome"}),
                ("sms", "1234567890", f"User account created: {validated_data.username}", 
                 {"priority": "normal"}),
                ("push", "device_token_123", f"New user registered: {validated_data.username}", 
                 {"device_type": "mobile"})
            ]
            
            for method, recipient, message, kwargs in notifications:
                self.notification_manager.send_notification(method, recipient, message, **kwargs)
            
            self.logger.info(f"✅ User created successfully: {new_user.username}")
            
            return {
                "success": True,
                "user": {
                    "id": new_user.id,
                    "username": new_user.username,
                    "email": new_user.email,
                    "role": new_user.role
                },
                "service_result": service_result
            }
            
        except ValidationError as e:
            return {"success": False, "message": f"Validation error: {str(e)}"}
        except Exception as e:
            return {"success": False, "message": f"Error creating user: {str(e)}"}
    
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user by ID using Factory Method pattern."""
        try:
            # Use Factory Method pattern
            service = self.service_factory.create_service("user")
            result = service.execute(user_id, "get")
            
            # Get actual user from database
            user = User.query.get(user_id)
            if not user:
                return {"success": False, "message": "User not found"}
            
            self.logger.info(f"👤 Retrieved user: {user.username}")
            
            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role
                },
                "service_result": result
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error getting user: {str(e)}"}


class EnhancedCategoryService:
    """
    Enhanced Category Service demonstrating design patterns integration.
    """
    
    def __init__(self):
        self.db_manager = DatabaseConnectionManager()
        self.logger = logging.getLogger(__name__)
        self.service_factory = ServiceFactory()
        self.notification_manager = NotificationManager()
    
    def create_category(self, category_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new category with design patterns."""
        try:
            # Validate category data
            validated_data = CategoryCreate(**category_data)
            
            # Use singleton database connection
            connection = self.db_manager.get_connection()
            self.logger.info(f"🗄️ Using database connection: {connection}")
            
            # Check for duplicate category
            existing_category = Category.query.filter_by(name=validated_data.name).first()
            if existing_category:
                return {"success": False, "message": f"Category '{validated_data.name}' already exists"}
            
            # Create new category
            new_category = Category(
                name=validated_data.name,
                description=validated_data.description
            )
            
            db.session.add(new_category)
            db.session.commit()
            
            # Use Factory Method pattern
            service = self.service_factory.create_service("category")
            service_result = service.execute(new_category.id, "get")
            
            # Send notification
            self.notification_manager.send_notification(
                "email",
                "admin@inventory.com",
                f"New category created: {new_category.name}",
                subject="Category Creation Notification"
            )
            
            self.logger.info(f"📂 Category created successfully: {new_category.name}")
            
            return {
                "success": True,
                "category": {
                    "id": new_category.id,
                    "name": new_category.name,
                    "description": new_category.description
                },
                "service_result": service_result
            }
            
        except ValidationError as e:
            return {"success": False, "message": f"Validation error: {str(e)}"}
        except Exception as e:
            return {"success": False, "message": f"Error creating category: {str(e)}"}


# ==============================
# SERVICE FACTORY ENHANCEMENT
# ==============================

class EnhancedServiceFactory(ServiceFactory):
    """Enhanced Service Factory with additional services."""
    
    @classmethod
    def create_enhanced_service(cls, service_type: str):
        """Create enhanced service instances."""
        if service_type.lower() == "product":
            return EnhancedProductService()
        elif service_type.lower() == "user":
            return EnhancedUserService()
        elif service_type.lower() == "category":
            return EnhancedCategoryService()
        else:
            # Fall back to original factory
            return cls.create_service(service_type)
    
    @classmethod
    def get_enhanced_services(cls) -> List[str]:
        """Get list of enhanced service types."""
        return ["product", "user", "category"]


# ==============================
# DEMONSTRATION FUNCTION
# ==============================

def demonstrate_enhanced_services():
    """Demonstrate the enhanced services with design patterns."""
    logger = logging.getLogger(__name__)
    
    print("\n" + "="*60)
    print("🚀 ENHANCED SERVICES WITH DESIGN PATTERNS")
    print("="*60)
    
    # Test Enhanced Product Service
    print("\n📦 Testing Enhanced Product Service")
    print("-" * 40)
    
    product_service = EnhancedProductService()
    
    # Create product
    product_data = {
        "name": "Laptop",
        "description": "High-performance laptop",
        "price": 999.99,
        "stock": 50,
        "category_id": 1
    }
    
    result = product_service.create_product(product_data)
    print(f"Create Product: {result}")
    
    # Test Enhanced User Service
    print("\n👤 Testing Enhanced User Service")
    print("-" * 40)
    
    user_service = EnhancedUserService()
    
    # Create user
    user_data = {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "securepassword123",
        "role": "staff"
    }
    
    result = user_service.create_user(user_data)
    print(f"Create User: {result}")
    
    # Test Enhanced Category Service
    print("\n📂 Testing Enhanced Category Service")
    print("-" * 40)
    
    category_service = EnhancedCategoryService()
    
    # Create category
    category_data = {
        "name": "Electronics",
        "description": "Electronic devices and accessories"
    }
    
    result = category_service.create_category(category_data)
    print(f"Create Category: {result}")
    
    # Test Enhanced Service Factory
    print("\n🏭 Testing Enhanced Service Factory")
    print("-" * 40)
    
    enhanced_services = EnhancedServiceFactory.get_enhanced_services()
    print(f"Enhanced services available: {enhanced_services}")
    
    for service_type in enhanced_services:
        service = EnhancedServiceFactory.create_enhanced_service(service_type)
        print(f"Created enhanced service: {type(service).__name__}")
    
    print("\n" + "="*60)
    print("🎉 ENHANCED SERVICES DEMONSTRATION COMPLETED")
    print("="*60)


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    demonstrate_enhanced_services()
