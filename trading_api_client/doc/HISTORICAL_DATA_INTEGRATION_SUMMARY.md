# Historical Data Integration Summary

## Overview
The historical data logging system is now fully integrated with `HistoryDataManager` from the `nslogger` library.

## Components

### 1. Database Table (nslogger/sql_script.py)
**CREATE_HISTORICAL_DATA_TABLE** - Stores OHLCV (Open, High, Low, Close, Volume) and OI (Open Interest) data
```sql
CREATE TABLE IF NOT EXISTS historical_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    oi INTEGER,
    symbol TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (timestamp, symbol)
)
```

### 2. HistoryDataManager Methods (nslogger/history_data_manager.py)

#### insert_historical_data(data, table='historical_data')
Inserts historical OHLCV data into the database.

**Parameters:**
- `data`: Can be a dict, list of dicts, or pandas DataFrame
- `table`: Target table name (default: 'historical_data')

**Features:**
- Converts input to DataFrame format
- Handles individual records or batch inserts
- Clears caches after insertion
- Provides error handling and logging
- Returns count of successfully inserted records

**Example Usage:**
```python
from nslogger.history_data_manager import HistoryDataManager

# Create manager
hdm = HistoryDataManager(db_dir='path/to/db', db_date='2025-12-06')

# Insert single record
hdm.insert_historical_data({
    'timestamp': 1733000000,
    'open': 100.5,
    'high': 102.0,
    'low': 99.5,
    'close': 101.0,
    'volume': 50000,
    'oi': 100000,
    'symbol': 'INFY'
})

# Insert multiple records
hdm.insert_historical_data([
    {'timestamp': 1733000000, 'open': 100.5, ...},
    {'timestamp': 1733003600, 'open': 101.0, ...}
])
```

#### get_historical_data(symbol, start_timestamp=None, end_timestamp=None)
Retrieves historical data for a symbol with optional timestamp range.

**Parameters:**
- `symbol`: Stock symbol
- `start_timestamp`: Optional start timestamp (Unix timestamp)
- `end_timestamp`: Optional end timestamp (Unix timestamp)

**Returns:** pandas DataFrame

**Example Usage:**
```python
# Get all historical data for a symbol
data = hdm.get_historical_data('INFY')

# Get data within a specific range
data = hdm.get_historical_data('INFY', start_timestamp=1733000000, end_timestamp=1733086400)
```

#### get_historical_data_range(symbol, start_timestamp, end_timestamp)
Convenience method for retrieving data within a specific timestamp range.

**Example Usage:**
```python
data = hdm.get_historical_data_range('INFY', 1733000000, 1733086400)
```

### 3. Historical Data Fetcher Integration (client/utils/historical_data_fetcher.py)

**Updated to use HistoryDataManager:**
- Imports `HistoryDataManager` instead of `OptionChainManager`
- Converts API response data (list of lists) to dict format matching historical_data table schema
- Calls `insert_historical_data()` method for database logging
- Exports data to CSV if `HISTORICAL_CSV_EXPORT_ENABLED` is True

**Data Conversion Flow:**
```
API Response: [timestamp, open, high, low, close, volume, oi]
         ↓
Dict Format: {
    'timestamp': value,
    'open': value,
    'high': value,
    'low': value,
    'close': value,
    'volume': value,
    'oi': value,
    'symbol': historical_symbol
}
         ↓
insert_historical_data() method
         ↓
historical_data table
```

## Configuration Required

Ensure your `config.xml` or configuration has these settings:
```xml
<HISTORICAL_DATA_ENABLED>true</HISTORICAL_DATA_ENABLED>
<HISTORICAL_SYMBOL>INFY:NSE</HISTORICAL_SYMBOL>
<HISTORICAL_BACKDAYS>30</HISTORICAL_BACKDAYS>
<HISTORICAL_DURATION>5</HISTORICAL_DURATION>
<HISTORICAL_CSV_EXPORT_ENABLED>true</HISTORICAL_CSV_EXPORT_ENABLED>
```

## Data Flow

1. **Fetch**: `fetch_historical_data()` retrieves data from broker API
2. **Convert**: List of lists is converted to list of dicts with proper field names
3. **Store**: `insert_historical_data()` inserts into `historical_data` table
4. **Export**: Data is saved to CSV file if enabled
5. **Query**: Use `get_historical_data()` to retrieve stored data

## Error Handling

Both the insert and retrieval methods include:
- Try-catch blocks for exception handling
- Detailed error logging and messages
- Graceful handling of empty datasets
- Type checking for input validation

## Performance Considerations

- **UNIQUE constraint**: Prevents duplicate entries for the same timestamp and symbol
- **Indexes**: Available for fast queries by symbol and timestamp
- **Caching**: Clears caches after data insertion to ensure fresh data
- **Batch inserts**: Efficiently handles multiple records in a single operation

## Verification

To verify the integration is working:

```python
from nslogger.history_data_manager import HistoryDataManager

hdm = HistoryDataManager(db_dir='your_db_dir', db_date='2025-12-06')

# Check method exists
print(hasattr(hdm, 'insert_historical_data'))  # Should return True
print(hasattr(hdm, 'get_historical_data'))     # Should return True

# Test insertion
test_data = {
    'timestamp': 1733000000,
    'open': 100.0,
    'high': 101.0,
    'low': 99.0,
    'close': 100.5,
    'volume': 50000,
    'oi': 0,
    'symbol': 'TEST'
}
hdm.insert_historical_data(test_data)

# Test retrieval
result = hdm.get_historical_data('TEST')
print(result)
```
