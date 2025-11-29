# Option Chain Monitor API - User Guide

Production-ready REST API to monitor and log option chain data for NSE symbols with comprehensive error handling and resource management.

## Features

- ✅ **Thread-safe operations** with proper locking mechanisms
- ✅ **Graceful shutdown** handling (SIGINT/SIGTERM)
- ✅ **Resource cleanup** (database connections, watchers)
- ✅ **Rotating log files** (10MB per file, 5 backups)
- ✅ **Environment variable** configuration support
- ✅ **Type hints** throughout for better IDE support
- ✅ **Input validation** for all API endpoints
- ✅ **Health check** endpoint for monitoring
- ✅ **Dynamic symbol addition** without restart
- ✅ **Configurable poll intervals** per symbol
- ✅ **Windows Task Scheduler** compatible

## Quick Start

### 1. Install Dependencies

```bash
pip install flask
pip install nslogger
```

### 2. Configure Settings

Edit `config.xml` to configure the option monitor:

```xml
<!-- Option Chain Monitor API Configuration -->
<option_monitor>
    <!-- API Server Settings -->
    <api_host>0.0.0.0</api_host>
    <api_port>5000</api_port>
    
    <!-- Monitor Settings -->
    <auto_start>true</auto_start>
    <default_strikes>15</default_strikes>
    <max_symbols>10</max_symbols>
    
    <!-- Symbols to Monitor -->
    <symbols>
        <symbol name="NSE:NIFTY50-INDEX" poll_seconds="0,30" />
        <symbol name="NSE:NIFTYBANK-INDEX" poll_seconds="0,30" />
    </symbols>
</option_monitor>
```

### 3. Run the Application

```bash
python option_chain_monitor_api_simple.py
```

The monitor will:
- Load configuration from `config.xml`
- Start API server on configured host:port
- Auto-start monitoring (if `auto_start = true`)
- Begin logging option chain data at specified intervals

## Architecture

The application is organized into clean, separated classes:

### `Config` Class
- Loads configuration from `config.xml`
- Environment variable overrides
- Provides validation methods
- Centralizes default values

### `OptionChainMonitor` Class
- Core monitoring logic
- Thread management
- Symbol polling with custom intervals
- State management

### `OptionChainAPI` Class
- Flask REST API endpoints
- Delegates to monitor instance
- Input validation and response formatting

## Configuration Details

### XML Configuration

The application reads configuration from `config.xml`. Add this section to your existing XML:

```xml
<option_monitor>
    <!-- API Server Settings -->
    <api_host>0.0.0.0</api_host>          <!-- Bind address -->
    <api_port>5000</api_port>             <!-- Server port -->
    
    <!-- Monitor Settings -->
    <auto_start>true</auto_start>          <!-- Auto-start on launch -->
    <default_strikes>15</default_strikes>  <!-- Number of strikes -->
    <max_symbols>10</max_symbols>          <!-- Max concurrent symbols -->
    
    <!-- Symbols to Monitor -->
    <symbols>
        <!-- poll_seconds: comma-separated seconds (0-59) to poll -->
        <symbol name="NSE:NIFTY50-INDEX" poll_seconds="0,30" />
        <symbol name="NSE:NIFTYBANK-INDEX" poll_seconds="0,30" />
        <symbol name="NSE:FINNIFTY-INDEX" poll_seconds="0,20,40" />
    </symbols>
</option_monitor>
```

### Environment Variables Override

You can override XML configuration with environment variables:

```bash
export API_HOST=127.0.0.1
export API_PORT=8080
export DEFAULT_STRIKES=20
export MAX_SYMBOLS=15
export AUTO_START=false
export LOG_LEVEL=DEBUG
```

### Configuration Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `api_host` | string | 0.0.0.0 | Server bind address |
| `api_port` | integer | 5000 | Server port |
| `auto_start` | boolean | true | Auto-start monitoring |
| `default_strikes` | integer | 15 | Number of strikes to fetch |
| `max_symbols` | integer | 10 | Maximum symbols allowed |

### Symbol Configuration

```xml
<symbol name="NSE:NIFTY50-INDEX" poll_seconds="0,30" />
DEFAULT_SYMBOL_CONFIG = {
    "NSE:NIFTY50-INDEX": [0, 30],      # Every 30 seconds
    "NSE:NIFTYBANK-INDEX": [0, 30],    # Every 30 seconds
}

# API settings
API_HOST = '0.0.0.0'
API_PORT = 5000
AUTO_START = True  # Auto-start monitoring
```

