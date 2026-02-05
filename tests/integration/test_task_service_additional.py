"""
Integration Tests for Additional Task Service Scenarios

This module contains additional task service integration scenarios.
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
from src.models.models import db, User, Task
from src.services.task_service import TaskService
from src.core.exceptions import ValidationErrorException, NotFoundError


class TestTaskServiceAdditional:
    """Additional task service integration testing scenarios."""
    
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
    
    def test_task_service_bulk_operations(self, app, client):
        """Test bulk task operations."""
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
            
            # Bulk update tasks
            update_data = {
                "status": "in_progress",
                "priority": "high"
            }
            
            updated_tasks = task_service.update_bulk([task.id for task in created_tasks], update_data)
            assert len(updated_tasks) == 5
            
            for task in updated_tasks:
                assert task.status == "in_progress"
                assert task.priority == "high"
            
            # Bulk delete tasks
            deleted_count = task_service.delete_bulk([task.id for task in created_tasks])
            assert deleted_count == 5
    
    def test_task_service_workflow_transitions(self, app, client):
        """Test task workflow transitions."""
        with app.app_context():
            task_service = TaskService()
            
            # Create task
            task_data = {
                "title": "Workflow Test Task",
                "description": "Task for workflow testing",
                "status": "pending",
                "priority": "medium",
                "assigned_to": 1
            }
            
            task = task_service.create(task_data)
            
            # Test valid workflow transitions
            valid_transitions = [
                ("pending", "in_progress"),
                ("in_progress", "completed"),
                ("in_progress", "blocked"),
                ("blocked", "in_progress"),
                ("completed", "closed")
            ]
            
            for from_status, to_status in valid_transitions:
                task.status = from_status
                db.session.commit()
                
                updated_task = task_service.update_status(task.id, to_status)
                assert updated_task.status == to_status
            
            # Test invalid transitions
            invalid_transitions = [
                ("completed", "pending"),
                ("closed", "in_progress"),
                ("blocked", "completed")
            ]
            
            for from_status, to_status in invalid_transitions:
                task.status = from_status
                db.session.commit()
                
                with pytest.raises(ValidationErrorException):
                    task_service.update_status(task.id, to_status)
    
    def test_task_service_assignment_workflow(self, app, client):
        """Test task assignment workflow."""
        with app.app_context():
            task_service = TaskService()
            
            # Create task
            task_data = {
                "title": "Assignment Test Task",
                "description": "Task for assignment testing",
                "status": "pending",
                "priority": "medium"
            }
            
            task = task_service.create(task_data)
            
            # Test assignment to user
            assigned_task = task_service.assign_task(task.id, 1)
            assert assigned_task.assigned_to == 1
            assert assigned_task.status == "assigned"
            
            # Test reassignment
            reassigned_task = task_service.assign_task(task.id, 2)
            assert reassigned_task.assigned_to == 2
            
            # Test unassignment
            unassigned_task = task_service.unassign_task(task.id)
            assert unassigned_task.assigned_to is None
            assert unassigned_task.status == "pending"
    
    def test_task_service_deadline_management(self, app, client):
        """Test task deadline management."""
        with app.app_context():
            task_service = TaskService()
            
            # Create task with deadline
            task_data = {
                "title": "Deadline Test Task",
                "description": "Task for deadline testing",
                "status": "pending",
                "priority": "medium",
                "due_date": datetime.now() + timedelta(days=7),
                "assigned_to": 1
            }
            
            task = task_service.create(task_data)
            
            # Test deadline update
            new_deadline = datetime.now() + timedelta(days=14)
            updated_task = task_service.update_deadline(task.id, new_deadline)
            assert updated_task.due_date == new_deadline
            
            # Test overdue tasks
            # Create overdue task
            overdue_data = {
                "title": "Overdue Task",
                "description": "Overdue task for testing",
                "status": "pending",
                "priority": "high",
                "due_date": datetime.now() - timedelta(days=1),
                "assigned_to": 1
            }
            
            overdue_task = task_service.create(overdue_data)
            
            overdue_tasks = task_service.get_overdue_tasks()
            assert len(overdue_tasks) >= 1
            assert overdue_task in overdue_tasks
            
            # Test upcoming deadlines
            upcoming_tasks = task_service.get_tasks_due_soon(days=7)
            assert len(upcoming_tasks) >= 1
    
    def test_task_service_priority_management(self, app, client):
        """Test task priority management."""
        with app.app_context():
            task_service = TaskService()
            
            # Create tasks with different priorities
            priorities = ["low", "medium", "high", "critical"]
            tasks = []
            
            for priority in priorities:
                task_data = {
                    "title": f"{priority.title()} Priority Task",
                    "description": f"Task with {priority} priority",
                    "status": "pending",
                    "priority": priority,
                    "assigned_to": 1
                }
                
                task = task_service.create(task_data)
                tasks.append(task)
            
            # Test priority ordering
            ordered_tasks = task_service.get_tasks_by_priority()
            assert len(ordered_tasks) >= 4
            
            # Test priority escalation
            low_task = next(t for t in tasks if t.priority == "low")
            escalated_task = task_service.escalate_priority(low_task.id)
            assert escalated_task.priority == "medium"
            
            # Test priority de-escalation
            critical_task = next(t for t in tasks if t.priority == "critical")
            deescalated_task = task_service.deescalate_priority(critical_task.id)
            assert deescalated_task.priority == "high"
    
    def test_task_service_dependency_management(self, app, client):
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
            
            # Create child tasks
            child_tasks = []
            for i in range(3):
                child_data = {
                    "title": f"Child Task {i}",
                    "description": f"Child task {i} for dependency testing",
                    "status": "pending",
                    "priority": "medium",
                    "assigned_to": 1,
                    "depends_on": parent_task.id
                }
                
                child_task = task_service.create(child_data)
                child_tasks.append(child_task)
            
            # Test dependency relationships
            dependencies = task_service.get_task_dependencies(parent_task.id)
            assert len(dependencies) >= 3
            
            # Test blocking tasks
            blocking_tasks = task_service.get_blocking_tasks(parent_task.id)
            assert len(blocking_tasks) >= 3
            
            # Test cannot complete parent while children are pending
            with pytest.raises(ValidationErrorException):
                task_service.update_status(parent_task.id, "completed")
            
            # Complete child tasks
            for child_task in child_tasks:
                task_service.update_status(child_task.id, "completed")
            
            # Now parent can be completed
            completed_parent = task_service.update_status(parent_task.id, "completed")
            assert completed_parent.status == "completed"
    
    def test_task_service_collaboration_features(self, app, client):
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
            
            # Test adding collaborators
            collaborators = [2, 3]
            updated_task = task_service.add_collaborators(task.id, collaborators)
            assert len(updated_task.collaborators) >= 2
            
            # Test removing collaborators
            updated_task = task_service.remove_collaborators(task.id, [2])
            assert 2 not in updated_task.collaborators
            
            # Test task comments
            comment_data = {
                "content": "Test comment",
                "author_id": 1
            }
            
            comment = task_service.add_comment(task.id, comment_data)
            assert comment is not None
            assert comment.content == "Test comment"
            
            # Test getting comments
            comments = task_service.get_comments(task.id)
            assert len(comments) >= 1
            
            # Test task history
            history = task_service.get_task_history(task.id)
            assert len(history) >= 1
    
    def test_task_service_reporting_analytics(self, app, client):
        """Test task reporting and analytics."""
        with app.app_context():
            task_service = TaskService()
            
            # Create tasks with different properties
            users = [1, 2, 3]
            statuses = ["pending", "in_progress", "completed"]
            priorities = ["low", "medium", "high"]
            
            for i in range(27):  # 3 users * 3 statuses * 3 priorities
                task_data = {
                    "title": f"Analytics Task {i}",
                    "description": f"Task {i} for analytics",
                    "status": statuses[i % 3],
                    "priority": priorities[i % 3],
                    "assigned_to": users[i % 3],
                    "due_date": datetime.now() + timedelta(days=i % 7)
                }
                
                task_service.create(task_data)
            
            # Test user workload report
            workload_report = task_service.get_user_workload_report()
            assert len(workload_report) >= 3
            
            # Test status distribution report
            status_report = task_service.get_status_distribution_report()
            assert len(status_report) >= 3
            assert "pending" in status_report
            assert "in_progress" in status_report
            assert "completed" in status_report
            
            # Test priority distribution report
            priority_report = task_service.get_priority_distribution_report()
            assert len(priority_report) >= 3
            
            # Test completion rate report
            completion_report = task_service.get_completion_rate_report()
            assert completion_report["total_tasks"] >= 27
            assert completion_report["completion_rate"] >= 0
            
            # Test overdue tasks report
            overdue_report = task_service.get_overdue_tasks_report()
            assert len(overdue_report) >= 0
    
    def test_task_service_search_filtering(self, app, client):
        """Test task search and filtering."""
        with app.app_context():
            task_service = TaskService()
            
            # Create diverse tasks
            task_data_list = [
                {
                    "title": "API Development Task",
                    "description": "Develop REST API endpoints",
                    "status": "in_progress",
                    "priority": "high",
                    "assigned_to": 1,
                    "tags": ["development", "api", "backend"]
                },
                {
                    "title": "Frontend Testing",
                    "description": "Test frontend components",
                    "status": "pending",
                    "priority": "medium",
                    "assigned_to": 2,
                    "tags": ["testing", "frontend", "ui"]
                },
                {
                    "title": "Database Optimization",
                    "description": "Optimize database queries",
                    "status": "completed",
                    "priority": "low",
                    "assigned_to": 3,
                    "tags": ["database", "optimization", "performance"]
                }
            ]
            
            created_tasks = []
            for task_data in task_data_list:
                task = task_service.create(task_data)
                created_tasks.append(task)
            
            # Test text search
            search_results = task_service.search_tasks("development")
            assert len(search_results) >= 1
            
            # Test tag-based filtering
            api_tasks = task_service.get_tasks_by_tag("api")
            assert len(api_tasks) >= 1
            
            # Test advanced filtering
            filters = {
                "status": "in_progress",
                "priority": "high",
                "assigned_to": 1,
                "tags": ["development"]
            }
            
            filtered_tasks = task_service.filter_tasks(filters)
            assert len(filtered_tasks) >= 1
            
            # Test date range filtering
            date_range = {
                "start_date": datetime.now() - timedelta(days=1),
                "end_date": datetime.now() + timedelta(days=1)
            }
            
            date_filtered_tasks = task_service.get_tasks_by_date_range(date_range)
            assert len(date_filtered_tasks) >= 0
    
    def test_task_service_notifications(self, app, client):
        """Test task notification system."""
        with app.app_context():
            task_service = TaskService()
            
            # Create task
            task_data = {
                "title": "Notification Test Task",
                "description": "Task for notification testing",
                "status": "pending",
                "priority": "medium",
                "assigned_to": 1
            }
            
            task = task_service.create(task_data)
            
            # Test assignment notification
            notification = task_service.send_assignment_notification(task.id, 1)
            assert notification is not None
            assert notification.type == "assignment"
            
            # Test status change notification
            notification = task_service.send_status_change_notification(task.id, "in_progress")
            assert notification is not None
            assert notification.type == "status_change"
            
            # Test deadline reminder notification
            notification = task_service.send_deadline_reminder(task.id)
            assert notification is not None
            assert notification.type == "deadline_reminder"
            
            # Test overdue notification
            notification = task_service.send_overdue_notification(task.id)
            assert notification is not None
            assert notification.type == "overdue"
    
    def test_task_service_templates(self, app, client):
        """Test task template system."""
        with app.app_context():
            task_service = TaskService()
            
            # Create task template
            template_data = {
                "name": "Bug Fix Template",
                "title_template": "Fix Bug: {bug_title}",
                "description_template": "Fix the bug: {bug_description}\n\nSteps to reproduce:\n{reproduction_steps}",
                "default_priority": "high",
                "default_status": "pending",
                "tags": ["bug", "fix"]
            }
            
            template = task_service.create_task_template(template_data)
            assert template is not None
            assert template.name == "Bug Fix Template"
            
            # Create task from template
            template_vars = {
                "bug_title": "Login button not working",
                "bug_description": "Login button is unresponsive when clicked",
                "reproduction_steps": "1. Go to login page\n2. Click login button\n3. Nothing happens"
            }
            
            task_from_template = task_service.create_from_template(template.id, template_vars, assigned_to=1)
            assert task_from_template is not None
            assert "Fix Bug: Login button not working" in task_from_template.title
            assert "Fix the bug: Login button is unresponsive" in task_from_template.description
            
            # Test template listing
            templates = task_service.get_task_templates()
            assert len(templates) >= 1
            
            # Test template update
            updated_template = task_service.update_task_template(template.id, {
                "name": "Updated Bug Fix Template",
                "default_priority": "critical"
            })
            assert updated_template.name == "Updated Bug Fix Template"
            assert updated_template.default_priority == "critical"
    
    def test_task_service_automation(self, app, client):
        """Test task automation features."""
        with app.app_context():
            task_service = TaskService()
            
            # Create automation rule
            rule_data = {
                "name": "Auto-escalate overdue tasks",
                "trigger": "overdue",
                "conditions": {
                    "days_overdue": 3,
                    "priority": ["low", "medium"]
                },
                "actions": {
                    "escalate_priority": True,
                    "notify_assignee": True,
                    "add_tag": "overdue"
                }
            }
            
            rule = task_service.create_automation_rule(rule_data)
            assert rule is not None
            assert rule.name == "Auto-escalate overdue tasks"
            
            # Create overdue task that matches rule
            overdue_task_data = {
                "title": "Overdue Automation Task",
                "description": "Task for automation testing",
                "status": "pending",
                "priority": "low",  # Matches rule condition
                "due_date": datetime.now() - timedelta(days=5),  # Overdue by 5 days
                "assigned_to": 1
            }
            
            overdue_task = task_service.create(overdue_task_data)
            
            # Apply automation rules
            applied_tasks = task_service.apply_automation_rules()
            assert len(applied_tasks) >= 1
            
            # Check if task was escalated
            escalated_task = task_service.get_by_id(overdue_task.id)
            assert escalated_task.priority in ["medium", "high"]  # Should be escalated
            
            # Test automation rule listing
            rules = task_service.get_automation_rules()
            assert len(rules) >= 1
            
            # Test rule deactivation
            deactivated_rule = task_service.deactivate_automation_rule(rule.id)
            assert deactivated_rule.is_active is False
    
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
            
            # Test calendar integration
            calendar_event = task_service.create_calendar_event(task.id)
            assert calendar_event is not None
            assert calendar_event.title == task.title
            
            # Test email integration
            email_sent = task_service.send_task_email(task.id, "assignment")
            assert email_sent is True
            
            # Test file attachment
            attachment_data = {
                "filename": "test_file.txt",
                "content": b"test file content",
                "content_type": "text/plain"
            }
            
            attachment = task_service.add_attachment(task.id, attachment_data)
            assert attachment is not None
            assert attachment.filename == "test_file.txt"
            
            # Test external API integration
            api_response = task_service.sync_with_external_system(task.id)
            assert api_response is not None
            
            # Test webhook integration
            webhook_response = task_service.trigger_webhook(task.id, "task_created")
            assert webhook_response is not None
    
    def test_task_service_performance_optimization(self, app, client):
        """Test task service performance optimization."""
        import time
        
        with app.app_context():
            task_service = TaskService()
            
            # Create large dataset
            tasks = []
            for i in range(1000):
                task_data = {
                    "title": f"Performance Task {i}",
                    "description": f"Task {i} for performance testing",
                    "status": "pending",
                    "priority": "medium",
                    "assigned_to": (i % 3) + 1,
                    "due_date": datetime.now() + timedelta(days=i % 30)
                }
                
                task = task_service.create(task_data)
                tasks.append(task)
            
            # Test bulk operations performance
            start_time = time.time()
            
            # Bulk status update
            updated_tasks = task_service.bulk_update_status([task.id for task in tasks[:100]], "in_progress")
            
            bulk_update_time = time.time() - start_time
            assert len(updated_tasks) == 100
            assert bulk_update_time < 2.0  # Should complete within 2 seconds
            
            # Test search performance
            start_time = time.time()
            
            search_results = task_service.search_tasks("Performance")
            
            search_time = time.time() - start_time
            assert len(search_results) >= 1000
            assert search_time < 1.0  # Should complete within 1 second
            
            # Test report generation performance
            start_time = time.time()
            
            report = task_service.generate_comprehensive_report()
            
            report_time = time.time() - start_time
            assert report is not None
            assert report_time < 3.0  # Should complete within 3 seconds
    
    def test_task_service_error_recovery(self, app, client):
        """Test task service error recovery."""
        with app.app_context():
            task_service = TaskService()
            
            # Test database connection error recovery
            with patch('src.models.models.db.session') as mock_session:
                mock_session.commit.side_effect = Exception("Database connection lost")
                
                try:
                    task_data = {
                        "title": "Error Recovery Task",
                        "description": "Task for error recovery testing",
                        "status": "pending",
                        "priority": "medium",
                        "assigned_to": 1
                    }
                    
                    task_service.create(task_data)
                    assert False, "Should have raised an error"
                    
                except Exception:
                    # Error should be handled gracefully
                    pass
            
            # Test validation error recovery
            try:
                invalid_data = {
                    "title": "",  # Invalid
                    "description": "Invalid task",
                    "status": "invalid_status",  # Invalid
                    "priority": "invalid_priority",  # Invalid
                    "assigned_to": -1  # Invalid
                }
                
                task_service.create(invalid_data)
                assert False, "Should have raised validation error"
                
            except ValidationErrorException:
                # Validation error should be handled
                pass
            
            # Test recovery after error
            valid_data = {
                "title": "Recovery Task",
                "description": "Task after error recovery",
                "status": "pending",
                "priority": "medium",
                "assigned_to": 1
            }
            
            recovered_task = task_service.create(valid_data)
            assert recovered_task is not None
            assert recovered_task.title == "Recovery Task"
