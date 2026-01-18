# LivePriceFetcher - Quick Reference

## What is LivePriceFetcher?

A class that manages real-time live price subscriptions, similar to `HistoricalDataFetcher` but for continuous WebSocket streaming instead of one-time historical fetches.

## Quick Start

### 1. Basic Usage
```python
from client.utils.live_price_fetcher import LivePriceFetcher
from client.watchlist import PriceWatcher

# Create watchers
watchers = {'NSE:NIFTY50-INDEX': PriceWatcher()}

# Initialize and start
fetcher = LivePriceFetcher(watchers)
fetcher.subscribe_to_live_prices()

# Later: stop
fetcher.unsubscribe_from_live_prices()
fetcher.cleanup()
```

### 2. In OptionChainMonitor (Already Integrated)
```python
# Automatically starts during polling
monitor.start_live_price_monitoring()

# Manually control
status = monitor.live_price_fetcher.get_subscription_status()
monitor.stop_live_price_monitoring()
```

### 3. With Custom Callback
```python
def my_callback(symbol: str, message: dict) -> None:
    ltp = message.get('ltp', 0)
    print(f"{symbol}: {ltp}")

fetcher.subscribe_with_custom_callback("NSE:NIFTY50-INDEX", my_callback)
fetcher.unsubscribe_with_custom_callback("NSE:NIFTY50-INDEX")
```

## Key Methods

| Method | Purpose |
|--------|---------|
| `subscribe_to_live_prices()` | Subscribe all configured symbols |
| `unsubscribe_from_live_prices()` | Unsubscribe all symbols |
| `subscribe_with_custom_callback(symbol, callback)` | Subscribe one symbol with custom handler |
| `unsubscribe_with_custom_callback(symbol)` | Unsubscribe one symbol |
| `get_subscription_status()` | Get current subscription stats |
| `cleanup()` | Clean up all resources |

## Automatic Integration

LivePriceFetcher is **automatically integrated** into OptionChainMonitor:

```
Monitor starts polling
    ↓
poll_option_chain() initializes
    ↓
start_live_price_monitoring() called (if HISTORICAL_DATA_ENABLED=true)
    ↓
LivePriceFetcher subscribes to all symbols
    ↓
Live prices stream to database
    ↓
Monitor stops
    ↓
stop_live_price_monitoring() cleans up
```

## Configuration

Enable in `config.xml`:
```xml
<historical_data>
    <historical_data_enabled>true</historical_data_enabled>
    <symbols>
        <symbol name="NSE:NIFTY50-INDEX" />
        <symbol name="BSE:SENSEX-INDEX" />
    </symbols>
</historical_data>
```

## Data Available

When price updates arrive, your callback receives:
```python
{
    'ltp': 23450.50,          # Last Traded Price
    'bid': 23450.00,
    'ask': 23451.00,
    'open': 23400.00,
    'high': 23500.00,
    'low': 23400.00,
    'close': 23450.00,
    'volume': 1000000,
    'change': 50.50,
    'changep': 0.22,
    'symbol': 'NSE:NIFTY50-INDEX'
}
```

## Files

- **Implementation**: `client/utils/live_price_fetcher.py`
- **Usage Guide**: `LIVE_PRICE_FETCHER_GUIDE.md`
- **Examples**: `LIVE_DATA_EXAMPLES.py`
- **Integration**: `client/utils/monitor.py` (already done)

## Comparison: LivePriceFetcher vs HistoricalDataFetcher

| Aspect | Historical | Live Price |
|--------|-----------|-----------|
| Data Fetch | REST API call | WebSocket stream |
| Update Rate | Once on demand | Real-time ticks |
| Execution | Synchronous | Asynchronous |
| Callback | No callbacks | Yes, event-driven |
| Symbol Scope | Per-symbol | Multi-symbol |
| Typical Use | Historical analysis | Live monitoring |

## Status Check

```python
status = fetcher.get_subscription_status()
# {
#     'total_symbols': 3,
#     'subscribed_count': 3,
#     'subscribed_symbols': ['NSE:NIFTY50-INDEX', ...],
#     'history_manager_available': True,
#     'active_subscriptions': [...]
# }
```

## Error Handling

All errors are logged automatically:
```
ERROR: Error subscribing to NSE:NIFTY50-INDEX: Connection failed
```

Check logs in `trading_api.log` for details.

## Thread Model

- **Main thread**: Subscribes/unsubscribes (blocking)
- **WebSocket thread**: Handles live data (daemon, non-blocking)
- **Your callback**: Invoked on WebSocket thread

## Example: In Your Monitor

```python
class MyMonitor:
    def start_monitoring(self):
        # Start polling
        self.start_option_chain_polling()
        
        # Auto-starts live price monitoring (if enabled in config)
        
    def stop_monitoring(self):
        # Auto-stops live price monitoring (via cleanup)
        self.stop_option_chain_polling()
```

## Logging

Logs appear in `trading_api.log`:
```
INFO - Initializing live price monitoring...
INFO - Subscribed to live prices for NSE:NIFTY50-INDEX
DEBUG - [LIVE PRICE] NSE:NIFTY50-INDEX: LTP = 23450.50
INFO - Live price subscriptions active: 3/3 symbols
```

## Testing

```python
import time
from client.utils.live_price_fetcher import LivePriceFetcher
from client.watchlist import PriceWatcher

# Simple test
watchers = {'NSE:NIFTY50-INDEX': PriceWatcher()}
fetcher = LivePriceFetcher(watchers)
fetcher.subscribe_to_live_prices()

print("Listening for 30 seconds...")
time.sleep(30)

fetcher.unsubscribe_from_live_prices()
print("Done!")
```

## That's It!

LivePriceFetcher provides a complete, ready-to-use live price streaming solution that works exactly like HistoricalDataFetcher but for real-time data.

**Key Point**: It's automatically integrated into your monitor - no code changes needed unless you want custom handling!

