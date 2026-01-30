"""
Pytest configuration and shared fixtures for all tests
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from mongoengine import connect, disconnect
import mongomock

# Add service directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Test configuration - simplified setup without external dependencies

try:
    from app import app as flask_app
    from config_params import *
except ImportError as e:
    print(f"Warning: Could not import app or config_params: {e}")
    flask_app = Flask(__name__)
    
# Apply basic test configuration
flask_app.config.update({
    'TESTING': True,
    'WTF_CSRF_ENABLED': False,
    'MONGODB_SETTINGS': {'host': 'mongomock://localhost'}
})


@pytest.fixture
def app():
    """Create and configure a test Flask app."""
    flask_app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'JWT_SECRET_KEY': 'test-jwt-secret',
        'DATABASE_NAME': 'test_scans_db'
    })
    
    # Create application context
    with flask_app.app_context():
        yield flask_app


@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    return app.test_client()


@pytest.fixture
def auth_headers():
    """Create authorization headers with mock JWT token."""
    return {
        'Authorization': 'Bearer test-jwt-token',
        'Content-Type': 'application/json'
    }


@pytest.fixture(scope='function')
def mock_db():
    """Mock MongoDB connection for tests."""
    # Disconnect any existing connections
    disconnect()
    
    # Create mock connection with proper mongo_client_class
    connect('mongoenginetest', host='localhost', mongo_client_class=mongomock.MongoClient)
    
    yield
    
    # Cleanup
    disconnect()


@pytest.fixture
def mock_jwt():
    """Mock JWT token validation."""
    with patch('flask_jwt_extended.verify_jwt_in_request') as mock_verify, \
         patch('flask_jwt_extended.get_jwt_identity') as mock_identity, \
         patch('controllers.util.verify_jwt_in_request') as mock_util_verify, \
         patch('controllers.util.get_jwt_identity') as mock_util_identity:
        
        mock_verify.return_value = True
        mock_identity.return_value = 'test-user-id'
        mock_util_verify.return_value = True
        mock_util_identity.return_value = 'test-user-id'
        
        yield mock_verify, mock_identity


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        'domain_value': 'https://test-example.com',
        'organization': 'Test Organization',
        'name': 'Test Security Project',
        'description': 'A test project for security assessments',
        'owner': 'test-user@example.com',
        'created_by': 'test-user-id',
        'project_type': 'web_application',
        'status': 'active'
    }


@pytest.fixture
def sample_scanner_data():
    """Sample scanner data for testing."""
    return {
        'name': 'Test OWASP ZAP Scanner',
        'scanner_type': 'DAST',
        'description': 'Dynamic Application Security Testing',
        'configuration': {
            'url': 'http://localhost:8080',
            'timeout': 300
        },
        'capabilities': ['web_scan', 'api_scan'],
        'status': 'active'
    }


@pytest.fixture
def sample_domain_target_data():
    """Sample domain target data for testing."""
    return {
        'project_id': '507f1f77bcf86cd799439011',
        'domain_url': 'https://test-example.com',
        'name': 'Test Website',
        'description': 'Test website for security scanning',
        'scan_config': {
            'authentication': {
                'type': 'none'
            },
            'max_depth': 3
        }
    }


@pytest.fixture
def sample_repo_target_data():
    """Sample repository target data for testing."""
    return {
        'project_id': '507f1f77bcf86cd799439011',
        'repository_url': 'https://github.com/test/repo.git',
        'name': 'Test Repository',
        'description': 'Test repository for security scanning',
        'branch': 'main',
        'scan_config': {
            'include_paths': ['src/', 'lib/'],
            'exclude_paths': ['node_modules/', 'test/'],
            'scan_secrets': True,
            'scan_dependencies': True
        }
    }


@pytest.fixture
def sample_scan_data():
    """Sample scan data for testing."""
    return {
        'project_id': '507f1f77bcf86cd799439011',
        'target_id': '507f1f77bcf86cd799439012',
        'target_type': 'domain',
        'scanner_type_ids_list': ['zap', 'wapiti'],
        'scan_name': 'Test Security Scan',
        'scan_description': 'Automated security scan for testing'
    }


@pytest.fixture
def sample_finding_data():
    """Sample finding data for testing."""
    return {
        'project_id': '507f1f77bcf86cd799439011',
        'scan_id': '507f1f77bcf86cd799439012',
        'title': 'SQL Injection Vulnerability',
        'description': 'SQL injection found in login form',
        'severity': 'high',
        'status': 'open',
        'scanner_type': 'zap',
        'target_type': 'web_application',
        'cvss_score': 8.5,
        'location': '/login.php',
        'evidence': 'Payload: \' OR 1=1--',
        'remediation': 'Use parameterized queries'
    }


@pytest.fixture
def sample_compliance_data():
    """Sample compliance data for testing."""
    return {
        'compliance_type': 'SAMM',
        'compliance_group_name': 'Governance',
        'control_id': 'G-EG-1',
        'control_title': 'Establish governance and compliance',
        'control_description': 'Implement security governance processes',
        'maturity_level': 2,
        'assessment_status': 'compliant'
    }


@pytest.fixture
def sample_scheduler_data():
    """Sample scheduler data for testing."""
    return {
        'name': 'Weekly Security Scan',
        'project_id': '507f1f77bcf86cd799439011',
        'schedule_config': {
            'frequency': 'weekly',
            'time': '02:00',
            'day_of_week': 1
        },
        'scanner_types': ['zap', 'trivy'],
        'enabled': True,
        'description': 'Automated weekly security assessment'
    }


@pytest.fixture
def mock_scanner_responses():
    """Mock scanner responses for testing."""
    return {
        'zap': {
            'scan_id': 'zap-scan-123',
            'status': 'completed',
            'findings': [
                {
                    'title': 'Cross-Site Scripting',
                    'severity': 'medium',
                    'location': '/search.php',
                    'evidence': '<script>alert(1)</script>'
                }
            ]
        },
        'trivy': {
            'scan_id': 'trivy-scan-456',
            'status': 'completed',
            'vulnerabilities': [
                {
                    'cve_id': 'CVE-2023-1234',
                    'severity': 'high',
                    'package': 'lodash@4.17.15',
                    'fixed_version': '4.17.21'
                }
            ]
        }
    }


@pytest.fixture
def mock_external_services():
    """Mock external service calls."""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post, \
         patch('requests.put') as mock_put, \
         patch('requests.delete') as mock_delete:
        
        # Configure default responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True, 'data': {}}
        
        mock_get.return_value = mock_response
        mock_post.return_value = mock_response
        mock_put.return_value = mock_response
        mock_delete.return_value = mock_response
        
        yield {
            'get': mock_get,
            'post': mock_post,
            'put': mock_put,
            'delete': mock_delete
        }


@pytest.fixture
def mock_github_oauth():
    """Mock GitHub OAuth responses."""
    with patch('requests.post') as mock_token_request, \
         patch('requests.get') as mock_api_request:
        
        # Mock token exchange
        mock_token_response = Mock()
        mock_token_response.json.return_value = {
            'access_token': 'ghp_test_token_123',
            'token_type': 'bearer'
        }
        mock_token_request.return_value = mock_token_response
        
        # Mock GitHub API calls
        mock_api_response = Mock()
        mock_api_response.status_code = 200
        mock_api_response.json.return_value = [
            {
                'id': 123456,
                'name': 'test-repo',
                'full_name': 'testuser/test-repo',
                'clone_url': 'https://github.com/testuser/test-repo.git',
                'private': False,
                'language': 'Python'
            }
        ]
        mock_api_request.return_value = mock_api_response
        
        yield mock_token_request, mock_api_request


@pytest.fixture
def flask_app_context():
    """Provide Flask application context for controller tests."""
    with flask_app.app_context():
        with flask_app.test_request_context(
            path='/',
            method='POST',
            headers={'Authorization': 'Bearer test-token', 'Content-Type': 'application/json'},
            json={'test': 'data'}
        ):
            yield flask_app


@pytest.fixture
def mock_flask_request():
    """Mock Flask request object for controller tests."""
    mock_request = Mock()
    mock_request.get_json.return_value = {'test': 'data'}
    mock_request.method = 'POST'
    mock_request.headers = {'Authorization': 'Bearer test-token'}
    mock_request.data = b'{"test": "data"}'
    return mock_request


@pytest.fixture
def comprehensive_controller_mocks():
    """Comprehensive mocking setup for controller tests."""
    with patch('controllers.util.verify_jwt_in_request') as mock_verify_jwt, \
         patch('controllers.util.get_jwt_identity') as mock_get_identity, \
         patch('controllers.util.get_current_user_from_jwt_token') as mock_get_user, \
         patch('flask_jwt_extended.verify_jwt_in_request') as mock_ext_verify, \
         patch('flask_jwt_extended.get_jwt_identity') as mock_ext_identity:
        
        # Setup all JWT mocks
        mock_verify_jwt.return_value = True
        mock_get_identity.return_value = 'test-user-id'
        mock_get_user.return_value = 'test-user-id'
        mock_ext_verify.return_value = True
        mock_ext_identity.return_value = 'test-user-id'
        
        yield {
            'verify_jwt': mock_verify_jwt,
            'get_identity': mock_get_identity,
            'get_user': mock_get_user,
            'ext_verify': mock_ext_verify,
            'ext_identity': mock_ext_identity
        }


@pytest.fixture
def controller_test_context():
    """Helper fixture for controller tests that need Flask app context and request mocking."""
    with flask_app.app_context():
        with flask_app.test_request_context(
            path='/',
            method='POST',
            headers={'Authorization': 'Bearer test-token', 'Content-Type': 'application/json'},
            json={'test': 'data'}
        ):
            yield flask_app


class ControllerTestHelper:
    """Helper class for controller test operations."""
    
    @staticmethod
    def mock_flask_request(request_data):
        """Create a proper Flask request mock with the given data."""
        from contextlib import contextmanager
        
        @contextmanager
        def mock_context():
            with patch('flask.request') as mock_request:
                mock_request.get_json.return_value = request_data
                mock_request.method = 'POST'
                mock_request.headers = {'Authorization': 'Bearer test-token'}
                mock_request.json = request_data
                yield mock_request
        
        return mock_context()
    
    @staticmethod
    def extract_response_data(response_tuple):
        """Extract response data from controller response tuple."""
        if not isinstance(response_tuple, tuple) or len(response_tuple) != 2:
            return response_tuple, None
        
        response_data, status_code = response_tuple
        
        # Handle Flask Response objects
        if hasattr(response_data, 'get_json'):
            response_data = response_data.get_json()
        elif hasattr(response_data, 'data'):
            import json
            try:
                response_data = json.loads(response_data.data.decode())
            except:
                pass
        
        return response_data, status_code
    
    @staticmethod
    def assert_success_response(response_tuple, expected_keys=None):
        """Assert that response is successful with expected structure."""
        response_data, status_code = ControllerTestHelper.extract_response_data(response_tuple)
        
        assert isinstance(response_tuple, tuple)
        assert 'success' in response_data or 'data' in response_data
        assert status_code in ['200 Ok', '201 Created']
        
        if expected_keys:
            for key in expected_keys:
                assert key in response_data
    
    @staticmethod
    def assert_error_response(response_tuple, expected_error=None):
        """Assert that response is an error with optional message check."""
        response_data, status_code = ControllerTestHelper.extract_response_data(response_tuple)
        
        assert isinstance(response_tuple, tuple)
        assert 'error' in response_data or 'message' in response_data
        assert status_code.startswith('4') or status_code.startswith('5')
        
        if expected_error:
            error_msg = response_data.get('error', response_data.get('message', ''))
            assert expected_error in str(error_msg)


@pytest.fixture(autouse=True)
def setup_mocks():
    """Automatically setup common mocks for all tests."""
    with patch('controllers.util.get_current_user_from_jwt_token') as mock_user:
        mock_user.return_value = 'test-user-id'
        yield mock_user


@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup after each test."""
    yield
    # Add any cleanup logic here
    pass


# Test utilities
class TestUtils:
    """Utility functions for tests."""
    
    @staticmethod
    def create_mock_object_id():
        """Create a mock MongoDB ObjectId."""
        return '507f1f77bcf86cd799439011'
    
    @staticmethod
    def assert_response_structure(response_data, expected_keys):
        """Assert that response has expected structure."""
        for key in expected_keys:
            assert key in response_data, f"Missing key: {key}"
    
    @staticmethod
    def assert_error_response(response_data, expected_error=None):
        """Assert that response is an error with optional message check."""
        assert 'error' in response_data or 'message' in response_data
        if expected_error:
            error_msg = response_data.get('error', response_data.get('message', ''))
            assert expected_error in error_msg


# Make TestUtils available as fixture
@pytest.fixture
def test_utils():
    """Test utilities fixture."""
    return TestUtils


# Make ControllerTestHelper available as fixture
@pytest.fixture
def controller_helper():
    """Controller test helper fixture."""
    return ControllerTestHelper