"""
Fixed unit tests for DomainController using proper Flask context
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import uuid
from datetime import datetime, timezone
from bson import ObjectId
from mongoengine.errors import DoesNotExist, ValidationError as MongoValidationError
from marshmallow import ValidationError

from controllers.DomainController import DomainController, DomainAddSchema, DomainUpdateSchema
from tests.unit.controllers.controller_test_base import ControllerTestBase


class TestDomainController(ControllerTestBase):
    """Fixed test cases for DomainController class."""
    
    @pytest.fixture
    def controller(self):
        """Create DomainController instance for testing."""
        return DomainController()
    
    @pytest.fixture
    def sample_domain_data(self):
        """Sample domain data for testing."""
        return {
            'project_id': '507f1f77bcf86cd799439011',
            'domain_url': 'https://test-example.com',
            'domain_label': 'Test Website'
        }
    
    @patch('controllers.DomainController.get_current_user_from_jwt_token')
    @patch('controllers.DomainController.Domain')
    @patch('uuid.uuid4')
    def test_add_entity_success(self, mock_uuid, mock_domain, mock_get_user, controller, sample_domain_data):
        """Test successful domain creation."""
        # Setup mocks
        mock_get_user.return_value = 'test-user-id'
        mock_uuid.return_value = Mock(hex="test-domain-id")
        
        mock_domain_entity = Mock()
        mock_domain_entity.save.return_value = None
        mock_domain_entity.to_json.return_value = json.dumps(sample_domain_data)
        mock_domain.return_value = mock_domain_entity
        
        # Execute using base class helper
        result = self.call_controller_method(controller, 'add_entity', sample_domain_data)
        
        # Assert using base class helper
        self.assert_success_response(result, ['success', 'data'])
        
        # Verify mocks
        mock_get_user.assert_called_once()
        mock_domain.assert_called_once()
        mock_domain_entity.save.assert_called_once()
    
    @patch('controllers.DomainController.get_current_user_from_jwt_token')
    def test_add_entity_validation_error(self, mock_get_user, controller):
        """Test domain creation with validation error."""
        mock_get_user.return_value = 'test-user-id'
        
        # Invalid data missing required fields
        invalid_data = {
            'domain_url': 'invalid-url'  # Missing project_id
        }
        
        # Execute
        result = self.call_controller_method(controller, 'add_entity', invalid_data)
        
        # Assert error response
        self.assert_error_response(result, 'Project ID')
    
    @patch('controllers.DomainController.get_current_user_from_jwt_token')
    @patch('controllers.DomainController.Domain')
    def test_add_entity_database_error(self, mock_domain, mock_get_user, controller, sample_domain_data):
        """Test domain creation with database error."""
        # Setup mocks
        mock_get_user.return_value = 'test-user-id'
        
        mock_domain_entity = Mock()
        # Use mongoengine ValidationError which the controller should catch
        mock_domain_entity.save.side_effect = MongoValidationError("Database error")
        mock_domain.return_value = mock_domain_entity
        
        # Execute
        result = self.call_controller_method(controller, 'add_entity', sample_domain_data)
        
        # Assert error response
        self.assert_error_response(result, 'Database validation error')
    
    @patch('controllers.DomainController.get_current_user_from_jwt_token')
    @patch('controllers.DomainController.Domain')
    def test_update_by_id_success(self, mock_domain, mock_get_user, controller):
        """Test successful domain update."""
        # Setup mocks
        mock_get_user.return_value = 'test-user-id'
        
        # Mock existing domain with dict-like behavior for item assignment
        mock_existing_domain = MagicMock()
        mock_existing_domain.__setitem__ = MagicMock()  # Allow item assignment
        mock_existing_domain.__getitem__ = MagicMock()  # Allow item access
        mock_existing_domain.save.return_value = None
        mock_existing_domain.to_json.return_value = json.dumps({'updated': True})
        
        mock_domain.objects.get.return_value = mock_existing_domain
        
        update_data = {
            'target_domain_id': 'test-id',  # Must match the URL parameter
            'domain_url': 'https://updated-example.com',
            'domain_label': 'Updated Website'
        }
        
        # Execute
        result = self.call_controller_method(controller, 'update_by_id', update_data)
        
        # Assert success
        self.assert_success_response(result, ['success', 'data'])
        
        # Verify mocks
        mock_get_user.assert_called_once()
        mock_existing_domain.save.assert_called_once()
    
    @patch('controllers.DomainController.get_current_user_from_jwt_token')
    @patch('controllers.DomainController.Domain')
    def test_update_by_id_not_found(self, mock_domain, mock_get_user, controller):
        """Test domain update when domain not found."""
        # Setup mocks
        mock_get_user.return_value = 'test-user-id'
        mock_domain.objects.get.side_effect = DoesNotExist("Domain not found")
        
        update_data = {
            'target_domain_id': 'test-id',  # Must match the URL parameter
            'domain_url': 'https://updated-example.com'
        }
        
        # Execute
        result = self.call_controller_method(controller, 'update_by_id', update_data)
        
        # Assert error response
        self.assert_error_response(result, 'Domain not found')
    
    @patch('controllers.DomainController.get_current_user_from_jwt_token')
    @patch('controllers.DomainController.Domain')
    def test_delete_by_id_success(self, mock_domain, mock_get_user, controller):
        """Test successful domain deletion."""
        # Setup mocks
        mock_get_user.return_value = 'test-user-id'
        
        mock_existing_domain = Mock()
        mock_existing_domain.delete.return_value = None
        mock_domain.objects.get.return_value = mock_existing_domain
        
        # Mock the findings check to return no findings (DomainController uses FindingMaster)
        with patch('controllers.DomainController.FindingMaster') as mock_findings, \
             patch('controllers.DomainController.verify_jwt_in_request') as mock_verify_jwt:
            
            # Mock no findings
            mock_finding_queryset = Mock()
            mock_finding_queryset.to_json.return_value = "[]"  # Empty JSON array
            mock_findings.objects.return_value = mock_finding_queryset
            
            # Mock JWT verification to pass
            mock_verify_jwt.return_value = None
            
            # Execute - use delete_by_id instead of remove_entity for DomainController
            result = self.call_controller_method(controller, 'delete_by_id', 'test-domain-id')
            
            # Assert success
            self.assert_success_response(result, ['success'])
    
    @patch('controllers.DomainController.get_current_user_from_jwt_token')
    @patch('controllers.DomainController.Domain')
    def test_delete_by_id_with_findings(self, mock_domain, mock_get_user, controller):
        """Test domain deletion when findings exist."""
        # Setup mocks
        mock_get_user.return_value = 'test-user-id'
        
        mock_existing_domain = Mock()
        mock_domain.objects.get.return_value = mock_existing_domain
        
        # Mock the findings check to return findings (DomainController uses FindingMaster)
        with patch('controllers.DomainController.FindingMaster') as mock_findings, \
             patch('controllers.DomainController.verify_jwt_in_request') as mock_verify_jwt:
            
            # Mock findings exist - need to mock both the queryset and its to_json method
            mock_finding1 = Mock()
            mock_finding1.extended_finding_details_id = 'finding-detail-1'
            
            # Create a proper mock queryset that is iterable and has to_json
            mock_finding_queryset = Mock()
            mock_finding_queryset.__iter__ = Mock(return_value=iter([mock_finding1]))  # Make iterable
            mock_finding_queryset.to_json.return_value = '[{"some": "finding"}]'  # Non-empty JSON
            
            # Mock the objects() call to return our queryset
            mock_findings.objects.return_value = mock_finding_queryset
            
            # Mock JWT verification to pass
            mock_verify_jwt.return_value = None
            
            # Execute - use delete_by_id instead of remove_entity for DomainController
            result = self.call_controller_method(controller, 'delete_by_id', 'test-domain-id')
            
            # Assert error response - when findings exist, deletion should still succeed (soft delete)
            self.assert_success_response(result, ['success'])
    
    @patch('controllers.DomainController.get_current_user_from_jwt_token')
    @patch('controllers.DomainController.Domain')
    def test_delete_by_id_not_found(self, mock_domain, mock_get_user, controller):
        """Test domain deletion when domain not found."""
        # Setup mocks
        mock_get_user.return_value = 'test-user-id'
        mock_domain.objects.get.side_effect = DoesNotExist("Domain not found")
        
        # Mock JWT verification
        with patch('controllers.DomainController.verify_jwt_in_request') as mock_verify_jwt:
            mock_verify_jwt.return_value = None
            
            # Execute
            result = self.call_controller_method(controller, 'delete_by_id', 'nonexistent-id')
            
            # Assert error response
            self.assert_error_response(result, 'Domain record with ID nonexistent-id not found')
    
    @patch('controllers.DomainController.get_current_user_from_jwt_token')
    @patch('controllers.DomainController.Domain')
    def test_fetch_all_success(self, mock_domain, mock_get_user, controller):
        """Test successful domain fetch."""
        # Setup mocks
        mock_get_user.return_value = 'test-user-id'
        
        mock_domains = [
            Mock(to_json=lambda: json.dumps({'id': '1', 'domain_url': 'https://example1.com'})),
            Mock(to_json=lambda: json.dumps({'id': '2', 'domain_url': 'https://example2.com'}))
        ]
        
        mock_domain.objects.aggregate.return_value = mock_domains
        
        # Execute
        result = self.call_controller_method(controller, 'fetch_all', {})
        
        # Assert success
        self.assert_success_response(result, ['success', 'data'])
        
        # Verify response data structure
        response_data, _ = self.extract_response(result)
        assert len(response_data['data']) == 2
    
    @patch('controllers.DomainController.get_current_user_from_jwt_token')
    @patch('controllers.DomainController.Domain')
    def test_fetch_all_empty_result(self, mock_domain, mock_get_user, controller):
        """Test domain fetch with empty result."""
        # Setup mocks
        mock_get_user.return_value = 'test-user-id'
        mock_domain.objects.aggregate.return_value = []
        
        # Execute
        result = self.call_controller_method(controller, 'fetch_all', {})
        
        # Assert success with empty data
        response_data, status_code = self.extract_response(result)
        assert status_code == '200 Ok'
        assert response_data['data'] == []
    
    def test_validation_schemas(self):
        """Test validation schemas work correctly."""
        # Test DomainAddSchema
        add_schema = DomainAddSchema()
        
        # Valid data should pass
        valid_data = {
            'project_id': '507f1f77bcf86cd799439011',
            'domain_url': 'https://example.com',
            'domain_label': 'Test Site'
        }
        
        try:
            result = add_schema.load(valid_data)
            assert result == valid_data
        except ValidationError:
            pytest.fail("Valid data should not raise ValidationError")
        
        # Invalid data should fail
        invalid_data = {
            'domain_url': 'https://example.com'  # Missing project_id
        }
        
        with pytest.raises(ValidationError) as exc_info:
            add_schema.load(invalid_data)
        
        assert 'project_id' in str(exc_info.value)
    
    def test_controller_initialization(self):
        """Test controller initializes correctly."""
        controller = DomainController()
        assert controller is not None
        assert hasattr(controller, '_validateDomainAdd')
        assert hasattr(controller, '_validateDomainUpdate')
        assert hasattr(controller, '_validateDomain')