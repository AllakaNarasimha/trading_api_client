# subscribe_to_price Implementation Summary

## What You Asked
How to use `subscribe_to_price` method from `PriceWatcher` to get live stock data from Fyers?

## How It Works (Technical Overview)

### Architecture
```
Fyers API (WebSocket)
        ↓
FyersAPI.subscribe_to_price()
        ↓
FyersDataSocket Connection (Background Thread)
        ↓
_on_data_message() Callback
        ↓
Your Callback Function (invoked with live price)
```

### Code Flow

1. **Call subscribe_to_price** with a symbol and callback:
   ```python
   watcher.subscribe_to_price("NSE:NIFTY50-INDEX", my_callback)
   ```

2. **FyersAPI initializes WebSocket** (one time):
   - Creates persistent connection to Fyers
   - Starts background daemon thread to keep it alive
   - Handles auto-reconnection

3. **Your callback is invoked** when price updates arrive:
   ```python
   def my_callback(symbol: str, message: Dict[str, Any]) -> None:
       ltp = message.get('ltp')  # Last Traded Price
       print(f"{symbol}: {ltp}")
   ```

4. **Message contains live data**:
   - `ltp` - Last Traded Price
   - `bid`, `ask` - Bid/Ask prices
   - `volume` - Volume traded
   - `change`, `changep` - Change amount & percent
   - And more...

## Implementation in Monitor

### Simple Integration

Add this to your `OptionChainMonitor` class:

```python
def _handle_live_price(self, symbol: str, message: Dict[str, Any]) -> None:
    """Handle live price updates from WebSocket."""
    try:
        ltp = message.get('ltp', 0)
        logger.info(f"[LIVE] {symbol}: LTP = {ltp}")
    except Exception as e:
        logger.error(f"Error in live price callback: {e}")

def start_live_price_subscriptions(self) -> None:
    """Subscribe to live prices for all symbols."""
    for symbol in self.current_watchers.keys():
        success = self.current_watchers[symbol].subscribe_to_price(
            symbol,
            self._handle_live_price
        )
        if success:
            logger.info(f"Subscribed to live prices: {symbol}")

def stop_live_price_subscriptions(self) -> None:
    """Unsubscribe from all live prices."""
    for symbol in self.current_watchers.keys():
        self.current_watchers[symbol].unsubscribe_from_price(symbol)
```

### Usage in poll_option_chain

```python
def poll_option_chain(self, symbol_config: Dict[str, Dict[str, Any]]) -> None:
    """Main polling with live prices."""
    logger.info("[THREAD STARTED] fetch_monitor")
    
    # ... existing setup code ...
    
    # START: Subscribe to live prices
    self.start_live_price_subscriptions()
    
    try:
        # ... your existing polling loop ...
        pass
    
    finally:
        # STOP: Unsubscribe from live prices
        self.stop_live_price_subscriptions()
        logger.info("[THREAD STOPPED] fetch_monitor")
```

## Key Characteristics

| Feature | Details |
|---------|---------|
| **Async** | Non-blocking, callback-driven |
| **Persistent** | WebSocket stays connected in background |
| **Multi-symbol** | Subscribe to unlimited symbols simultaneously |
| **Auto-reconnect** | Automatically reconnects if connection drops |
| **Real-time** | Updates arrive within milliseconds |
| **Single Thread** | Uses daemon thread to keep connection alive |
| **Lightweight** | Efficient DataSocket implementation |

## Data Available in Callback

```python
def callback(symbol: str, message: Dict[str, Any]) -> None:
    message = {
        'symbol': 'NSE:NIFTY50-INDEX',  # Symbol name
        'ltp': 23450.50,                 # Last Traded Price ✓
        'bid': 23450.00,                 # Bid price
        'ask': 23451.00,                 # Ask price
        'open': 23400.00,                # Open price
        'high': 23500.00,                # High price
        'low': 23400.00,                 # Low price
        'close': 23450.00,               # Previous close
        'change': 50.50,                 # Change amount
        'changep': 0.22,                 # Change %
        'volume': 1000000,               # Volume
        'atp': 23425.00,                 # Average trade price
        'spread': 1.00,                  # Bid-ask spread
        'exchange': 'NSE'                # Exchange
    }
```

## Common Use Cases

### 1. Log Live Prices
```python
def callback(symbol: str, message: Dict[str, Any]) -> None:
    logger.info(f"{symbol}: {message.get('ltp')}")
```

### 2. Database Logging
```python
def callback(symbol: str, message: Dict[str, Any]) -> None:
    self.history_manager.insert_tick_data({
        'symbol': symbol,
        'price': message.get('ltp'),
        'timestamp': datetime.datetime.now()
    })
```

### 3. Price Analysis
```python
def callback(symbol: str, message: Dict[str, Any]) -> None:
    ltp = message.get('ltp')
    bid = message.get('bid')
    ask = message.get('ask')
    spread = ask - bid
    logger.info(f"{symbol}: Spread = {spread}")
```

### 4. OHLC Candle Aggregation
```python
candle = {
    'open': first_price,
    'high': max_price,
    'low': min_price,
    'close': latest_price
}
```

## Error Handling

```python
def callback(symbol: str, message: Dict[str, Any]) -> None:
    try:
        ltp = message.get('ltp', 0)
        if ltp <= 0:
            logger.warning(f"Invalid price for {symbol}")
            return
        
        logger.info(f"{symbol}: {ltp}")
    
    except Exception as e:
        logger.error(f"Error in callback: {e}", exc_info=True)
```

## Testing Live Data

Quick test in Python:

```python
from client.watchlist import PriceWatcher
import time

def test_callback(symbol: str, message: dict):
    ltp = message.get('ltp', 0)
    print(f"{symbol}: {ltp}")

watcher = PriceWatcher()
watcher.subscribe_to_price("NSE:NIFTY50-INDEX", test_callback)

print("Listening for 30 seconds...")
time.sleep(30)

watcher.unsubscribe_from_price("NSE:NIFTY50-INDEX")
print("Done!")
```

## Files Reference

1. **LIVE_DATA_USAGE_GUIDE.md** - Comprehensive guide with examples
2. **LIVE_DATA_EXAMPLES.py** - 7 practical examples with code
3. **Trading API Source** - `$VENV/Lib/site-packages/trading_api/implementations/fyers_api.py`
4. **PriceWatcher** - `client/watchlist.py` (lines 89+)

## Summary

**To use subscribe_to_price:**

1. Define a callback function that accepts (symbol, message)
2. Call `watcher.subscribe_to_price(symbol, callback)`
3. Your callback will be invoked asynchronously whenever price updates
4. Access price data from the message dictionary
5. Call `watcher.unsubscribe_from_price(symbol)` when done

**In your monitor:**

```python
# Start: In poll_option_chain setup
self.start_live_price_subscriptions()

# Stop: In finally block  
self.stop_live_price_subscriptions()
```

That's it! You now have real-time price data streaming to your monitor via WebSocket.