## API Endpoints

### 1. Start Monitoring

**Endpoint:** `POST /api/start`

**Description:** Start monitoring option chains for specified symbols.

**Request Body (all optional):**
```json
{
  "symbol_config": {
    "NSE:NIFTY50-INDEX": [0, 30],
    "NSE:NIFTYBANK-INDEX": [0]
  },
  "number_of_strikes": 15
}
```

**Example:**

```bash
# Start with default symbols
curl -X POST http://localhost:5000/api/start

# Start with custom symbols
curl -X POST http://localhost:5000/api/start \
  -H "Content-Type: application/json" \
  -d '{
    "symbol_config": {
      "NSE:NIFTY50-INDEX": [0, 30],
      "NSE:NIFTYBANK-INDEX": [0]
    },
    "number_of_strikes": 10
  }'
```

**PowerShell:**
```powershell
# Start with default symbols
Invoke-RestMethod -Uri "http://localhost:5000/api/start" -Method POST

# Start with custom symbols
$body = @{
    symbol_config = @{
        "NSE:NIFTY50-INDEX" = @(0, 30)
        "NSE:NIFTYBANK-INDEX" = @(0)
    }
    number_of_strikes = 15
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/start" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

**Response:**
```json
{
  "status": "success",
  "message": "Monitor started",
  "symbol_config": {
    "NSE:NIFTY50-INDEX": [0, 30],
    "NSE:NIFTYBANK-INDEX": [0]
  }
}
```

---

### 2. Add Symbol

**Endpoint:** `POST /api/add-symbol`

**Description:** Add a new symbol to monitoring without stopping the monitor.

**Request Body:**
```json
{
  "symbol": "NSE:NIFTY25DEC31000CE",
  "poll_seconds": [0, 30]
}
```

**Example:**

```bash
# Add a new symbol with default 30-second interval
curl -X POST http://localhost:5000/api/add-symbol \
  -H "Content-Type: application/json" \
  -d '{"symbol": "NSE:NIFTY25DEC31000CE"}'

# Add a symbol with custom 1-minute interval
curl -X POST http://localhost:5000/api/add-symbol \
  -H "Content-Type: application/json" \
  -d '{"symbol": "NSE:FINNIFTY-INDEX", "poll_seconds": [0]}'
