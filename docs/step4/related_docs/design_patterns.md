# Design Patterns Implementation

## Overview

This document outlines the design patterns implemented throughout the application to solve common software design problems and promote code reusability, maintainability, and scalability.

## Creational Patterns

### 1. Singleton Pattern

#### Configuration Management
```python
# src/core/config.py
class EnvironmentConfig(BaseSettings):
    """Singleton configuration instance"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# Global settings instance
settings = EnvironmentConfig()
```

#### Logger Configuration
```python
# src/core/logging.py
class LoggerConfig:
    """Singleton logger configuration"""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self):
        """Setup structured logger"""
        self._logger = structlog.get_logger()
```

### 2. Factory Pattern

#### Service Factory
```python
# src/factories/service_factory.py
class ServiceFactory:
    """Factory for creating service instances"""
    
    @staticmethod
    def create_auth_service() -> AuthService:
        """Create authentication service"""
        return AuthService(
            user_repository=RepositoryFactory.create_user_repository(),
            password_service=ServiceFactory.create_password_service(),
            token_service=ServiceFactory.create_token_service()
        )
    
    @staticmethod
    def create_task_service() -> TaskService:
        """Create task service"""
        return TaskService(
            task_repository=RepositoryFactory.create_task_repository(),
            validator=ValidatorFactory.create_task_validator()
        )
```

#### Repository Factory
```python
# src/factories/repository_factory.py
class RepositoryFactory:
    """Factory for creating repository instances"""
    
    @staticmethod
    def create_user_repository() -> UserRepository:
        """Create user repository"""
        return UserRepository()
    
    @staticmethod
    def create_task_repository() -> TaskRepository:
        """Create task repository"""
        return TaskRepository()
```

### 3. Builder Pattern

#### Configuration Builder
```python
# src/builders/config_builder.py
class ConfigBuilder:
    """Builder for application configuration"""
    
    def __init__(self):
        self._config = {}
    
    def with_database(self, url: str) -> 'ConfigBuilder':
        """Add database configuration"""
        self._config['DATABASE_URL'] = url
        return self
    
    def with_logging(self, level: str) -> 'ConfigBuilder':
        """Add logging configuration"""
        self._config['LOG_LEVEL'] = level
        return self
    
    def with_auth(self, jwt_secret: str) -> 'ConfigBuilder':
        """Add authentication configuration"""
        self._config['JWT_SECRET_KEY'] = jwt_secret
        return self
    
    def build(self) -> dict:
        """Build final configuration"""
        return self._config.copy()

# Usage
config = (ConfigBuilder()
          .with_database("postgresql://localhost/test")
          .with_logging("INFO")
          .with_auth("secret-key")
          .build())
```

#### Query Builder
```python
# src/builders/query_builder.py
class QueryBuilder:
    """Builder for database queries"""
    
    def __init__(self, model_class):
        self.query = db.session.query(model_class)
    
    def where(self, **kwargs) -> 'QueryBuilder':
        """Add where conditions"""
        for key, value in kwargs.items():
            self.query = self.query.filter(getattr(model_class, key) == value)
        return self
    
    def order_by(self, field: str, direction: str = 'asc') -> 'QueryBuilder':
        """Add ordering"""
        column = getattr(model_class, field)
        if direction == 'desc':
            column = column.desc()
        self.query = self.query.order_by(column)
        return self
    
    def limit(self, count: int) -> 'QueryBuilder':
        """Add limit"""
        self.query = self.query.limit(count)
        return self
    
    def build(self):
        """Build final query"""
        return self.query
```

## Structural Patterns

### 1. Adapter Pattern

#### Database Adapter
```python
# src/adapters/database_adapter.py
class DatabaseAdapter:
    """Adapter for different database types"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.db_type = self._detect_db_type()
    
    def _detect_db_type(self) -> str:
        """Detect database type from connection string"""
        if 'postgresql' in self.connection_string:
            return 'postgresql'
        elif 'mysql' in self.connection_string:
            return 'mysql'
        else:
            return 'sqlite'
    
    def get_connection(self):
        """Get database connection"""
        if self.db_type == 'postgresql':
            return PostgreSQLConnection(self.connection_string)
        elif self.db_type == 'mysql':
            return MySQLConnection(self.connection_string)
        else:
            return SQLiteConnection(self.connection_string)
```

#### Logger Adapter
```python
# src/adapters/logger_adapter.py
class LoggerAdapter:
    """Adapter for different logging frameworks"""
    
    def __init__(self, logger_type: str):
        self.logger_type = logger_type
        self.logger = self._create_logger()
    
    def _create_logger(self):
        """Create logger based on type"""
        if self.logger_type == 'structlog':
            return StructlogLogger()
        elif self.logger_type == 'python':
            return PythonLogger()
        else:
            return DefaultLogger()
    
    def log(self, level: str, message: str, **kwargs):
        """Log message"""
        self.logger.log(level, message, **kwargs)
```

