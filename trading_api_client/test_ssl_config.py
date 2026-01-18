"""
Test SSL Configuration

Quick test to verify SSL patches are applied correctly.
Run this from any directory to test.
"""

import sys
import os

# Get the trading_api_client directory path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Import client package (this applies SSL patches)
import client.ssl_config

print("\n" + "="*60)
print("SSL Configuration Test")
print("="*60)

# Test 1: Check environment variables
print("\n[1] Environment Variables:")
print(f"  PYTHONHTTPSVERIFY: {os.environ.get('PYTHONHTTPSVERIFY', 'Not Set')}")
print(f"  REQUESTS_CA_BUNDLE: {os.environ.get('REQUESTS_CA_BUNDLE', 'Not Set')}")

# Test 2: Check SSL context
print("\n[2] SSL Context:")
import ssl
try:
    context = ssl._create_default_https_context()
    print(f"  Default SSL Context: {type(context).__name__}")
    print(f"  Check Hostname: {context.check_hostname}")
    print(f"  Verify Mode: {context.verify_mode}")
except Exception as e:
    print(f"  Error: {e}")

# Test 3: Test requests library
print("\n[3] Requests Library:")
try:
    import requests
    
    # Check if requests is patched
    is_patched = hasattr(requests, '_ssl_patched')
    print(f"  Requests patched: {is_patched}")
    
    # Try to fetch from public.fyers.in
    print(f"\n  Testing download from public.fyers.in...")
    response = requests.get('https://public.fyers.in/sym_details/NSE_CM.csv', timeout=10)
    print(f"  Status Code: {response.status_code}")
    print(f"  Response Length: {len(response.content)} bytes")
    
    if response.status_code == 200:
        print("  ✓ SSL configuration working correctly!")
    else:
        print(f"  ✗ Unexpected status code: {response.status_code}")
        
except Exception as e:
    print(f"  ✗ Error: {e}")
    print("\n  SSL configuration may not be working properly.")

print("\n" + "="*60)
print("Test complete")
print("="*60 + "\n")
