# Logger Context Solution for PriceWatcher

## Problem
`PriceWatcher` is used by multiple controllers (live, history, option chain) but currently uses a single logger. You want separate log files based on the calling context.

## Current State
- `LiveDataFetchController` uses logger named `"live"` → logs to `option_chain_monitor_api_live.log`
- `HistoryDataFetchController` uses logger named `"history"` → logs to `option_chain_monitor_api_history.log`
- `PriceWatcher` uses `logger = logging.getLogger(__name__)` → logs to default location

## Solution

### Option 1: Pass Logger to PriceWatcher (RECOMMENDED)
Pass the parent's logger instance to PriceWatcher instead of creating a new one.

**Benefits:**
- Simplest approach
- Minimal changes to PriceWatcher
- Logs automatically go to parent's file
- No duplication

**Implementation:**

```python
# In watchlist.py
class PriceWatcher:
    def __init__(self, logger=None):
        """Initialize with optional parent logger."""
        self.auth_manager = get_auth_manager()
        self.price_watcher = self.auth_manager.price_watcher
        self.watchlist = []
        
        # Use provided logger or create default
        if logger is None:
            logger = logging.getLogger(__name__)
        self.logger = logger

    # Rest of code remains the same, just use self.logger
```

**Usage in controllers:**

```python
# In live_data_fetch_controller.py
def _fetch_live_data(self):
    def _actual_fetch():
        try:
            self.logger.info("Waiting 5 seconds before fetching live data...")
            time.sleep(5)
            self.logger.info("Fetching live data...")
            
            # Pass logger to PriceWatcher
            price_watcher = PriceWatcher(logger=self.logger)
            price_watcher.subscribe_to_live_prices()
            
            self.logger.info("Live data fetch completed")
        except Exception as e:
            self.logger.error(f"Error fetching live data: {e}", exc_info=True)
```

---

### Option 2: Context-Based Logger Factory
Create a logger factory that returns the appropriate logger based on context.

**Implementation:**

Create new file: `client/utils/logger_factory.py`

```python
"""Logger factory for context-aware logging."""
import logging
from logging.handlers import RotatingFileHandler
import os
from .config import Config

class LoggerFactory:
    """Create loggers for different contexts (live, history, option_chain)."""
    
    _loggers = {}
    _config = Config()
    
    @classmethod
    def get_logger(cls, context: str) -> logging.Logger:
        """Get or create logger for a specific context.
        
        Args:
            context: One of 'live', 'history', 'option_chain', or None (default)
        
        Returns:
            Configured logger instance
        """
        if context in cls._loggers:
            return cls._loggers[context]
        
        # Create new logger
        logger = logging.getLogger(context or 'default')
        
        # Skip if already configured
        if logger.handlers:
            cls._loggers[context] = logger
            return logger
        
        logger.setLevel(cls._config.LOG_LEVEL)
        
        # Get log file path with context name
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = cls._config.get_log_file_path(script_dir, context)
        
        logging_settings = cls._config.get_logging_settings()
        
        # File handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=logging_settings['max_bytes'],
            backupCount=logging_settings['backup_count']
        )
        file_formatter = logging.Formatter(
            logging_settings['format'],
            datefmt=logging_settings['date_format']
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console = logging.StreamHandler()
        console.setLevel(logging_settings['level'])
        console_formatter = logging.Formatter(logging_settings['format'])
        console.setFormatter(console_formatter)
        logger.addHandler(console)
        
        cls._loggers[context] = logger
        return logger
```

**Usage in watchlist.py:**

```python
from client.utils.logger_factory import LoggerFactory

class PriceWatcher:
    def __init__(self, context: str = None):
        """Initialize with optional context for logging.
        
        Args:
            context: 'live', 'history', 'option_chain', or None
        """
        self.auth_manager = get_auth_manager()
        self.price_watcher = self.auth_manager.price_watcher
        self.watchlist = []
        
        # Get context-aware logger
        self.logger = LoggerFactory.get_logger(context)
```

**Usage in controllers:**

```python
# In live_data_fetch_controller.py
from client.watchlist import PriceWatcher

def _fetch_live_data(self):
    def _actual_fetch():
        try:
            self.logger.info("Waiting 5 seconds before fetching live data...")
            time.sleep(5)
            self.logger.info("Fetching live data...")
            
            # Create PriceWatcher with live context
            price_watcher = PriceWatcher(context='live')
            price_watcher.subscribe_to_live_prices()
            
            self.logger.info("Live data fetch completed")
        except Exception as e:
            self.logger.error(f"Error fetching live data: {e}", exc_info=True)

# In history_data_fetch_controller.py
def _fetch_history_data(self):
    # Create with 'history' context
    price_watcher = PriceWatcher(context='history')
    price_watcher.fetch_historical_data()

# In option_chain code
def get_option_chain(self, symbol):
    # Create with 'option_chain' context
    price_watcher = PriceWatcher(context='option_chain')
    return price_watcher.get_option_chain(symbol)
```

---

## Log File Output

After implementation, you'll have separate log files:

```
option_chain_monitor_api_live.log      # Live data operations
option_chain_monitor_api_history.log   # Historical data operations
option_chain_monitor_api_option_chain.log  # Option chain operations
```

---

## Comparison

| Aspect | Option 1 | Option 2 |
|--------|----------|---------|
| **Simplicity** | Very simple | Moderate |
| **Coupling** | Slightly coupled | Decoupled |
| **Flexibility** | Good | Better |
| **Code changes** | Minimal | More but reusable |
| **Scalability** | Works well | Better for many contexts |

---

## Recommendation

**Start with Option 1** if you just want to use parent loggers. **Move to Option 2** if you need:
- Standalone PriceWatcher instances
- Multiple concurrent contexts
- Cleaner separation of concerns
- Ability to change context at runtime

---

## Integration Steps

1. **For Option 1:**
   - Modify `PriceWatcher.__init__()` to accept optional logger
   - Update callers to pass `logger=self.logger`

2. **For Option 2:**
   - Create `client/utils/logger_factory.py`
   - Modify `PriceWatcher.__init__()` to accept optional context
   - Update all instantiations with context parameter