### 2. Decorator Pattern

#### Authentication Decorator
```python
# src/decorators/auth_decorators.py
def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        try:
            user = decode_token(token)
            g.current_user = user
            return f(*args, **kwargs)
        except Exception:
            return jsonify({'error': 'Invalid token'}), 401
    
    return decorated_function

def rate_limit(limit: int, window: int):
    """Decorator for rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            key = f"rate_limit:{client_ip}"
            
            if redis.get(key):
                count = int(redis.get(key))
                if count >= limit:
                    return jsonify({'error': 'Rate limit exceeded'}), 429
            
            redis.setex(key, window, count + 1)
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
```

#### Validation Decorator
```python
# src/decorators/validation_decorators.py
def validate_request(schema_class):
    """Decorator to validate request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = request.get_json()
                validated_data = schema_class(**data)
                g.validated_data = validated_data.dict()
                return f(*args, **kwargs)
            except ValidationError as e:
                return jsonify({'error': e.errors()}), 400
        
        return decorated_function
    return decorator
```

### 3. Facade Pattern

#### Application Facade
```python
# src/facades/app_facade.py
class ApplicationFacade:
    """Facade for application operations"""
    
    def __init__(self):
        self.auth_service = ServiceFactory.create_auth_service()
        self.task_service = ServiceFactory.create_task_service()
        self.user_service = ServiceFactory.create_user_service()
    
    def register_user(self, user_data: dict) -> dict:
        """Register new user"""
        user = self.user_service.create(user_data)
        token = self.auth_service.generate_token(user)
        return {'user': user.to_dict(), 'token': token}
    
    def create_task(self, task_data: dict, user_id: int) -> dict:
        """Create task for user"""
        task = self.task_service.create(task_data, user_id)
        return task.to_dict()
    
    def get_user_tasks(self, user_id: int) -> list:
        """Get all tasks for user"""
        tasks = self.task_service.get_user_tasks(user_id)
        return [task.to_dict() for task in tasks]
```

## Behavioral Patterns

### 1. Strategy Pattern

#### Validation Strategy
```python
# src/strategies/validation_strategy.py
class ValidationStrategy:
    """Base validation strategy"""
    
    def validate(self, data: dict) -> bool:
        pass

class EmailValidationStrategy(ValidationStrategy):
    """Email validation strategy"""
    
    def validate(self, data: dict) -> bool:
        email = data.get('email', '')
        return '@' in email and '.' in email

class PasswordValidationStrategy(ValidationStrategy):
    """Password validation strategy"""
    
    def validate(self, data: dict) -> bool:
        password = data.get('password', '')
        return len(password) >= 8 and any(c.isupper() for c in password)

class ValidationContext:
    """Context for validation strategies"""
    
    def __init__(self, strategy: ValidationStrategy):
        self.strategy = strategy
    
    def set_strategy(self, strategy: ValidationStrategy):
        self.strategy = strategy
    
    def validate(self, data: dict) -> bool:
        return self.strategy.validate(data)
```

#### Authentication Strategy
```python
# src/strategies/auth_strategy.py
class AuthenticationStrategy:
    """Base authentication strategy"""
    
    def authenticate(self, credentials: dict) -> Optional[User]:
        pass

class JWTAuthenticationStrategy(AuthenticationStrategy):
    """JWT authentication strategy"""
    
    def authenticate(self, credentials: dict) -> Optional[User]:
        token = credentials.get('token')
        try:
            payload = decode_jwt_token(token)
            return User.query.get(payload['user_id'])
        except Exception:
            return None

class BasicAuthStrategy(AuthenticationStrategy):
    """Basic authentication strategy"""
    
    def authenticate(self, credentials: dict) -> Optional[User]:
        username = credentials.get('username')
        password = credentials.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and verify_password(password, user.password_hash):
            return user
        return None
```

### 2. Observer Pattern

#### Event System
```python
# src/observers/event_system.py
class EventObserver:
    """Base event observer"""
    
    def update(self, event_type: str, data: dict):
        pass

class TaskEventObserver(EventObserver):
    """Observer for task events"""
    
    def update(self, event_type: str, data: dict):
        if event_type == 'task_created':
            self._handle_task_created(data)
        elif event_type == 'task_updated':
            self._handle_task_updated(data)
    
    def _handle_task_created(self, data: dict):
        """Handle task creation event"""
        logger.info(f"Task created: {data['task_id']}")
    
    def _handle_task_updated(self, data: dict):
        """Handle task update event"""
        logger.info(f"Task updated: {data['task_id']}")

class EventSubject:
    """Subject for event notifications"""
    
    def __init__(self):
        self.observers = []
    
    def attach(self, observer: EventObserver):
        """Attach observer"""
        self.observers.append(observer)
    
    def detach(self, observer: EventObserver):
        """Detach observer"""
        self.observers.remove(observer)
    
    def notify(self, event_type: str, data: dict):
        """Notify all observers"""
        for observer in self.observers:
            observer.update(event_type, data)
```

