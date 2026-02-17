"""
Design Patterns Implementation

This module demonstrates the implementation of three key design patterns:
1. Singleton Pattern - Database Connection Manager
2. Factory Method Pattern - Service Factory
3. Abstract Method Pattern - Notification Service
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import threading
import logging


# ==============================
# 1. SINGLETON PATTERN
# ==============================


class DatabaseConnectionManager:
    """
    Singleton Pattern Implementation for Database Connection Management

    Ensures only one instance of database connection manager exists throughout the application.
    Thread-safe implementation using double-checked locking.
    """

    _instance = None
    _lock = threading.Lock()
    _connection = None

    def __new__(cls):
        """Create singleton instance using double-checked locking."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseConnectionManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the singleton instance only once."""
        if self._initialized:
            return

        self._initialized = True
        self._connection_config = {}
        self.logger = logging.getLogger(__name__)
        self.logger.info("🗄️ DatabaseConnectionManager singleton initialized")

    def set_connection_config(self, config: Dict[str, Any]):
        """Set database connection configuration."""
        self._connection_config = config
        self.logger.info("📝 Database connection configuration set")

    def get_connection(self):
        """Get or create database connection."""
        if self._connection is None:
            self.logger.info("🔗 Creating new database connection")
            # Simulate connection creation
            self._connection = f"DatabaseConnection({self._connection_config})"
        return self._connection

    def close_connection(self):
        """Close database connection."""
        if self._connection:
            self.logger.info("🔒 Closing database connection")
            self._connection = None

    def get_connection_status(self) -> str:
        """Get current connection status."""
        if self._connection:
            return "Connected"
        return "Disconnected"


# ==============================
# 2. FACTORY METHOD PATTERN
# ==============================


