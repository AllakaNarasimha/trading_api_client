# Logger Context Usage Guide

## Quick Start

### For Live Data Controller

```python
from client.watchlist import PriceWatcher

class LiveDataFetchController:
    def _fetch_live_data(self):
        def _actual_fetch():
            try:
                self.logger.info("Waiting 5 seconds before fetching live data...")
                time.sleep(5)
                self.logger.info("Fetching live data...")
                
                # Create PriceWatcher with 'live' context
                price_watcher = PriceWatcher(context='live')
                price_watcher.subscribe_to_live_prices()
                
                self.logger.info("Live data fetch completed")
            except Exception as e:
                self.logger.error(f"Error fetching live data: {e}", exc_info=True)
```

**Result:** All logs go to `option_chain_monitor_api_live.log`

---

### For Historical Data Controller

```python
from client.watchlist import PriceWatcher

class HistoryDataFetchController:
    def _fetch_history_data(self):
        def _actual_fetch():
            try:
                self.logger.info("Waiting 5 seconds before fetching history data...")
                time.sleep(5)
                self.logger.info("Fetching history data...")
                
                # Create PriceWatcher with 'history' context
                price_watcher = PriceWatcher(context='history')
                price_watcher.fetch_historical_data()
                
                self.logger.info("History data fetch completed")
            except Exception as e:
                self.logger.error(f"Error fetching history data: {e}", exc_info=True)
```

**Result:** All logs go to `option_chain_monitor_api_history.log`

---

### For Option Chain Operations

```python
from client.watchlist import PriceWatcher

# In your option chain module
def monitor_option_chain(symbol):
    """Monitor option chain for a symbol."""
    # Create PriceWatcher with 'option_chain' context
    price_watcher = PriceWatcher(context='option_chain')
    
    option_chain = price_watcher.get_option_chain(symbol, strikecount=15)
    return option_chain
```

**Result:** All logs go to `option_chain_monitor_api_option_chain.log`

---

### Standalone Usage (Default Logger)

```python
from client.watchlist import PriceWatcher

# Without context - uses default 'price_watcher' logger
price_watcher = PriceWatcher()
price = price_watcher.get_price("RELIANCE")
```

**Result:** All logs go to `option_chain_monitor_api_price_watcher.log`

---

## Log File Structure

After implementation, you'll have:

```
logs/
├── option_chain_monitor_api_live.log          # Live data operations
├── option_chain_monitor_api_history.log       # Historical data operations
├── option_chain_monitor_api_option_chain.log  # Option chain operations
└── option_chain_monitor_api_price_watcher.log # Default/standalone usage
```

---

## Features

✅ **Separate Log Files** - Each context has its own log file  
✅ **Automatic Rotation** - Log files rotate based on size (10MB by default)  
✅ **Context-Aware** - Logger name matches context for easy identification  
✅ **Console + File** - Logs go to both console and file  
✅ **Cached Loggers** - Same context reuses the same logger instance  

---

## Implementation Details

### LoggerFactory Class

Located in: `client/utils/logger_factory.py`

```python
from client.utils.logger_factory import LoggerFactory

# Get logger for specific context
live_logger = LoggerFactory.get_logger('live')
hist_logger = LoggerFactory.get_logger('history')
opt_logger = LoggerFactory.get_logger('option_chain')

# Get default logger
default_logger = LoggerFactory.get_logger()  # or LoggerFactory.get_logger(None)
```

### PriceWatcher Integration

```python
class PriceWatcher:
    def __init__(self, context: str = None):
        """
        Initialize with optional context for logging.
        
        Args:
            context: 'live', 'history', 'option_chain', or None (default)
        """
        self.logger = LoggerFactory.get_logger(context)
```

---

## Configuration

Logging settings are controlled via `client/utils/config.py`:

```python
self.LOG_LEVEL = logging.INFO
self.LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
self.LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
self.LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
self.LOG_BACKUP_COUNT = 5  # Keep 5 backup files
```

---

## Example Log Output

**File: `option_chain_monitor_api_live.log`**
```
2026-01-16 14:30:45 - live - INFO - Waiting 5 seconds before fetching live data...
2026-01-16 14:30:50 - live - INFO - Fetching live data...
2026-01-16 14:30:51 - live - INFO - Subscribing to price updates for RELIANCE...
2026-01-16 14:30:52 - live - INFO - LTP update for RELIANCE:
2026-01-16 14:30:52 - live - INFO -   ltp: 2850.50
2026-01-16 14:30:52 - live - INFO - Live data fetch completed
```

**File: `option_chain_monitor_api_history.log`**
```
2026-01-16 14:31:00 - history - INFO - Waiting 5 seconds before fetching history data...
2026-01-16 14:31:05 - history - INFO - Fetching history data...
2026-01-16 14:31:06 - history - INFO - Fetching historical data for RELIANCE...
2026-01-16 14:31:08 - history - INFO - History data fetch completed
```

---

## Testing

To test the implementation:

```python
from client.watchlist import PriceWatcher

# Test live context
live_watcher = PriceWatcher(context='live')
live_watcher.logger.info("Testing live logger")

# Test history context
hist_watcher = PriceWatcher(context='history')
hist_watcher.logger.info("Testing history logger")

# Test option_chain context
opt_watcher = PriceWatcher(context='option_chain')
opt_watcher.logger.info("Testing option_chain logger")
```

Check the respective log files to verify logs are being written to the correct files.

---

## Benefits

1. **Easy Debugging** - Filter logs by execution context (live/history/option)
2. **Log Rotation** - Automatic cleanup of old logs
3. **Scalability** - Easy to add new contexts (e.g., 'backtesting', 'reporting')
4. **Decoupled** - PriceWatcher doesn't care where logger comes from
5. **Reusable** - Same pattern can be applied to other shared modules
