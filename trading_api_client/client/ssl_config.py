"""
SSL Configuration Module

Apply SSL certificate verification bypass globally.
Import this module FIRST before any other imports that use HTTPS.

This module can be imported multiple times safely - patches are idempotent.
"""

import logging
import os
import ssl
import warnings
from functools import wraps

logger = logging.getLogger(__name__)

# Set environment variable to disable SSL verification for urllib
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

# Disable SSL verification at the ssl module level
ssl._create_default_https_context = ssl._create_unverified_context

# Patch requests library if available
try:
    import requests
    import urllib3
    
    # Disable SSL warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    
    # Check if requests is already patched
    if not hasattr(requests, '_ssl_patched'):
        # Patch requests to disable SSL verification globally
        _original_request = requests.request
        
        @wraps(_original_request)
        def _patched_request(*args, **kwargs):
            kwargs.setdefault('verify', False)
            return _original_request(*args, **kwargs)
        
        requests.request = _patched_request
        requests._ssl_patched = True
        
    # Also patch requests.Session
    _original_session_request = requests.Session.request
    
    @wraps(_original_session_request)
    def _patched_session_request(self, *args, **kwargs):
        kwargs.setdefault('verify', False)
        return _original_session_request(self, *args, **kwargs)
    
    requests.Session.request = _patched_session_request
    
except ImportError:
    # requests/urllib3 not yet installed
    pass

# Print confirmation (only once)
if not hasattr(ssl, '_config_applied'):
    logger.info("Certificate verification disabled globally")
    ssl._config_applied = True
