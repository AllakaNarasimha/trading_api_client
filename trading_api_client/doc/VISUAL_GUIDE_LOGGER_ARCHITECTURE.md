# Visual Guide: Context-Based Logger Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Your Trading System                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
    ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
    │  LiveData        │ │  HistoryData     │ │  OptionChain     │
    │  Controller      │ │  Controller      │ │  Monitor         │
    │                  │ │                  │ │                  │
    │ context='live'   │ │ context='history'│ │ context=         │
    │                  │ │                  │ │ 'option_chain'   │
    └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  │
                                  ▼
                        ┌──────────────────────┐
                        │   PriceWatcher       │
                        │   (Shared Module)    │
                        │                      │
                        │  __init__(context)   │
                        │  └─> self.logger =   │
                        │      LoggerFactory   │
                        │      .get_logger()   │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │  LoggerFactory       │
                        │  (Factory Pattern)   │
                        │                      │
                        │  get_logger()        │
                        │  - Caches loggers    │
                        │  - Creates new ones  │
                        │  - Configures files  │
                        └──────────┬───────────┘
                                   │
        ┌──────────────┬───────────┼───────────┬──────────────┐
        │              │           │           │              │
        ▼              ▼           ▼           ▼              ▼
    ┌────────┐  ┌────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
    │Live    │  │History │  │Option    │  │Price     │  │Console   │
    │Logger  │  │Logger  │  │Chain     │  │Watcher   │  │Output    │
    │        │  │        │  │Logger    │  │Logger    │  │(All      │
    │        │  │        │  │          │  │          │  │contexts) │
    └────┬───┘  └────┬───┘  └────┬─────┘  └────┬─────┘  └──────────┘
         │           │           │            │
         ▼           ▼           ▼            ▼
    ┌─────────────────────────────────────────────────────────────┐
    │              Log File Rotation (RotatingFileHandler)         │
    │  (10MB max, keeps 5 backups)                                │
    └─────────────────────────────────────────────────────────────┘
         │           │           │            │
         ▼           ▼           ▼            ▼
    ┌─────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐
    │live.log │ │hist.log│ │option.   │ │price_    │
    │         │ │        │ │chain.log │ │watcher.  │
    │7.2 MB   │ │2.1 MB  │ │3.5 MB    │ │log       │
    │         │ │        │ │          │ │1.8 MB    │
    └─────────┘ └────────┘ └──────────┘ └──────────┘
```

---

## Data Flow: From LiveDataFetchController to Log File

```
1. Create Instance
   ┌──────────────────────────────────────┐
   │ price_watcher =                       │
   │   PriceWatcher(context='live')        │
   └────────────────┬─────────────────────┘
                    │
                    ▼
2. Initialize PriceWatcher
   ┌──────────────────────────────────────┐
   │ def __init__(self, context='live'):  │
   │   self.logger =                       │
   │     LoggerFactory.get_logger(context) │
   └────────────────┬─────────────────────┘
                    │
                    ▼
3. Get Logger from Factory
   ┌──────────────────────────────────────┐
   │ LoggerFactory.get_logger('live')      │
   │                                       │
   │ - Check cache for 'live'              │
   │ - Not found, create new logger        │
   │ - Set logger name = 'live'            │
   │ - Add file handler → live.log         │
   │ - Add console handler                 │
   │ - Cache and return logger             │
   └────────────────┬─────────────────────┘
                    │
                    ▼
4. Log Messages Go to Both Targets
   ┌──────────────────────────────────────┐
   │ price_watcher.logger.info(...)        │
   │                                       │
   │ ┌─────────────┐  ┌────────────────┐  │
   │ │Console      │  │File (Rotating) │  │
   │ │             │  │                │  │
   │ │ [16:30:51]  │  │option_chain_   │  │
   │ │ live - INFO │  │monitor_api_    │  │
   │ │ Subscribing │  │live.log        │  │
   │ │ ...         │  │                │  │
   │ └─────────────┘  └────────────────┘  │
   └──────────────────────────────────────┘
```

---

## Log File Organization

```
Current Working Directory
│
├── option_chain_monitor_api_live.log
│   ├── [2026-01-16 14:30:51] - live - INFO - Subscribing to price updates...
│   ├── [2026-01-16 14:30:52] - live - INFO - LTP update for RELIANCE:
│   ├── [2026-01-16 14:30:52] - live - INFO -   ltp: 2850.50
│   └── ... (more live events)
│
├── option_chain_monitor_api_history.log
│   ├── [2026-01-16 14:31:06] - history - INFO - Fetching historical data...
│   ├── [2026-01-16 14:31:08] - history - INFO - Retrieved 100 candles
│   └── ... (more history events)
│
├── option_chain_monitor_api_option_chain.log
│   ├── [2026-01-16 14:32:15] - option_chain - INFO - Fetching option chain...
│   ├── [2026-01-16 14:32:17] - option_chain - INFO - Retrieved 30 entries
│   └── ... (more option chain events)
│
└── option_chain_monitor_api_price_watcher.log
    └── (Default context, rarely used in production)
