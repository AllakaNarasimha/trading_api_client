# LivePriceFetcher Visual Guide

## Class Hierarchy & Relationships

```
┌─────────────────────────────────────────────────────────────┐
│            OptionChainMonitor                               │
│  ────────────────────────────────────────────────────────   │
│  + current_watchers: Dict[str, PriceWatcher]               │
│  + live_price_fetcher: Optional[LivePriceFetcher]   [NEW]   │
│  ────────────────────────────────────────────────────────   │
│  + start_live_price_monitoring()          [NEW]             │
│  + stop_live_price_monitoring()           [NEW]             │
│  + poll_option_chain()                    [UPDATED]         │
│  + _cleanup_resources()                   [UPDATED]         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ uses
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            LivePriceFetcher                [NEW CLASS]       │
│  ────────────────────────────────────────────────────────   │
│  - watchers: Dict[str, PriceWatcher]                        │
│  - symbols: List[str]                                       │
│  - history_manager: HistoryDataManager                      │
│  - subscribed_symbols: Set[str]                             │
│  - active_subscriptions: Dict[str, Callable]                │
│  ────────────────────────────────────────────────────────   │
│  + __init__(watchers)                                       │
│  + subscribe_to_live_prices()                               │
│  + unsubscribe_from_live_prices()                           │
│  + subscribe_with_custom_callback(symbol, callback)         │
│  + unsubscribe_with_custom_callback(symbol)                 │
│  + get_subscription_status()                                │
│  + cleanup()                                                │
│  - _live_price_callback(symbol, message)                    │
│  - _convert_live_price_message(symbol, message)             │
│  - insert_live_price_to_db(data, symbol)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ uses
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            PriceWatcher                                      │
│  ────────────────────────────────────────────────────────   │
│  + subscribe_to_price(symbol, callback) → bool             │
│  + unsubscribe_from_price(symbol) → bool                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ uses
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            FyersAPI.subscribe_to_price()                     │
│  ────────────────────────────────────────────────────────   │
│  Creates WebSocket connection to Fyers                      │
│  Streams live prices in background                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ invokes
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  _live_price_callback() on each price update                │
│  ────────────────────────────────────────────────────────   │
│  1. Receives: {symbol, ltp, bid, ask, ...}                │
│  2. Converts via _convert_live_price_message()             │
│  3. Inserts via insert_live_price_to_db()                  │
│  4. Saved to database via HistoryDataManager               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ saves to
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            Database (Live Price Records)                     │
│  ────────────────────────────────────────────────────────   │
│  timestamp | symbol | ltp | bid | ask | open | high | low  │
│  ────────────────────────────────────────────────────────   │
│  1733676543 NSE:NIFTY50 23450.5 ...                        │
│  1733676544 NSE:NIFTY50 23450.6 ...                        │
│  1733676545 NSE:NIFTY50 23450.7 ...                        │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌──────────────┐
│ Fyers WebSocket
│ (Real-time)
└───────┬──────┘
        │
        │ price update
        │ {symbol, ltp, bid, ask, ...}
        │
        ▼
┌──────────────────────────┐
│ subscribe_to_price()     │
│ callback triggered       │
└───────┬──────────────────┘
        │
        ▼
┌────────────────────────────────────────┐
│ _live_price_callback(symbol, message)  │
│ - Log: [LIVE PRICE] NSE:NIFTY50: LTP   │
│ - Validate: Check for empty messages   │
│ - Convert: Call convert function       │
└───────┬────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────────┐
│ _convert_live_price_message()          │
│ - Extract timestamp                    │
│ - Map bid/ask/ltp fields               │
│ - Add symbol & created_at              │
│ - Return: {ts, symbol, ltp, ...}       │
└───────┬────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────────┐
│ insert_live_price_to_db(data, symbol)  │
│ - Validate: Check if HistoryManager OK │
│ - Insert: Call history_manager method  │
│ - Log: Success/failure                 │
│ - Return: True/False                   │
└───────┬────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────────┐
│ HistoryDataManager.insert_historical() │
│ - Database insertion                   │
│ - Commit transaction                   │
│ - Return: Success/failure              │
└───────┬────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────────┐
│ Database Record Saved                  │
│ {ts:..., symbol:..., ltp:..., ...}     │
└────────────────────────────────────────┘
```

## Lifecycle Diagram

```
Monitor Start
     │
     ▼
┌──────────────────────┐
│ start_monitoring()   │
│  (inherited)         │
└──────────────────────┘
     │
     ▼
┌──────────────────────┐
│ poll_option_chain()  │
│ starts in thread     │
└──────────┬───────────┘
           │
           ▼
    ┌──────────────────────┐
    │ Sync to minute bound │
    └──────────┬───────────┘
               │
               ▼
    ┌─────────────────────────────────┐
    │ if config.HISTORICAL_DATA_ENABLED:
    │   start_live_price_monitoring() │
    └──────────────┬──────────────────┘
                   │
                   ▼
        ┌──────────────────────────────┐
        │ LivePriceFetcher.__init__()  │
        │ - Create instance            │
        │ - Init HistoryManager        │
        │ - Load symbols from config   │
        └──────────────┬───────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │ subscribe_to_live_prices()   │
        │ - For each symbol:           │
        │   - Call watcher.subscribe() │
        │   - Add to subscribed_set    │
        │ - Log: "Subscribed X/Y"      │
        └──────────────┬───────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │ WebSocket Connection Active  │
        │ - Stream live prices         │
        │ - Invoke callbacks           │
        │ - Log to database            │
        └──────────────┬───────────────┘
                       │
        [POLLING CONTINUES]
        [LIVE PRICES STREAM]
                       │
      (When Stop Signal)
                       │
                       ▼
        ┌──────────────────────────────┐
        │ stop_live_price_monitoring() │
        │ - Call unsubscribe_all()     │
        │ - Call cleanup()             │
        │ - Close WebSocket            │
        │ - Log: "Stopped"             │
        └──────────────┬───────────────┘
                       │
                       ▼
┌──────────────────────────────────────┐
│ _cleanup_resources()                 │
│ (called on monitor stop)             │
│ - Closes manager connections         │
│ - Clears all dictionaries            │
└──────────────────────────────────────┘
     │
     ▼
Monitor Stop
```

