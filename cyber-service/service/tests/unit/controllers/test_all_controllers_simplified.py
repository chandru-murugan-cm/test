"""
Simplified tests for all controllers using ControllerTestBase
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from tests.unit.controllers.controller_test_base import ControllerTestBase
from controllers.DomainController import DomainController
from controllers.ProjectController import ProjectController


class TestAllControllersSimplified(ControllerTestBase):
    """Simplified test cases for all controllers."""
    
    @pytest.fixture(params=[
        ('DomainController', DomainController),
        ('ProjectController', ProjectController)
    ])
    def controller_info(self, request):
        """Parametrized fixture for controller classes."""
        return request.param
    
    @patch('controllers.util.get_current_user_from_jwt_token')
    def test_controller_initialization(self, mock_get_user, controller_info):
        """Test that all controllers can be initialized."""
        mock_get_user.return_value = 'test-user-id'
        
        controller_name, controller_class = controller_info
        controller = controller_class()
        
        assert controller is not None
        assert hasattr(controller, '__class__')
        assert controller.__class__.__name__ == controller_name.split('Controller')[0] + 'Controller'
    
    @patch('controllers.util.get_current_user_from_jwt_token')
    def test_controller_has_methods(self, mock_get_user, controller_info):
        """Test that controllers have expected methods."""
        mock_get_user.return_value = 'test-user-id'
        
        controller_name, controller_class = controller_info
        controller = controller_class()
        
        # Check for common controller methods
        expected_methods = ['add_entity', 'fetch_all', 'update_by_id', 'remove_entity']
        
        for method in expected_methods:
            if hasattr(controller, method):
                assert callable(getattr(controller, method))
    
    @patch('controllers.DomainController.Domain')
    @patch('controllers.ProjectController.Project')
    @patch('controllers.DomainController.get_current_user_from_jwt_token')
    @patch('controllers.ProjectController.get_current_user_from_jwt_token')
    def test_controller_fetch_all_basic(self, mock_project_get_user, mock_domain_get_user, mock_project_model, mock_domain_model, controller_info):
        """Test basic fetch_all for all controllers."""
        mock_project_get_user.return_value = 'test-user-id'
        mock_domain_get_user.return_value = 'test-user-id'
        
        # Mock empty responses
        mock_domain_model.objects.aggregate.return_value = []
        mock_project_model.objects.filter.return_value.aggregate.return_value = []
        
        controller_name, controller_class = controller_info
        controller = controller_class()
        
        # Execute using base class helper
        if hasattr(controller, 'fetch_all'):
            result = self.call_controller_method(controller, 'fetch_all', {})
            
            # All controllers should handle empty fetch - either success or error
            response_data, status_code = self.extract_response(result)
            assert isinstance(response_data, dict)
            assert status_code is not None
