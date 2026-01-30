"""
Test package initialization for CyberSecurity Service
"""

# Test configuration
import os
import sys

# Add the service directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Test environment configuration
os.environ['TESTING'] = 'True'
os.environ['DATABASE_NAME'] = 'test_scans_db'
os.environ['FLASK_ENV'] = 'testing'