# Quick Reference - trading_api Usage

## Two Project Setup

### 1. Package Project (Source)
```
D:\NSLearn\trader_api/
- Package code, build, and distribution
```

### 2. Client Project (Application)
```
D:\NSLearn\trading_api_client/
- Application using trading_api
- Already installed and tested ✓
```

---

## Quick Commands

### From trading_api_client folder:

**Test Installation**
```bash
python quick_test.py
```

**Run Demo Application**
```bash
python app.py
```

**Check Package Info**
```bash
pip show trading-api
```

**Use in Your Code**
```python
from trading_api import DhanAPI, FyersAPI, Config

config = Config()
dhan = DhanAPI()
fyers = FyersAPI()
```

---

## Project Files

### trading_api_client/

| File | Purpose |
|------|---------|
| `app.py` | Main application demo |
| `quick_test.py` | Installation test |
| `config.xml` | Broker configuration |
| `requirements.txt` | Dependencies |
| `README.md` | Setup guide |
| `TEST_SUMMARY.md` | Test results |
| `PROJECT_COMPARISON.md` | Architecture overview |
| `client/portfolio.py` | Portfolio module |
| `client/orders.py` | Orders module |
| `client/watchlist.py` | Watchlist module |

---

## Configuration

Edit `config.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<config>
  <dhan>
    <client_id>YOUR_DHAN_ID</client_id>
  </dhan>
  <fyers>
    <app_id>YOUR_FYERS_APP_ID</app_id>
  </fyers>
</config>
```

---

## API Classes

### DhanAPI
```python
from trading_api import DhanAPI

dhan = DhanAPI()
# Use for Dhan trading
```

### FyersAPI
```python
from trading_api import FyersAPI

fyers = FyersAPI()
# Use for Fyers trading
```

### Config
```python
from trading_api import Config

config = Config()
# Load configuration from config.xml
```

---

## Using Client Modules

### Portfolio Management
```python
from client.portfolio import Portfolio

portfolio = Portfolio()
holdings = portfolio.get_total_portfolio()
```

### Order Management
```python
from client.orders import OrderManager

orders = OrderManager()
orders.place_dhan_order("RELIANCE", 1, 2800, "BUY")
orders.place_fyers_order("TCS", 1, 3500, "BUY")
```

### Price Watching
```python
from client.watchlist import PriceWatcher

watcher = PriceWatcher()
watcher.add_to_watchlist("RELIANCE")
prices = watcher.get_all_prices()
```

---

## Installation Recap

```bash
# Install from wheel file (already done)
pip install D:\NSLearn\trader_api\dist\trading_api-1.0.0-py3-none-any.whl

# Verify
pip show trading-api
# Should show: Version: 1.0.0

# Test
python quick_test.py
# Should show: ✓ All tests passed!
```

---

## Status Summary

✅ **Both projects set up and tested**

- Source project: `D:\NSLearn\trader_api` - Package code ready
- Client project: `D:\NSLearn\trading_api_client` - Application ready
- Package installed: `trading-api v1.0.0`
- All tests: PASSED
- Ready for: Production use

---

## Common Tasks

### Run the application
```bash
cd D:\NSLearn\trading_api_client
python app.py
```

### Test the package
```bash
cd D:\NSLearn\trading_api_client
python quick_test.py
```

### Update configuration
```bash
# Edit config.xml with your credentials
# Place trading credentials in the file
```

### Develop custom modules
```bash
# Create new files in client/ folder
# Import trading_api as needed
# Extend Portfolio, OrderManager, PriceWatcher classes
```

### Deploy application
```bash
# Copy trading_api_client/ folder to target
# Ensure Python 3.8+ is installed
# Run: python app.py
```

---

## Documentation

Read these for more info:
- `README.md` - Project overview
- `TEST_SUMMARY.md` - What was tested
- `PROJECT_COMPARISON.md` - Architecture details
- `D:\NSLearn\trader_api\docs/` - Package documentation

---

## Support

For package issues:
- Check `D:\NSLearn\trader_api\docs/INDEX.md`
- Review `D:\NSLearn\trader_api\INSTALL_TEST_GUIDE.md`

For client application:
- Review `D:\NSLearn\trading_api_client\README.md`
- Check `D:\NSLearn\trading_api_client\PROJECT_COMPARISON.md`
