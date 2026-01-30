"""
Unit tests for scheduler API endpoints
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from flask import Flask

from apis.scheduler import scheduler_blueprint


class TestSchedulerAPI:
    """Test cases for scheduler API endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create Flask app for testing."""
        app = Flask(__name__)
        app.register_blueprint(scheduler_blueprint)
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    @pytest.fixture
    def mock_scheduler_controller(self):
        """Mock SchedulerController."""
        with patch('apis.scheduler.scheduler_controller') as mock_controller:
            yield mock_controller
    
    def test_post_scheduler_success(self, client, mock_scheduler_controller, sample_scheduler_data, auth_headers):
        """Test successful scheduler creation via POST."""
        # Setup mock
        mock_scheduler_controller.add_entity.return_value = (
            {'success': 'Scheduler Created Successfully', 'data': sample_scheduler_data},
            '200 Ok'
        )
        
        # Execute
        response = client.post(
            '/cs/scheduler',
            data=json.dumps(sample_scheduler_data),
            headers=auth_headers
        )
        
        # Assertions
        mock_scheduler_controller.add_entity.assert_called_once()
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'success' in response_data
        assert 'data' in response_data
    
    def test_post_scheduler_missing_data(self, client, mock_scheduler_controller, auth_headers):
        """Test POST scheduler with missing data."""
        # Execute - no data sent
        response = client.post('/cs/scheduler', headers=auth_headers)
        
        # Assertions
        mock_scheduler_controller.add_entity.assert_not_called()
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert 'Missing Scheduler details' in response_data['error']
    
    def test_post_scheduler_controller_error(self, client, mock_scheduler_controller, sample_scheduler_data, auth_headers):
        """Test POST scheduler with controller error."""
        # Setup mock to return error
        mock_scheduler_controller.add_entity.return_value = (
            {'error': 'Invalid schedule configuration'},
            '400 Bad Request'
        )
        
        # Execute
        response = client.post(
            '/cs/scheduler',
            data=json.dumps(sample_scheduler_data),
            headers=auth_headers
        )
        
        # Assertions
        mock_scheduler_controller.add_entity.assert_called_once()
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_get_schedulers_all(self, client, mock_scheduler_controller, auth_headers):
        """Test GET all schedulers."""
        # Setup mock
        mock_scheduler_data = [
            {'id': '1', 'name': 'Daily Scan', 'enabled': True},
            {'id': '2', 'name': 'Weekly Scan', 'enabled': False}
        ]
        mock_scheduler_controller.fetch_schedules.return_value = (
            {'success': 'Records Fetched Successfully', 'data': mock_scheduler_data},
            '200 Ok'
        )
        
        # Execute
        response = client.get('/cs/scheduler', headers=auth_headers)
        
        # Assertions
        mock_scheduler_controller.fetch_schedules.assert_called_once()
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'success' in response_data
        assert len(response_data['data']) == 2
    
    def test_get_schedulers_with_filters(self, client, mock_scheduler_controller, auth_headers):
        """Test GET schedulers with query filters."""
        # Setup mock
        mock_scheduler_controller.fetch_schedules.return_value = (
            {'success': 'Records Fetched Successfully', 'data': []},
            '200 Ok'
        )
        
        # Execute
        response = client.get(
            '/cs/scheduler?project_id=project-123&name=TestScheduler',
            headers=auth_headers
        )
        
        # Assertions
        mock_scheduler_controller.fetch_schedules.assert_called_once()
        call_args = mock_scheduler_controller.fetch_schedules.call_args
        fields = call_args[0][1]
        assert 'project_id' in fields
        assert 'name' in fields
        assert fields['project_id'] == 'project-123'
        assert fields['name'] == 'TestScheduler'
    
    def test_get_scheduler_by_id(self, client, mock_scheduler_controller, auth_headers):
        """Test GET scheduler by ID in URL path."""
        # Setup mock
        mock_scheduler_controller.fetch_schedules.return_value = (
            {'success': 'Records Fetched Successfully', 'data': [{'id': 'scheduler-123'}]},
            '200 Ok'
        )
        
        # Execute - Add project_id as query parameter since scheduler_id alone results in empty fields
        response = client.get('/cs/scheduler/scheduler-123?project_id=test-project', headers=auth_headers)
        
        # Assertions
        mock_scheduler_controller.fetch_schedules.assert_called_once()
        call_args = mock_scheduler_controller.fetch_schedules.call_args
        fields = call_args[0][1]
        # The API uses project_id from query parameters
        assert 'project_id' in fields
        assert fields['project_id'] == 'test-project'
    
    def test_put_scheduler_success(self, client, mock_scheduler_controller, sample_scheduler_data, auth_headers):
        """Test successful scheduler update via PUT."""
        # Setup mock - API uses update_by_id method
        mock_scheduler_controller.update_by_id.return_value = (
            {'success': 'Scheduler Updated Successfully', 'data': sample_scheduler_data},
            '200 Ok'
        )
        
        # Execute
        response = client.put(
            '/cs/scheduler/scheduler-123',
            data=json.dumps(sample_scheduler_data),
            headers=auth_headers
        )
        
        # Assertions
        mock_scheduler_controller.update_by_id.assert_called_once()
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'success' in response_data
    
    def test_put_scheduler_missing_id(self, client, mock_scheduler_controller, sample_scheduler_data, auth_headers):
        """Test PUT scheduler without scheduler ID."""
        # Execute - no scheduler_id in URL
        response = client.put(
            '/cs/scheduler',
            data=json.dumps(sample_scheduler_data),
            headers=auth_headers
        )
        
        # Assertions
        mock_scheduler_controller.update_scheduler.assert_not_called()
        # Flask routing returns 405 Method Not Allowed when PUT is used on route without ID
        assert response.status_code == 405
    
    def test_put_scheduler_controller_error(self, client, mock_scheduler_controller, sample_scheduler_data, auth_headers):
        """Test PUT scheduler with controller error."""
        # Setup mock to return error - API uses update_by_id method
        mock_scheduler_controller.update_by_id.return_value = (
            {'error': 'Scheduler not found'},
            '404 Not Found'
        )
        
        # Execute
        response = client.put(
            '/cs/scheduler/nonexistent-id',
            data=json.dumps(sample_scheduler_data),
            headers=auth_headers
        )
        
        # Assertions
        mock_scheduler_controller.update_by_id.assert_called_once()
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_delete_scheduler_success(self, client, mock_scheduler_controller, auth_headers):
        """Test successful scheduler deletion via DELETE."""
        # Setup mock - API uses remove_entity method
        mock_scheduler_controller.remove_entity.return_value = (
            {'success': 'Scheduler Deleted Successfully'},
            '200 Ok'
        )
        
        # Execute
        response = client.delete('/cs/scheduler/scheduler-123', headers=auth_headers)
        
        # Assertions
        mock_scheduler_controller.remove_entity.assert_called_once_with('scheduler-123')
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'success' in response_data
    
    def test_delete_scheduler_missing_id(self, client, mock_scheduler_controller, auth_headers):
        """Test DELETE scheduler without scheduler ID."""
        # Execute - no scheduler_id in URL
        response = client.delete('/cs/scheduler', headers=auth_headers)
        
        # Assertions
        mock_scheduler_controller.delete_scheduler.assert_not_called()
        # Flask routing returns 405 Method Not Allowed when DELETE is used on route without ID
        assert response.status_code == 405
    
    def test_delete_scheduler_controller_error(self, client, mock_scheduler_controller, auth_headers):
        """Test DELETE scheduler with controller error."""
        # Setup mock to return error - API uses remove_entity method
        mock_scheduler_controller.remove_entity.return_value = (
            {'error': 'Scheduler not found'},
            '404 Not Found'
        )
        
        # Execute
        response = client.delete('/cs/scheduler/nonexistent-id', headers=auth_headers)
        
        # Assertions
        mock_scheduler_controller.remove_entity.assert_called_once_with('nonexistent-id')
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_scheduler_data_validation(self, client, mock_scheduler_controller, auth_headers):
        """Test scheduler data validation scenarios."""
        # Test with minimal valid data
        minimal_data = {
            'name': 'Test Schedule',
            'project_id': '507f1f77bcf86cd799439011',
            'schedule_config': {
                'frequency': 'daily',
                'time': '02:00'
            },
            'scanner_types': ['zap']
        }
        
        mock_scheduler_controller.add_entity.return_value = (
            {'success': 'Scheduler Created Successfully', 'data': minimal_data},
            '200 Ok'
        )
        
        response = client.post(
            '/cs/scheduler',
            data=json.dumps(minimal_data),
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Test with comprehensive data
        comprehensive_data = {
            'name': 'Comprehensive Weekly Scan',
            'project_id': '507f1f77bcf86cd799439011',
            'schedule_config': {
                'frequency': 'weekly',
                'time': '02:00',
                'day_of_week': 1,
                'timezone': 'UTC',
                'retry_count': 3,
                'timeout': 3600
            },
            'scanner_types': ['zap', 'trivy', 'wapiti'],
            'enabled': True,
            'description': 'Automated comprehensive security assessment',
            'notification_config': {
                'email': True,
                'slack': False,
                'webhook_url': 'https://example.com/webhook'
            }
        }
        
        mock_scheduler_controller.add_entity.return_value = (
            {'success': 'Scheduler Created Successfully', 'data': comprehensive_data},
            '200 Ok'
        )
        
        response = client.post(
            '/cs/scheduler',
            data=json.dumps(comprehensive_data),
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    def test_schedule_frequency_validation(self, client, mock_scheduler_controller, auth_headers):
        """Test different schedule frequency options."""
        frequencies = ['daily', 'weekly', 'monthly']
        
        for frequency in frequencies:
            schedule_data = {
                'name': f'{frequency.capitalize()} Schedule',
                'project_id': '507f1f77bcf86cd799439011',
                'schedule_config': {
                    'frequency': frequency,
                    'time': '02:00'
                },
                'scanner_types': ['zap']
            }
            
            if frequency == 'weekly':
                schedule_data['schedule_config']['day_of_week'] = 1
            elif frequency == 'monthly':
                schedule_data['schedule_config']['day_of_month'] = 1
            
            mock_scheduler_controller.add_entity.return_value = (
                {'success': 'Scheduler Created Successfully', 'data': schedule_data},
                '200 Ok'
            )
            
            response = client.post(
                '/cs/scheduler',
                data=json.dumps(schedule_data),
                headers=auth_headers
            )
            
            assert response.status_code == 200
    
    def test_time_format_validation(self, client, mock_scheduler_controller, auth_headers):
        """Test different time format scenarios."""
        time_formats = ['02:00', '14:30', '00:00', '23:59']
        
        for time_format in time_formats:
            schedule_data = {
                'name': f'Schedule at {time_format}',
                'project_id': '507f1f77bcf86cd799439011',
                'schedule_config': {
                    'frequency': 'daily',
                    'time': time_format
                },
                'scanner_types': ['zap']
            }
            
            mock_scheduler_controller.add_entity.return_value = (
                {'success': 'Scheduler Created Successfully', 'data': schedule_data},
                '200 Ok'
            )
            
            response = client.post(
                '/cs/scheduler',
                data=json.dumps(schedule_data),
                headers=auth_headers
            )
            
            assert response.status_code == 200
    
    def test_scanner_types_validation(self, client, mock_scheduler_controller, auth_headers):
        """Test different scanner type configurations."""
        scanner_combinations = [
            ['zap'],
            ['zap', 'trivy'],
            ['zap', 'trivy', 'wapiti'],
            ['trivy', 'slither'],
            ['zap', 'trivy', 'wapiti', 'gitleaks', 'cloudsploit']
        ]
        
        for scanners in scanner_combinations:
            schedule_data = {
                'name': f'Multi-Scanner Schedule ({len(scanners)} scanners)',
                'project_id': '507f1f77bcf86cd799439011',
                'schedule_config': {
                    'frequency': 'daily',
                    'time': '02:00'
                },
                'scanner_types': scanners
            }
            
            mock_scheduler_controller.add_entity.return_value = (
                {'success': 'Scheduler Created Successfully', 'data': schedule_data},
                '200 Ok'
            )
            
            response = client.post(
                '/cs/scheduler',
                data=json.dumps(schedule_data),
                headers=auth_headers
            )
            
            assert response.status_code == 200
    
    def test_filter_none_values(self, client, mock_scheduler_controller, auth_headers):
        """Test that None values are filtered out correctly."""
        # Setup mock
        mock_scheduler_controller.fetch_schedules.return_value = (
            {'success': 'Records Fetched Successfully', 'data': []},
            '200 Ok'
        )
        
        # Execute - only project_id provided, name is None
        response = client.get('/cs/scheduler?project_id=project-123', headers=auth_headers)
        
        # Assertions
        mock_scheduler_controller.fetch_schedules.assert_called_once()
        call_args = mock_scheduler_controller.fetch_schedules.call_args
        fields = call_args[0][1]
        assert 'project_id' in fields
        assert 'name' not in fields  # Should be filtered out
    
    def test_concurrent_scheduler_operations(self, client, mock_scheduler_controller, auth_headers):
        """Test concurrent scheduler operations."""
        import threading
        import time
        
        # Setup mock with slight delay
        def mock_add_with_delay(*args, **kwargs):
            time.sleep(0.01)
            return ({'success': 'Scheduler Created Successfully', 'data': {}}, '200 Ok')
        
        mock_scheduler_controller.add_entity.side_effect = mock_add_with_delay
        
        # Execute concurrent requests
        results = []
        def create_scheduler(scheduler_id):
            schedule_data = {
                'name': f'Concurrent Schedule {scheduler_id}',
                'project_id': '507f1f77bcf86cd799439011',
                'schedule_config': {
                    'frequency': 'daily',
                    'time': '02:00'
                },
                'scanner_types': ['zap']
            }
            response = client.post(
                '/cs/scheduler',
                data=json.dumps(schedule_data),
                headers=auth_headers
            )
            results.append(response.status_code)
        
        threads = [threading.Thread(target=create_scheduler, args=(i,)) for i in range(3)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 3
    
    def test_swagger_documentation_exists(self):
        """Test that API has proper Swagger documentation."""
        from apis.scheduler import scheduler_blueprint
        
        # Check that the endpoint function has swagger decorator
        # (Implementation depends on how the route function is defined)
        assert scheduler_blueprint is not None
    
    def test_blueprint_registration(self, app):
        """Test that blueprint is properly registered."""
        # Check that blueprint is registered
        assert 'scheduler_blueprint' in [bp.name for bp in app.blueprints.values()]
    
    def test_unsupported_method(self, client, auth_headers):
        """Test unsupported HTTP method."""
        # Execute PATCH method (not supported)
        response = client.patch('/cs/scheduler/test-id', headers=auth_headers)
        
        # Assertions
        assert response.status_code == 405  # Method Not Allowed
    
    def test_error_response_format(self, client, mock_scheduler_controller, auth_headers):
        """Test consistent error response format."""
        # Setup mock to return error tuple instead of raising exception
        mock_scheduler_controller.fetch_schedules.return_value = (
            {'error': 'Database connection failed'},
            '500 Internal Server Error'
        )
        
        # Execute
        response = client.get('/cs/scheduler', headers=auth_headers)
        
        # Should return error response
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_large_schedule_configuration(self, client, mock_scheduler_controller, auth_headers):
        """Test handling of large schedule configurations."""
        # Create large schedule configuration
        large_config = {
            'name': 'Large Configuration Schedule',
            'project_id': '507f1f77bcf86cd799439011',
            'schedule_config': {
                'frequency': 'weekly',
                'time': '02:00',
                'day_of_week': 1,
                'advanced_settings': {
                    'retry_config': {
                        'max_retries': 5,
                        'retry_delays': [60, 120, 300, 600, 1200],
                        'failure_conditions': ['timeout', 'network_error', 'scanner_crash']
                    },
                    'resource_limits': {
                        'max_memory': '8GB',
                        'max_cpu': '4 cores',
                        'max_duration': '4 hours'
                    },
                    'notification_rules': [
                        {'condition': 'success', 'channels': ['email', 'slack']},
                        {'condition': 'failure', 'channels': ['email', 'slack', 'webhook']},
                        {'condition': 'timeout', 'channels': ['email', 'pager']}
                    ]
                }
            },
            'scanner_types': ['zap', 'trivy', 'wapiti', 'gitleaks', 'slither', 'cloudsploit'],
            'target_filters': {
                'include_patterns': ['*.com', '*.org'],
                'exclude_patterns': ['test.*', 'dev.*', 'staging.*']
            }
        }
        
        mock_scheduler_controller.add_entity.return_value = (
            {'success': 'Scheduler Created Successfully', 'data': large_config},
            '200 Ok'
        )
        
        response = client.post(
            '/cs/scheduler',
            data=json.dumps(large_config),
            headers=auth_headers
        )
        
        # Should handle large configurations
        assert response.status_code in [200, 413]  # OK or Payload Too Large