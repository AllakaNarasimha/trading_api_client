# 📊 LivePriceFetcher - 30-Second Overview

## What is it?
A new Python class that streams **live stock prices from Fyers in real-time** to your database.

## How similar is it to HistoricalDataFetcher?
**Exactly the same pattern:**
- Same initialization (`__init__` with watchers)
- Same config reading (historical_data section)
- Same database insertion (HistoryDataManager)
- Same symbol management

**But different execution:**
- Historical: One-time REST API call → database
- Live: Continuous WebSocket stream → database

## Location
```
client/utils/live_price_fetcher.py
```

## How to Use

### Option 1: Automatic (Default)
```python
# In config.xml, set:
<historical_data_enabled>true</historical_data_enabled>

# Then just run your monitor
monitor = OptionChainMonitor()
monitor.start_monitoring()
# ✓ Live prices automatically stream to database
```

### Option 2: Manual Control
```python
monitor = OptionChainMonitor()
monitor.start_monitoring()

# Later, check status
status = monitor.live_price_fetcher.get_subscription_status()
print(f"Streaming {status['subscribed_count']} symbols")

# Or stop manually
monitor.stop_live_price_monitoring()
```

### Option 3: Custom Callback
```python
from client.utils.live_price_fetcher import LivePriceFetcher

fetcher = LivePriceFetcher(watchers)

def my_handler(symbol: str, price_data: dict) -> None:
    print(f"{symbol}: {price_data['ltp']}")

fetcher.subscribe_with_custom_callback("NSE:NIFTY50-INDEX", my_handler)
```

## What Gets Saved to Database

```python
{
    'timestamp': 1733676543,
    'symbol': 'NSE:NIFTY50-INDEX',
    'ltp': 23450.50,          # Last Traded Price
    'bid': 23450.00,
    'ask': 23451.00,
    'open': 23400.00,
    'high': 23500.00,
    'low': 23400.00,
    'close': 23450.00,
    'volume': 1000000,
    'change': 50.50,
    'changep': 0.22
}
```

## Key Methods

| Method | What it does |
|--------|-------------|
| `subscribe_to_live_prices()` | Start streaming all symbols |
| `unsubscribe_from_live_prices()` | Stop streaming |
| `get_subscription_status()` | Check what's streaming |
| `cleanup()` | Clean up resources |

## Configuration

Edit `config.xml`:
```xml
<historical_data>
    <historical_data_enabled>true</historical_data_enabled>
    <symbols>
        <symbol name="NSE:NIFTY50-INDEX" />
        <symbol name="BSE:SENSEX-INDEX" />
    </symbols>
</historical_data>
```

When enabled → Live prices automatically logged to database during polling.

## Performance
- ⚡ Real-time updates (milliseconds)
- 🔄 Non-blocking (background thread)
- 💾 Minimal memory (no buffering)
- 🔌 Auto-reconnects if connection drops

## Documentation
- **Detailed**: `LIVE_PRICE_FETCHER_GUIDE.md`
- **Quick**: `LIVE_PRICE_FETCHER_QUICK_REF.md`
- **Comparison**: `LIVE_VS_HISTORICAL_COMPARISON.md`

## Already Integrated Into Monitor
✅ Automatically starts when polling begins
✅ Automatically stops when polling ends
✅ Handles all cleanup automatically
✅ No code changes needed!

## That's It! 🎯

LivePriceFetcher is production-ready and working. Just enable it in config and enjoy real-time price logging! 

