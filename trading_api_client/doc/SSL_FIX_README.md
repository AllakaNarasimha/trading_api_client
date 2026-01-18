# SSL Certificate Verification Fix

## Problem
When running the option chain monitor from a different directory, you may encounter SSL certificate verification errors:

```
SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1028)'))
```

This error occurs when downloading market data from `public.fyers.in`.

## Solution
The application now automatically disables SSL certificate verification through a comprehensive approach:

### 1. **Automatic SSL Configuration** (Preferred)
The SSL configuration is automatically applied when you import the `client` package. No manual configuration is needed.

**What was changed:**
- Created `client/ssl_config.py` that applies SSL patches globally
- Updated `client/__init__.py` to import `ssl_config` automatically
- Simplified `option_chain_monitor_api_simple.py` to rely on the client package

### 2. **How it Works**

When you import any module from the `client` package, the following happens automatically:

1. **Environment Variables** are set:
   - `PYTHONHTTPSVERIFY=0`
   - `REQUESTS_CA_BUNDLE=''`
   - `CURL_CA_BUNDLE=''`

2. **SSL Module** is patched:
   - `ssl._create_default_https_context` uses unverified context

3. **Requests Library** is patched:
   - All `requests.request()` calls default to `verify=False`
   - All `requests.Session.request()` calls default to `verify=False`
   - SSL warnings are suppressed

### 3. **Testing the Fix**

Run the test script from any directory:

```bash
# From project directory
cd D:\NSLearn\trading_api_client
python test_ssl_config.py

# From a different directory
cd C:\
python D:\NSLearn\trading_api_client\test_ssl_config.py
```

Expected output:
```
[SSL Config] Certificate verification disabled globally
...
✓ SSL configuration working correctly!
```

### 4. **Running Your Application**

Now you can run the option chain monitor from any directory:

```bash
# From any directory
cd C:\your\working\directory
python D:\NSLearn\trading_api_client\option_chain_monitor_api_simple.py
```

The SSL patches are applied automatically when the client package is imported.

## Security Note

⚠️ **Important**: Disabling SSL certificate verification is a security risk and should only be used in development or when you trust the network. In production, you should:

1. Install the proper CA certificates for your system
2. Use the `certifi` package: `pip install certifi`
3. Configure requests to use the certifi bundle
4. Or obtain and trust the specific certificate from `public.fyers.in`

## Alternative: Manual SSL Configuration

If you need to apply SSL patches in a different module that doesn't import `client`, add this at the very top:

```python
#!/usr/bin/env python3
import sys
import os

# Add project directory to path
project_dir = r"D:\NSLearn\trading_api_client"
sys.path.insert(0, project_dir)

# Import SSL config to apply patches
import client.ssl_config

# Now continue with your imports
from client.utils.config import Config
# ... rest of your code
```

## Files Modified

1. **client/ssl_config.py** (NEW)
   - Comprehensive SSL patch module
   - Sets environment variables
   - Patches ssl, requests, urllib3

2. **client/__init__.py**
   - Imports ssl_config automatically
   - Applies patches when client package is imported

3. **option_chain_monitor_api_simple.py**
   - Simplified to rely on client package SSL configuration
   - Removed duplicate SSL patching code

4. **test_ssl_config.py** (NEW)
   - Test script to verify SSL configuration
   - Can be run from any directory

## Troubleshooting

If you still encounter SSL errors:

1. **Clear Python cache**:
   ```bash
   cd D:\NSLearn\trading_api_client
   python -c "import py_compile; py_compile.compile('client/ssl_config.py', doraise=True)"
   ```

2. **Check if module is imported**:
   ```python
   import client
   print(hasattr(ssl, '_config_applied'))  # Should print True
   ```

3. **Verify environment variables**:
   ```python
   import os
   print(os.environ.get('PYTHONHTTPSVERIFY'))  # Should print '0'
   ```

4. **Force reimport**:
   ```python
   import sys
   if 'client.ssl_config' in sys.modules:
       del sys.modules['client.ssl_config']
   import client.ssl_config
   ```