```

---

## Class Relationships

```
┌────────────────────────┐
│   PriceWatcher         │
├────────────────────────┤
│ - context: str         │
│ - logger: Logger       │◄──────────────┐
│ - auth_manager         │               │
│ - watchlist            │               │
├────────────────────────┤               │
│ + __init__(context)    │               │
│ + get_price()          │               │
│ + get_quotes()         │               │ Uses
│ + subscribe_to_price() │               │
│ + get_option_chain()   │               │
│ + get_historical_data()│               │
└────────────────────────┘               │
                                         │
                    ┌────────────────────┘
                    │
                    ▼
        ┌────────────────────────┐
        │  LoggerFactory         │
        ├────────────────────────┤
        │ - _loggers: dict       │
        │ - _config: Config      │
        ├────────────────────────┤
        │ + get_logger(context)  │
        │ + clear_cache()        │
        └────────────────────────┘
               │
               │ Uses
               ▼
        ┌────────────────────────┐
        │  Config                │
        ├────────────────────────┤
        │ + get_log_file_path()  │
        │ + get_logging_settings()
        └────────────────────────┘
```

---

## Context → Logger → File Mapping

```
Context Name          Logger Name          Log File
────────────────────────────────────────────────────────────────
'live'          →     'live'          →    option_chain_monitor_api_live.log
'history'       →     'history'       →    option_chain_monitor_api_history.log
'option_chain'  →     'option_chain'  →    option_chain_monitor_api_option_chain.log
None/'default'  →     'price_watcher' →    option_chain_monitor_api_price_watcher.log
```

---

## Runtime Example

### Scenario: Two Concurrent Operations

```
Time    Operation 1 (Live)          Operation 2 (History)
────────────────────────────────────────────────────────
14:30   Create PriceWatcher('live')  
        └─> Get 'live' logger
        └─> Add live.log handler
        
14:31                                Create PriceWatcher('history')
                                      └─> Get 'history' logger
                                      └─> Add history.log handler
                                      
14:32   Log to 'live' logger         Log to 'history' logger
        └─> Writes to live.log       └─> Writes to history.log
        
14:33   Same logger instance         Same logger instance
        (cached from step 1)         (cached from step 2)
        
Result:
├── live.log has logs from operation 1 only
└── history.log has logs from operation 2 only
```

---

## Code Flow: From Call to Log File

```
LiveDataFetchController._fetch_live_data()
    │
    ├─ price_watcher = PriceWatcher(context='live')
    │                  │
    │                  └─ PriceWatcher.__init__(context='live')
    │                     │
    │                     └─ self.logger = LoggerFactory.get_logger('live')
    │                        │
    │                        └─ Create/Get logger('live')
    │                           │
    │                           ├─ Set logger name = 'live'
    │                           ├─ Configure handlers
    │                           ├─ Set log file = option_chain_monitor_api_live.log
    │                           ├─ Cache logger
    │                           └─ Return logger
    │
    ├─ price_watcher.subscribe_to_live_prices()
    │                 │
    │                 └─ self.logger.info("Subscribing...")
    │                    │
    │                    └─ Write to both:
    │                       ├─ Console: [live] INFO Subscribing...
    │                       └─ File: option_chain_monitor_api_live.log
    │
    └─ (Operation completes)
```

---

## Benefits Visualization

```
WITHOUT Context-Based Logging:
┌──────────────────────────────────────────────────┐
│ option_chain_monitor_api.log                     │
│                                                  │
│ [14:30] live - INFO - Subscribing to prices     │
│ [14:31] live - INFO - LTP update RELIANCE       │
│ [14:32] history - INFO - Fetching historical... │
│ [14:33] live - INFO - LTP update TCS            │
│ [14:34] history - INFO - Retrieved 100 candles  │
│ [14:35] option - INFO - Fetching option chain   │
│ [14:36] live - INFO - LTP update INFY           │
│ ...                                              │
│ ▲ Mixed logs - hard to debug                    │
└──────────────────────────────────────────────────┘

WITH Context-Based Logging:
┌─────────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ live.log            │  │ history.log      │  │ option_chain.log │
│                     │  │                  │  │                  │
│ [14:30] Subscribing │  │ [14:32] Fetching │  │ [14:35] Fetching │
│ [14:31] LTP RELIANCE│  │ [14:34] Retrieved│  │ [14:36] Got 30   │
│ [14:33] LTP TCS     │  │ [14:35] Process  │  │ [14:37] Calc IV  │
│ [14:36] LTP INFY    │  │ [14:36] Save CSV │  │ [14:38] Store DB │
│ ...                 │  │ ...              │  │ ...              │
│ ✓ Easy to debug     │  │ ✓ Easy to debug  │  │ ✓ Easy to debug  │
└─────────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## Summary

The implementation provides:

1. **Separation** - Each workflow has its own log file
2. **Clarity** - Context name in logger identifies the source
3. **Performance** - Cached loggers avoid recreation overhead
4. **Flexibility** - Easy to add new contexts
5. **Compatibility** - Works with existing Config and logging setup
