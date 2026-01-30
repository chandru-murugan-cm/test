"""
Base class for controller tests with proper Flask context handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
import json

class ControllerTestBase:
    """Base class for controller tests that handles Flask context properly."""
    
    def setup_method(self):
        """Setup method called before each test."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def teardown_method(self):
        """Teardown method called after each test."""
        if hasattr(self, 'app_context'):
            self.app_context.pop()
    
    def mock_flask_request(self, json_data=None, method='POST', headers=None):
        """Create a proper Flask request mock."""
        if headers is None:
            headers = {'Authorization': 'Bearer test-token', 'Content-Type': 'application/json'}
        
        mock_request = Mock()
        mock_request.get_json.return_value = json_data or {}
        mock_request.json = json_data or {}
        mock_request.method = method
        mock_request.headers = headers
        mock_request.data = json.dumps(json_data or {}).encode() if json_data else b'{}'
        
        return mock_request
    
    def call_controller_method(self, controller, method_name, request_data=None):
        """Call a controller method with proper Flask context."""
        # Use Flask test request context within the app context
        with self.app.test_request_context(
            path='/',
            method='POST',
            headers={'Authorization': 'Bearer test-token', 'Content-Type': 'application/json'},
            json=request_data or {}
        ):
            from flask import request
            method = getattr(controller, method_name)
            
            # For methods that need arguments
            if method_name in ['remove_entity', 'delete_by_id']:
                if isinstance(request_data, str):
                    return method(request_data)
                else:
                    # Extract ID from request data
                    entity_id = request_data.get('id', 'test-id') if request_data else 'test-id'
                    return method(entity_id)
            elif method_name == 'update_by_id':
                # ProjectController.update_by_id gets data from Flask request context
                if controller.__class__.__name__ == 'ProjectController':
                    return method(request_data)  # It will ignore this parameter and use request.get_json()
                else:
                    # Other controllers need request object and ID parameter  
                    if isinstance(request_data, dict):
                        entity_id = request_data.get('id', 'test-id')
                        return method(request, entity_id)  # Use Flask request object
                    else:
                        return method(request, 'test-id')
            elif method_name in ['fetch_all', 'fetch_schedules']:
                # These methods typically take (request, fields) parameters
                fields = request_data or {}
                mock_request = Mock()
                mock_request.args = Mock()
                mock_request.args.get = lambda key, default=None: fields.get(key, default)
                return method(mock_request, fields)
            else:
                # Most methods expect request parameter - use Flask request object
                return method(request)
    
    def extract_response(self, response_tuple):
        """Extract and normalize response data from controller response."""
        if not isinstance(response_tuple, tuple) or len(response_tuple) != 2:
            return response_tuple, None
        
        response_data, status_code = response_tuple
        
        # Handle Flask Response objects
        if hasattr(response_data, 'get_json'):
            response_data = response_data.get_json()
        elif hasattr(response_data, 'data'):
            try:
                response_data = json.loads(response_data.data.decode())
            except:
                pass
        
        return response_data, status_code
    
    def assert_success_response(self, response_tuple, expected_keys=None):
        """Assert successful response."""
        response_data, status_code = self.extract_response(response_tuple)
        
        assert isinstance(response_tuple, tuple)
        assert 'success' in response_data or 'data' in response_data
        assert status_code in ['200 Ok', '201 Created']
        
        if expected_keys:
            for key in expected_keys:
                assert key in response_data
        
        return response_data, status_code
    
    def assert_error_response(self, response_tuple, expected_error=None):
        """Assert error response."""
        response_data, status_code = self.extract_response(response_tuple)
        
        assert isinstance(response_tuple, tuple)
        
        # Check for different error response formats
        has_error = (
            'error' in response_data or 
            'message' in response_data or
            # Validation errors (field-level errors)
            any(isinstance(v, list) for v in response_data.values()) or
            # Status code indicates error
            (status_code and (status_code.startswith('4') or status_code.startswith('5')))
        )
        
        assert has_error, f"Expected error response but got: {response_data}"
        assert status_code.startswith('4') or status_code.startswith('5')
        
        if expected_error:
            error_msg = str(response_data)
            assert expected_error in error_msg
        
        return response_data, status_code
