"""
API Tests for Tasks Router

This module contains comprehensive API tests for task management API endpoints and workflows.
"""

import pytest
import json
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from src.models.models import Task, User
from src.core.exceptions import ValidationErrorException, NotFoundError


class TestTasksRouter:
    """Test task management API endpoints and workflows."""
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    @pytest.fixture
    def sample_user(self, app):
        """Create sample user for testing."""
        with app.app_context():
            user = User(
                username="testuser",
                email="test@example.com",
                role="staff"
            )
            user.set_password("TestPassword123!")
            return user
    
    @pytest.fixture
    def sample_task(self, app):
        """Create sample task for testing."""
        with app.app_context():
            task = Task(
                title="Test Task",
                description="Test task description",
                status="pending",
                priority="medium",
                due_date=datetime.now() + timedelta(days=7),
                assigned_to=1
            )
            return task
    
    def test_create_task_success(self, client, sample_user):
        """Test successful task creation."""
        task_data = {
            "title": "New Task",
            "description": "New task description",
            "status": "pending",
            "priority": "medium",
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "assigned_to": 1
        }
        
        with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.models.models.db.session') as mock_session:
                    mock_session.add = Mock()
                    mock_session.commit = Mock()
                    
                    response = client.post('/tasks/',
                                         data=json.dumps(task_data),
                                         headers={'Authorization': 'Bearer valid_token'},
                                         content_type='application/json')
                    
                    assert response.status_code == 201
                    result = response.get_json()
                    assert result['message'] == "Task created successfully"
                    assert result['task']['title'] == "New Task"
    
    def test_create_task_validation_error(self, client):
        """Test task creation with validation errors."""
        invalid_data = {
            "title": "",  # Empty title
            "description": "Task description",
            "status": "invalid_status",  # Invalid status
            "priority": "invalid_priority",  # Invalid priority
            "due_date": "invalid_date",  # Invalid date
            "assigned_to": -1  # Invalid user ID
        }
        
        with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                response = client.post('/tasks/',
                                     data=json.dumps(invalid_data),
                                     headers={'Authorization': 'Bearer valid_token'},
                                     content_type='application/json')
                
                assert response.status_code == 400
                result = response.get_json()
                assert 'error' in result
    
    def test_create_task_missing_data(self, client):
        """Test task creation with missing required data."""
        response = client.post('/tasks/',
                             data=json.dumps({}),
                             headers={'Authorization': 'Bearer valid_token'},
                             content_type='application/json')
        
        assert response.status_code == 400
        result = response.get_json()
        assert 'error' in result
    
    def test_get_all_tasks_success(self, client, sample_task):
        """Test getting all tasks with valid authentication."""
        with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.models.models.Task.query') as mock_query:
                    mock_query.all.return_value = [sample_task]
                    
                    response = client.get('/tasks/',
                                        headers={'Authorization': 'Bearer valid_token'})
                    
                    assert response.status_code == 200
                    result = response.get_json()
                    assert isinstance(result['tasks'], list)
                    assert len(result['tasks']) >= 1
    
    def test_get_all_tasks_with_filters(self, client, sample_task):
        """Test getting all tasks with filters."""
        filters = {
            "status": "pending",
            "priority": "medium",
            "assigned_to": 1
        }
        
        with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.models.models.Task.query') as mock_query:
                    mock_query.filter.return_value.all.return_value = [sample_task]
                    
                    response = client.get('/tasks/?status=pending&priority=medium&assigned_to=1',
                                        headers={'Authorization': 'Bearer valid_token'})
                    
                    assert response.status_code == 200
                    result = response.get_json()
                    assert isinstance(result['tasks'], list)
    
    def test_get_all_tasks_pagination(self, client, sample_task):
        """Test getting all tasks with pagination."""
        with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.models.models.Task.query') as mock_query:
                    mock_pagination = Mock()
                    mock_pagination.items = [sample_task]
                    mock_pagination.total = 1
                    mock_pagination.pages = 1
                    mock_pagination.has_next = False
                    mock_pagination.has_prev = False
                    mock_query.paginate.return_value = mock_pagination
                    
                    response = client.get('/tasks/?page=1&per_page=10',
                                        headers={'Authorization': 'Bearer valid_token'})
                    
                    assert response.status_code == 200
                    result = response.get_json()
                    assert 'tasks' in result
                    assert 'pagination' in result
    
    def test_get_task_by_id_success(self, client, sample_task):
        """Test getting task by ID with valid authentication."""
        with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.models.models.Task.query') as mock_query:
                    mock_query.get_or_404.return_value = sample_task
                    
                    response = client.get('/tasks/1',
                                        headers={'Authorization': 'Bearer valid_token'})
                    
                    assert response.status_code == 200
                    result = response.get_json()
                    assert result['id'] == sample_task.id
                    assert result['title'] == sample_task.title
    
    def test_get_task_by_id_not_found(self, client):
        """Test getting non-existent task by ID."""
        with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.models.models.Task.query') as mock_query:
                    mock_query.get_or_404.side_effect = Exception("Task not found")
                    
                    response = client.get('/tasks/999',
                                        headers={'Authorization': 'Bearer valid_token'})
                    
                    assert response.status_code == 404
    
    def test_update_task_success(self, client, sample_task):
        """Test updating task with valid authentication."""
        update_data = {
            "title": "Updated Task",
            "description": "Updated task description",
            "status": "in_progress",
            "priority": "high"
        }
        
        with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.models.models.Task.query') as mock_query:
                    mock_query.get_or_404.return_value = sample_task
                    
                    with patch('src.models.models.db.session') as mock_session:
                        mock_session.commit = Mock()
                        
                        response = client.put('/tasks/1',
                                            data=json.dumps(update_data),
                                            headers={'Authorization': 'Bearer valid_token'},
                                            content_type='application/json')
                        
                        assert response.status_code == 200
                        result = response.get_json()
                        assert result['message'] == "Task updated successfully"
                        assert result['task']['title'] == "Updated Task"
    
    def test_update_task_validation_error(self, client):
        """Test updating task with validation errors."""
        invalid_data = {
            "title": "",  # Empty title
            "status": "invalid_status",  # Invalid status
            "priority": "invalid_priority"  # Invalid priority
        }
        
        with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                response = client.put('/tasks/1',
                                    data=json.dumps(invalid_data),
                                    headers={'Authorization': 'Bearer valid_token'},
                                    content_type='application/json')
                
                assert response.status_code == 400
                result = response.get_json()
                assert 'error' in result
    
    def test_delete_task_success(self, client, sample_task):
        """Test deleting task with valid authentication."""
        with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.models.models.Task.query') as mock_query:
                    mock_query.get_or_404.return_value = sample_task
                    
                    with patch('src.models.models.db.session') as mock_session:
                        mock_session.delete = Mock()
                        mock_session.commit = Mock()
                        
                        response = client.delete('/tasks/1',
                                              headers={'Authorization': 'Bearer valid_token'})
                        
                        assert response.status_code == 200
                        result = response.get_json()
                        assert "deleted successfully" in result['message']
    
    def test_delete_task_not_found(self, client):
        """Test deleting non-existent task."""
        with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.models.models.Task.query') as mock_query:
                    mock_query.get_or_404.side_effect = Exception("Task not found")
                    
                    response = client.delete('/tasks/999',
                                          headers={'Authorization': 'Bearer valid_token'})
                    
                    assert response.status_code == 404
    
    def test_assign_task_success(self, client, sample_task):
        """Test assigning task to user."""
        assign_data = {
            "assigned_to": 2
        }
        
        with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.models.models.Task.query') as mock_query:
                    mock_query.get_or_404.return_value = sample_task
                    
                    with patch('src.models.models.User.query') as mock_user_query:
                        mock_user = Mock()
                        mock_user.id = 2
                        mock_user_query.get.return_value = mock_user
                        
                        with patch('src.models.models.db.session') as mock_session:
                            mock_session.commit = Mock()
                            
                            response = client.post('/tasks/1/assign',
                                                data=json.dumps(assign_data),
                                                headers={'Authorization': 'Bearer valid_token'},
                                                content_type='application/json')
                            
                            assert response.status_code == 200
                            result = response.get_json()
                            assert result['message'] == "Task assigned successfully"
    
    def test_assign_task_user_not_found(self, client, sample_task):
        """Test assigning task to non-existent user."""
        assign_data = {
            "assigned_to": 999
        }
        
        with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.models.models.Task.query') as mock_query:
                    mock_query.get_or_404.return_value = sample_task
                    
                    with patch('src.models.models.User.query') as mock_user_query:
                        mock_user_query.get.return_value = None
                        
                        response = client.post('/tasks/1/assign',
                                            data=json.dumps(assign_data),
                                            headers={'Authorization': 'Bearer valid_token'},
                                            content_type='application/json')
                            
                            assert response.status_code == 404
                            result = response.get_json()
                            assert 'error' in result
    
    def test_update_task_status_success(self, client, sample_task):
        """Test updating task status."""
        status_data = {
            "status": "completed"
        }
        
        with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.models.models.Task.query') as mock_query:
                    mock_query.get_or_404.return_value = sample_task
                    
                    with patch('src.models.models.db.session') as mock_session:
                        mock_session.commit = Mock()
                        
                        response = client.patch('/tasks/1/status',
                                             data=json.dumps(status_data),
                                             headers={'Authorization': 'Bearer valid_token'},
                                             content_type='application/json')
                        
                        assert response.status_code == 200
                        result = response.get_json()
                        assert result['message'] == "Task status updated successfully"
                        assert result['task']['status'] == "completed"
    
    def test_update_task_status_invalid_status(self, client):
        """Test updating task status with invalid status."""
        status_data = {
            "status": "invalid_status"
        }
        
        with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                response = client.patch('/tasks/1/status',
                                     data=json.dumps(status_data),
                                     headers={'Authorization': 'Bearer valid_token'},
                                     content_type='application/json')
                
                assert response.status_code == 400
                result = response.get_json()
                assert 'error' in result
    
    def test_get_task_comments_success(self, client, sample_task):
        """Test getting task comments."""
        with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.models.models.Task.query') as mock_query:
                    mock_query.get_or_404.return_value = sample_task
                    
                    with patch('src.models.models.Comment.query') as mock_comment_query:
                        mock_comment = Mock()
                        mock_comment.id = 1
                        mock_comment.content = "Test comment"
                        mock_comment.created_at = datetime.now()
                        mock_comment_query.filter_by.return_value.all.return_value = [mock_comment]
                        
                        response = client.get('/tasks/1/comments',
                                            headers={'Authorization': 'Bearer valid_token'})
                        
                        assert response.status_code == 200
                        result = response.get_json()
                        assert isinstance(result['comments'], list)
    
    def test_add_task_comment_success(self, client, sample_task):
        """Test adding comment to task."""
        comment_data = {
            "content": "New comment"
        }
        
        with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.models.models.Task.query') as mock_query:
                    mock_query.get_or_404.return_value = sample_task
                    
                    with patch('src.models.models.db.session') as mock_session:
                        mock_session.add = Mock()
                        mock_session.commit = Mock()
                        
                        response = client.post('/tasks/1/comments',
                                            data=json.dumps(comment_data),
                                            headers={'Authorization': 'Bearer valid_token'},
                                            content_type='application/json')
                        
                        assert response.status_code == 201
                        result = response.get_json()
                        assert result['message'] == "Comment added successfully"
    
    def test_get_task_statistics_success(self, client):
        """Test getting task statistics."""
        with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.models.models.Task.query') as mock_query:
                    mock_query.count.return_value = 100
                    
                    with patch('src.models.models.Task.query') as mock_status_query:
                        mock_status_query.filter_by.return_value.count.return_value = 25
                        
                        response = client.get('/tasks/statistics',
                                            headers={'Authorization': 'Bearer valid_token'})
                        
                        assert response.status_code == 200
                        result = response.get_json()
                        assert 'total_tasks' in result
                        assert 'tasks_by_status' in result
    
    def test_search_tasks_success(self, client, sample_task):
        """Test searching tasks."""
        search_data = {
            "query": "test",
            "filters": {
                "status": "pending",
                "priority": "medium"
            }
        }
        
        with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.models.models.Task.query') as mock_query:
                    mock_query.filter.return_value.all.return_value = [sample_task]
                    
                    response = client.post('/tasks/search',
                                         data=json.dumps(search_data),
                                         headers={'Authorization': 'Bearer valid_token'},
                                         content_type='application/json')
                    
                    assert response.status_code == 200
                    result = response.get_json()
                    assert isinstance(result['tasks'], list)
    
    def test_bulk_update_tasks_success(self, client, sample_task):
        """Test bulk updating tasks."""
        bulk_data = {
            "task_ids": [1, 2, 3],
            "updates": {
                "status": "completed",
                "priority": "low"
            }
        }
        
        with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.models.models.Task.query') as mock_query:
                    mock_query.filter.return_value.all.return_value = [sample_task]
                    
                    with patch('src.models.models.db.session') as mock_session:
                        mock_session.commit = Mock()
                        
                        response = client.put('/tasks/bulk',
                                            data=json.dumps(bulk_data),
                                            headers={'Authorization': 'Bearer valid_token'},
                                            content_type='application/json')
                        
                        assert response.status_code == 200
                        result = response.get_json()
                        assert result['message'] == "Tasks updated successfully"
                        assert 'updated_count' in result
    
    def test_export_tasks_success(self, client, sample_task):
        """Test exporting tasks."""
        with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.models.models.Task.query') as mock_query:
                    mock_query.all.return_value = [sample_task]
                    
                    response = client.get('/tasks/export',
                                        headers={'Authorization': 'Bearer valid_token'})
                    
                    assert response.status_code == 200
                    assert response.content_type == 'application/json'
    
    def test_import_tasks_success(self, client):
        """Test importing tasks."""
        import_data = {
            "tasks": [
                {
                    "title": "Imported Task 1",
                    "description": "Imported task description",
                    "status": "pending",
                    "priority": "medium"
                },
                {
                    "title": "Imported Task 2",
                    "description": "Another imported task",
                    "status": "pending",
                    "priority": "high"
                }
            ]
        }
        
        with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "1"
                
                with patch('src.models.models.db.session') as mock_session:
                    mock_session.add_all = Mock()
                    mock_session.commit = Mock()
                    
                    response = client.post('/tasks/import',
                                         data=json.dumps(import_data),
                                         headers={'Authorization': 'Bearer valid_token'},
                                         content_type='application/json')
                    
                    assert response.status_code == 201
                    result = response.get_json()
                    assert result['message'] == "Tasks imported successfully"
                    assert 'imported_count' in result
    
    def test_task_workflow_validation(self, client, sample_task):
        """Test task workflow validation."""
        # Test invalid status transition
        invalid_transitions = [
            {"from": "completed", "to": "pending"},
            {"from": "cancelled", "to": "in_progress"}
        ]
        
        for transition in invalid_transitions:
            sample_task.status = transition["from"]
            
            status_data = {
                "status": transition["to"]
            }
            
            with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
                mock_verify.return_value = None
                
                with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                    mock_identity.return_value = "1"
                    
                    with patch('src.models.models.Task.query') as mock_query:
                        mock_query.get_or_404.return_value = sample_task
                        
                        response = client.patch('/tasks/1/status',
                                             data=json.dumps(status_data),
                                             headers={'Authorization': 'Bearer valid_token'},
                                             content_type='application/json')
                        
                        assert response.status_code == 400
                        result = response.get_json()
                        assert 'error' in result
    
    def test_task_permission_validation(self, client, sample_task):
        """Test task permission validation."""
        with patch('src.api.tasks.routes.verify_jwt_in_request') as mock_verify:
            mock_verify.return_value = None
            
            with patch('src.api.tasks.routes.get_jwt_identity') as mock_identity:
                mock_identity.return_value = "2"  # Different user
                
                with patch('src.models.models.Task.query') as mock_query:
                    sample_task.assigned_to = 1  # Assigned to different user
                    mock_query.get_or_404.return_value = sample_task
                    
                    # Test unauthorized access
                    response = client.put('/tasks/1',
                                        data=json.dumps({"title": "Updated"}),
                                        headers={'Authorization': 'Bearer valid_token'},
                                        content_type='application/json')
                    
                    assert response.status_code == 403
                    result = response.get_json()
                    assert 'error' in result
