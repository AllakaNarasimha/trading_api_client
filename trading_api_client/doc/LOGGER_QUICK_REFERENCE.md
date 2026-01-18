# Quick Reference: Context-Based Logger Usage

## TL;DR

### Create PriceWatcher with context:
```python
from client.watchlist import PriceWatcher

# Live context
pw = PriceWatcher(context='live')

# History context  
pw = PriceWatcher(context='history')

# Option chain context
pw = PriceWatcher(context='option_chain')

# Default context
pw = PriceWatcher()
```

### Log files generated:
- `option_chain_monitor_api_live.log` ← Live operations
- `option_chain_monitor_api_history.log` ← Historical operations
- `option_chain_monitor_api_option_chain.log` ← Option chain operations
- `option_chain_monitor_api_price_watcher.log` ← Default operations

---

## Where To Add Context

### In LiveDataFetchController

**File:** `client/live_data_fetch_controller.py`

```python
def _fetch_live_data(self):
    def _actual_fetch():
        try:
            self.logger.info("Waiting 5 seconds before fetching live data...")
            time.sleep(5)
            
            # ADD THIS LINE: Pass context='live'
            price_watcher = PriceWatcher(context='live')
            price_watcher.subscribe_to_live_prices()
            
            self.logger.info("Live data fetch completed")
        except Exception as e:
            self.logger.error(f"Error fetching live data: {e}", exc_info=True)
```

### In HistoryDataFetchController

**File:** `client/history_data_fetch_controller.py`

```python
def _fetch_history_data(self):
    def _actual_fetch():
        try:
            self.logger.info("Waiting 5 seconds before fetching history data...")
            time.sleep(5)
            
            # ADD THIS LINE: Pass context='history'
            price_watcher = PriceWatcher(context='history')
            price_watcher.fetch_historical_data()
            
            self.logger.info("History data fetch completed")
        except Exception as e:
            self.logger.error(f"Error fetching history data: {e}", exc_info=True)
```

### In Option Chain Monitor

**File:** `client/utils/option_chain_monitor.py` (or similar)

```python
def fetch_for_symbol(self, symbol):
    # ADD THIS LINE: Pass context='option_chain'
    price_watcher = PriceWatcher(context='option_chain')
    return price_watcher.get_option_chain(symbol, strikecount=self.strikes)
```

---

## Implementation Checklist

- [x] Created `client/utils/logger_factory.py`
- [x] Updated `client/watchlist.py` to use context-based logger
- [ ] Update `client/live_data_fetch_controller.py` - Add `context='live'`
- [ ] Update `client/history_data_fetch_controller.py` - Add `context='history'`
- [ ] Update `client/utils/option_chain_monitor.py` - Add `context='option_chain'`
- [ ] Test: Run live data controller and check `option_chain_monitor_api_live.log`
- [ ] Test: Run history controller and check `option_chain_monitor_api_history.log`
- [ ] Test: Run option chain and check `option_chain_monitor_api_option_chain.log`

---

## Sample Log Output

### Live Context
```
2026-01-16 14:30:50 - live - INFO - Subscribing to price updates for RELIANCE...
2026-01-16 14:30:51 - live - INFO - LTP update for RELIANCE:
2026-01-16 14:30:51 - live - INFO -   ltp: 2850.50
2026-01-16 14:30:51 - live - INFO -   vol_traded_today: 1250000
```

### History Context
```
2026-01-16 14:31:06 - history - INFO - Fetching historical data for RELIANCE...
2026-01-16 14:31:08 - history - INFO - Retrieved 100 candles for RELIANCE
```

### Option Chain Context
```
2026-01-16 14:32:15 - option_chain - INFO - Fetching option chain for NIFTY50-INDEX...
2026-01-16 14:32:17 - option_chain - INFO - Retrieved 30 option chain entries
```

---

## How It Works

```
LiveDataFetchController
    └─> PriceWatcher(context='live')
            └─> LoggerFactory.get_logger('live')
                    └─> Returns logger that writes to 'option_chain_monitor_api_live.log'

HistoryDataFetchController
    └─> PriceWatcher(context='history')
            └─> LoggerFactory.get_logger('history')
                    └─> Returns logger that writes to 'option_chain_monitor_api_history.log'

OptionChainMonitor
    └─> PriceWatcher(context='option_chain')
            └─> LoggerFactory.get_logger('option_chain')
                    └─> Returns logger that writes to 'option_chain_monitor_api_option_chain.log'
```

---

## Need Help?

See detailed documentation:
- **`LOGGER_CONTEXT_SOLUTION.md`** - Explains why this approach
- **`LOGGER_USAGE_EXAMPLES.md`** - More code examples
- **`IMPLEMENTATION_SUMMARY.md`** - Complete implementation details
