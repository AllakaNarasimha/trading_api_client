# Live Stock Data Subscription Guide

## Overview

The `subscribe_to_price` method in `PriceWatcher` provides real-time LTP (Last Traded Price) updates from Fyers using their WebSocket connection.

## How subscribe_to_price Works

### Method Signature
```python
def subscribe_to_price(self, symbol: str, callback: Callable) -> bool:
    """Subscribe to real-time LTP price updates for a symbol."""
```

### Architecture Flow

1. **Fyers DataSocket WebSocket** - Opens persistent connection to Fyers
2. **Callback Function** - Receives updates asynchronously when price changes
3. **Multiple Subscriptions** - Can subscribe to multiple symbols simultaneously
4. **Keep Running Thread** - Background daemon thread keeps connection alive

## Implementation Details (From trading_api)

The `subscribe_to_price` method in FyersAPI:

1. **Creates DataSocket Connection** (if not already created):
   ```python
   self._data_ws = data_ws.FyersDataSocket(
       access_token=self._access_token,
       on_message=self._on_data_message,  # Receives updates
       reconnect=True,
       ...
   )
   ```

2. **Starts Background Thread**:
   - Daemon thread to keep WebSocket running
   - Automatically reconnects if connection drops

3. **Subscribes to Symbol**:
   ```python
   self._data_ws.subscribe(symbols=symbols_list, data_type="SymbolUpdate")
   ```

4. **Invokes Callback** when data arrives:
   ```python
   def _on_data_message(self, message: Dict[str, Any]) -> None:
       symbol = message.get('symbol')
       if symbol in self._data_subscriptions:
           callback(symbol, message)  # Your callback gets called
   ```

## How to Use in Your Code

### 1. Define a Callback Function

```python
def my_price_callback(symbol: str, message: Dict[str, Any]) -> None:
    """Handle live price updates."""
    ltp = message.get('ltp', 0)  # Last Traded Price
    print(f"[LIVE] {symbol}: LTP = {ltp}")
    
    # Access other fields:
    # message.get('bid')        # Bid price
    # message.get('ask')        # Ask price
    # message.get('volume')     # Volume
    # message.get('change')     # Change amount
    # message.get('changep')    # Change percent
```

### 2. Subscribe to Live Data

```python
from client.watchlist import PriceWatcher

watcher = PriceWatcher()

# Subscribe to single symbol
success = watcher.subscribe_to_price("NSE:NIFTY50-INDEX", my_price_callback)

# Subscribe to multiple symbols
watcher.subscribe_to_price("BSE:SENSEX-INDEX", my_price_callback)
watcher.subscribe_to_price("NSE:NIFTYBANK-INDEX", my_price_callback)
```

### 3. Unsubscribe When Done

```python
watcher.unsubscribe_from_price("NSE:NIFTY50-INDEX")
```

## Usage in Monitor Context

### Option 1: Live Price Updates During Polling

Add to your polling loop to log live prices alongside option chain data:

```python
def poll_option_chain(self, symbol_config: Dict[str, Dict[str, Any]]) -> None:
    """Main polling with live price tracking."""
    
    # Setup live price callbacks
    def live_price_callback(symbol: str, message: Dict[str, Any]) -> None:
        ltp = message.get('ltp', 0)
        logger.info(f"[LIVE PRICE] {symbol}: {ltp}")
        # Can log to database or use for analysis
    
    # Subscribe to live prices for all symbols
    for symbol in self.current_watchers.keys():
        self.current_watchers[symbol].subscribe_to_price(
            symbol, 
            live_price_callback
        )
    
    try:
        # ... rest of polling logic ...
        pass
    finally:
        # Unsubscribe on exit
        for symbol in self.current_watchers.keys():
            self.current_watchers[symbol].unsubscribe_from_price(symbol)
```

### Option 2: Dedicated Live Data Thread

```python
def _start_live_price_monitor(self) -> None:
    """Start monitoring live prices in background thread."""
    
    def price_callback(symbol: str, message: Dict[str, Any]) -> None:
        ltp = message.get('ltp', 0)
        timestamp = datetime.datetime.now()
        logger.info(f"[LIVE] {timestamp} | {symbol}: {ltp}")
        
        # Can insert into database
        # self.history_manager.insert_tick_data({
        #     'symbol': symbol,
        #     'price': ltp,
        #     'timestamp': timestamp
        # })
    
    # Start live price subscriptions
    live_price_thread = threading.Thread(
        target=self._subscribe_to_live_prices,
        args=(price_callback,),
        daemon=True,
        name="live_price_monitor"
    )
    live_price_thread.start()
    return live_price_thread

def _subscribe_to_live_prices(self, callback: Callable) -> None:
    """Subscribe to live prices for all symbols."""
    try:
        for symbol in self.current_watchers.keys():
            self.current_watchers[symbol].subscribe_to_price(symbol, callback)
            logger.info(f"Subscribed to live prices for {symbol}")
        
        # Keep running - WebSocket stays connected in daemon thread
        while not self.stop_event.is_set():
            self.stop_event.wait(timeout=1)
    finally:
        # Cleanup on exit
        for symbol in self.current_watchers.keys():
            try:
                self.current_watchers[symbol].unsubscribe_from_price(symbol)
            except Exception as e:
                logger.error(f"Error unsubscribing from {symbol}: {e}")
```

