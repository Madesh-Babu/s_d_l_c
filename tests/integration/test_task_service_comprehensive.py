"""
Integration Tests for Core Task Service Integration

This module contains core task service integration testing.
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
from src.models.models import db, User, Task
from src.services.task_service import TaskService
from src.core.exceptions import ValidationErrorException, NotFoundError


class TestTaskServiceComprehensive:
    """Core task service integration testing."""
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self, app, client):
        """Set up clean test environment."""
        with app.app_context():
            # Clean up test data
            Task.query.filter(Task.title.like('test_%')).delete()
            User.query.filter(User.username.like('test_%')).delete()
            db.session.commit()
            
            # Create test users
            users = []
            for i in range(3):
                user = User(
                    username=f"test_user_{i}",
                    email=f"test_{i}@example.com",
                    role="staff"
                )
                user.set_password("TestPassword123!")
                db.session.add(user)
                users.append(user)
            
            db.session.commit()
            return users
    
    def test_task_service_basic_crud(self, app, client):
        """Test basic task service CRUD operations."""
        with app.app_context():
            task_service = TaskService()
            
            # Create task
            task_data = {
                "title": "Test Task",
                "description": "Test task description",
                "status": "pending",
                "priority": "medium",
                "assigned_to": 1
            }
            
            created_task = task_service.create(task_data)
            assert created_task is not None
            assert created_task.title == "Test Task"
            assert created_task.description == "Test task description"
            assert created_task.status == "pending"
            assert created_task.priority == "medium"
            assert created_task.assigned_to == 1
            
            # Read task
            retrieved_task = task_service.get_by_id(created_task.id)
            assert retrieved_task is not None
            assert retrieved_task.title == "Test Task"
            
            # Update task
            update_data = {
                "title": "Updated Test Task",
                "status": "in_progress",
                "priority": "high"
            }
            
            updated_task = task_service.update(created_task.id, update_data)
            assert updated_task.title == "Updated Test Task"
            assert updated_task.status == "in_progress"
            assert updated_task.priority == "high"
            
            # Delete task
            deleted = task_service.delete(created_task.id)
            assert deleted is True
            
            # Verify deletion
            deleted_task = task_service.get_by_id(created_task.id)
            assert deleted_task is None
    
    def test_task_service_status_management(self, app, client):
        """Test task status management."""
        with app.app_context():
            task_service = TaskService()
            
            # Create task
            task_data = {
                "title": "Status Test Task",
                "description": "Task for status testing",
                "status": "pending",
                "priority": "medium",
                "assigned_to": 1
            }
            
            task = task_service.create(task_data)
            
            # Test status transitions
            status_transitions = [
                ("pending", "in_progress"),
                ("in_progress", "completed"),
                ("completed", "closed")
            ]
            
            for from_status, to_status in status_transitions:
                updated_task = task_service.update_status(task.id, to_status)
                assert updated_task.status == to_status
                
                # Verify status history
                history = task_service.get_task_history(task.id)
                assert len(history) >= 1
                
                # Verify latest status change
                latest_change = history[-1]
                assert latest_change.new_status == to_status
                assert latest_change.old_status == from_status
    
    def test_task_service_assignment_management(self, app, client):
        """Test task assignment management."""
        with app.app_context():
            task_service = TaskService()
            
            # Create unassigned task
            task_data = {
                "title": "Assignment Test Task",
                "description": "Task for assignment testing",
                "status": "pending",
                "priority": "medium"
            }
            
            task = task_service.create(task_data)
            assert task.assigned_to is None
            
            # Assign task to user
            assigned_task = task_service.assign_task(task.id, 1)
            assert assigned_task.assigned_to == 1
            assert assigned_task.status == "assigned"
            
            # Reassign task to different user
            reassigned_task = task_service.assign_task(task.id, 2)
            assert reassigned_task.assigned_to == 2
            
            # Unassign task
            unassigned_task = task_service.unassign_task(task.id)
            assert unassigned_task.assigned_to is None
            assert unassigned_task.status == "pending"
            
            # Test assignment history
            history = task_service.get_task_history(task.id)
            assignment_changes = [h for h in history if h.field == "assigned_to"]
            assert len(assignment_changes) >= 3
    
    def test_task_service_priority_management(self, app, client):
        """Test task priority management."""
        with app.app_context():
            task_service = TaskService()
            
            # Create task
            task_data = {
                "title": "Priority Test Task",
                "description": "Task for priority testing",
                "status": "pending",
                "priority": "low",
                "assigned_to": 1
            }
            
            task = task_service.create(task_data)
            
            # Test priority escalation
            escalated_task = task_service.escalate_priority(task.id)
            assert escalated_task.priority == "medium"
            
            # Test priority escalation again
            escalated_task = task_service.escalate_priority(task.id)
            assert escalated_task.priority == "high"
            
            # Test priority de-escalation
            deescalated_task = task_service.deescalate_priority(task.id)
            assert deescalated_task.priority == "medium"
            
            # Test priority de-escalation again
            deescalated_task = task_service.deescalate_priority(task.id)
            assert deescalated_task.priority == "low"
            
            # Verify priority history
            history = task_service.get_task_history(task.id)
            priority_changes = [h for h in history if h.field == "priority"]
            assert len(priority_changes) >= 4
    
    def test_task_service_deadline_management(self, app, client):
        """Test task deadline management."""
        with app.app_context():
            task_service = TaskService()
            
            # Create task with deadline
            future_date = datetime.now() + timedelta(days=7)
            task_data = {
                "title": "Deadline Test Task",
                "description": "Task for deadline testing",
                "status": "pending",
                "priority": "medium",
                "due_date": future_date,
                "assigned_to": 1
            }
            
            task = task_service.create(task_data)
            assert task.due_date == future_date
            
            # Update deadline
            new_deadline = datetime.now() + timedelta(days=14)
            updated_task = task_service.update_deadline(task.id, new_deadline)
            assert updated_task.due_date == new_deadline
            
            # Test overdue detection
            # Create overdue task
            past_date = datetime.now() - timedelta(days=1)
            overdue_data = {
                "title": "Overdue Test Task",
                "description": "Overdue task for testing",
                "status": "pending",
                "priority": "high",
                "due_date": past_date,
                "assigned_to": 1
            }
            
            overdue_task = task_service.create(overdue_data)
            
            # Check if task is overdue
            is_overdue = task_service.is_task_overdue(overdue_task.id)
            assert is_overdue is True
            
            # Get overdue tasks
            overdue_tasks = task_service.get_overdue_tasks()
            assert len(overdue_tasks) >= 1
            assert overdue_task in overdue_tasks
            
            # Get tasks due soon
            tasks_due_soon = task_service.get_tasks_due_soon(days=7)
            assert len(tasks_due_soon) >= 1
    
    def test_task_service_search_and_filtering(self, app, client):
        """Test task search and filtering."""
        with app.app_context():
            task_service = TaskService()
            
            # Create diverse tasks
            tasks_data = [
                {
                    "title": "API Development Task",
                    "description": "Develop REST API endpoints",
                    "status": "in_progress",
                    "priority": "high",
                    "assigned_to": 1,
                    "tags": ["development", "api"]
                },
                {
                    "title": "Frontend Testing",
                    "description": "Test frontend components",
                    "status": "pending",
                    "priority": "medium",
                    "assigned_to": 2,
                    "tags": ["testing", "frontend"]
                },
                {
                    "title": "Database Optimization",
                    "description": "Optimize database queries",
                    "status": "completed",
                    "priority": "low",
                    "assigned_to": 3,
                    "tags": ["database", "optimization"]
                }
            ]
            
            created_tasks = []
            for task_data in tasks_data:
                task = task_service.create(task_data)
                created_tasks.append(task)
            
            # Test text search
            search_results = task_service.search_tasks("development")
            assert len(search_results) >= 1
            
            # Test filtering by status
            pending_tasks = task_service.get_tasks_by_status("pending")
            assert len(pending_tasks) >= 1
            
            # Test filtering by priority
            high_priority_tasks = task_service.get_tasks_by_priority("high")
            assert len(high_priority_tasks) >= 1
            
            # Test filtering by assignee
            assignee_tasks = task_service.get_tasks_by_assignee(1)
            assert len(assignee_tasks) >= 1
            
            # Test filtering by tags
            api_tasks = task_service.get_tasks_by_tag("api")
            assert len(api_tasks) >= 1
            
            # Test combined filtering
            filters = {
                "status": "pending",
                "priority": "medium",
                "assigned_to": 2,
                "tags": ["testing"]
            }
            
            filtered_tasks = task_service.filter_tasks(filters)
            assert len(filtered_tasks) >= 1
    
    def test_task_service_collaboration(self, app, client):
        """Test task collaboration features."""
        with app.app_context():
            task_service = TaskService()
            
            # Create task
            task_data = {
                "title": "Collaboration Test Task",
                "description": "Task for collaboration testing",
                "status": "pending",
                "priority": "medium",
                "assigned_to": 1
            }
            
            task = task_service.create(task_data)
            
            # Add collaborators
            collaborators = [2, 3]
            updated_task = task_service.add_collaborators(task.id, collaborators)
            assert len(updated_task.collaborators) >= 2
            assert 2 in updated_task.collaborators
            assert 3 in updated_task.collaborators
            
            # Add comment
            comment_data = {
                "content": "This is a test comment",
                "author_id": 1
            }
            
            comment = task_service.add_comment(task.id, comment_data)
            assert comment is not None
            assert comment.content == "This is a test comment"
            assert comment.author_id == 1
            
            # Get comments
            comments = task_service.get_comments(task.id)
            assert len(comments) >= 1
            
            # Remove collaborator
            updated_task = task_service.remove_collaborators(task.id, [2])
            assert 2 not in updated_task.collaborators
            assert 3 in updated_task.collaborators
    
    def test_task_service_dependencies(self, app, client):
        """Test task dependency management."""
        with app.app_context():
            task_service = TaskService()
            
            # Create parent task
            parent_data = {
                "title": "Parent Task",
                "description": "Parent task for dependency testing",
                "status": "pending",
                "priority": "high",
                "assigned_to": 1
            }
            
            parent_task = task_service.create(parent_data)
            
            # Create child task
            child_data = {
                "title": "Child Task",
                "description": "Child task depending on parent",
                "status": "pending",
                "priority": "medium",
                "assigned_to": 1,
                "depends_on": parent_task.id
            }
            
            child_task = task_service.create(child_data)
            assert child_task.depends_on == parent_task.id
            
            # Test dependency relationships
            dependencies = task_service.get_task_dependencies(child_task.id)
            assert len(dependencies) >= 1
            assert parent_task in dependencies
            
            # Test blocking tasks
            blocking_tasks = task_service.get_blocking_tasks(parent_task.id)
            assert len(blocking_tasks) >= 1
            assert child_task in blocking_tasks
            
            # Test completion constraint
            with pytest.raises(ValidationErrorException):
                task_service.update_status(parent_task.id, "completed")
            
            # Complete child task first
            task_service.update_status(child_task.id, "completed")
            
            # Now parent can be completed
            completed_parent = task_service.update_status(parent_task.id, "completed")
            assert completed_parent.status == "completed"
    
    def test_task_service_bulk_operations(self, app, client):
        """Test task bulk operations."""
        with app.app_context():
            task_service = TaskService()
            
            # Create multiple tasks
            task_data_list = [
                {
                    "title": f"Bulk Task {i}",
                    "description": f"Bulk task {i} description",
                    "status": "pending",
                    "priority": "medium",
                    "assigned_to": 1
                }
                for i in range(5)
            ]
            
            created_tasks = task_service.create_bulk(task_data_list)
            assert len(created_tasks) == 5
            
            # Bulk update
            update_data = {
                "status": "in_progress",
                "priority": "high"
            }
            
            updated_tasks = task_service.update_bulk([task.id for task in created_tasks], update_data)
            assert len(updated_tasks) == 5
            
            for task in updated_tasks:
                assert task.status == "in_progress"
                assert task.priority == "high"
            
            # Bulk delete
            deleted_count = task_service.delete_bulk([task.id for task in created_tasks])
            assert deleted_count == 5
    
    def test_task_service_validation(self, app, client):
        """Test task service validation."""
        with app.app_context():
            task_service = TaskService()
            
            # Test invalid task data
            invalid_data = {
                "title": "",  # Empty title
                "description": "Task description",
                "status": "invalid_status",  # Invalid status
                "priority": "invalid_priority",  # Invalid priority
                "assigned_to": -1  # Invalid user ID
            }
            
            with pytest.raises(ValidationErrorException):
                task_service.create(invalid_data)
            
            # Test invalid status update
            valid_data = {
                "title": "Valid Task",
                "description": "Valid task description",
                "status": "pending",
                "priority": "medium",
                "assigned_to": 1
            }
            
            task = task_service.create(valid_data)
            
            with pytest.raises(ValidationErrorException):
                task_service.update_status(task.id, "invalid_status")
            
            # Test invalid priority update
            with pytest.raises(ValidationErrorException):
                task_service.update_priority(task.id, "invalid_priority")
            
            # Test invalid assignment
            with pytest.raises(ValidationErrorException):
                task_service.assign_task(task.id, -1)
    
    def test_task_service_error_handling(self, app, client):
        """Test task service error handling."""
        with app.app_context():
            task_service = TaskService()
            
            # Test non-existent task operations
            non_existent_id = 99999
            
            # Test get by ID
            task = task_service.get_by_id(non_existent_id)
            assert task is None
            
            # Test update non-existent task
            update_result = task_service.update(non_existent_id, {"title": "Updated"})
            assert update_result is None
            
            # Test delete non-existent task
            delete_result = task_service.delete(non_existent_id)
            assert delete_result is False
            
            # Test status update non-existent task
            with pytest.raises(NotFoundError):
                task_service.update_status(non_existent_id, "completed")
            
            # Test assignment non-existent task
            with pytest.raises(NotFoundError):
                task_service.assign_task(non_existent_id, 1)
    
    def test_task_service_performance(self, app, client):
        """Test task service performance."""
        import time
        
        with app.app_context():
            task_service = TaskService()
            
            # Create performance test data
            tasks = []
            for i in range(100):
                task_data = {
                    "title": f"Performance Task {i}",
                    "description": f"Performance task {i} description",
                    "status": "pending",
                    "priority": "medium",
                    "assigned_to": (i % 3) + 1
                }
                
                task = task_service.create(task_data)
                tasks.append(task)
            
            # Test bulk operation performance
            start_time = time.time()
            
            update_data = {"status": "in_progress"}
            updated_tasks = task_service.update_bulk([task.id for task in tasks[:50]], update_data)
            
            bulk_time = time.time() - start_time
            assert len(updated_tasks) == 50
            assert bulk_time < 2.0  # Should complete within 2 seconds
            
            # Test search performance
            start_time = time.time()
            
            search_results = task_service.search_tasks("Performance")
            
            search_time = time.time() - start_time
            assert len(search_results) >= 100
            assert search_time < 1.0  # Should complete within 1 second
    
    def test_task_service_integrations(self, app, client):
        """Test task service integrations."""
        with app.app_context():
            task_service = TaskService()
            
            # Create task
            task_data = {
                "title": "Integration Test Task",
                "description": "Task for integration testing",
                "status": "pending",
                "priority": "medium",
                "assigned_to": 1
            }
            
            task = task_service.create(task_data)
            
            # Test notification integration
            notification = task_service.send_notification(task.id, "assignment", {
                "user_id": 1,
                "message": "Task assigned to you"
            })
            assert notification is not None
            
            # Test email integration
            email_sent = task_service.send_email_notification(task.id, "task_assigned", {
                "to": "test@example.com",
                "subject": "New Task Assigned",
                "message": "You have been assigned a new task"
            })
            assert email_sent is True
            
            # Test calendar integration
            calendar_event = task_service.create_calendar_event(task.id)
            assert calendar_event is not None
            
            # Test webhook integration
            webhook_response = task_service.trigger_webhook(task.id, "task_created", {
                "url": "https://example.com/webhook",
                "data": {"task_id": task.id}
            })
            assert webhook_response is not None
    
    def test_task_service_reporting(self, app, client):
        """Test task service reporting."""
        with app.app_context():
            task_service = TaskService()
            
            # Create test data
            for i in range(10):
                task_data = {
                    "title": f"Report Task {i}",
                    "description": f"Report task {i} description",
                    "status": ["pending", "in_progress", "completed"][i % 3],
                    "priority": ["low", "medium", "high"][i % 3],
                    "assigned_to": (i % 3) + 1
                }
                
                task_service.create(task_data)
            
            # Test status distribution report
            status_report = task_service.get_status_distribution_report()
            assert len(status_report) >= 3
            assert "pending" in status_report
            assert "in_progress" in status_report
            assert "completed" in status_report
            
            # Test priority distribution report
            priority_report = task_service.get_priority_distribution_report()
            assert len(priority_report) >= 3
            assert "low" in priority_report
            assert "medium" in priority_report
            assert "high" in priority_report
            
            # Test user workload report
            workload_report = task_service.get_user_workload_report()
            assert len(workload_report) >= 3
            
            # Test completion rate report
            completion_report = task_service.get_completion_rate_report()
            assert completion_report["total_tasks"] >= 10
            assert 0 <= completion_report["completion_rate"] <= 100
            
            # Test overdue tasks report
            overdue_report = task_service.get_overdue_tasks_report()
            assert isinstance(overdue_report, list)
            
            # Test comprehensive report
            comprehensive_report = task_service.generate_comprehensive_report()
            assert comprehensive_report is not None
            assert "status_distribution" in comprehensive_report
            assert "priority_distribution" in comprehensive_report
            assert "user_workload" in comprehensive_report