## Configuration Impact

```
config.xml
│
├─ HISTORICAL_DATA_ENABLED = true
│  │
│  ├─ During polling:
│  │  └─ ✓ Live prices stream
│  │
│  └─ On shutdown:
│     └─ ✓ Historical data fetched
│
├─ HISTORICAL_DATA_ENABLED = false
│  │
│  ├─ During polling:
│  │  └─ ✗ No live price streaming
│  │
│  └─ On shutdown:
│     └─ ✗ No historical data fetch
│
└─ HISTORICAL_SYMBOLS
   │
   ├─ If provided:
   │  └─ ✓ Use these symbols
   │
   └─ If empty:
      └─ ✓ Use all watcher symbols
```

## Method Call Sequence

```
Manual Usage:
─────────────

1. Create LivePriceFetcher(watchers)
   ↓
2. subscribe_to_live_prices()
   ├─ For each symbol:
   │  └─ watcher.subscribe_to_price(symbol, _live_price_callback)
   └─ Add to subscribed_symbols
   ↓
3. [Wait for price updates]
   └─ _live_price_callback() invoked on each update
   ↓
4. unsubscribe_from_live_prices()
   ├─ For each subscribed symbol:
   │  └─ watcher.unsubscribe_from_price(symbol)
   └─ Clear subscribed_symbols
   ↓
5. cleanup()
   └─ Final resource cleanup


Automatic Usage (via OptionChainMonitor):
───────────────────────────────────────

1. monitor.start_monitoring()
   ↓
2. poll_option_chain() starts
   ↓
3. if HISTORICAL_DATA_ENABLED:
     monitor.start_live_price_monitoring()
   ↓
4. LivePriceFetcher created & subscribed
   ↓
5. [Polling continues, prices stream]
   ↓
6. monitor.stop_monitoring()
   ↓
7. _cleanup_resources() called
   ↓
8. monitor.stop_live_price_monitoring() called
   ↓
9. Unsubscribe & cleanup automatic
```

## Status Information Structure

```
get_subscription_status() returns:
{
    'total_symbols': 3,                    # Configured
    'subscribed_count': 3,                 # Currently active
    'subscribed_symbols': [                # Which ones
        'NSE:NIFTY50-INDEX',
        'BSE:SENSEX-INDEX',
        'NSE:NIFTYBANK-INDEX'
    ],
    'configured_symbols': [...],           # From config
    'history_manager_available': True,     # DB connection OK
    'active_subscriptions': [...]          # Same as subscribed
}
```

## Error Handling Flow

```
Any method call
  │
  ▼
try:
  │
  ├─ Validate inputs
  ├─ Perform operation
  ├─ Log success/debug
  │
  └─ return True/status
  
except Exception as e:
  │
  ├─ logger.error(f"Error: {e}")
  ├─ logger.error(f"Traceback: ...")
  ├─ Graceful degradation
  │
  └─ return False/None/empty
```

## File Organization

```
trading_api_client/
│
├─ client/
│  └─ utils/
│     ├─ monitor.py                      [UPDATED]
│     ├─ historical_data_fetcher.py      [EXISTING]
│     └─ live_price_fetcher.py           [NEW ← YOU ARE HERE]
│
└─ Documentation/
   ├─ LIVE_PRICE_FETCHER_GUIDE.md        [REFERENCE]
   ├─ LIVE_PRICE_FETCHER_QUICK_REF.md    [QUICK START]
   ├─ LIVE_VS_HISTORICAL_COMPARISON.md   [COMPARISON]
   ├─ LIVE_PRICE_IMPLEMENTATION_SUMMARY  [SUMMARY]
   ├─ README_LIVE_PRICE_FETCHER.md       [OVERVIEW]
   └─ IMPLEMENTATION_CHECKLIST.md        [THIS CHECKLIST]
```

## Testing Paths

```
Path 1: Direct Class Usage
──────────────────────────
from client.utils.live_price_fetcher import LivePriceFetcher

fetcher = LivePriceFetcher(watchers)
fetcher.subscribe_to_live_prices()
status = fetcher.get_subscription_status()
fetcher.unsubscribe_from_live_prices()
fetcher.cleanup()


Path 2: Via Monitor (Automatic)
────────────────────────────────
monitor = OptionChainMonitor()
monitor.start_monitoring()
# ✓ Live prices auto-start (if enabled)
monitor.stop_monitoring()
# ✓ Live prices auto-stop


Path 3: Via Monitor (Manual)
─────────────────────────────
monitor = OptionChainMonitor()
monitor.start_live_price_monitoring()
status = monitor.live_price_fetcher.get_subscription_status()
monitor.stop_live_price_monitoring()


Path 4: Custom Callback
───────────────────────
def my_handler(symbol: str, message: dict) -> None:
    print(f"{symbol}: {message['ltp']}")

fetcher.subscribe_with_custom_callback(symbol, my_handler)
```

This visual guide shows the complete architecture and data flow of the LivePriceFetcher system! 🎯