class Service(ABC):
    """Abstract base class for services."""

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the service."""
        pass

    @abstractmethod
    def get_service_name(self) -> str:
        """Get the service name."""
        pass


class ProductService(Service):
    """Concrete service for product operations."""

    def execute(self, product_id: int, action: str = "get") -> Dict[str, Any]:
        """Execute product service operation."""
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"📦 ProductService: {action} product {product_id}")

        if action == "get":
            return {
                "product_id": product_id,
                "name": f"Product {product_id}",
                "price": 99.99,
            }
        elif action == "delete":
            return {"product_id": product_id, "deleted": True}
        else:
            return {"product_id": product_id, "action": action, "status": "completed"}

    def get_service_name(self) -> str:
        return "ProductService"


class UserService(Service):
    """Concrete service for user operations."""

    def execute(self, user_id: int, action: str = "get") -> Dict[str, Any]:
        """Execute user service operation."""
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"👤 UserService: {action} user {user_id}")

        if action == "get":
            return {"user_id": user_id, "username": f"user_{user_id}", "role": "staff"}
        elif action == "update":
            return {"user_id": user_id, "updated": True}
        else:
            return {"user_id": user_id, "action": action, "status": "completed"}

    def get_service_name(self) -> str:
        return "UserService"


class CategoryService(Service):
    """Concrete service for category operations."""

    def execute(self, category_id: int, action: str = "get") -> Dict[str, Any]:
        """Execute category service operation."""
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"📂 CategoryService: {action} category {category_id}")

        if action == "get":
            return {"category_id": category_id, "name": f"Category {category_id}"}
        elif action == "list":
            return {
                "categories": [
                    {"id": 1, "name": "Electronics"},
                    {"id": 2, "name": "Books"},
                ]
            }
        else:
            return {"category_id": category_id, "action": action, "status": "completed"}

    def get_service_name(self) -> str:
        return "CategoryService"


class ServiceFactory:
    """
    Factory Method Pattern Implementation

    Creates different types of services based on the requested service type.
    """

    _services = {
        "product": ProductService,
        "user": UserService,
        "category": CategoryService,
    }

    @classmethod
    def create_service(cls, service_type: str) -> Service:
        """
        Factory method to create services.

        Args:
            service_type: Type of service to create

        Returns:
            Service instance

        Raises:
            ValueError: If service type is not supported
        """
        logger = logging.getLogger(__name__)

        if service_type.lower() not in cls._services:
            available_services = ", ".join(cls._services.keys())
            error_msg = (
                f"Unknown service type: {service_type}. Available: {available_services}"
            )
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)

        service_class = cls._services[service_type.lower()]
        service_instance = service_class()

        logger.info(f"🏭 Created {service_instance.get_service_name()} instance")
        return service_instance

    @classmethod
    def get_available_services(cls) -> list:
        """Get list of available service types."""
        return list(cls._services.keys())

    @classmethod
    def register_service(cls, service_type: str, service_class: type):
        """Register a new service type."""
        if not issubclass(service_class, Service):
            raise ValueError("Service class must inherit from Service")

        cls._services[service_type.lower()] = service_class
        logger = logging.getLogger(__name__)
        logger.info(f"📝 Registered new service: {service_type}")


# ==============================
# 3. ABSTRACT METHOD PATTERN
# ==============================


class NotificationService(ABC):
    """
    Abstract Method Pattern Implementation for Notification Services

    Defines the interface for different notification methods.
    """

    @abstractmethod
    def send_notification(self, recipient: str, message: str, **kwargs) -> bool:
        """
        Send notification to recipient.

        Args:
            recipient: Notification recipient
            message: Notification message
            **kwargs: Additional parameters

        Returns:
            True if notification sent successfully, False otherwise
        """
        pass

    @abstractmethod
    def get_notification_method(self) -> str:
        """Get the notification method name."""
        pass

    @abstractmethod
    def validate_recipient(self, recipient: str) -> bool:
        """Validate recipient format."""
        pass


class EmailNotificationService(NotificationService):
    """Concrete implementation of email notification service."""

    def send_notification(
        self, recipient: str, message: str, subject: str = "Notification", **kwargs
    ) -> bool:
        """Send email notification."""
        logger = logging.getLogger(__name__)

        if not self.validate_recipient(recipient):
            logger.error(f"❌ Invalid email recipient: {recipient}")
            return False

        logger.info(f"📧 Sending email to {recipient}")
        logger.info(f"   Subject: {subject}")
        logger.info(f"   Message: {message}")

        # Simulate email sending
        return True

    def get_notification_method(self) -> str:
        return "Email"

    def validate_recipient(self, recipient: str) -> bool:
        """Validate email format."""
        return "@" in recipient and "." in recipient.split("@")[-1]


class SMSNotificationService(NotificationService):
    """Concrete implementation of SMS notification service."""

    def send_notification(
        self, recipient: str, message: str, priority: str = "normal", **kwargs
    ) -> bool:
        """Send SMS notification."""
        logger = logging.getLogger(__name__)

        if not self.validate_recipient(recipient):
            logger.error(f"❌ Invalid phone number: {recipient}")
            return False

        logger.info(f"📱 Sending SMS to {recipient}")
        logger.info(f"   Priority: {priority}")
        logger.info(f"   Message: {message}")

        # Simulate SMS sending
        return True

    def get_notification_method(self) -> str:
        return "SMS"

    def validate_recipient(self, recipient: str) -> bool:
        """Validate phone number format."""
        return recipient.isdigit() and len(recipient) >= 10


class PushNotificationService(NotificationService):
    """Concrete implementation of push notification service."""

    def send_notification(
        self, recipient: str, message: str, device_type: str = "mobile", **kwargs
    ) -> bool:
        """Send push notification."""
        logger = logging.getLogger(__name__)

        if not self.validate_recipient(recipient):
            logger.error(f"❌ Invalid device token: {recipient}")
            return False

        logger.info(f"🔔 Sending push notification to {recipient}")
        logger.info(f"   Device Type: {device_type}")
        logger.info(f"   Message: {message}")

        # Simulate push notification sending
        return True

    def get_notification_method(self) -> str:
        return "Push"

    def validate_recipient(self, recipient: str) -> bool:
        """Validate device token format."""
        return len(recipient) >= 20  # Simple validation


class NotificationManager:
    """
    Manager class that uses different notification services.
    Demonstrates the Abstract Method pattern usage.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.notification_services: Dict[str, NotificationService] = {}
        self._register_default_services()

    def _register_default_services(self):
        """Register default notification services."""
        self.notification_services["email"] = EmailNotificationService()
        self.notification_services["sms"] = SMSNotificationService()
        self.notification_services["push"] = PushNotificationService()

        self.logger.info("📋 Registered default notification services")

    def send_notification(
        self, method: str, recipient: str, message: str, **kwargs
    ) -> bool:
        """
        Send notification using specified method.

        Args:
            method: Notification method (email, sms, push)
            recipient: Notification recipient
            message: Notification message
            **kwargs: Additional parameters

        Returns:
            True if notification sent successfully
        """
        if method not in self.notification_services:
            available = ", ".join(self.notification_services.keys())
            error_msg = f"Unknown notification method: {method}. Available: {available}"
            self.logger.error(f"❌ {error_msg}")
            return False

        service = self.notification_services[method]
        self.logger.info(
            f"🚀 Using {service.get_notification_method()} notification service"
        )

        return service.send_notification(recipient, message, **kwargs)

    def get_available_methods(self) -> list:
        """Get list of available notification methods."""
        return list(self.notification_services.keys())

    def register_notification_service(self, method: str, service: NotificationService):
        """Register a new notification service."""
        self.notification_services[method] = service
        self.logger.info(f"📝 Registered new notification method: {method}")