```

**PowerShell:**
```powershell
$body = @{
    symbol = "NSE:NIFTY25DEC31000CE"
    poll_seconds = @(0, 30)
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/add-symbol" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

**Response:**
```json
{
  "status": "success",
  "message": "Symbol NSE:NIFTY25DEC31000CE added",
  "symbol_config": {
    "NSE:NIFTY50-INDEX": [0, 30],
    "NSE:NIFTYBANK-INDEX": [0, 30],
    "NSE:NIFTY25DEC31000CE": [0, 30]
  }
}
```

---

### 3. Stop Monitoring

**Endpoint:** `POST /api/stop`

**Description:** Stop the monitoring process gracefully.

**Example:**

```bash
# Stop monitoring
curl -X POST http://localhost:5000/api/stop
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/stop" -Method POST
```

---

### 4. Get Status

**Endpoint:** `GET /api/status`

**Description:** Get current monitor status and configuration.

**Example:**

```bash
# Get status
curl http://localhost:5000/api/status
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/status" -Method GET
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "running": true,
    "symbols": ["NSE:NIFTY50-INDEX", "NSE:NIFTYBANK-INDEX"],
    "symbol_config": {
      "NSE:NIFTY50-INDEX": [0, 30],
      "NSE:NIFTYBANK-INDEX": [0, 30]
    },
    "strikes": 15
  }
}
```

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "status": "error",
  "message": "Error description here"
}
```

**Common Errors:**

| HTTP Code | Error Message | Cause |
|-----------|---------------|-------|
| 400 | Monitor already running | Tried to start when already running |
| 400 | Monitor not running | Tried to stop/add-symbol when not running |
| 400 | Symbol not provided | Missing symbol in add-symbol request |
| 500 | Internal error | Server-side error (check logs) |

---

## Logs

Logs are written to:
- **File:** `option_chain_monitor_api.log` (in same directory as script)
- **Console:** Real-time output

**Log Levels:**
- `INFO` - Normal operations
- `WARNING` - Non-critical issues (no data returned)
- `ERROR` - Failures (API errors, database errors)

**Example Log Output:**
```
2025-11-19 09:30:00 - INFO - Monitor started: symbols=['NSE:NIFTY50-INDEX']
2025-11-19 09:30:00 - INFO - Polling thread started for: ['NSE:NIFTY50-INDEX']
2025-11-19 09:30:30 - INFO - ✓ NSE:NIFTY50-INDEX: 120 options
2025-11-19 09:31:00 - INFO - ✓ NSE:NIFTY50-INDEX: 120 options
```

---

## Database

Option chain data is stored in SQLite databases:
- One database per symbol
- Format: `{SYMBOL_NAME}.db` (e.g., `NIFTY50-INDEX.db`)
- Location: Same directory as script
- Tables managed by `nslogger.OptionChainManager`

---

## Windows Task Scheduler Setup

### 1. Create Batch File

Create `run_option_chain_monitor.bat`:

```batch
@echo off
cd /d D:\NSLearn\trading_api_client
call .venv\Scripts\activate.bat
python option_chain_monitor_api_simple.py
```

### 2. Schedule Task

1. Open **Task Scheduler**
2. Click **Create Task**
3. **General Tab:**
   - Name: "Option Chain Monitor"
   - Run whether user is logged on or not
   - Run with highest privileges
4. **Triggers Tab:**
   - New → At startup (or specific time)
5. **Actions Tab:**
   - Action: Start a program
   - Program: `cmd.exe`
   - Arguments: `/c "D:\NSLearn\trading_api_client\run_option_chain_monitor.bat"`
6. **Settings Tab:**
   - If task fails, restart every 1 minute

### 3. Test

Right-click task → Run

Check `option_chain_monitor_api.log` for output.

---

## Graceful Shutdown

The application handles shutdown signals properly:

- **Ctrl+C**: Stops monitoring and exits
- **SIGTERM**: Windows Task Scheduler sends this when stopping
- **API Stop**: Stops monitoring but keeps API running

All methods ensure:
- Database connections are closed
- Threads terminate cleanly
- Resources are released

---

## Troubleshooting

### Monitor won't start
- Check if already running: Look for "Monitor already running" in logs
- Check API response for specific error
- Verify authentication credentials in `config.xml`

### No data being logged
- Check logs for API errors
- Verify symbols are correct (use NSE format: `NSE:SYMBOL`)
- Ensure market hours (NSE: 9:15 AM - 3:30 PM IST)

### High CPU usage
- Reduce polling frequency (e.g., `[0, 30]` instead of `[0, 15, 30, 45]`)
- Reduce number of symbols
- Increase `number_of_strikes` to fetch less data

### Process not stopping
- Use Task Manager to end `python.exe` process
- Check logs for errors during shutdown
- Restart Windows Task Scheduler service

---

## Examples

### Complete Workflow

```bash
# 1. Start monitoring with default symbols
curl -X POST http://localhost:5000/api/start

# 2. Add more symbols dynamically
curl -X POST http://localhost:5000/api/add-symbol \
  -H "Content-Type: application/json" \
  -d '{"symbol": "NSE:FINNIFTY-INDEX", "poll_seconds": [0]}'

curl -X POST http://localhost:5000/api/add-symbol \
  -H "Content-Type: application/json" \
  -d '{"symbol": "NSE:MIDCPNIFTY-INDEX", "poll_seconds": [30]}'

# 3. Check status
curl http://localhost:5000/api/status

# 3. Let it run...
# (monitor polls every 30 seconds and logs to database)

# 4. Stop when done
curl -X POST http://localhost:5000/api/stop
```

### PowerShell Workflow

```powershell
# Start
Invoke-RestMethod -Uri "http://localhost:5000/api/start" -Method POST

# Add symbol with custom interval
$addSymbol = @{ 
    symbol = "NSE:FINNIFTY-INDEX"
    poll_seconds = @(0)  # Every minute
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5000/api/add-symbol" `
  -Method POST -ContentType "application/json" -Body $addSymbol

# Get status
Invoke-RestMethod -Uri "http://localhost:5000/api/status" -Method GET

# Stop
Invoke-RestMethod -Uri "http://localhost:5000/api/stop" -Method POST
```

---

## Support

For issues or questions:
1. Check logs in `option_chain_monitor_api.log`
2. Verify configuration in script header
3. Test API endpoints with curl/PowerShell
4. Check Windows Task Scheduler logs (if applicable)

---

## License

This project is part of the `trading_api_client` package.
