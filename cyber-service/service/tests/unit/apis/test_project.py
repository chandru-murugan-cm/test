"""
Unit tests for project API endpoints
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from flask import Flask

from apis.project import project_blueprint, project


class TestProjectAPI:
    """Test cases for project API endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create Flask app for testing."""
        app = Flask(__name__)
        app.register_blueprint(project_blueprint)
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    @pytest.fixture
    def mock_project_controller(self):
        """Mock ProjectController."""
        with patch('apis.project.project_controller') as mock_controller:
            yield mock_controller
    
    def test_post_project_success(self, client, mock_project_controller, sample_project_data, auth_headers):
        """Test successful project creation via POST."""
        # Setup mock
        mock_project_controller.add_entity.return_value = (
            {'success': 'Record Created Successfully', 'data': sample_project_data},
            '200 Ok'
        )
        
        # Execute
        response = client.post(
            '/crscan/project',
            data=json.dumps(sample_project_data),
            headers=auth_headers
        )
        
        # Assertions
        mock_project_controller.add_entity.assert_called_once()
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'success' in response_data
        assert 'data' in response_data
    
    def test_post_project_missing_data(self, client, mock_project_controller, auth_headers):
        """Test POST project with missing data."""
        # Execute - no data sent
        response = client.post(
            '/crscan/project',
            headers=auth_headers
        )
        
        # Assertions
        mock_project_controller.add_entity.assert_not_called()
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert 'Missing Project details' in response_data['error']
    
    def test_post_project_controller_error(self, client, mock_project_controller, sample_project_data, auth_headers):
        """Test POST project with controller error."""
        # Setup mock to return error
        mock_project_controller.add_entity.return_value = (
            {'error': 'Validation failed'},
            '400 Bad Request'
        )
        
        # Execute
        response = client.post(
            '/crscan/project',
            data=json.dumps(sample_project_data),
            headers=auth_headers
        )
        
        # Assertions
        mock_project_controller.add_entity.assert_called_once()
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_get_project_all(self, client, mock_project_controller, auth_headers):
        """Test GET all projects."""
        # Setup mock
        mock_project_data = [
            {'id': '1', 'name': 'Project 1'},
            {'id': '2', 'name': 'Project 2'}
        ]
        mock_project_controller.fetch_all.return_value = (
            {'success': 'Records Fetched Successfully', 'data': mock_project_data},
            '200 Ok'
        )
        
        # Execute
        response = client.get('/crscan/project', headers=auth_headers)
        
        # Assertions
        mock_project_controller.fetch_all.assert_called_once()
        call_args = mock_project_controller.fetch_all.call_args
        assert call_args[0][1] == {}  # Empty fields dict
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'success' in response_data
        assert len(response_data['data']) == 2
    
    def test_get_project_with_query_params(self, client, mock_project_controller, auth_headers):
        """Test GET projects with query parameters."""
        # Setup mock
        mock_project_controller.fetch_all.return_value = (
            {'success': 'Records Fetched Successfully', 'data': []},
            '200 Ok'
        )
        
        # Execute
        response = client.get(
            '/crscan/project?project_id=123&name=TestProject',
            headers=auth_headers
        )
        
        # Assertions
        mock_project_controller.fetch_all.assert_called_once()
        call_args = mock_project_controller.fetch_all.call_args
        fields = call_args[0][1]
        assert '_id' in fields
        assert 'name' in fields
        assert fields['_id'] == '123'
        assert fields['name'] == 'TestProject'
    
    def test_get_project_by_id(self, client, mock_project_controller, auth_headers):
        """Test GET project by ID in URL path."""
        # Setup mock
        mock_project_controller.fetch_all.return_value = (
            {'success': 'Records Fetched Successfully', 'data': [{'id': 'test-id'}]},
            '200 Ok'
        )
        
        # Execute
        response = client.get('/crscan/project/test-id', headers=auth_headers)
        
        # Assertions
        mock_project_controller.fetch_all.assert_called_once()
        call_args = mock_project_controller.fetch_all.call_args
        fields = call_args[0][1]
        assert '_id' in fields
        assert fields['_id'] == 'test-id'
    
    def test_get_project_filter_none_values(self, client, mock_project_controller, auth_headers):
        """Test GET projects filters out None values correctly."""
        # Setup mock
        mock_project_controller.fetch_all.return_value = (
            {'success': 'Records Fetched Successfully', 'data': []},
            '200 Ok'
        )
        
        # Execute - only project_id provided, name is None
        response = client.get('/crscan/project?project_id=123', headers=auth_headers)
        
        # Assertions
        mock_project_controller.fetch_all.assert_called_once()
        call_args = mock_project_controller.fetch_all.call_args
        fields = call_args[0][1]
        assert '_id' in fields
        assert 'name' not in fields  # Should be filtered out
    
    def test_put_project_success(self, client, mock_project_controller, sample_project_data, auth_headers):
        """Test successful project update via PUT."""
        # Setup mock
        mock_project_controller.update_by_id.return_value = (
            {'success': 'Record Updated Successfully', 'data': sample_project_data},
            '200 Ok'
        )
        
        # Execute
        response = client.put(
            '/crscan/project/test-id',
            data=json.dumps(sample_project_data),
            headers=auth_headers
        )
        
        # Assertions
        mock_project_controller.update_by_id.assert_called_once()
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'success' in response_data
    
    def test_put_project_missing_id(self, client, mock_project_controller, sample_project_data, auth_headers):
        """Test PUT project without project ID."""
        # Execute - no project_id in URL
        response = client.put(
            '/crscan/project',
            data=json.dumps(sample_project_data),
            headers=auth_headers
        )
        
        # Assertions - PUT without ID returns 405 Method Not Allowed
        mock_project_controller.update_by_id.assert_not_called()
        assert response.status_code == 405  # Method Not Allowed
    
    def test_put_project_controller_error(self, client, mock_project_controller, sample_project_data, auth_headers):
        """Test PUT project with controller error."""
        # Setup mock to return error
        mock_project_controller.update_by_id.return_value = (
            {'error': 'Project not found'},
            '404 Not Found'
        )
        
        # Execute
        response = client.put(
            '/crscan/project/nonexistent-id',
            data=json.dumps(sample_project_data),
            headers=auth_headers
        )
        
        # Assertions
        mock_project_controller.update_by_id.assert_called_once()
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_delete_project_success(self, client, mock_project_controller, auth_headers):
        """Test successful project deletion via DELETE."""
        # Setup mock
        mock_project_controller.remove_entity.return_value = (
            {'success': 'Record Deleted Successfully'},
            '200 Ok'
        )
        
        # Execute
        response = client.delete('/crscan/project/test-id', headers=auth_headers)
        
        # Assertions
        mock_project_controller.remove_entity.assert_called_once_with('test-id')
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'success' in response_data
    
    def test_delete_project_missing_id(self, client, mock_project_controller, auth_headers):
        """Test DELETE project without project ID."""
        # Execute - no project_id in URL
        response = client.delete('/crscan/project', headers=auth_headers)
        
        # Assertions - DELETE without ID returns 405 Method Not Allowed
        mock_project_controller.remove_entity.assert_not_called()
        assert response.status_code == 405  # Method Not Allowed
    
    def test_delete_project_controller_error(self, client, mock_project_controller, auth_headers):
        """Test DELETE project with controller error."""
        # Setup mock to return error
        mock_project_controller.remove_entity.return_value = (
            {'error': 'Project not found'},
            '404 Not Found'
        )
        
        # Execute
        response = client.delete('/crscan/project/nonexistent-id', headers=auth_headers)
        
        # Assertions
        mock_project_controller.remove_entity.assert_called_once_with('nonexistent-id')
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_unsupported_method(self, client, auth_headers):
        """Test unsupported HTTP method."""
        # Execute PATCH method (not supported)
        response = client.patch('/crscan/project/test-id', headers=auth_headers)
        
        # Assertions
        assert response.status_code == 405  # Method Not Allowed
    
    def test_request_parsing_edge_cases(self, client, mock_project_controller, auth_headers):
        """Test edge cases in request parsing."""
        # Test with empty query parameters
        response = client.get('/crscan/project?project_id=&name=', headers=auth_headers)
        
        mock_project_controller.fetch_all.assert_called()
        call_args = mock_project_controller.fetch_all.call_args
        fields = call_args[0][1]
        
        # Empty strings are kept in the API (only None values are filtered out)
        expected_fields = {'_id': '', 'name': ''}
        assert fields == expected_fields
    
    def test_content_type_handling(self, client, mock_project_controller, sample_project_data):
        """Test different content types."""
        # Test with proper JSON content type
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token'
        }
        
        mock_project_controller.add_entity.return_value = (
            {'success': 'Record Created Successfully', 'data': sample_project_data},
            '200 Ok'
        )
        
        response = client.post(
            '/crscan/project',
            data=json.dumps(sample_project_data),
            headers=headers
        )
        
        assert response.status_code == 200
    
    def test_concurrent_requests(self, client, mock_project_controller, auth_headers):
        """Test handling of concurrent requests."""
        import threading
        import time
        
        # Setup mock with slight delay
        def mock_fetch_with_delay(*args, **kwargs):
            time.sleep(0.01)  # Small delay to simulate processing
            return ({'success': 'Records Fetched Successfully', 'data': []}, '200 Ok')
        
        mock_project_controller.fetch_all.side_effect = mock_fetch_with_delay
        
        # Execute concurrent requests
        results = []
        def make_request():
            response = client.get('/crscan/project', headers=auth_headers)
            results.append(response.status_code)
        
        threads = [threading.Thread(target=make_request) for _ in range(5)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 5
    
    def test_blueprint_registration(self, app):
        """Test that blueprint is properly registered."""
        # Check that blueprint is registered
        assert 'project_blueprint' in [bp.name for bp in app.blueprints.values()]
        
        # Check route registration by testing rule existence
        route_found = False
        for rule in app.url_map.iter_rules():
            if rule.rule == '/crscan/project':
                route_found = True
                break
        assert route_found  # Route exists
    
    def test_swagger_documentation(self):
        """Test that API has proper Swagger documentation."""
        # The swag_from decorator should be applied
        # This is more of a structural test to ensure documentation exists
        import inspect
        func_source = inspect.getsource(project)
        assert '@swag_from' in func_source
    
    def test_error_response_format(self, client, mock_project_controller, auth_headers):
        """Test consistent error response format."""
        # Setup mock to return error tuple instead of raising exception
        mock_project_controller.fetch_all.return_value = (
            {'error': 'Database connection failed'},
            '500 Internal Server Error'
        )
        
        # Execute
        response = client.get('/crscan/project', headers=auth_headers)
        
        # Should return error response
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_response_headers(self, client, mock_project_controller, auth_headers):
        """Test response headers."""
        mock_project_controller.fetch_all.return_value = (
            {'success': 'Records Fetched Successfully', 'data': []},
            '200 Ok'
        )
        
        response = client.get('/crscan/project', headers=auth_headers)
        
        # Check content type
        assert 'application/json' in response.headers.get('Content-Type', '')
    
    def test_large_data_handling(self, client, mock_project_controller, auth_headers):
        """Test handling of large data sets."""
        # Create large mock data
        large_data = [{'id': f'project-{i}', 'name': f'Project {i}'} for i in range(1000)]
        
        mock_project_controller.fetch_all.return_value = (
            {'success': 'Records Fetched Successfully', 'data': large_data},
            '200 Ok'
        )
        
        response = client.get('/crscan/project', headers=auth_headers)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert len(response_data['data']) == 1000