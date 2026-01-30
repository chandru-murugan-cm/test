"""
Unit tests for target_domain API endpoints
"""

import pytest
from unittest.mock import Mock, patch
import json
from flask import Flask

from apis.target_domain import domain_blueprint


class TestTargetDomainAPI:
    """Test cases for target domain API endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create Flask app for testing."""
        app = Flask(__name__)
        app.register_blueprint(domain_blueprint)
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    @pytest.fixture
    def mock_domain_controller(self):
        """Mock DomainController."""
        with patch('apis.target_domain.domain_controller') as mock_controller:
            yield mock_controller
    
    def test_post_domain_success(self, client, mock_domain_controller, sample_domain_target_data, auth_headers):
        """Test successful domain creation via POST."""
        mock_domain_controller.add_entity.return_value = (
            {'success': 'Domain Created Successfully', 'data': sample_domain_target_data},
            '200 Ok'
        )
        
        response = client.post(
            '/crscan/domain',
            data=json.dumps(sample_domain_target_data),
            headers=auth_headers
        )
        
        mock_domain_controller.add_entity.assert_called_once()
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'success' in response_data
    
    def test_get_domains_with_filters(self, client, mock_domain_controller, auth_headers):
        """Test GET domains with query filters."""
        mock_domain_controller.fetch_all.return_value = (
            {'success': 'Records Fetched Successfully', 'data': []},
            '200 Ok'
        )
        
        response = client.get(
            '/crscan/domain?project_id=project-123&domain_url=https://example.com',
            headers=auth_headers
        )
        
        mock_domain_controller.fetch_all.assert_called_once()
        call_args = mock_domain_controller.fetch_all.call_args
        fields = call_args[0][1]
        assert 'project_id' in fields
        assert 'domain_url' in fields
    
    def test_put_domain_success(self, client, mock_domain_controller, sample_domain_target_data, auth_headers):
        """Test successful domain update via PUT."""
        mock_domain_controller.update_by_id.return_value = (
            {'success': 'Domain Updated Successfully', 'data': sample_domain_target_data},
            '200 Ok'
        )
        
        response = client.put(
            '/crscan/domain/domain-123',
            data=json.dumps(sample_domain_target_data),
            headers=auth_headers
        )
        
        mock_domain_controller.update_by_id.assert_called_once()
        assert response.status_code == 200
    
    def test_delete_domain_success(self, client, mock_domain_controller, auth_headers):
        """Test successful domain deletion via DELETE."""
        mock_domain_controller.delete_by_id.return_value = (
            {'success': 'Domain Deleted Successfully'},
            '200 Ok'
        )
        
        response = client.delete('/crscan/domain/domain-123', headers=auth_headers)
        
        mock_domain_controller.delete_by_id.assert_called_once_with('domain-123')
        assert response.status_code == 200