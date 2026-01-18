# LivePriceFetcher Class Implementation

## Overview

`LivePriceFetcher` is a new class similar to `HistoricalDataFetcher` that manages real-time live price subscriptions and logging from Fyers API using WebSocket connections.

## File Location
- **Path**: `client/utils/live_price_fetcher.py`
- **Class**: `LivePriceFetcher`

## Key Features

✅ **WebSocket Streaming** - Real-time price updates via Fyers WebSocket
✅ **Multi-symbol** - Subscribe to multiple symbols simultaneously  
✅ **Database Logging** - Logs live prices to database via HistoryDataManager
✅ **Message Conversion** - Converts Fyers messages to database format
✅ **Subscription Management** - Track and manage active subscriptions
✅ **Custom Callbacks** - Support for custom callback functions
✅ **Clean Cleanup** - Proper resource cleanup on shutdown
✅ **Status Tracking** - Get subscription status and statistics

## Architecture

```
OptionChainMonitor
    ↓
start_live_price_monitoring()
    ↓
LivePriceFetcher.__init__(watchers)
    ↓
subscribe_to_live_prices()
    ↓
For each symbol:
    PriceWatcher.subscribe_to_price(symbol, _live_price_callback)
    ↓
    Fyers WebSocket Connection (background thread)
    ↓
    _on_data_message() → _live_price_callback()
    ↓
    insert_live_price_to_db() → HistoryDataManager
```

## Class Methods

### Constructor
```python
__init__(self, watchers: Dict[str, PriceWatcher])
```
Initializes fetcher with watchers, reads config, sets up HistoryDataManager.

### Main Methods

**`subscribe_to_live_prices()`**
- Subscribes to live prices for all configured symbols
- Uses internal `_live_price_callback` for data handling
- Tracks subscribed symbols

**`unsubscribe_from_live_prices()`**
- Unsubscribes from all live price subscriptions
- Cleans up internal tracking
- Stops WebSocket connections

**`subscribe_with_custom_callback(symbol, callback)`**
- Subscribe to specific symbol with custom callback
- Returns: bool (success/failure)
- Useful for specialized price handling

**`unsubscribe_with_custom_callback(symbol)`**
- Unsubscribe from specific symbol
- Returns: bool (success/failure)

**`get_subscription_status()`**
- Returns dict with subscription statistics
- Shows total symbols, subscribed count, active subscriptions

**`cleanup()`**
- Comprehensive cleanup of all resources
- Stops all subscriptions
- Clears tracking dictionaries

### Data Handling

**`_convert_live_price_message(symbol, message)`**
- Converts Fyers WebSocket message to database format
- Extracts: timestamp, ltp, bid, ask, open, high, low, close, volume, etc.
- Adds: symbol, created_at, exchange info

**`insert_live_price_to_db(data, symbol)`**
- Inserts converted price data to database
- Uses HistoryDataManager
- Returns: bool (success/failure)

**`_live_price_callback(symbol, message)`**
- Internal callback invoked when price updates arrive
- Converts message format
- Logs to database if enabled
- Handles errors gracefully

## Usage in OptionChainMonitor

The `LivePriceFetcher` is already integrated into `OptionChainMonitor`:

### Automatic Integration

When polling starts, live price monitoring is automatically enabled:

```python
# In poll_option_chain method (line ~283):
if config.HISTORICAL_DATA_ENABLED:
    self.start_live_price_monitoring()
```

### Manual Control

You can manually control live price monitoring:

```python
# Start live price streaming
monitor.start_live_price_monitoring()

# Check status
status = monitor.live_price_fetcher.get_subscription_status()
print(f"Subscribed: {status['subscribed_count']}/{status['total_symbols']}")

# Stop live price streaming
monitor.stop_live_price_monitoring()
```

## Configuration

Live price fetcher respects these config settings:

```xml
<!-- In config.xml -->
<historical_data>
    <!-- Enable/disable historical data fetching -->
    <historical_data_enabled>true</historical_data_enabled>
    
    <!-- Symbols to fetch data for -->
    <symbols>
        <symbol name="NSE:NIFTY50-INDEX" />
        <symbol name="BSE:SENSEX-INDEX" />
        <symbol name="NSE:NIFTYBANK-INDEX" />
    </symbols>
</historical_data>
```

When `HISTORICAL_DATA_ENABLED=true`:
- Live prices are logged to database
- Subscriptions are automatic during polling

## Data Structure

Live price message contains:

```python
{
    'timestamp': 1733676543,        # Unix timestamp
    'symbol': 'NSE:NIFTY50-INDEX',
    'ltp': 23450.50,                # Last Traded Price
    'bid': 23450.00,
    'ask': 23451.00,
    'open': 23400.00,
    'high': 23500.00,
    'low': 23400.00,
    'close': 23450.00,
    'volume': 1000000,
    'change': 50.50,
    'changep': 0.22,
    'atp': 23425.00,                # Average Trade Price
    'spread': 1.00,
    'exchange': 'NSE',
    'created_at': '2025-12-08T...'
}
```