### Option 3: Live Data with Historical Aggregation

```python
class LivePriceAggregator:
    """Aggregate live prices with configurable intervals."""
    
    def __init__(self, interval_seconds: int = 60):
        self.interval = interval_seconds
        self.price_buffer = {}
        self.last_flush = datetime.datetime.now()
    
    def price_callback(self, symbol: str, message: Dict[str, Any]) -> None:
        """Collect live prices."""
        ltp = message.get('ltp', 0)
        timestamp = int(datetime.datetime.now().timestamp())
        
        if symbol not in self.price_buffer:
            self.price_buffer[symbol] = {
                'ltp': ltp,
                'high': ltp,
                'low': ltp,
                'volume': 0,
                'first_timestamp': timestamp
            }
        else:
            buf = self.price_buffer[symbol]
            buf['ltp'] = ltp
            buf['high'] = max(buf['high'], ltp)
            buf['low'] = min(buf['low'], ltp)
            buf['volume'] += message.get('volume', 0)
        
        # Flush buffer periodically
        if (datetime.datetime.now() - self.last_flush).total_seconds() >= self.interval:
            self.flush_buffer()
    
    def flush_buffer(self) -> None:
        """Save aggregated prices to database."""
        for symbol, data in self.price_buffer.items():
            logger.info(f"[AGGREGATED] {symbol}: High={data['high']}, Low={data['low']}, LTP={data['ltp']}")
            # Insert into database
        
        self.price_buffer.clear()
        self.last_flush = datetime.datetime.now()
```

## Data Structure - Message Format

When your callback is invoked, it receives a message dictionary with:

```python
{
    'symbol': 'NSE:NIFTY50-INDEX',      # Symbol name
    'ltp': 23450.50,                     # Last Traded Price
    'bid': 23450.00,                     # Bid price
    'ask': 23451.00,                     # Ask price
    'open': 23400.00,                    # Open price
    'high': 23500.00,                    # High price
    'low': 23400.00,                     # Low price
    'close': 23450.00,                   # Previous close
    'change': 50.50,                     # Change amount
    'changep': 0.22,                     # Change percent
    'volume': 1000000,                   # Volume traded
    'atp': 23425.00,                     # Average trade price
    'spread': 1.00,                      # Bid-ask spread
    'exchange': 'NSE'                    # Exchange
}
```

## Key Points

✅ **Non-blocking** - Callback is invoked asynchronously
✅ **Persistent** - WebSocket stays connected in background thread
✅ **Multiple symbols** - Subscribe to unlimited symbols
✅ **Auto-reconnect** - Automatically reconnects if connection drops
✅ **Lightweight** - Uses efficient Fyers DataSocket
✅ **Real-time** - Updates arrive milliseconds after trade

## Error Handling

```python
def safe_price_callback(symbol: str, message: Dict[str, Any]) -> None:
    """Callback with error handling."""
    try:
        ltp = message.get('ltp', 0)
        if ltp == 0:
            logger.warning(f"Invalid price for {symbol}: {message}")
            return
        
        logger.info(f"[LIVE] {symbol}: {ltp}")
    except Exception as e:
        logger.error(f"Error in price callback: {e}", exc_info=True)
```

## Integration with Monitor

To integrate with your existing monitor, add this to `_ensure_watchers_initialized()`:

```python
def _ensure_watchers_initialized(self) -> None:
    """Initialize watchers with optional live price tracking."""
    if not self.current_symbols:
        logger.warning("No symbols configured")
        return
    
    for symbol in self.current_symbols:
        if symbol not in self.current_watchers:
            try:
                self.current_watchers[symbol] = PriceWatcher()
                
                # Optionally start live price tracking
                if config.LIVE_PRICE_ENABLED:
                    self.current_watchers[symbol].subscribe_to_price(
                        symbol,
                        self._handle_live_price_update
                    )
                logger.debug(f"Initialized watcher for {symbol}")
            except Exception as e:
                logger.error(f"Failed to initialize watcher for {symbol}: {e}")

def _handle_live_price_update(self, symbol: str, message: Dict[str, Any]) -> None:
    """Handle live price updates from WebSocket."""
    try:
        ltp = message.get('ltp', 0)
        # Log or process live price
        logger.debug(f"[LIVE] {symbol}: {ltp}")
    except Exception as e:
        logger.error(f"Error handling live price for {symbol}: {e}")
```

## Testing

```python
# Simple test
from client.watchlist import PriceWatcher

def test_callback(symbol: str, message: dict):
    print(f"{symbol}: {message.get('ltp')}")

watcher = PriceWatcher()
watcher.subscribe_to_price("NSE:NIFTY50-INDEX", test_callback)

# Keep running for 30 seconds
import time
time.sleep(30)

watcher.unsubscribe_from_price("NSE:NIFTY50-INDEX")
```

