"""
Unit tests for util.py utility functions
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import jwt
from flask_jwt_extended.exceptions import JWTExtendedException

from controllers.util import get_current_user_from_jwt_token, get_decoded_token


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    def test_get_current_user_from_jwt_token_success(self):
        """Test successful JWT token user extraction."""
        with patch('controllers.util.verify_jwt_in_request') as mock_verify, \
             patch('controllers.util.get_jwt_identity') as mock_identity:
            
            mock_verify.return_value = True
            mock_identity.return_value = 'test-user-123'
            
            # Execute
            result = get_current_user_from_jwt_token()
            
            # Assertions
            mock_verify.assert_called_once()
            mock_identity.assert_called_once()
            assert result == 'test-user-123'
    
    def test_get_current_user_from_jwt_token_invalid_token(self):
        """Test JWT token validation failure."""
        with patch('controllers.util.verify_jwt_in_request') as mock_verify:
            mock_verify.side_effect = JWTExtendedException("Invalid token")
            
            # Execute and expect exception
            with pytest.raises(JWTExtendedException):
                get_current_user_from_jwt_token()
            
            mock_verify.assert_called_once()
    
    def test_get_current_user_from_jwt_token_no_identity(self):
        """Test JWT token with no identity."""
        with patch('controllers.util.verify_jwt_in_request') as mock_verify, \
             patch('controllers.util.get_jwt_identity') as mock_identity:
            
            mock_verify.return_value = True
            mock_identity.return_value = None
            
            # Execute
            result = get_current_user_from_jwt_token()
            
            # Assertions
            assert result is None
    
    @patch('controllers.util.JWTSECRET', 'test-secret-key')
    def test_get_decoded_token_success(self):
        """Test successful token decoding."""
        # Create a test token
        payload = {'user_id': 'test-user-123', 'exp': 9999999999}
        token = jwt.encode(payload, 'test-secret-key', algorithm='HS256')
        
        # Create mock request
        mock_request = Mock()
        mock_request.headers.get.return_value = f'Bearer {token}'
        
        # Execute
        result = get_decoded_token(mock_request)
        
        # Assertions
        assert result['user_id'] == 'test-user-123'
        assert 'exp' in result
    
    @patch('controllers.util.JWTSECRET', 'test-secret-key')
    def test_get_decoded_token_invalid_token(self):
        """Test decoding invalid token."""
        # Create mock request with invalid token
        mock_request = Mock()
        mock_request.headers.get.return_value = 'Bearer invalid-token'
        
        # Execute and expect exception
        with pytest.raises(jwt.InvalidTokenError):
            get_decoded_token(mock_request)
    
    @patch('controllers.util.JWTSECRET', 'test-secret-key')
    def test_get_decoded_token_expired_token(self):
        """Test decoding expired token."""
        # Create expired token
        payload = {'user_id': 'test-user-123', 'exp': 1}  # Expired timestamp
        token = jwt.encode(payload, 'test-secret-key', algorithm='HS256')
        
        # Create mock request
        mock_request = Mock()
        mock_request.headers.get.return_value = f'Bearer {token}'
        
        # Execute and expect exception
        with pytest.raises(jwt.ExpiredSignatureError):
            get_decoded_token(mock_request)
    
    def test_get_decoded_token_missing_authorization_header(self):
        """Test token decoding with missing Authorization header."""
        # Create mock request without Authorization header
        mock_request = Mock()
        mock_request.headers.get.return_value = None
        
        # Execute and expect exception
        with pytest.raises(AttributeError):
            get_decoded_token(mock_request)
    
    def test_get_decoded_token_malformed_header(self):
        """Test token decoding with malformed Authorization header."""
        # Create mock request with malformed header
        mock_request = Mock()
        mock_request.headers.get.return_value = 'InvalidFormat'
        
        # Execute and expect exception
        with pytest.raises(IndexError):
            get_decoded_token(mock_request)
    
    @patch('controllers.util.JWTSECRET', 'different-secret-key')
    def test_get_decoded_token_wrong_secret(self):
        """Test decoding token with wrong secret key."""
        # Create token with one secret
        payload = {'user_id': 'test-user-123', 'exp': 9999999999}
        token = jwt.encode(payload, 'original-secret-key', algorithm='HS256')
        
        # Create mock request
        mock_request = Mock()
        mock_request.headers.get.return_value = f'Bearer {token}'
        
        # Execute with different secret and expect exception
        with pytest.raises(jwt.InvalidSignatureError):
            get_decoded_token(mock_request)
    
    @patch('controllers.util.JWTSECRET', 'test-secret-key')
    def test_get_decoded_token_algorithm_mismatch(self):
        """Test decoding token with different algorithm."""
        # Create token with different algorithm (if supported)
        payload = {'user_id': 'test-user-123', 'exp': 9999999999}
        
        # Test with HS256 token but expecting different algorithm
        token = jwt.encode(payload, 'test-secret-key', algorithm='HS256')
        
        mock_request = Mock()
        mock_request.headers.get.return_value = f'Bearer {token}'
        
        # This should still work since we specify HS256 in the decode
        result = get_decoded_token(mock_request)
        assert result['user_id'] == 'test-user-123'
    
    def test_get_current_user_edge_cases(self):
        """Test edge cases for get_current_user_from_jwt_token."""
        # Test with empty string identity
        with patch('controllers.util.verify_jwt_in_request') as mock_verify, \
             patch('controllers.util.get_jwt_identity') as mock_identity:
            
            mock_verify.return_value = True
            mock_identity.return_value = ''
            
            result = get_current_user_from_jwt_token()
            assert result == ''
        
        # Test with numeric identity
        with patch('controllers.util.verify_jwt_in_request') as mock_verify, \
             patch('controllers.util.get_jwt_identity') as mock_identity:
            
            mock_verify.return_value = True
            mock_identity.return_value = 12345
            
            result = get_current_user_from_jwt_token()
            assert result == 12345
    
    @patch('controllers.util.JWTSECRET', 'test-secret-key')
    def test_get_decoded_token_payload_variations(self):
        """Test decoding tokens with different payload structures."""
        # Test with minimal payload
        minimal_payload = {'exp': 9999999999}
        token = jwt.encode(minimal_payload, 'test-secret-key', algorithm='HS256')
        
        mock_request = Mock()
        mock_request.headers.get.return_value = f'Bearer {token}'
        
        result = get_decoded_token(mock_request)
        assert 'exp' in result
        
        # Test with complex payload
        complex_payload = {
            'user_id': 'test-user-123',
            'email': 'test@example.com',
            'roles': ['admin', 'user'],
            'permissions': {'read': True, 'write': True},
            'exp': 9999999999,
            'iat': 1640995200,
            'iss': 'cybersecurity-service'
        }
        token = jwt.encode(complex_payload, 'test-secret-key', algorithm='HS256')
        
        mock_request.headers.get.return_value = f'Bearer {token}'
        
        result = get_decoded_token(mock_request)
        assert result['user_id'] == 'test-user-123'
        assert result['email'] == 'test@example.com'
        assert result['roles'] == ['admin', 'user']
        assert result['permissions']['read'] is True
    
    def test_import_dependencies(self):
        """Test that all required dependencies are importable."""
        # Test that all imports work correctly
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        import jwt
        
        # Verify functions exist
        assert callable(verify_jwt_in_request)
        assert callable(get_jwt_identity)
        assert hasattr(jwt, 'decode')
        assert hasattr(jwt, 'encode')
    
    def test_function_signatures(self):
        """Test function signatures and parameter handling."""
        # Test get_current_user_from_jwt_token has no parameters
        import inspect
        sig = inspect.signature(get_current_user_from_jwt_token)
        assert len(sig.parameters) == 0
        
        # Test get_decoded_token has one parameter
        sig = inspect.signature(get_decoded_token)
        assert len(sig.parameters) == 1
        assert 'request' in sig.parameters
    
    def test_error_propagation(self):
        """Test that errors are properly propagated."""
        # Test that JWT verification errors bubble up
        with patch('controllers.util.verify_jwt_in_request') as mock_verify:
            mock_verify.side_effect = Exception("Custom JWT error")
            
            with pytest.raises(Exception) as excinfo:
                get_current_user_from_jwt_token()
            
            assert "Custom JWT error" in str(excinfo.value)
        
        # Test that JWT decoding errors bubble up
        with patch('controllers.util.JWTSECRET', 'test-secret'):
            mock_request = Mock()
            mock_request.headers.get.return_value = 'Bearer invalid.token.format'
            
            with pytest.raises(jwt.DecodeError):
                get_decoded_token(mock_request)