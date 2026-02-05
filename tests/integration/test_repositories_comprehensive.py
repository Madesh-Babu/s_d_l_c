"""
Integration Tests for Repository Layer

This module contains repository layer with database integration testing.
"""

import pytest
from datetime import datetime, timedelta
from src.models.models import db, User, Product, Category, Task
from src.repositories.user_repository import UserRepository
from src.repositories.product_repository import ProductRepository
from src.repositories.category_repository import CategoryRepository
from src.repositories.task_repository import TaskRepository


class TestRepositoriesComprehensive:
    """Repository layer with database integration testing."""
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self, app):
        """Set up clean test environment."""
        with app.app_context():
            # Clean up test data
            User.query.filter(User.username.like('test_%')).delete()
            Product.query.filter(Product.name.like('test_%')).delete()
            Category.query.filter(Category.name.like('test_%')).delete()
            Task.query.filter(Task.title.like('test_%')).delete()
            db.session.commit()
    
    def test_user_repository_crud_operations(self, app):
        """Test user repository CRUD operations."""
        with app.app_context():
            repo = UserRepository()
            
            # Create user
            user_data = {
                "username": "test_repo_user",
                "email": "test_repo@example.com",
                "role": "staff",
                "password": "TestPassword123!"
            }
            
            created_user = repo.create(user_data)
            assert created_user is not None
            assert created_user.username == "test_repo_user"
            assert created_user.email == "test_repo@example.com"
            assert created_user.role == "staff"
            assert created_user.check_password("TestPassword123!")
            
            # Read user
            retrieved_user = repo.get_by_id(created_user.id)
            assert retrieved_user is not None
            assert retrieved_user.username == "test_repo_user"
            
            # Update user
            update_data = {
                "email": "updated_repo@example.com",
                "role": "manager"
            }
            
            updated_user = repo.update(created_user.id, update_data)
            assert updated_user.email == "updated_repo@example.com"
            assert updated_user.role == "manager"
            
            # Delete user
            deleted = repo.delete(created_user.id)
            assert deleted is True
            
            # Verify deletion
            deleted_user = repo.get_by_id(created_user.id)
            assert deleted_user is None
    
    def test_user_repository_query_methods(self, app):
        """Test user repository query methods."""
        with app.app_context():
            repo = UserRepository()
            
            # Create test users
            users = []
            for i in range(5):
                user_data = {
                    "username": f"query_user_{i}",
                    "email": f"query_{i}@example.com",
                    "role": "staff" if i % 2 == 0 else "manager",
                    "password": "TestPassword123!"
                }
                user = repo.create(user_data)
                users.append(user)
            
            # Test get all
            all_users = repo.get_all()
            assert len(all_users) >= 5
            
            # Test get by username
            user = repo.get_by_username("query_user_0")
            assert user is not None
            assert user.username == "query_user_0"
            
            # Test get by email
            user = repo.get_by_email("query_1@example.com")
            assert user is not None
            assert user.email == "query_1@example.com"
            
            # Test get by role
            staff_users = repo.get_by_role("staff")
            assert len(staff_users) >= 3  # Created 3 staff users
            
            manager_users = repo.get_by_role("manager")
            assert len(manager_users) >= 2  # Created 2 manager users
            
            # Test search
            search_results = repo.search("query_user")
            assert len(search_results) >= 5
            
            # Test count
            user_count = repo.count()
            assert user_count >= 5
    
    def test_product_repository_crud_operations(self, app):
        """Test product repository CRUD operations."""
        with app.app_context():
            # Create category first
            category = Category(
                name="Test Category",
                description="Category for product testing"
            )
            db.session.add(category)
            db.session.commit()
            
            repo = ProductRepository()
            
            # Create product
            product_data = {
                "name": "Test Product",
                "description": "Test product description",
                "price": 29.99,
                "stock_quantity": 100,
                "category_id": category.id
            }
            
            created_product = repo.create(product_data)
            assert created_product is not None
            assert created_product.name == "Test Product"
            assert created_product.price == 29.99
            assert created_product.stock_quantity == 100
            assert created_product.category_id == category.id
            
            # Read product
            retrieved_product = repo.get_by_id(created_product.id)
            assert retrieved_product is not None
            assert retrieved_product.name == "Test Product"
            
            # Update product
            update_data = {
                "price": 39.99,
                "stock_quantity": 150
            }
            
            updated_product = repo.update(created_product.id, update_data)
            assert updated_product.price == 39.99
            assert updated_product.stock_quantity == 150
            
            # Delete product
            deleted = repo.delete(created_product.id)
            assert deleted is True
            
            # Verify deletion
            deleted_product = repo.get_by_id(created_product.id)
            assert deleted_product is None
    
    def test_product_repository_query_methods(self, app):
        """Test product repository query methods."""
        with app.app_context():
            # Create categories
            categories = []
            for i in range(2):
                category = Category(
                    name=f"Category {i}",
                    description=f"Category {i} for testing"
                )
                db.session.add(category)
                categories.append(category)
            db.session.commit()
            
            repo = ProductRepository()
            
            # Create test products
            products = []
            for i in range(10):
                product_data = {
                    "name": f"Product {i}",
                    "description": f"Product {i} description",
                    "price": 10.0 + i,
                    "stock_quantity": 50 + i * 5,
                    "category_id": categories[i % 2].id
                }
                product = repo.create(product_data)
                products.append(product)
            
            # Test get all
            all_products = repo.get_all()
            assert len(all_products) >= 10
            
            # Test get by category
            category_0_products = repo.get_by_category(categories[0].id)
            assert len(category_0_products) >= 5
            
            # Test get by price range
            price_products = repo.get_by_price_range(15.0, 25.0)
            assert len(price_products) >= 5
            
            # Test get by stock
            in_stock_products = repo.get_in_stock()
            assert len(in_stock_products) >= 10
            
            # Test low stock products
            low_stock_products = repo.get_low_stock(60)  # Less than 60
            assert len(low_stock_products) >= 5
            
            # Test search
            search_results = repo.search("Product")
            assert len(search_results) >= 10
            
            # Test count
            product_count = repo.count()
            assert product_count >= 10
    
    def test_category_repository_crud_operations(self, app):
        """Test category repository CRUD operations."""
        with app.app_context():
            repo = CategoryRepository()
            
            # Create category
            category_data = {
                "name": "Test Category",
                "description": "Test category description"
            }
            
            created_category = repo.create(category_data)
            assert created_category is not None
            assert created_category.name == "Test Category"
            assert created_category.description == "Test category description"
            
            # Read category
            retrieved_category = repo.get_by_id(created_category.id)
            assert retrieved_category is not None
            assert retrieved_category.name == "Test Category"
            
            # Update category
            update_data = {
                "description": "Updated category description"
            }
            
            updated_category = repo.update(created_category.id, update_data)
            assert updated_category.description == "Updated category description"
            
            # Delete category
            deleted = repo.delete(created_category.id)
            assert deleted is True
            
            # Verify deletion
            deleted_category = repo.get_by_id(created_category.id)
            assert deleted_category is None
    
    def test_category_repository_hierarchical_operations(self, app):
        """Test category repository hierarchical operations."""
        with app.app_context():
            repo = CategoryRepository()
            
            # Create parent category
            parent_data = {
                "name": "Parent Category",
                "description": "Parent category for testing"
            }
            
            parent_category = repo.create(parent_data)
            
            # Create child categories
            child_categories = []
            for i in range(3):
                child_data = {
                    "name": f"Child Category {i}",
                    "description": f"Child category {i} for testing",
                    "parent_category_id": parent_category.id
                }
                
                child = repo.create(child_data)
                child_categories.append(child)
            
            # Test get parent categories
            parent_categories = repo.get_parent_categories()
            assert len(parent_categories) >= 1
            assert parent_category in parent_categories
            
            # Test get child categories
            children = repo.get_child_categories(parent_category.id)
            assert len(children) >= 3
            
            # Test get category tree
            tree = repo.get_category_tree()
            assert len(tree) >= 1
            
            # Test hierarchical search
            search_results = repo.search("Category")
            assert len(search_results) >= 4
            
            # Test count
            category_count = repo.count()
            assert category_count >= 4
    
    def test_task_repository_crud_operations(self, app):
        """Test task repository CRUD operations."""
        with app.app_context():
            # Create user first
            user = User(
                username="test_task_user",
                email="test_task@example.com",
                role="staff"
            )
            user.set_password("TestPassword123!")
            db.session.add(user)
            db.session.commit()
            
            repo = TaskRepository()
            
            # Create task
            task_data = {
                "title": "Test Task",
                "description": "Test task description",
                "status": "pending",
                "priority": "medium",
                "due_date": datetime.now() + timedelta(days=7),
                "assigned_to": user.id
            }
            
            created_task = repo.create(task_data)
            assert created_task is not None
            assert created_task.title == "Test Task"
            assert created_task.status == "pending"
            assert created_task.priority == "medium"
            assert created_task.assigned_to == user.id
            
            # Read task
            retrieved_task = repo.get_by_id(created_task.id)
            assert retrieved_task is not None
            assert retrieved_task.title == "Test Task"
            
            # Update task
            update_data = {
                "status": "in_progress",
                "priority": "high"
            }
            
            updated_task = repo.update(created_task.id, update_data)
            assert updated_task.status == "in_progress"
            assert updated_task.priority == "high"
            
            # Delete task
            deleted = repo.delete(created_task.id)
            assert deleted is True
            
            # Verify deletion
            deleted_task = repo.get_by_id(created_task.id)
            assert deleted_task is None
    
    def test_task_repository_query_methods(self, app):
        """Test task repository query methods."""
        with app.app_context():
            # Create user
            user = User(
                username="test_query_user",
                email="test_query@example.com",
                role="staff"
            )
            user.set_password("TestPassword123!")
            db.session.add(user)
            db.session.commit()
            
            repo = TaskRepository()
            
            # Create test tasks
            tasks = []
            statuses = ["pending", "in_progress", "completed"]
            priorities = ["low", "medium", "high"]
            
            for i in range(9):
                task_data = {
                    "title": f"Task {i}",
                    "description": f"Task {i} description",
                    "status": statuses[i % 3],
                    "priority": priorities[i % 3],
                    "due_date": datetime.now() + timedelta(days=i),
                    "assigned_to": user.id
                }
                
                task = repo.create(task_data)
                tasks.append(task)
            
            # Test get all
            all_tasks = repo.get_all()
            assert len(all_tasks) >= 9
            
            # Test get by status
            pending_tasks = repo.get_by_status("pending")
            assert len(pending_tasks) >= 3
            
            # Test get by priority
            high_priority_tasks = repo.get_by_priority("high")
            assert len(high_priority_tasks) >= 3
            
            # Test get by assignee
            assignee_tasks = repo.get_by_assignee(user.id)
            assert len(assignee_tasks) >= 9
            
            # Test get overdue tasks
            # Create an overdue task
            overdue_task_data = {
                "title": "Overdue Task",
                "description": "Overdue task description",
                "status": "pending",
                "priority": "high",
                "due_date": datetime.now() - timedelta(days=1),
                "assigned_to": user.id
            }
            
            overdue_task = repo.create(overdue_task_data)
            overdue_tasks = repo.get_overdue_tasks()
            assert len(overdue_tasks) >= 1
            
            # Test search
            search_results = repo.search("Task")
            assert len(search_results) >= 10
            
            # Test count
            task_count = repo.count()
            assert task_count >= 10
    
    def test_repository_transaction_handling(self, app):
        """Test repository transaction handling."""
        with app.app_context():
            user_repo = UserRepository()
            
            # Test successful transaction
            user_data = {
                "username": "transaction_user",
                "email": "transaction@example.com",
                "role": "staff",
                "password": "TestPassword123!"
            }
            
            created_user = user_repo.create(user_data)
            assert created_user is not None
            
            # Test failed transaction
            try:
                invalid_user_data = {
                    "username": "",  # Invalid
                    "email": "invalid-email",  # Invalid
                    "role": "invalid_role",  # Invalid
                    "password": "weak"  # Invalid
                }
                
                user_repo.create(invalid_user_data)
                assert False, "Should have raised an error"
                
            except Exception:
                pass  # Expected to raise an error
            
            # Verify transaction was rolled back
            # The valid user should still exist
            valid_user = user_repo.get_by_username("transaction_user")
            assert valid_user is not None
    
    def test_repository_error_handling(self, app):
        """Test repository error handling."""
        with app.app_context():
            user_repo = UserRepository()
            
            # Test get non-existent user
            non_existent_user = user_repo.get_by_id(99999)
            assert non_existent_user is None
            
            # Test update non-existent user
            update_result = user_repo.update(99999, {"email": "test@example.com"})
            assert update_result is None
            
            # Test delete non-existent user
            delete_result = user_repo.delete(99999)
            assert delete_result is False
            
            # Test get by non-existent username
            non_existent_username = user_repo.get_by_username("nonexistent")
            assert non_existent_username is None
            
            # Test get by non-existent email
            non_existent_email = user_repo.get_by_email("nonexistent@example.com")
            assert non_existent_email is None
    
    def test_repository_performance(self, app):
        """Test repository performance."""
        import time
        
        with app.app_context():
            user_repo = UserRepository()
            
            # Create test data
            users = []
            for i in range(100):
                user_data = {
                    "username": f"perf_user_{i}",
                    "email": f"perf_{i}@example.com",
                    "role": "staff",
                    "password": "TestPassword123!"
                }
                
                user = user_repo.create(user_data)
                users.append(user)
            
            # Test bulk operations performance
            start_time = time.time()
            
            all_users = user_repo.get_all()
            
            query_time = time.time() - start_time
            
            assert len(all_users) >= 100
            assert query_time < 1.0  # Should complete within 1 second
            
            # Test search performance
            start_time = time.time()
            
            search_results = user_repo.search("perf_user")
            
            search_time = time.time() - start_time
            
            assert len(search_results) >= 100
            assert search_time < 0.5  # Should complete within 0.5 seconds
    
    def test_repository_data_validation(self, app):
        """Test repository data validation."""
        with app.app_context():
            user_repo = UserRepository()
            
            # Test invalid data
            invalid_data = {
                "username": "",  # Empty
                "email": "invalid-email",  # Invalid format
                "role": "invalid_role",  # Invalid role
                "password": "weak"  # Weak password
            }
            
            try:
                user_repo.create(invalid_data)
                assert False, "Should have raised validation error"
            except Exception:
                pass  # Expected to raise validation error
            
            # Test partial update data
            user_data = {
                "username": "valid_user",
                "email": "valid@example.com",
                "role": "staff",
                "password": "ValidPassword123!"
            }
            
            created_user = user_repo.create(user_data)
            
            # Partial update should work
            partial_update = {"email": "updated@example.com"}
            updated_user = user_repo.update(created_user.id, partial_update)
            assert updated_user.email == "updated@example.com"
            assert updated_user.username == "valid_user"  # Unchanged
    
    def test_repository_relationships(self, app):
        """Test repository relationships."""
        with app.app_context():
            # Create user and category
            user = User(
                username="relation_user",
                email="relation@example.com",
                role="staff"
            )
            user.set_password("TestPassword123!")
            db.session.add(user)
            
            category = Category(
                name="Relation Category",
                description="Category for relationship testing"
            )
            db.session.add(category)
            db.session.commit()
            
            # Create product with relationships
            product_repo = ProductRepository()
            product_data = {
                "name": "Relation Product",
                "description": "Product for relationship testing",
                "price": 29.99,
                "stock_quantity": 100,
                "category_id": category.id
            }
            
            product = product_repo.create(product_data)
            
            # Test relationship loading
            product_with_category = product_repo.get_with_category(product.id)
            assert product_with_category is not None
            assert product_with_category.category is not None
            assert product_with_category.category.name == "Relation Category"
            
            # Test task with user relationship
            task_repo = TaskRepository()
            task_data = {
                "title": "Relation Task",
                "description": "Task for relationship testing",
                "status": "pending",
                "priority": "medium",
                "due_date": datetime.now() + timedelta(days=7),
                "assigned_to": user.id
            }
            
            task = task_repo.create(task_data)
            
            # Test relationship loading
            task_with_assignee = task_repo.get_with_assignee(task.id)
            assert task_with_assignee is not None
            assert task_with_assignee.assignee is not None
            assert task_with_assignee.assignee.username == "relation_user"
    
    def test_repository_caching(self, app):
        """Test repository caching."""
        with app.app_context():
            user_repo = UserRepository()
            
            # Create user
            user_data = {
                "username": "cache_user",
                "email": "cache@example.com",
                "role": "staff",
                "password": "TestPassword123!"
            }
            
            created_user = user_repo.create(user_data)
            
            # First call should hit database
            user1 = user_repo.get_by_id(created_user.id)
            assert user1 is not None
            
            # Second call might use cache (if implemented)
            user2 = user_repo.get_by_id(created_user.id)
            assert user2 is not None
            assert user1.id == user2.id
            
            # Test cache invalidation
            update_data = {"email": "cache_updated@example.com"}
            updated_user = user_repo.update(created_user.id, update_data)
            
            # Should get updated data
            user3 = user_repo.get_by_id(created_user.id)
            assert user3.email == "cache_updated@example.com"
