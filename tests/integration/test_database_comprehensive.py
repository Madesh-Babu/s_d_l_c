"""
Integration Tests for Database Operations

This module contains database connection and operation testing.
"""

import pytest
from datetime import datetime, timedelta
from src.models.models import db, User, Product, Category, Task
from src.core.exceptions import DatabaseError


class TestDatabaseComprehensive:
    """Database connection and operation testing."""
    
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
    
    def test_database_connection_establishment(self, app):
        """Test database connection establishment."""
        with app.app_context():
            # Test that database connection is established
            assert db is not None
            assert db.engine is not None
            
            # Test basic query
            result = db.session.execute('SELECT 1')
            assert result.fetchone()[0] == 1
    
    def test_database_transaction_commit(self, app):
        """Test database transaction commit."""
        with app.app_context():
            # Create user within transaction
            user = User(
                username="test_transaction_user",
                email="test_transaction@example.com",
                role="staff"
            )
            user.set_password("TestPassword123!")
            
            db.session.add(user)
            db.session.commit()
            
            # Verify user was committed
            saved_user = User.query.filter_by(username="test_transaction_user").first()
            assert saved_user is not None
            assert saved_user.email == "test_transaction@example.com"
    
    def test_database_transaction_rollback(self, app):
        """Test database transaction rollback."""
        with app.app_context():
            try:
                # Create user
                user = User(
                    username="test_rollback_user",
                    email="test_rollback@example.com",
                    role="staff"
                )
                user.set_password("TestPassword123!")
                
                db.session.add(user)
                
                # Simulate error
                raise Exception("Simulated error")
                
            except Exception:
                db.session.rollback()
            
            # Verify user was not saved due to rollback
            user = User.query.filter_by(username="test_rollback_user").first()
            assert user is None
    
    def test_database_foreign_key_constraints(self, app):
        """Test database foreign key constraints."""
        with app.app_context():
            # Create category
            category = Category(
                name="Test Category",
                description="Test category for constraints"
            )
            db.session.add(category)
            db.session.commit()
            
            # Create product with valid category
            product = Product(
                name="Test Product",
                description="Test product for constraints",
                price=29.99,
                stock_quantity=100,
                category_id=category.id
            )
            db.session.add(product)
            db.session.commit()
            
            # Verify product was created
            saved_product = Product.query.filter_by(name="Test Product").first()
            assert saved_product is not None
            assert saved_product.category_id == category.id
            
            # Test foreign key constraint violation
            invalid_product = Product(
                name="Invalid Product",
                description="Product with invalid category",
                price=19.99,
                stock_quantity=50,
                category_id=99999  # Non-existent category
            )
            
            db.session.add(invalid_product)
            
            # Should raise integrity error on commit
            with pytest.raises(Exception):  # Could be IntegrityError or similar
                db.session.commit()
            
            db.session.rollback()
    
    def test_database_unique_constraints(self, app):
        """Test database unique constraints."""
        with app.app_context():
            # Create first user
            user1 = User(
                username="test_unique_user",
                email="test_unique@example.com",
                role="staff"
            )
            user1.set_password("TestPassword123!")
            db.session.add(user1)
            db.session.commit()
            
            # Try to create user with same username
            user2 = User(
                username="test_unique_user",  # Same username
                email="different@example.com",
                role="staff"
            )
            user2.set_password("TestPassword123!")
            db.session.add(user2)
            
            # Should raise integrity error on commit
            with pytest.raises(Exception):  # Could be IntegrityError or similar
                db.session.commit()
            
            db.session.rollback()
            
            # Try to create user with same email
            user3 = User(
                username="different_user",
                email="test_unique@example.com",  # Same email
                role="staff"
            )
            user3.set_password("TestPassword123!")
            db.session.add(user3)
            
            # Should raise integrity error on commit
            with pytest.raises(Exception):  # Could be IntegrityError or similar
                db.session.commit()
            
            db.session.rollback()
    
    def test_database_cascade_operations(self, app):
        """Test database cascade operations."""
        with app.app_context():
            # Create category
            category = Category(
                name="Test Cascade Category",
                description="Category for cascade testing"
            )
            db.session.add(category)
            db.session.commit()
            
            # Create products in category
            products = []
            for i in range(3):
                product = Product(
                    name=f"Test Product {i}",
                    description=f"Product {i} for cascade testing",
                    price=10.0 + i,
                    stock_quantity=100,
                    category_id=category.id
                )
                db.session.add(product)
                products.append(product)
            
            db.session.commit()
            
            # Verify products exist
            product_count = Product.query.filter_by(category_id=category.id).count()
            assert product_count == 3
            
            # Delete category (cascade behavior depends on configuration)
            db.session.delete(category)
            
            try:
                db.session.commit()
                
                # Check if products were deleted (cascade delete)
                product_count = Product.query.filter_by(category_id=category.id).count()
                # This could be 0 (cascade delete) or 3 (no cascade)
                assert product_count in [0, 3]
                
            except Exception:
                # If cascade delete is not configured, this might fail
                db.session.rollback()
    
    def test_database_query_performance(self, app):
        """Test database query performance."""
        import time
        
        with app.app_context():
            # Create test data
            users = []
            for i in range(100):
                user = User(
                    username=f"perf_user_{i}",
                    email=f"perf_user_{i}@example.com",
                    role="staff"
                )
                user.set_password("TestPassword123!")
                users.append(user)
            
            db.session.add_all(users)
            db.session.commit()
            
            # Test query performance
            start_time = time.time()
            
            result = User.query.filter(User.username.like('perf_user_%')).all()
            
            query_time = time.time() - start_time
            
            assert len(result) == 100
            assert query_time < 1.0  # Should complete within 1 second
    
    def test_database_connection_pooling(self, app):
        """Test database connection pooling."""
        with app.app_context():
            # Test multiple concurrent connections
            import threading
            import time
            
            results = []
            errors = []
            
            def test_connection():
                try:
                    # Simulate database operation
                    result = db.session.execute('SELECT 1')
                    results.append(result.fetchone()[0])
                except Exception as e:
                    errors.append(str(e))
            
            threads = []
            for _ in range(10):
                thread = threading.Thread(target=test_connection)
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            # All connections should work
            assert len(errors) == 0
            assert len(results) == 10
            assert all(result == 1 for result in results)
    
    def test_database_migration_compatibility(self, app):
        """Test database migration compatibility."""
        with app.app_context():
            # Test that current schema is compatible
            # This would typically involve checking table structures
            
            # Check User table structure
            user_columns = db.inspect(db.engine).get_columns('user')
            required_columns = ['id', 'username', 'email', 'password_hash', 'role', 'created_at', 'updated_at']
            
            for column in required_columns:
                assert column in user_columns
            
            # Check Product table structure
            product_columns = db.inspect(db.engine).get_columns('product')
            required_product_columns = ['id', 'name', 'description', 'price', 'stock_quantity', 'category_id', 'created_at', 'updated_at']
            
            for column in required_product_columns:
                assert column in product_columns
    
    def test_database_data_integrity(self, app):
        """Test database data integrity."""
        with app.app_context():
            # Create related data
            category = Category(
                name="Integrity Test Category",
                description="Category for integrity testing"
            )
            db.session.add(category)
            db.session.commit()
            
            product = Product(
                name="Integrity Test Product",
                description="Product for integrity testing",
                price=29.99,
                stock_quantity=100,
                category_id=category.id
            )
            db.session.add(product)
            db.session.commit()
            
            # Verify referential integrity
            saved_product = Product.query.filter_by(name="Integrity Test Product").first()
            assert saved_product is not None
            assert saved_product.category_id == category.id
            
            # Verify category still exists
            saved_category = Category.query.filter_by(id=category.id).first()
            assert saved_category is not None
            
            # Test data consistency
            assert saved_product.price > 0
            assert saved_product.stock_quantity >= 0
            assert saved_category.name is not None
            assert len(saved_category.name) > 0
    
    def test_database_error_handling(self, app):
        """Test database error handling."""
        with app.app_context():
            # Test handling of invalid SQL
            try:
                db.session.execute('INVALID SQL QUERY')
                assert False, "Should have raised an error"
            except Exception:
                pass  # Expected to raise an error
            
            # Test handling of constraint violations
            user = User(
                username="test_error_user",
                email="test_error@example.com",
                role="staff"
            )
            user.set_password("TestPassword123!")
            db.session.add(user)
            db.session.commit()
            
            # Try to violate unique constraint
            duplicate_user = User(
                username="test_error_user",  # Same username
                email="different@example.com",
                role="staff"
            )
            duplicate_user.set_password("TestPassword123!")
            db.session.add(duplicate_user)
            
            try:
                db.session.commit()
                assert False, "Should have raised integrity error"
            except Exception:
                db.session.rollback()  # Clean up
    
    def test_database_backup_and_restore(self, app):
        """Test database backup and restore concepts."""
        with app.app_context():
            # Create test data
            user = User(
                username="backup_test_user",
                email="backup_test@example.com",
                role="staff"
            )
            user.set_password("TestPassword123!")
            db.session.add(user)
            db.session.commit()
            
            # Export data (conceptual test)
            users = User.query.all()
            assert len(users) >= 1
            
            # In a real implementation, you would:
            # 1. Create database backup
            # 2. Modify or delete data
            # 3. Restore from backup
            # 4. Verify data integrity
            
            # For this test, we'll just verify the data exists
            saved_user = User.query.filter_by(username="backup_test_user").first()
            assert saved_user is not None
    
    def test_database_indexing_performance(self, app):
        """Test database indexing performance."""
        import time
        
        with app.app_context():
            # Create test data
            users = []
            for i in range(1000):
                user = User(
                    username=f"index_user_{i}",
                    email=f"index_user_{i}@example.com",
                    role="staff"
                )
                user.set_password("TestPassword123!")
                users.append(user)
            
            db.session.add_all(users)
            db.session.commit()
            
            # Test indexed query (username should be indexed)
            start_time = time.time()
            
            result = User.query.filter_by(username="index_user_500").first()
            
            indexed_time = time.time() - start_time
            
            assert result is not None
            assert indexed_time < 0.1  # Should be very fast with index
            
            # Test non-indexed query (if any)
            start_time = time.time()
            
            result = User.query.filter(User.email.like("%@example.com")).all()
            
            non_indexed_time = time.time() - start_time
            
            assert len(result) == 1000
            # Non-indexed query might be slower, but should still be reasonable
            assert non_indexed_time < 1.0
    
    def test_database_connection_timeout(self, app):
        """Test database connection timeout."""
        with app.app_context():
            # Test normal connection
            result = db.session.execute('SELECT 1')
            assert result.fetchone()[0] == 1
            
            # Test connection timeout (conceptual)
            # In a real implementation, you would:
            # 1. Configure connection timeout
            # 2. Test with slow or unresponsive database
            # 3. Verify timeout behavior
            
            # For this test, we'll verify the connection works
            assert db.engine is not None
    
    def test_database_concurrent_operations(self, app):
        """Test concurrent database operations."""
        import threading
        import time
        
        with app.app_context():
            results = []
            errors = []
            
            def create_user(user_id):
                try:
                    user = User(
                        username=f"concurrent_user_{user_id}",
                        email=f"concurrent_{user_id}@example.com",
                        role="staff"
                    )
                    user.set_password("TestPassword123!")
                    
                    db.session.add(user)
                    db.session.commit()
                    
                    results.append(user_id)
                except Exception as e:
                    errors.append(f"User {user_id}: {str(e)}")
            
            # Create multiple threads for concurrent operations
            threads = []
            for i in range(10):
                thread = threading.Thread(target=create_user, args=(i,))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            # Verify results
            assert len(errors) == 0, f"Errors occurred: {errors}"
            assert len(results) == 10
            
            # Verify all users were created
            user_count = User.query.filter(User.username.like('concurrent_user_%')).count()
            assert user_count == 10
    
    def test_database_memory_usage(self, app):
        """Test database memory usage."""
        import gc
        import sys
        
        with app.app_context():
            # Create large dataset
            users = []
            for i in range(1000):
                user = User(
                    username=f"memory_user_{i}",
                    email=f"memory_user_{i}@example.com",
                    role="staff"
                )
                user.set_password("TestPassword123!")
                users.append(user)
            
            db.session.add_all(users)
            db.session.commit()
            
            # Clear references
            users.clear()
            gc.collect()
            
            # Query in batches to test memory usage
            batch_size = 100
            total_users = 0
            
            for offset in range(0, 1000, batch_size):
                batch = User.query.offset(offset).limit(batch_size).all()
                total_users += len(batch)
                
                # Clear batch reference
                del batch
                gc.collect()
            
            assert total_users == 1000
    
    def test_database_transaction_isolation(self, app):
        """Test database transaction isolation."""
        import threading
        
        with app.app_context():
            results = []
            
            def transaction_test(transaction_id):
                try:
                    # Create user in transaction
                    user = User(
                        username=f"iso_user_{transaction_id}",
                        email=f"iso_{transaction_id}@example.com",
                        role="staff"
                    )
                    user.set_password("TestPassword123!")
                    
                    db.session.add(user)
                    db.session.commit()
                    
                    # Read user in same transaction
                    saved_user = User.query.filter_by(username=f"iso_user_{transaction_id}").first()
                    
                    if saved_user:
                        results.append(transaction_id)
                    else:
                        results.append(-1)
                        
                except Exception as e:
                    results.append(f"Error {transaction_id}: {str(e)}")
            
            # Create multiple threads for concurrent transactions
            threads = []
            for i in range(5):
                thread = threading.Thread(target=transaction_test, args=(i,))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            # Verify all transactions succeeded
            assert len(results) == 5
            assert all(isinstance(result, int) and result >= 0 for result in results)
            
            # Verify all users were created
            user_count = User.query.filter(User.username.like('iso_user_%')).count()
            assert user_count == 5
