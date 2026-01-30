"""
Unit tests for CyberServiceEntity models
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from mongoengine.errors import ValidationError, NotUniqueError
from bson import ObjectId

from entities.CyberServiceEntity import (
    Scanners, ScannerTypes, Project, Domain, Repository, Scans,
    FindingMaster, Scheduler, SchedulerType, ProjectStatus, 
    ScanTargetType, ScanStatus, FindingStatus, FindingSeverity,
    CloudPurposeType
)


class TestEnums:
    """Test enum classes."""
    
    def test_scheduler_type_enum(self):
        """Test SchedulerType enum values."""
        assert SchedulerType.Daily.value == 'daily'
        assert SchedulerType.Monthly.value == 'monthly'
        assert SchedulerType.Weekly.value == 'weekly'
        assert SchedulerType.Custom.value == 'custom'
        assert SchedulerType.ScanNow.value == 'scanNow'
    
    def test_project_status_enum(self):
        """Test ProjectStatus enum values."""
        assert ProjectStatus.Init.value == 'init'
        assert ProjectStatus.Pending.value == 'pending'
        assert ProjectStatus.Completed.value == 'completed'
    
    def test_scan_target_type_enum(self):
        """Test ScanTargetType enum values."""
        assert ScanTargetType.REPO.value == 'repo'
        assert ScanTargetType.DOMAIN.value == 'domain'
        assert ScanTargetType.CONTAINER.value == 'container'
        assert ScanTargetType.CLOUD.value == 'cloud'
        assert ScanTargetType.WEB3.value == 'web3'
        assert ScanTargetType.VM.value == 'vm'
    
    def test_scan_status_enum(self):
        """Test ScanStatus enum values."""
        assert ScanStatus.Scheduled.value == 'scheduled'
        assert ScanStatus.Running.value == 'running'
        assert ScanStatus.Completed.value == 'completed'
        assert ScanStatus.Error.value == 'error'
    
    def test_finding_status_enum(self):
        """Test FindingStatus enum values."""
        assert FindingStatus.Open.value == 'open'
        assert FindingStatus.Closed.value == 'closed'
        assert FindingStatus.Ignored.value == 'ignored'
        assert FindingStatus.FalsePositive.value == 'false positive'
    
    def test_finding_severity_enum(self):
        """Test FindingSeverity enum values."""
        assert FindingSeverity.Critical.value == 'critical'
        assert FindingSeverity.High.value == 'high'
        assert FindingSeverity.Medium.value == 'medium'
        assert FindingSeverity.Low.value == 'low'
        assert FindingSeverity.Informational.value == 'informational'
    
    def test_cloud_purpose_type_enum(self):
        """Test CloudPurposeType enum values."""
        assert CloudPurposeType.Development.value == 'development'
        assert CloudPurposeType.Staging.value == 'staging'
        assert CloudPurposeType.Production.value == 'production'


class TestScannersEntity:
    """Test Scanners entity model."""
    
    @pytest.fixture
    def scanner_data(self):
        """Sample scanner data for testing."""
        return {
            'scanner_id': 'test-scanner-123',
            'name': 'Test OWASP ZAP Scanner',
            'description': 'Web application security scanner',
            'version': '2.11.0',
            'created': datetime.now(timezone.utc),
            'creator': 'test-user-id'
        }
    
    def test_scanner_creation_success(self, mock_db, scanner_data):
        """Test successful scanner creation."""
        scanner = Scanners(**scanner_data)
        scanner.save()
        
        assert scanner.scanner_id == scanner_data['scanner_id']
        assert scanner.name == scanner_data['name']
        assert scanner.description == scanner_data['description']
        assert scanner.version == scanner_data['version']
        assert scanner.isdeleted is None or scanner.isdeleted is False
    
    def test_scanner_required_fields(self, mock_db):
        """Test scanner creation with missing required fields."""
        # Missing scanner_id
        with pytest.raises(ValidationError):
            scanner = Scanners(name='Test Scanner')
            scanner.save()
        
        # Missing name
        with pytest.raises(ValidationError):
            scanner = Scanners(scanner_id='test-123')
            scanner.save()
    
    def test_scanner_soft_delete(self, mock_db, scanner_data):
        """Test soft delete functionality."""
        scanner = Scanners(**scanner_data)
        scanner.save()
        
        # Mark as deleted
        scanner.isdeleted = True
        scanner.save()
        
        assert scanner.isdeleted is True
    
    def test_scanner_meta_configuration(self):
        """Test scanner model meta configuration."""
        assert Scanners._meta['collection'] == 'Scanners'
        assert 'name' in Scanners._meta['indexes']
        assert Scanners._meta['strict'] is False
        assert Scanners._meta['soft_delete']['isdeleted'] is True
    
    def test_scanner_string_field_validation(self, mock_db):
        """Test string field validation."""
        # Test description max length
        long_description = 'A' * 300  # Exceeds max_length=255
        
        with pytest.raises(ValidationError):
            scanner = Scanners(
                scanner_id='test-123',
                name='Test Scanner',
                description=long_description
            )
            scanner.save()
    
    def test_scanner_update_fields(self, mock_db, scanner_data):
        """Test updating scanner fields."""
        scanner = Scanners(**scanner_data)
        scanner.save()
        
        # Update fields
        scanner.name = 'Updated Scanner Name'
        scanner.version = '2.12.0'
        scanner.updated = datetime.now(timezone.utc)
        scanner.updator = 'updater-user-id'
        scanner.save()
        
        assert scanner.name == 'Updated Scanner Name'
        assert scanner.version == '2.12.0'
        assert scanner.updated is not None
        assert scanner.updator == 'updater-user-id'


class TestScannerTypesEntity:
    """Test ScannerTypes entity model."""
    
    @pytest.fixture
    def scanner_type_data(self):
        """Sample scanner type data for testing."""
        return {
            'scan_type_id': 'zap-dast-web',
            'scanner_ids': ['zap-scanner-1', 'zap-scanner-2'],
            'scan_type': 'DAST',
            'scan_target_type': ScanTargetType.DOMAIN,
            'cloud_provider': None,
            'description': 'Dynamic Application Security Testing for web applications',
            'created': datetime.now(timezone.utc),
            'creator': 'test-user-id'
        }
    
    def test_scanner_type_creation_success(self, mock_db, scanner_type_data):
        """Test successful scanner type creation."""
        scanner_type = ScannerTypes(**scanner_type_data)
        scanner_type.save()
        
        assert scanner_type.scan_type_id == scanner_type_data['scan_type_id']
        assert scanner_type.scanner_ids == scanner_type_data['scanner_ids']
        assert scanner_type.scan_type == scanner_type_data['scan_type']
        assert scanner_type.scan_target_type == ScanTargetType.DOMAIN
        assert scanner_type.isdeleted is None or scanner_type.isdeleted is False
    
    def test_scanner_type_required_fields(self, mock_db):
        """Test scanner type creation with missing required fields."""
        # Missing scan_type_id
        with pytest.raises(ValidationError):
            scanner_type = ScannerTypes(
                scanner_ids=['scanner-1'],
                scan_type='SAST',
                description='Test description'
            )
            scanner_type.save()
        
        # Missing scanner_ids
        with pytest.raises(ValidationError):
            scanner_type = ScannerTypes(
                scan_type_id='test-type',
                scan_type='SAST',
                description='Test description'
            )
            scanner_type.save()
    
    def test_scanner_type_list_field(self, mock_db):
        """Test scanner_ids list field functionality."""
        scanner_type = ScannerTypes(
            scan_type_id='multi-scanner-type',
            scanner_ids=['scanner-1', 'scanner-2', 'scanner-3'],
            scan_type='COMPREHENSIVE',
            description='Multi-scanner type'
        )
        scanner_type.save()
        
        assert len(scanner_type.scanner_ids) == 3
        assert 'scanner-2' in scanner_type.scanner_ids
        
        # Test adding to list
        scanner_type.scanner_ids.append('scanner-4')
        scanner_type.save()
        
        assert len(scanner_type.scanner_ids) == 4
        assert 'scanner-4' in scanner_type.scanner_ids
    
    def test_scanner_type_enum_field(self, mock_db):
        """Test enum field functionality."""
        # Test valid enum value
        scanner_type = ScannerTypes(
            scan_type_id='cloud-scanner',
            scanner_ids=['cloudsploit'],
            scan_type='CLOUD',
            scan_target_type=ScanTargetType.CLOUD,
            description='Cloud security scanner'
        )
        scanner_type.save()
        
        assert scanner_type.scan_target_type == ScanTargetType.CLOUD
    
    def test_scanner_type_cloud_provider_field(self, mock_db):
        """Test cloud provider field."""
        # Test with cloud provider
        scanner_type = ScannerTypes(
            scan_type_id='gcp-scanner',
            scanner_ids=['gcp-cloudsploit'],
            scan_type='CLOUD',
            scan_target_type=ScanTargetType.CLOUD,
            cloud_provider='GCP',
            description='Google Cloud Platform security scanner'
        )
        scanner_type.save()
        
        assert scanner_type.cloud_provider == 'GCP'
        
        # Test without cloud provider (null=True)
        scanner_type2 = ScannerTypes(
            scan_type_id='generic-scanner',
            scanner_ids=['generic'],
            scan_type='GENERIC',
            description='Generic scanner'
        )
        scanner_type2.save()
        
        assert scanner_type2.cloud_provider is None


class TestProjectEntity:
    """Test Project entity model (if exists)."""
    
    def test_project_enum_usage(self):
        """Test project status enum usage."""
        # Test that ProjectStatus enum can be used
        status_values = [status.value for status in ProjectStatus]
        assert 'init' in status_values
        assert 'pending' in status_values
        assert 'completed' in status_values


class TestEntityMetaConfiguration:
    """Test entity meta configurations."""
    
    def test_scanners_meta_config(self):
        """Test Scanners meta configuration."""
        meta = Scanners._meta
        assert meta['collection'] == 'Scanners'
        assert 'name' in meta['indexes']
        assert meta['strict'] is False
        assert meta['soft_delete']['isdeleted'] is True
    
    def test_scanner_types_meta_config(self):
        """Test ScannerTypes meta configuration."""
        meta = ScannerTypes._meta
        assert meta['collection'] == 'ScannerTypes'
        assert 'scan_type' in meta['indexes']
        assert meta['strict'] is False
        assert meta['soft_delete']['isdeleted'] is True


class TestSoftDeleteFunctionality:
    """Test soft delete functionality across entities."""
    
    def test_soft_delete_default_values(self, mock_db):
        """Test that isdeleted defaults to False."""
        scanner = Scanners(
            scanner_id='test-soft-delete',
            name='Test Scanner'
        )
        scanner.save()
        
        assert scanner.isdeleted is None or scanner.isdeleted is False
        
        scanner_type = ScannerTypes(
            scan_type_id='test-soft-delete-type',
            scanner_ids=['scanner-1'],
            scan_type='TEST',
            description='Test type'
        )
        scanner_type.save()
        
        assert scanner_type.isdeleted is None or scanner_type.isdeleted is False
    
    def test_soft_delete_field_update(self, mock_db):
        """Test updating soft delete field."""
        scanner = Scanners(
            scanner_id='test-delete-update',
            name='Test Scanner'
        )
        scanner.save()
        
        # Mark as deleted
        scanner.isdeleted = True
        scanner.save()
        
        assert scanner.isdeleted is True
        
        # Mark as not deleted
        scanner.isdeleted = False
        scanner.save()
        
        assert scanner.isdeleted is None or scanner.isdeleted is False


class TestEntityValidation:
    """Test entity validation scenarios."""
    
    def test_null_field_validation(self, mock_db):
        """Test null field validation."""
        # Test null=True fields can be None
        scanner = Scanners(
            scanner_id='test-null-fields',
            name='Test Scanner',
            version=None,  # null=True
            created=None,  # null=True
            creator=None   # null=True
        )
        scanner.save()
        
        assert scanner.version is None
        assert scanner.created is None
        assert scanner.creator is None
    
    def test_required_field_validation(self, mock_db):
        """Test required field validation."""
        # Test that required fields must be provided
        with pytest.raises(ValidationError):
            scanner = Scanners()  # Missing required fields
            scanner.save()
        
        with pytest.raises(ValidationError):
            scanner_type = ScannerTypes(
                scan_type_id='test'
                # Missing required scanner_ids, scan_type, description
            )
            scanner_type.save()


class TestEntityFields:
    """Test entity field types and constraints."""
    
    def test_string_field_constraints(self, mock_db):
        """Test string field constraints."""
        # Test max_length constraint on description
        with pytest.raises(ValidationError):
            scanner = Scanners(
                scanner_id='test-string-constraints',
                name='Test Scanner',
                description='A' * 300  # Exceeds max_length=255
            )
            scanner.save()
    
    def test_boolean_field_behavior(self, mock_db):
        """Test boolean field behavior."""
        scanner = Scanners(
            scanner_id='test-boolean',
            name='Test Scanner'
        )
        scanner.save()
        
        # Test default value
        assert scanner.isdeleted is None or scanner.isdeleted is False
        
        # Test explicit True
        scanner.isdeleted = True
        scanner.save()
        assert scanner.isdeleted is True
        
        # Test explicit False
        scanner.isdeleted = False
        scanner.save()
        assert scanner.isdeleted is None or scanner.isdeleted is False
    
    def test_datetime_field_behavior(self, mock_db):
        """Test datetime field behavior."""
        now = datetime.now(timezone.utc)
        
        scanner = Scanners(
            scanner_id='test-datetime',
            name='Test Scanner',
            created=now
        )
        scanner.save()
        
        assert scanner.created == now
        assert isinstance(scanner.created, datetime)
    
    def test_list_field_behavior(self, mock_db):
        """Test list field behavior."""
        scanner_ids = ['scanner-1', 'scanner-2', 'scanner-3']
        
        scanner_type = ScannerTypes(
            scan_type_id='test-list-field',
            scanner_ids=scanner_ids,
            scan_type='TEST',
            description='Test list field'
        )
        scanner_type.save()
        
        assert scanner_type.scanner_ids == scanner_ids
        assert len(scanner_type.scanner_ids) == 3
        
        # Test modifying list (can't be empty due to required=True)
        scanner_type.scanner_ids = ['scanner-1']
        scanner_type.save()
        assert scanner_type.scanner_ids == ['scanner-1']


class TestEntityIndexes:
    """Test entity index configurations."""
    
    def test_scanners_indexes(self):
        """Test Scanners indexes configuration."""
        indexes = Scanners._meta.get('indexes', [])
        assert 'name' in indexes
    
    def test_scanner_types_indexes(self):
        """Test ScannerTypes indexes configuration."""
        indexes = ScannerTypes._meta.get('indexes', [])
        assert 'scan_type' in indexes


class TestEntityInheritance:
    """Test entity inheritance from SoftDeleteNoCacheDocument."""
    
    def test_scanners_inheritance(self):
        """Test Scanners inheritance."""
        # Test that Scanners inherits from SoftDeleteNoCacheDocument
        from mongoengine_softdelete.document import SoftDeleteNoCacheDocument
        from mongoengine import Document
        
        assert issubclass(Scanners, SoftDeleteNoCacheDocument)
        assert issubclass(Scanners, Document)
    
    def test_scanner_types_inheritance(self):
        """Test ScannerTypes inheritance."""
        from mongoengine_softdelete.document import SoftDeleteNoCacheDocument
        from mongoengine import Document
        
        assert issubclass(ScannerTypes, SoftDeleteNoCacheDocument)
        assert issubclass(ScannerTypes, Document)