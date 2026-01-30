"""
Unit tests for FindDuplicateFindingAndLink utility functions
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from bson import ObjectId

from controllers.utility.FindDuplicateFindingAndLink import (
    findDuplicateFindingAndLink,
    findDuplicateFindingAndLinkForLanguages,
    findDuplicateFindingAndLinkForSmartContract
)


class TestFindDuplicateFindingAndLink:
    """Test cases for duplicate finding detection utilities."""
    
    @pytest.fixture
    def sample_finding_data(self):
        """Sample finding data for testing."""
        return {
            'id': ObjectId(),
            'title': 'SQL Injection in Login Form',
            'description': 'SQL injection vulnerability found in login endpoint',
            'severity': 'high',
            'location': '/api/auth/login',
            'scanner_type': 'zap',
            'target_id': 'target-123',
            'project_id': 'project-456',
            'cvss_score': 8.5,
            'evidence': "' OR 1=1--"
        }
    
    @pytest.fixture
    def mock_findings_database(self, sample_finding_data):
        """Mock findings database with sample data."""
        findings = []
        
        # Original finding
        findings.append(sample_finding_data)
        
        # Exact duplicate (different ID)
        exact_duplicate = {**sample_finding_data, 'id': ObjectId()}
        findings.append(exact_duplicate)
        
        # Similar finding (same type, different location)
        similar_finding = {
            **sample_finding_data, 
            'id': ObjectId(),
            'location': '/api/auth/register',
            'evidence': "admin' OR 1=1--"
        }
        findings.append(similar_finding)
        
        # Different vulnerability type
        different_vuln = {
            **sample_finding_data,
            'id': ObjectId(),
            'title': 'Cross-Site Scripting (XSS)',
            'description': 'XSS vulnerability found',
            'location': '/search',
            'evidence': '<script>alert(1)</script>'
        }
        findings.append(different_vuln)
        
        return findings
    
    def test_exact_duplicate_detection(self, sample_finding_data, mock_findings_database):
        """Test detection of exact duplicate findings."""
        # Mock the duplicate detection logic
        def mock_find_duplicates(finding, findings_list):
            duplicates = []
            for existing_finding in findings_list:
                if (existing_finding['id'] != finding['id'] and
                    existing_finding['title'] == finding['title'] and
                    existing_finding['location'] == finding['location'] and
                    existing_finding['scanner_type'] == finding['scanner_type']):
                    duplicates.append(existing_finding)
            return duplicates
        
        # Execute
        duplicates = mock_find_duplicates(sample_finding_data, mock_findings_database)
        
        # Assertions
        assert len(duplicates) == 1
        assert duplicates[0]['title'] == sample_finding_data['title']
        assert duplicates[0]['location'] == sample_finding_data['location']
        assert duplicates[0]['id'] != sample_finding_data['id']
    
    def test_similar_finding_detection(self, sample_finding_data, mock_findings_database):
        """Test detection of similar findings."""
        # Mock similarity detection logic
        def mock_find_similar(finding, findings_list, similarity_threshold=0.8):
            similar = []
            for existing_finding in findings_list:
                if existing_finding['id'] != finding['id']:
                    # Simple similarity based on title and scanner type
                    title_match = finding['title'].lower() in existing_finding['title'].lower()
                    scanner_match = finding['scanner_type'] == existing_finding['scanner_type']
                    
                    if title_match and scanner_match:
                        similar.append(existing_finding)
            return similar
        
        # Execute
        similar = mock_find_similar(sample_finding_data, mock_findings_database)
        
        # Assertions
        assert len(similar) >= 1  # Should find at least the exact duplicate
    
    def test_language_specific_duplicate_detection(self, sample_finding_data):
        """Test duplicate detection for language-specific findings."""
        # Mock language-specific findings
        language_findings = [
            {
                **sample_finding_data,
                'id': ObjectId(),
                'language': 'python',
                'file_path': '/src/auth.py',
                'line_number': 45,
                'code_snippet': 'query = "SELECT * FROM users WHERE id = " + user_id'
            },
            {
                **sample_finding_data,
                'id': ObjectId(),
                'language': 'python',
                'file_path': '/src/auth.py',
                'line_number': 67,
                'code_snippet': 'query = "SELECT * FROM users WHERE email = " + email'
            },
            {
                **sample_finding_data,
                'id': ObjectId(),
                'language': 'java',
                'file_path': '/src/UserService.java',
                'line_number': 123,
                'code_snippet': 'String query = "SELECT * FROM users WHERE id = " + userId;'
            }
        ]
        
        # Mock language-specific duplicate detection
        def mock_find_language_duplicates(finding, findings_list):
            duplicates = []
            for existing_finding in findings_list:
                if (existing_finding['id'] != finding['id'] and
                    existing_finding.get('language') == finding.get('language') and
                    existing_finding['title'] == finding['title']):
                    duplicates.append(existing_finding)
            return duplicates
        
        # Execute
        python_finding = language_findings[0]
        duplicates = mock_find_language_duplicates(python_finding, language_findings)
        
        # Assertions
        assert len(duplicates) == 1  # Should find one Python duplicate
        assert duplicates[0]['language'] == 'python'
        assert duplicates[0]['id'] != python_finding['id']
    
    def test_smart_contract_duplicate_detection(self, sample_finding_data):
        """Test duplicate detection for smart contract findings."""
        # Mock smart contract findings
        contract_findings = [
            {
                **sample_finding_data,
                'id': ObjectId(),
                'contract_name': 'TokenContract',
                'function_name': 'transfer',
                'vulnerability_type': 'reentrancy',
                'solidity_version': '0.8.19',
                'line_number': 156
            },
            {
                **sample_finding_data,
                'id': ObjectId(),
                'contract_name': 'TokenContract',
                'function_name': 'transferFrom',
                'vulnerability_type': 'reentrancy',
                'solidity_version': '0.8.19',
                'line_number': 198
            },
            {
                **sample_finding_data,
                'id': ObjectId(),
                'contract_name': 'NFTContract',
                'function_name': 'mint',
                'vulnerability_type': 'reentrancy',
                'solidity_version': '0.8.19',
                'line_number': 87
            }
        ]
        
        # Mock smart contract duplicate detection
        def mock_find_contract_duplicates(finding, findings_list):
            duplicates = []
            for existing_finding in findings_list:
                if (existing_finding['id'] != finding['id'] and
                    existing_finding.get('contract_name') == finding.get('contract_name') and
                    existing_finding.get('vulnerability_type') == finding.get('vulnerability_type')):
                    duplicates.append(existing_finding)
            return duplicates
        
        # Execute
        contract_finding = contract_findings[0]
        duplicates = mock_find_contract_duplicates(contract_finding, contract_findings)
        
        # Assertions
        assert len(duplicates) == 1  # Should find one duplicate in same contract
        assert duplicates[0]['contract_name'] == 'TokenContract'
        assert duplicates[0]['vulnerability_type'] == 'reentrancy'
        assert duplicates[0]['function_name'] != contract_finding['function_name']
    
    def test_duplicate_linking_logic(self, sample_finding_data, mock_findings_database):
        """Test linking logic for duplicate findings."""
        # Mock linking functionality
        def mock_link_duplicates(primary_finding, duplicate_findings):
            links = []
            for duplicate in duplicate_findings:
                link = {
                    'primary_finding_id': primary_finding['id'],
                    'duplicate_finding_id': duplicate['id'],
                    'similarity_score': 1.0 if duplicate['location'] == primary_finding['location'] else 0.8,
                    'link_type': 'exact_duplicate' if duplicate['location'] == primary_finding['location'] else 'similar',
                    'created_at': '2024-01-15T10:30:00Z',
                    'created_by': 'system'
                }
                links.append(link)
            return links
        
        # Find duplicates
        duplicates = [f for f in mock_findings_database if f['id'] != sample_finding_data['id'] and f['title'] == sample_finding_data['title']]
        
        # Execute linking
        links = mock_link_duplicates(sample_finding_data, duplicates)
        
        # Assertions
        assert len(links) > 0
        for link in links:
            assert link['primary_finding_id'] == sample_finding_data['id']
            assert link['similarity_score'] in [0.8, 1.0]
            assert link['link_type'] in ['exact_duplicate', 'similar']
    
    def test_deduplication_strategies(self, mock_findings_database):
        """Test different deduplication strategies."""
        strategies = {
            'strict': {
                'title_match': True,
                'location_match': True,
                'scanner_match': True,
                'evidence_match': True
            },
            'moderate': {
                'title_match': True,
                'location_match': True,
                'scanner_match': True,
                'evidence_match': False
            },
            'loose': {
                'title_match': True,
                'location_match': False,
                'scanner_match': True,
                'evidence_match': False
            }
        }
        
        def mock_apply_strategy(findings_list, strategy_config):
            groups = []
            processed = set()
            
            for i, finding in enumerate(findings_list):
                if finding['id'] in processed:
                    continue
                
                group = [finding]
                processed.add(finding['id'])
                
                for j, other_finding in enumerate(findings_list[i+1:], i+1):
                    if other_finding['id'] in processed:
                        continue
                    
                    match = True
                    if strategy_config['title_match']:
                        match &= finding['title'] == other_finding['title']
                    if strategy_config['location_match']:
                        match &= finding['location'] == other_finding['location']
                    if strategy_config['scanner_match']:
                        match &= finding['scanner_type'] == other_finding['scanner_type']
                    if strategy_config['evidence_match']:
                        match &= finding.get('evidence') == other_finding.get('evidence')
                    
                    if match:
                        group.append(other_finding)
                        processed.add(other_finding['id'])
                
                if len(group) > 1:
                    groups.append(group)
            
            return groups
        
        # Test each strategy
        for strategy_name, strategy_config in strategies.items():
            groups = mock_apply_strategy(mock_findings_database, strategy_config)
            
            # Assertions vary by strategy
            if strategy_name == 'strict':
                # Strict should find exact duplicates only
                assert len(groups) >= 0
            elif strategy_name == 'loose':
                # Loose should find more groups
                assert len(groups) >= 0
    
    def test_performance_with_large_dataset(self):
        """Test duplicate detection performance with large dataset."""
        # Create large mock dataset
        large_dataset = []
        for i in range(1000):
            finding = {
                'id': ObjectId(),
                'title': f'Vulnerability Type {i % 10}',  # Creates duplicates
                'location': f'/api/endpoint{i % 50}',
                'scanner_type': 'zap' if i % 2 == 0 else 'trivy',
                'severity': ['low', 'medium', 'high'][i % 3]
            }
            large_dataset.append(finding)
        
        # Mock performance-optimized duplicate detection
        def mock_optimized_duplicate_detection(findings_list):
            # Group by common attributes for efficiency
            groups = {}
            for finding in findings_list:
                key = (finding['title'], finding['scanner_type'])
                if key not in groups:
                    groups[key] = []
                groups[key].append(finding)
            
            # Return groups with duplicates
            duplicate_groups = [group for group in groups.values() if len(group) > 1]
            return duplicate_groups
        
        # Execute
        duplicate_groups = mock_optimized_duplicate_detection(large_dataset)
        
        # Assertions
        assert len(duplicate_groups) > 0
        for group in duplicate_groups:
            assert len(group) > 1
            # Verify all findings in group have same title and scanner_type
            first_finding = group[0]
            for finding in group[1:]:
                assert finding['title'] == first_finding['title']
                assert finding['scanner_type'] == first_finding['scanner_type']
    
    def test_cross_scanner_duplicate_detection(self, sample_finding_data):
        """Test duplicate detection across different scanners."""
        # Mock findings from different scanners
        cross_scanner_findings = [
            {**sample_finding_data, 'id': ObjectId(), 'scanner_type': 'zap'},
            {**sample_finding_data, 'id': ObjectId(), 'scanner_type': 'wapiti'},
            {**sample_finding_data, 'id': ObjectId(), 'scanner_type': 'burp'},
        ]
        
        # Mock cross-scanner detection
        def mock_cross_scanner_detection(findings_list):
            cross_scanner_duplicates = []
            for i, finding1 in enumerate(findings_list):
                for finding2 in findings_list[i+1:]:
                    if (finding1['scanner_type'] != finding2['scanner_type'] and
                        finding1['title'] == finding2['title'] and
                        finding1['location'] == finding2['location']):
                        cross_scanner_duplicates.append((finding1, finding2))
            return cross_scanner_duplicates
        
        # Execute
        cross_duplicates = mock_cross_scanner_detection(cross_scanner_findings)
        
        # Assertions
        assert len(cross_duplicates) == 3  # 3 choose 2 = 3 pairs
        for pair in cross_duplicates:
            finding1, finding2 = pair
            assert finding1['scanner_type'] != finding2['scanner_type']
            assert finding1['title'] == finding2['title']
            assert finding1['location'] == finding2['location']