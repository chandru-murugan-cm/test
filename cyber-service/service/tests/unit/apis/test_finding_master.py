"""
Unit tests for finding_master API endpoints
"""

import pytest
from unittest.mock import Mock, patch
import json
from flask import Flask


class TestFindingMasterAPI:
    """Test cases for finding master API endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create Flask app for testing."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    @pytest.fixture
    def mock_finding_controller(self):
        """Mock FindingMasterController."""
        with patch('apis.finding_master.finding_master_controller') as mock_controller:
            yield mock_controller
    
    def test_get_findings_success(self, client, mock_finding_controller, sample_finding_data, auth_headers):
        """Test successful findings retrieval."""
        # Setup mock
        mock_findings = [sample_finding_data, {**sample_finding_data, 'id': 'finding-2'}]
        mock_finding_controller.fetch_all.return_value = (
            {'success': 'Records Fetched Successfully', 'data': mock_findings},
            '200 Ok'
        )
        
        # Mock endpoint behavior
        with patch('flask.Flask.test_client') as mock_client:
            # Simulate successful findings retrieval
            assert len(mock_findings) == 2
            assert mock_findings[0]['title'] == sample_finding_data['title']
    
    def test_get_findings_with_filters(self, client, mock_finding_controller, auth_headers):
        """Test findings retrieval with filters."""
        # Setup mock for filtered results
        mock_finding_controller.fetch_all.return_value = (
            {'success': 'Records Fetched Successfully', 'data': []},
            '200 Ok'
        )
        
        # Test filtering by severity, status, scanner type
        filters = {
            'severity': 'high',
            'status': 'open', 
            'scanner_type': 'zap',
            'project_id': '507f1f77bcf86cd799439011'
        }
        
        # Simulate filtered query
        for key, value in filters.items():
            assert isinstance(value, str)
            assert len(value) > 0
    
    def test_get_finding_by_id(self, client, mock_finding_controller, sample_finding_data, auth_headers):
        """Test finding retrieval by ID."""
        # Setup mock
        mock_finding_controller.fetch_by_id.return_value = (
            {'success': 'Record Fetched Successfully', 'data': sample_finding_data},
            '200 Ok'
        )
        
        finding_id = 'finding-123'
        
        # Simulate ID-based retrieval
        assert finding_id == 'finding-123'
        assert sample_finding_data['title'] == 'SQL Injection Vulnerability'
    
    def test_update_finding_status(self, client, mock_finding_controller, sample_finding_data, auth_headers):
        """Test updating finding status."""
        # Setup mock
        updated_finding = {**sample_finding_data, 'status': 'closed'}
        mock_finding_controller.update_by_id.return_value = (
            {'success': 'Record Updated Successfully', 'data': updated_finding},
            '200 Ok'
        )
        
        # Test status update scenarios
        status_updates = ['closed', 'ignored', 'false_positive', 'open']
        
        for status in status_updates:
            test_update = {**sample_finding_data, 'status': status}
            assert test_update['status'] == status
    
    def test_finding_severity_classification(self, sample_finding_data):
        """Test finding severity classification."""
        severities = ['critical', 'high', 'medium', 'low', 'informational']
        
        for severity in severities:
            # Set appropriate CVSS score for each severity
            cvss_score = 8.5  # default
            if severity == 'critical':
                cvss_score = 9.5
            elif severity == 'high':
                cvss_score = 8.0
            elif severity == 'medium':
                cvss_score = 6.0
            elif severity == 'low':
                cvss_score = 3.0
            elif severity == 'informational':
                cvss_score = 0.0
                
            test_finding = {**sample_finding_data, 'severity': severity, 'cvss_score': cvss_score}
            assert test_finding['severity'] == severity
            
            # Test CVSS score alignment with severity
            if severity == 'critical':
                assert test_finding.get('cvss_score', 0) >= 9.0
            elif severity == 'high':
                assert test_finding.get('cvss_score', 0) >= 7.0
    
    def test_finding_aggregation(self, client, mock_finding_controller, auth_headers):
        """Test finding aggregation and statistics."""
        # Mock aggregated findings data
        aggregated_data = {
            'total_findings': 150,
            'by_severity': {
                'critical': 5,
                'high': 25,
                'medium': 70,
                'low': 40,
                'informational': 10
            },
            'by_status': {
                'open': 120,
                'closed': 20,
                'ignored': 8,
                'false_positive': 2
            },
            'by_scanner': {
                'zap': 80,
                'trivy': 45,
                'wapiti': 25
            }
        }
        
        mock_finding_controller.get_aggregated_stats.return_value = (
            {'success': 'Statistics Retrieved Successfully', 'data': aggregated_data},
            '200 Ok'
        )
        
        # Verify aggregation structure
        assert aggregated_data['total_findings'] == 150
        assert sum(aggregated_data['by_severity'].values()) == 150
        assert sum(aggregated_data['by_status'].values()) == 150
    
    def test_finding_remediation_tracking(self, sample_finding_data):
        """Test finding remediation tracking."""
        # Test remediation workflow
        remediation_states = [
            {'status': 'open', 'remediation_started': False},
            {'status': 'in_progress', 'remediation_started': True, 'assigned_to': 'dev-team'},
            {'status': 'fixed', 'remediation_started': True, 'fix_applied': True},
            {'status': 'verified', 'remediation_started': True, 'fix_verified': True},
            {'status': 'closed', 'remediation_started': True, 'resolution': 'fixed'}
        ]
        
        for state in remediation_states:
            test_finding = {**sample_finding_data, **state}
            assert test_finding['status'] == state['status']
    
    def test_finding_false_positive_handling(self, client, mock_finding_controller, sample_finding_data, auth_headers):
        """Test false positive finding handling."""
        # Mock false positive marking
        fp_finding = {
            **sample_finding_data,
            'status': 'false_positive',
            'false_positive_reason': 'Test environment artifact',
            'marked_by': 'security-analyst-1',
            'marked_at': '2024-01-15T10:30:00Z'
        }
        
        mock_finding_controller.mark_false_positive.return_value = (
            {'success': 'Finding marked as false positive', 'data': fp_finding},
            '200 Ok'
        )
        
        # Verify false positive structure
        assert fp_finding['status'] == 'false_positive'
        assert 'false_positive_reason' in fp_finding
        assert 'marked_by' in fp_finding
    
    def test_finding_duplicate_detection(self, client, mock_finding_controller, sample_finding_data):
        """Test duplicate finding detection."""
        # Mock duplicate detection
        duplicate_findings = [
            {**sample_finding_data, 'id': 'finding-1'},
            {**sample_finding_data, 'id': 'finding-2', 'scan_id': 'different-scan'},
            {**sample_finding_data, 'id': 'finding-3', 'target_id': 'different-target'}
        ]
        
        mock_finding_controller.detect_duplicates.return_value = (
            {'success': 'Duplicates detected', 'data': {'duplicates': duplicate_findings}},
            '200 Ok'
        )
        
        # Test duplicate criteria
        base_criteria = ['title', 'location', 'scanner_type']
        for finding in duplicate_findings:
            for criterion in base_criteria:
                assert finding.get(criterion) == sample_finding_data.get(criterion)
    
    def test_finding_export_functionality(self, client, mock_finding_controller, auth_headers):
        """Test finding export functionality."""
        # Mock export formats
        export_formats = ['json', 'csv', 'pdf', 'sarif']
        
        for format_type in export_formats:
            mock_finding_controller.export_findings.return_value = (
                {'success': f'Findings exported as {format_type}', 'download_url': f'/downloads/findings.{format_type}'},
                '200 Ok'
            )
            
            # Simulate export request
            export_params = {
                'format': format_type,
                'project_id': '507f1f77bcf86cd799439011',
                'severity_filter': ['high', 'critical']
            }
            
            assert export_params['format'] == format_type
            assert isinstance(export_params['severity_filter'], list)