# ==============================
# UTILITY FUNCTIONS
# ==============================


def demonstrate_patterns():
    """Demonstrate all three design patterns in action."""
    logger = logging.getLogger(__name__)

    print("\n" + "=" * 60)
    print("🎯 DESIGN PATTERNS DEMONSTRATION")
    print("=" * 60)

    # 1. Singleton Pattern Demo
    print("\n1️⃣ SINGLETON PATTERN - Database Connection Manager")
    print("-" * 50)

    db1 = DatabaseConnectionManager()
    db2 = DatabaseConnectionManager()

    print(f"DB Manager 1 ID: {id(db1)}")
    print(f"DB Manager 2 ID: {id(db2)}")
    print(f"Same instance? {db1 is db2}")

    db1.set_connection_config({"host": "localhost", "port": 5432})
    connection = db1.get_connection()
    print(f"Connection from DB1: {connection}")
    print(f"Connection status from DB2: {db2.get_connection_status()}")

    # 2. Factory Method Pattern Demo
    print("\n2️⃣ FACTORY METHOD PATTERN - Service Factory")
    print("-" * 50)

    available_services = ServiceFactory.get_available_services()
    print(f"Available services: {available_services}")

    for service_type in available_services:
        service = ServiceFactory.create_service(service_type)
        result = service.execute(1, "get")
        print(f"{service.get_service_name()} result: {result}")

    # 3. Abstract Method Pattern Demo
    print("\n3️⃣ ABSTRACT METHOD PATTERN - Notification Services")
    print("-" * 50)

    notification_manager = NotificationManager()
    available_methods = notification_manager.get_available_methods()
    print(f"Available notification methods: {available_methods}")

    # Test different notification methods
    test_notifications = [
        (
            "email",
            "user@example.com",
            "Welcome to our service!",
            {"subject": "Welcome"},
        ),
        ("sms", "1234567890", "Your order has been shipped!", {"priority": "high"}),
        (
            "push",
            "device_token_1234567890abcdef",
            "New update available!",
            {"device_type": "mobile"},
        ),
    ]

    for method, recipient, message, kwargs in test_notifications:
        success = notification_manager.send_notification(
            method, recipient, message, **kwargs
        )
        status = "✅ Success" if success else "❌ Failed"
        print(f"{method.upper()} notification: {status}")

    print("\n" + "=" * 60)
    print("🎉 DESIGN PATTERNS DEMONSTRATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    # Configure basic logging for demonstration
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    demonstrate_patterns()