### 3. Command Pattern

#### Command Queue
```python
# src/commands/command_pattern.py
class Command:
    """Base command interface"""
    
    def execute(self):
        pass

class CreateTaskCommand(Command):
    """Command to create task"""
    
    def __init__(self, task_data: dict, user_id: int):
        self.task_data = task_data
        self.user_id = user_id
    
    def execute(self):
        """Execute task creation"""
        task = Task(**self.task_data, user_id=self.user_id)
        db.session.add(task)
        db.session.commit()
        return task

class UpdateTaskCommand(Command):
    """Command to update task"""
    
    def __init__(self, task_id: int, update_data: dict):
        self.task_id = task_id
        self.update_data = update_data
    
    def execute(self):
        """Execute task update"""
        task = Task.query.get(self.task_id)
        for key, value in self.update_data.items():
            setattr(task, key, value)
        db.session.commit()
        return task

class CommandInvoker:
    """Invoker for command execution"""
    
    def __init__(self):
        self.history = []
    
    def execute_command(self, command: Command):
        """Execute command and record history"""
        result = command.execute()
        self.history.append(command)
        return result
    
    def get_history(self) -> list:
        """Get command execution history"""
        return self.history.copy()
```

## Architectural Patterns

### 1. Repository Pattern

#### Base Repository
```python
# src/repositories/base_repository.py
class BaseRepository:
    """Base repository interface"""
    
    def __init__(self, model_class):
        self.model_class = model_class
    
    def get_by_id(self, id: int) -> Optional[Any]:
        """Get entity by ID"""
        return self.model_class.query.get(id)
    
    def get_all(self) -> list:
        """Get all entities"""
        return self.model_class.query.all()
    
    def create(self, data: dict) -> Any:
        """Create new entity"""
        entity = self.model_class(**data)
        db.session.add(entity)
        db.session.commit()
        return entity
    
    def update(self, id: int, data: dict) -> Any:
        """Update entity"""
        entity = self.get_by_id(id)
        for key, value in data.items():
            setattr(entity, key, value)
        db.session.commit()
        return entity
    
    def delete(self, id: int) -> bool:
        """Delete entity"""
        entity = self.get_by_id(id)
        if entity:
            db.session.delete(entity)
            db.session.commit()
            return True
        return False
```

### 2. Service Layer Pattern

#### Service Layer
```python
# src/services/base_service.py
class BaseService:
    """Base service layer"""
    
    def __init__(self, repository: BaseRepository):
        self.repository = repository
    
    def get_by_id(self, id: int) -> Optional[Any]:
        """Get entity by ID"""
        return self.repository.get_by_id(id)
    
    def get_all(self) -> list:
        """Get all entities"""
        return self.repository.get_all()
    
    def create(self, data: dict) -> Any:
        """Create new entity"""
        return self.repository.create(data)
    
    def update(self, id: int, data: dict) -> Any:
        """Update entity"""
        return self.repository.update(id, data)
    
    def delete(self, id: int) -> bool:
        """Delete entity"""
        return self.repository.delete(id)
```

## Benefits of Design Patterns

### 1. Code Reusability
- Common solutions to recurring problems
- Reduced code duplication
- Consistent implementation across the application

### 2. Maintainability
- Clear separation of concerns
- Easy to understand and modify
- Well-defined interfaces

### 3. Scalability
- Flexible architecture that can grow
- Easy to add new features
- Modular design supports expansion

### 4. Testability
- Isolated components
- Easy to mock dependencies
- Clear interfaces for testing

## Pattern Selection Guidelines

### When to Use Which Pattern

1. **Singleton**: When you need exactly one instance (configuration, logger)
2. **Factory**: When object creation is complex or varies
3. **Builder**: When object construction has many steps
4. **Strategy**: When you need interchangeable algorithms
5. **Observer**: When you need event-driven communication
6. **Command**: When you need to queue or undo operations
7. **Repository**: When you need to abstract data access
8. **Service**: When you need to encapsulate business logic

## Pattern Combinations

### Common Combinations

1. **Factory + Strategy**: Create different strategy implementations
2. **Repository + Service**: Separate data access from business logic
3. **Observer + Command**: Event-driven command execution
4. **Builder + Factory**: Complex object creation with factories

## Conclusion

The application implements a comprehensive set of design patterns that provide:
- **Consistent architecture** across all components
- **Flexible design** that accommodates change
- **Maintainable code** that's easy to understand and extend
- **Scalable structure** that supports growth

These patterns serve as proven solutions to common software design problems and provide a solid foundation for continued development.
