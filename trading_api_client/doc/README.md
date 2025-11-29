# Trading API Client Project

This is a separate client project demonstrating how to use the `trading_api` package.

## Project Structure

```
trading_api_client/
├── README.md               # This file
├── requirements.txt        # Dependencies
├── quick_test.py          # Test script
├── config.xml             # Configuration
└── client/
    ├── __init__.py
    ├── portfolio.py       # Portfolio management
    ├── orders.py          # Order management
    └── watchlist.py       # Price watching
```

## Installation

### Step 1: Install trading_api package

From the `trader_api` folder:

```bash
pip install D:\NSLearn\trader_api\dist\trading_api-1.0.0-py3-none-any.whl
```

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run tests

```bash
python quick_test.py
```

## Usage

```python
from trading_api import DhanAPI, FyersAPI, Config

# Initialize
config = Config()
dhan = DhanAPI()
fyers = FyersAPI()

# Check configuration
print(f"Dhan Client: {config.get_dhan_client_id()}")
print(f"Fyers App: {config.get_fyers_app_id()}")
```

## Features

- ✓ Multi-broker trading (Dhan + Fyers)
- ✓ Configuration management
- ✓ Token caching
- ✓ OAuth authentication
- ✓ Order management
- ✓ Portfolio tracking
- ✓ Price watching

## Configuration

Edit `config.xml` with your broker credentials:

```xml
<config>
  <dhan>
    <client_id>YOUR_DHAN_CLIENT_ID</client_id>
    <access_token>YOUR_TOKEN</access_token>
  </dhan>
  <fyers>
    <app_id>YOUR_FYERS_APP_ID</app_id>
    <access_token>YOUR_TOKEN</access_token>
  </fyers>
</config>
```

## Testing

Run the quick test:

```bash
python quick_test.py
```

Or run individual tests:

```python
python -c "from trading_api import DhanAPI; print('DhanAPI OK')"
python -c "from trading_api import FyersAPI; print('FyersAPI OK')"
```

## Next Steps

1. Install the package (see above)
2. Update config.xml with your credentials
3. Run quick_test.py
4. Start using trading_api in your applications

## Support

For issues with trading_api, check:
- `D:\NSLearn\trader_api\docs/` - Documentation
- `D:\NSLearn\trader_api\INSTALL_TEST_GUIDE.md` - Installation guide
