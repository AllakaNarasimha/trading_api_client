# HistoricalDataFetcher vs LivePriceFetcher Comparison

## Side-by-Side Implementation

### HistoricalDataFetcher
```python
# Location: client/utils/historical_data_fetcher.py
class HistoricalDataFetcher:
    def __init__(self, watchers: Dict[str, PriceWatcher]):
        self.symbols = config.HISTORICAL_SYMBOLS or list(watchers.keys())
        self.history_manager = HistoryDataManager()
    
    def fetch_historical_data(self) -> None:
        """One-time fetch via REST API"""
        for symbol in self.symbols:
            historical_data = self.watchers[symbol].get_historical_data(...)
            self.insert_historical_data_to_db(historical_data, symbol)
```

### LivePriceFetcher (NEW)
```python
# Location: client/utils/live_price_fetcher.py
class LivePriceFetcher:
    def __init__(self, watchers: Dict[str, PriceWatcher]):
        self.symbols = config.HISTORICAL_SYMBOLS or list(watchers.keys())
        self.history_manager = HistoryDataManager()
    
    def subscribe_to_live_prices(self) -> None:
        """Continuous stream via WebSocket"""
        for symbol in self.symbols:
            self.watchers[symbol].subscribe_to_price(
                symbol, 
                self._live_price_callback
            )
```

## Feature Comparison

| Feature | Historical | Live Price |
|---------|-----------|-----------|
| **Data Source** | REST API | WebSocket |
| **Type** | OHLCV (candles) | Tick data (ltp, bid, ask) |
| **Frequency** | One-time fetch | Continuous real-time |
| **Latency** | Seconds/minutes | Milliseconds |
| **Method** | `get_historical_data()` | `subscribe_to_price()` |
| **Callback** | No | Yes (async) |
| **Thread Model** | Blocking | Non-blocking |
| **Duration** | Configurable (days back) | While subscribed |
| **Data Volume** | Fixed | Unlimited |
| **Use Case** | Analysis/backtesting | Live monitoring |

## Method Mapping

| Purpose | Historical | Live Price |
|---------|-----------|-----------|
| **Initialize** | `__init__(watchers)` | `__init__(watchers)` |
| **Get Symbols** | Read config | Read config |
| **Start Fetch** | `fetch_historical_data()` | `subscribe_to_live_prices()` |
| **Stop Fetch** | N/A (one-time) | `unsubscribe_from_live_prices()` |
| **Data Conversion** | `_convert_api_format()` | `_convert_live_price_message()` |
| **Database Insert** | `insert_historical_data_to_db()` | `insert_live_price_to_db()` |
| **Callback** | `fetch_historical_data()` | `_live_price_callback()` |
| **Cleanup** | None needed | `cleanup()` |
| **Status** | None | `get_subscription_status()` |

## Data Structure

### Historical Data
```python
# Single record (OHLCV)
{
    'timestamp': 1733676000,
    'open': 23400.00,
    'high': 23500.00,
    'low': 23400.00,
    'close': 23450.00,
    'volume': 1000000,
    'oi': 5000000,
    'symbol': 'NSE:NIFTY50-INDEX',
    'created_at': '2025-12-08...'
}
```

### Live Price Data
```python
# Single update (tick)
{
    'timestamp': 1733676543,
    'ltp': 23450.50,
    'bid': 23450.00,
    'ask': 23451.00,
    'open': 23400.00,
    'high': 23500.00,
    'low': 23400.00,
    'close': 23450.00,
    'volume': 1000000,
    'change': 50.50,
    'changep': 0.22,
    'atp': 23425.00,
    'spread': 1.00,
    'symbol': 'NSE:NIFTY50-INDEX',
    'exchange': 'NSE',
    'created_at': '2025-12-08...'
}
```

## Integration in OptionChainMonitor

### Historical Data Integration
```python
class OptionChainMonitor:
    def fetch_historical_data(self) -> None:
        """Fetch historical data when needed"""
        self._ensure_watchers_initialized()
        
        historical_fetcher = HistoricalDataFetcher(self.current_watchers)
        historical_fetcher.fetch_historical_data()
    
    # Called on shutdown or manually
```

### Live Price Integration (NEW)
```python
class OptionChainMonitor:
    def __init__(self):
        self.live_price_fetcher: Optional[LivePriceFetcher] = None
    
    def start_live_price_monitoring(self) -> None:
        """Start live price stream"""
        self.live_price_fetcher = LivePriceFetcher(self.current_watchers)
        self.live_price_fetcher.subscribe_to_live_prices()
    
    def stop_live_price_monitoring(self) -> None:
        """Stop live price stream"""
        if self.live_price_fetcher:
            self.live_price_fetcher.unsubscribe_from_live_prices()
            self.live_price_fetcher.cleanup()
    
    def poll_option_chain(self, symbol_config):
        # ... setup ...
        
        # Start live prices (automatic if enabled)
        if config.HISTORICAL_DATA_ENABLED:
            self.start_live_price_monitoring()
        
        try:
            # ... polling logic ...
        finally:
            # Stop live prices (automatic cleanup)
            self.stop_live_price_monitoring()
```