## Error Handling

All methods include comprehensive error handling:
- Exception caught and logged
- Traceback included in logs
- Boolean return values for success/failure
- Graceful degradation if subscription fails

## Subscription Status Example

```python
# Get current status
status = live_price_fetcher.get_subscription_status()

# Output:
{
    'total_symbols': 3,
    'subscribed_count': 3,
    'subscribed_symbols': ['NSE:NIFTY50-INDEX', 'BSE:SENSEX-INDEX', 'NSE:NIFTYBANK-INDEX'],
    'configured_symbols': ['NSE:NIFTY50-INDEX', 'BSE:SENSEX-INDEX', 'NSE:NIFTYBANK-INDEX'],
    'history_manager_available': True,
    'active_subscriptions': ['NSE:NIFTY50-INDEX', 'BSE:SENSEX-INDEX', 'NSE:NIFTYBANK-INDEX']
}
```

## Comparison with HistoricalDataFetcher

| Feature | HistoricalDataFetcher | LivePriceFetcher |
|---------|----------------------|------------------|
| **Data Type** | Historical OHLCV | Live tick prices |
| **Fetch Type** | One-time REST call | Continuous WebSocket |
| **Frequency** | Single fetch | Real-time updates |
| **Execution** | Synchronous | Asynchronous callbacks |
| **Database** | HistoryDataManager | HistoryDataManager |
| **Trigger** | Manual call or shutdown | Automatic during polling |
| **Data Points** | Open, High, Low, Close, Volume | Bid, Ask, LTP, Volume, etc. |

## Integration Points

1. **OptionChainMonitor.__init__** - Initialize live_price_fetcher variable
2. **OptionChainMonitor._cleanup_resources()** - Stop live price monitoring on cleanup
3. **OptionChainMonitor.poll_option_chain()** - Start live prices after sync_to_minute_boundary
4. **OptionChainMonitor.start_live_price_monitoring()** - Create fetcher and subscribe
5. **OptionChainMonitor.stop_live_price_monitoring()** - Stop fetcher and cleanup

## Example Usage

### Simple Usage
```python
from client.watchlist import PriceWatcher
from client.utils.live_price_fetcher import LivePriceFetcher

# Create watchers
watchers = {
    'NSE:NIFTY50-INDEX': PriceWatcher(),
    'BSE:SENSEX-INDEX': PriceWatcher()
}

# Initialize fetcher
live_fetcher = LivePriceFetcher(watchers)

# Subscribe to live prices
live_fetcher.subscribe_to_live_prices()

# Get status
status = live_fetcher.get_subscription_status()
print(f"Subscribed: {status['subscribed_count']} symbols")

# Unsubscribe and cleanup
live_fetcher.unsubscribe_from_live_prices()
live_fetcher.cleanup()
```

### Custom Callback
```python
def my_price_handler(symbol: str, message: Dict[str, Any]) -> None:
    ltp = message.get('ltp', 0)
    print(f"{symbol}: {ltp}")

# Subscribe with custom callback
live_fetcher.subscribe_with_custom_callback("NSE:NIFTY50-INDEX", my_price_handler)

# Later: unsubscribe
live_fetcher.unsubscribe_with_custom_callback("NSE:NIFTY50-INDEX")
```

## Logging

All operations are logged at appropriate levels:
- INFO: Subscribe/unsubscribe, status changes
- DEBUG: Live price updates, message conversions
- WARNING: Subscription failures, missing watchers
- ERROR: Exceptions with full traceback

Logs can be found in: `trading_api.log`

## Thread Safety

- Uses existing PriceWatcher thread-safe mechanisms
- WebSocket runs in Fyers' daemon thread
- Callbacks are thread-safe
- No explicit locking needed in LivePriceFetcher

## Performance Considerations

✅ **Efficient** - Uses WebSocket (not polling)
✅ **Low Overhead** - Single background thread per connection
✅ **Scalable** - Handles unlimited symbols
✅ **Responsive** - Millisecond-level updates
✅ **Memory** - No buffering, real-time processing

## Troubleshooting

**Issue**: Subscriptions not working
- Check `HISTORICAL_DATA_ENABLED` is `true` in config
- Verify symbols exist in watchers
- Check logs for authentication errors

**Issue**: Live prices not reaching database
- Verify HistoryDataManager initialized successfully
- Check database connection
- Review logs for insert errors

**Issue**: WebSocket connection drops
- Automatic reconnection built-in
- Check Fyers API status
- Verify internet connectivity

