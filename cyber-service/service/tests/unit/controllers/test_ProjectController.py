"""
Unit tests for ProjectController with proper Flask context handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime, timezone
from mongoengine.errors import DoesNotExist, ValidationError as MongoValidationError
from marshmallow import ValidationError

from controllers.ProjectController import ProjectController
from tests.unit.controllers.controller_test_base import ControllerTestBase


class TestProjectController(ControllerTestBase):
    """Test cases for ProjectController class."""
    
    @pytest.fixture
    def controller(self):
        """Create ProjectController instance for testing."""
        return ProjectController()
    
    def test_init(self, controller):
        """Test controller initialization."""
        assert controller is not None
    
    @patch('controllers.ProjectController.get_current_user_from_jwt_token')
    @patch('controllers.ProjectController.Project')
    @patch('uuid.uuid4')
    def test_add_entity_success(self, mock_uuid, mock_project, mock_get_user, controller):
        """Test successful project creation."""
        # Setup mocks
        mock_get_user.return_value = 'test-user-id'
        mock_uuid.return_value = Mock(hex="test-project-id")
        
        mock_project_entity = Mock()
        mock_project_entity.save.return_value = None
        mock_project_entity.to_json.return_value = json.dumps({'test': 'data'})
        mock_project.return_value = mock_project_entity
        
        # Test data
        test_data = {
            'name': 'Test Project',
            'description': 'Test Description',
            'domain_value': 'https://example.com',
            'organization': 'Test Organization'
        }
        
        # Execute using base class helper
        result = self.call_controller_method(controller, 'add_entity', test_data)
        
        # Assert using base class helper - expect success
        self.assert_success_response(result, ['success', 'data'])
    
    @patch('controllers.ProjectController.get_current_user_from_jwt_token')
    def test_add_entity_validation_error(self, mock_get_user, controller):
        """Test project creation with validation error."""
        mock_get_user.return_value = 'test-user-id'
        
        # Invalid data missing required fields
        invalid_data = {
            'description': 'Test Description'  # Missing name
        }
        
        # Execute
        result = self.call_controller_method(controller, 'add_entity', invalid_data)
        
        # Assert error response
        self.assert_error_response(result)
    
    @patch('controllers.ProjectController.get_current_user_from_jwt_token')
    @patch('controllers.ProjectController.Project')
    def test_fetch_all_success(self, mock_project, mock_get_user, controller):
        """Test successful project fetch."""
        mock_get_user.return_value = 'test-user-id'
        
        # Mock aggregation result
        mock_projects = [
            {'name': 'Project 1'},
            {'name': 'Project 2'}
        ]
        mock_project.objects.aggregate.return_value = mock_projects
        
        # Execute
        result = self.call_controller_method(controller, 'fetch_all', {})
        
        # Assert success
        self.assert_success_response(result, ['success', 'data'])
    
    @patch('controllers.ProjectController.serialize_mongo_data')
    @patch('controllers.ProjectController.get_current_user_from_jwt_token')  
    @patch('controllers.ProjectController.Project')
    def test_update_by_id_success(self, mock_project, mock_get_user, mock_serialize, controller):
        """Test successful project update."""
        mock_get_user.return_value = 'test-user-id'
        mock_serialize.return_value = {'serialized': 'data'}
        
        # Mock existing project with dict-like behavior
        mock_existing_project = MagicMock()
        mock_existing_project.__setitem__ = MagicMock()  # Allow item assignment
        mock_existing_project.__getitem__ = MagicMock()  # Allow item access
        mock_existing_project.save.return_value = None
        mock_existing_project.to_json.return_value = json.dumps({'updated': True})
        mock_existing_project.id = 'test-object-id'  # Mock the MongoDB ObjectId
        mock_project.objects.get.return_value = mock_existing_project
        
        # Mock the aggregation that runs after the update
        mock_aggregation_result = [{'_id': 'test-object-id', 'name': 'Updated Project', 'updated': True}]
        mock_project.objects.aggregate.return_value = mock_aggregation_result
        
        update_data = {
            '_id': 'test-project-id',  # ProjectController needs _id in the data
            'name': 'Updated Project',
            'description': 'Updated Description',
            'organization': 'Test Organization',  # Required field
            'status': 'active'  # Required field from schema
        }
        
        # Execute - ProjectController.update_by_id only takes request_json, not separate entity_id
        result = self.call_controller_method(controller, 'update_by_id', update_data)
        
        # Assert success
        self.assert_success_response(result, ['success', 'data'])
    
    @patch('controllers.ProjectController.verify_jwt_in_request')
    @patch('controllers.ProjectController.Project')  
    def test_remove_entity_success(self, mock_project, mock_verify_jwt, controller):
        """Test successful project deletion."""
        mock_verify_jwt.return_value = None
        
        # Mock existing project
        mock_existing_project = Mock()
        mock_existing_project.delete.return_value = None
        mock_project.objects.get.return_value = mock_existing_project
        
        # Execute
        result = self.call_controller_method(controller, 'remove_entity', 'test-project-id')
        
        # Assert success
        self.assert_success_response(result, ['success'])