## Usage Timeline

### Historical Data
```
Fetch @ 8:35 AM (Market Close)
    ↓
API Request → Data → Database
    ↓
Analysis complete → Done
```

### Live Price (NEW)
```
Poll starts @ 9:15 AM
    ↓
Subscribe → WebSocket → Live updates → Database (continuous)
    ↓
Poll stops @ 3:30 PM
    ↓
Unsubscribe → WebSocket closed
```

## Configuration

Both use the same config section but different purposes:

```xml
<historical_data>
    <!-- Shared: Enable feature -->
    <historical_data_enabled>true</historical_data_enabled>
    
    <!-- Shared: Which symbols to use -->
    <symbols>
        <symbol name="NSE:NIFTY50-INDEX" />
        <symbol name="BSE:SENSEX-INDEX" />
    </symbols>
    
    <!-- Historical only: How far back -->
    <historical_backdays>30</historical_backdays>
    
    <!-- Historical only: Data resolution -->
    <historical_duration>1</historical_duration>
    
    <!-- Both: CSV export -->
    <csv_export_enabled>true</csv_export_enabled>
</historical_data>
```

## Key Differences in Implementation

### HistoricalDataFetcher
- **Fetch Pattern**: Pull (request data)
- **Frequency**: Single call
- **Data Format**: Candles (OHLCV)
- **State**: Stateless
- **Error Recovery**: Simple try-catch
- **Memory**: Minimal (data discarded after save)

### LivePriceFetcher (NEW)
- **Fetch Pattern**: Push (WebSocket stream)
- **Frequency**: Real-time updates
- **Data Format**: Ticks (bid/ask/ltp)
- **State**: Maintains subscriptions
- **Error Recovery**: Auto-reconnect
- **Memory**: Minimal (no buffering)

## When to Use Each

### Use HistoricalDataFetcher When:
- You need past data for analysis
- Backtesting strategies
- Building historical database
- One-time data gathering
- Performance analysis of past trades

### Use LivePriceFetcher (NEW) When:
- Monitoring current market prices
- Real-time alerts/notifications
- Live trading decisions
- Continuous price logging
- Market microstructure analysis

## Combined Usage (Recommended)

For a complete solution, use both:

```python
monitor = OptionChainMonitor()

# Start monitoring (includes live prices)
monitor.start_monitoring()

# ... runs with real-time price streaming ...

# On shutdown, historical data is fetched
# Live prices automatically cleaned up
monitor.stop_monitoring()
```

## Code Structure Similarity

Both classes follow the same pattern:

```python
class FetcherBase:
    def __init__(self, watchers):
        self.watchers = watchers
        self.symbols = get_symbols_from_config()
        self.history_manager = HistoryDataManager()
    
    def start_service(self):
        # For historical: fetch_historical_data()
        # For live: subscribe_to_live_prices()
        pass
    
    def convert_data(self, raw_data):
        # Convert to database format
        pass
    
    def save_to_db(self, converted_data):
        # Use history_manager to insert
        pass
    
    def cleanup(self):
        # Clean up resources
        pass
```

## Testing Both

```python
# Setup
watchers = {
    'NSE:NIFTY50-INDEX': PriceWatcher(),
    'BSE:SENSEX-INDEX': PriceWatcher()
}

# Test Historical
hist_fetcher = HistoricalDataFetcher(watchers)
hist_fetcher.fetch_historical_data()

# Test Live
live_fetcher = LivePriceFetcher(watchers)
live_fetcher.subscribe_to_live_prices()
time.sleep(10)
live_fetcher.unsubscribe_from_live_prices()
live_fetcher.cleanup()
```

## Summary

| Aspect | Historical | Live Price |
|--------|-----------|-----------|
| **File** | `historical_data_fetcher.py` | `live_price_fetcher.py` |
| **Pattern** | Pull from API | Push via WebSocket |
| **Timing** | Batch/periodic | Real-time |
| **Best For** | Historical analysis | Live monitoring |
| **Database** | Same (HistoryDataManager) | Same (HistoryDataManager) |
| **Config** | Same section | Same section |
| **Integration** | On shutdown | During polling |

Both are production-ready and fully integrated! 🚀

