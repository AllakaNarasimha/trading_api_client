# Option Chain Monitor - REST API

A real-time option chain monitoring application with REST API control. Monitors NSE option chain data and provides multiple streaming and polling mechanisms for fetching live market data.

## Overview

The Option Chain Monitor is a Flask-based REST API server that:
- **Monitors** live option chain data from NSE (National Stock Exchange)
- **Polls** option chain data at configurable intervals per symbol
- **Streams** real-time data to connected watchers
- **Provides** HTTP REST endpoints for monitoring control
- **Logs** all activity to rotating log files
- **Schedules** automatic shutdown at a specified time (optional)

## Architecture

The application is organized into modular components:

```
option_chain_monitor_api_simple.py   # Entry point
├── client/
│   ├── utils/
│   │   ├── config.py                # Configuration management
│   │   ├── monitor.py               # Monitoring core logic
│   │   ├── api.py                   # Flask REST API
│   │   ├── cutoff_timer.py          # Scheduled shutdown
│   │   └── __init__.py              # Package exports
│   ├── auth.py                      # Broker authentication
│   ├── orders.py                    # Order management
│   ├── portfolio.py                 # Portfolio management
│   ├── watchlist.py                 # Real-time data streaming
│   └── __init__.py
├── config.xml                       # Application configuration
└── nslogger/                        # SQLite logging package
```

## Installation

### Prerequisites
- Python 3.11+
- Windows/Linux/macOS
- pip (Python package installer)

### Option 1: Direct Installation from Requirements

1. **Clone or extract the project**
   ```bash
   cd d:\NSLearn\trading_api_client
   ```

2. **Create virtual environment** (if not already created)
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**
   - **Windows (PowerShell):**
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - **Windows (CMD):**
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - **Linux/macOS:**
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure the application**
   - Edit `config.xml` with your broker credentials and settings
   - Configure symbols, polling intervals, and API settings

### Option 2: Build & Install as Package

Build and install the project as a Python package:

#### Prerequisites for Building
```bash
# Install build and twine tools (one-time setup)
pip install build twine
```

#### Build Distribution Packages

```bash
# Navigate to project directory
cd d:\NSLearn\trading_api_client

# Clean previous builds
python -m pip install --upgrade build
rm -r dist build *.egg-info  # Linux/macOS
# or for Windows: rmdir /s dist build *.egg-info

# Build both wheel and source distribution
python -m build
```

This creates:
- **Wheel distribution:** `dist/trading_api_monitor-1.0.0-py3-none-any.whl` (recommended)
- **Source distribution:** `dist/trading-api-monitor-1.0.0.tar.gz`

#### Install the Built Package

```bash
# Install from wheel (fastest)
pip install dist/trading_api_monitor-1.0.0-py3-none-any.whl

# Or install from source distribution
pip install dist/trading-api-monitor-1.0.0.tar.gz

# Or install in development mode (editable)
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

#### Verify Installation

```bash
# Check if package is installed
pip show trading-api-monitor

# Test the CLI command
option-chain-monitor --help

# Or run directly
python -m app
```

#### Create Distribution for Deployment

After building, the `dist/` folder contains:
- **Wheel file** (recommended for deployment) - smaller, faster to install
- **Source tarball** - includes source code, can be built on target system

To distribute:
```bash
# Copy wheel file to deployment system
cp dist/trading_api_monitor-1.0.0-py3-none-any.whl /deployment/path/

# On target system, install from wheel
pip install /deployment/path/trading_api_monitor-1.0.0-py3-none-any.whl
```

### Option 3: Docker Installation (Optional)

For containerized deployment, create a `Dockerfile`:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Copy project files
COPY . /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose API port
EXPOSE 5000

# Run the application
CMD ["python", "option_chain_monitor_api_simple.py"]
```

Build and run:
```bash
# Build Docker image
docker build -t trading-api-monitor:1.0.0 .

# Run container
docker run -p 5000:5000 -v $(pwd)/config.xml:/app/config.xml trading-api-monitor:1.0.0
```

### Verify Installation

After installation, verify everything is working:

```bash
# Test imports
python -c "import client; print('Client package OK')"
python -c "from client.utils import config, monitor, api; print('All modules OK')"

# Check version
pip show trading-api-monitor

# Run health check
curl http://localhost:5000/api/health  # After starting the application
```

## Configuration

### config.xml Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<root>
    <option_monitor>
        <api>
            <host>localhost</host>
            <port>5000</port>
            <auto_start>false</auto_start>
        </api>
        
        <symbols>
            <symbol>
                <name>NSE:NIFTY50-INDEX</name>
                <poll_seconds>5</poll_seconds>
                <strikes>10</strikes>
            </symbol>
            <symbol>
                <name>NSE:NIFTYBANK-INDEX</name>
                <poll_seconds>10</poll_seconds>
                <strikes>5</strikes>
            </symbol>
        </symbols>
        
        <cutoff_enabled>false</cutoff_enabled>
        <cutoff_hour>15</cutoff_hour>
        <cutoff_minute>30</cutoff_minute>
    </option_monitor>
    
    <settings>
        <log_level>INFO</log_level>
    </settings>
    
    <dhan>
        <client_id>YOUR_CLIENT_ID</client_id>
        <access_token>YOUR_ACCESS_TOKEN</access_token>
    </dhan>
    
    <fyers>
        <app_id>YOUR_APP_ID</app_id>
        <app_secret>YOUR_APP_SECRET</app_secret>
        <access_token>YOUR_ACCESS_TOKEN</access_token>
    </fyers>
</root>
```

### Configuration Options

| Option | Type | Description | Example |
|--------|------|-------------|---------|
| `api.host` | string | API server host | `localhost` |
| `api.port` | integer | API server port | `5000` |
| `api.auto_start` | boolean | Auto-start monitoring on startup | `false` |
| `symbols[].name` | string | Symbol name (broker-specific format) | `NSE:NIFTY50-INDEX` |
| `symbols[].poll_seconds` | integer | Polling interval in seconds | `5` |
| `symbols[].strikes` | integer | Number of strike prices to fetch | `10` |
| `cutoff_enabled` | boolean | Enable automatic shutdown timer | `true` |
| `cutoff_hour` | integer | Shutdown hour (24h format) | `15` |
| `cutoff_minute` | integer | Shutdown minute | `30` |
| `log_level` | string | Logging level | `INFO`, `DEBUG`, `WARNING` |

### Environment Variable Overrides

Any configuration value can be overridden via environment variables using the format:
```
OPTION_CHAIN_{SECTION}_{KEY}=value
```

Examples:
```bash
# Set API port
set OPTION_CHAIN_API_PORT=8000

# Set auto-start
set OPTION_CHAIN_API_AUTO_START=true

# Enable cutoff timer
set OPTION_CHAIN_CUTOFF_ENABLED=true
```

## Running the Application

### Option 1: Direct Python Execution

```bash
# Activate virtual environment first
.venv\Scripts\activate.bat  # Windows
# or
source .venv/bin/activate   # Linux/macOS

# Run the application
python option_chain_monitor_api_simple.py
```

### Option 2: Using Installed CLI Command

After installing as a package using Option 2 above:

```bash
# Simple command (if entry point is configured)
option-chain-monitor

# Or via module
python -m app
```

### Option 3: Using app.py Directly

```bash
# With virtual environment activated
python app.py
```

Expected output:
```
2025-11-22 14:30:45,123 - INFO - ============================================================
2025-11-22 14:30:45,124 - INFO - Option Chain Monitor API - Starting
2025-11-22 14:30:45,124 - INFO - ============================================================
2025-11-22 14:30:45,125 - INFO - Log file: logs/option_chain_monitor.log
2025-11-22 14:30:45,126 - INFO - API Host: localhost:5000
2025-11-22 14:30:45,127 - INFO - Max symbols: 20
2025-11-22 14:30:45,128 - INFO - Default strikes: 10
2025-11-22 14:30:45,129 - INFO - Default symbol config:
2025-11-22 14:30:45,130 - INFO -   NSE:NIFTY50-INDEX: poll at seconds 5, strikes: 10
2025-11-22 14:30:45,131 - INFO -   NSE:NIFTYBANK-INDEX: poll at seconds 10, strikes: 5
2025-11-22 14:30:45,132 - INFO - Auto-start enabled: False
2025-11-22 14:30:45,133 - INFO - Cutoff timer enabled: False
2025-11-22 14:30:45,134 - INFO - ============================================================
2025-11-22 14:30:45,135 - INFO - API endpoints available:
2025-11-22 14:30:45,136 - INFO -   GET  http://localhost:5000/api/health
2025-11-22 14:30:45,137 - INFO -   GET  http://localhost:5000/api/status
2025-11-22 14:30:45,138 - INFO -   POST http://localhost:5000/api/start
2025-11-22 14:30:45,139 - INFO -   POST http://localhost:5000/api/add-symbol
2025-11-22 14:30:45,140 - INFO -   POST http://localhost:5000/api/stop
2025-11-22 14:30:45,141 - INFO - ============================================================
2025-11-22 14:30:45,142 - INFO -  * Running on http://localhost:5000
```

### For Windows Task Scheduler

Use the provided batch file and VBScript wrapper:

```batch
# Run with visible console
run_api.bat

# Run hidden (no console window)
cscript run_hidden.vbs
```

## Build & Deployment Guide

### Development Build

For development with live code changes (editable install):

```bash
# One-time setup
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with code coverage
pytest --cov=client --cov-report=html tests/

# Code formatting with Black
black client/ app.py

# Code quality check
flake8 client/ app.py

# Type checking with mypy
mypy client/
```

### Production Build

For production deployment:

```bash
# 1. Clean previous builds
python -m pip install --upgrade build twine
rm -r dist build *.egg-info

# 2. Build distribution packages
python -m build

# 3. Verify builds (optional but recommended)
twine check dist/*

# 4. List contents of wheel
unzip -l dist/trading_api_monitor-1.0.0-py3-none-any.whl

# 5. For PyPI publication (if desired)
# twine upload dist/*
```

### Package Contents

The built package includes:

```
trading_api_monitor/
├── client/
│   ├── auth.py
│   ├── orders.py
│   ├── portfolio.py
│   ├── watchlist.py
│   ├── utils/
│   │   ├── config.py
│   │   ├── monitor.py
│   │   ├── api.py
│   │   ├── cutoff_timer.py
│   │   └── __init__.py
│   ├── libs/
│   │   ├── nslogger-1.0.0.tar.gz
│   │   └── trading_api-1.0.0.tar.gz
│   └── __init__.py
├── doc/
├── market_data/
├── config.xml
├── requirements.txt
└── README_OPTION_CHAIN_MONITOR.md
```

### Configuration Files

Key build configuration files:

- **`pyproject.toml`** - Modern Python packaging (PEP 517/518)
  - Build system configuration
  - Project metadata
  - Tool configurations (pytest, black, mypy)
  - Optional dependencies

- **`setup.py`** - Backward compatible setup script
  - Package discovery
  - Entry points configuration
  - Metadata fallback

- **`MANIFEST.in`** - Package data inclusion
  - Additional files to include in distribution
  - Configuration files (config.xml, requirements.txt)
  - Documentation files
  - Market data files

- **`requirements.txt`** - Runtime dependencies
  - External packages (Flask, requests, fyers-apiv3, dhanhq)
  - Custom libraries (trading-api, nslogger)

## REST API Reference

### Base URL
```
http://localhost:5000
```

### 1. Health Check

**Endpoint:** `GET /api/health`

**Description:** Check if the server is running and responsive.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-22T14:35:12.345678"
}
```

**Example:**
```bash
curl -X GET http://localhost:5000/api/health
```

---

### 2. Get Status

**Endpoint:** `GET /api/status`

**Description:** Get current monitoring status and configuration.

**Response:**
```json
{
  "monitor_running": true,
  "symbols": {
    "NSE:NIFTY50-INDEX": {
      "poll_seconds": 5,
      "strikes": 10,
      "active": true
    },
    "NSE:NIFTYBANK-INDEX": {
      "poll_seconds": 10,
      "strikes": 5,
      "active": true
    }
  },
  "config": {
    "api_host": "localhost",
    "api_port": 5000,
    "max_symbols": 20,
    "default_strikes": 10,
    "cutoff_enabled": false,
    "cutoff_time": "15:30"
  }
}
```

**Example:**
```bash
curl -X GET http://localhost:5000/api/status
```

---

### 3. Start Monitoring

**Endpoint:** `POST /api/start`

**Description:** Start option chain monitoring with optional configuration.

**Request Body (Optional):**
```json
{
  "symbols": {
    "NSE:NIFTY50-INDEX": {
      "poll_seconds": 5,
      "strikes": 10
    },
    "NSE:FINNIFTY-INDEX": {
      "poll_seconds": 8,
      "strikes": 8
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Monitoring started successfully",
  "symbols_monitoring": ["NSE:NIFTY50-INDEX", "NSE:FINNIFTY-INDEX"]
}
```

**Example (with default config):**
```bash
curl -X POST http://localhost:5000/api/start
```

**Example (with custom config):**
```bash
curl -X POST http://localhost:5000/api/start \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": {
      "NSE:NIFTY50-INDEX": {
        "poll_seconds": 5,
        "strikes": 10
      },
      "NSE:FINNIFTY-INDEX": {
        "poll_seconds": 8,
        "strikes": 8
      }
    }
  }'
```

---

### 4. Add Symbol While Running

**Endpoint:** `POST /api/add-symbol`

**Description:** Add a new symbol to monitor while monitoring is already running.

**Request Body:**
```json
{
  "symbol": "NSE:FINNIFTY-INDEX",
  "poll_seconds": 8,
  "strikes": 8
}
```

**Response:**
```json
{
  "success": true,
  "message": "Symbol 'NSE:FINNIFTY-INDEX' added successfully",
  "symbol": "NSE:FINNIFTY-INDEX"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/add-symbol \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "NSE:FINNIFTY-INDEX",
    "poll_seconds": 8,
    "strikes": 8
  }'
```

---

### 5. Stop Monitoring

**Endpoint:** `POST /api/stop`

**Description:** Stop all option chain monitoring and cleanup resources.

**Response:**
```json
{
  "success": true,
  "message": "Monitoring stopped successfully"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/stop
```

---

## API Consumption Examples

### Python - Using requests

```python
import requests
import json
from time import sleep

BASE_URL = "http://localhost:5000"

class OptionChainClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
    
    def health_check(self):
        """Check if server is running."""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Health check failed: {e}")
            return None
    
    def get_status(self):
        """Get current monitoring status."""
        try:
            response = requests.get(f"{self.base_url}/api/status", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Get status failed: {e}")
            return None
    
    def start_monitoring(self, symbols_config=None):
        """Start monitoring with optional custom config."""
        try:
            headers = {"Content-Type": "application/json"}
            payload = {}
            if symbols_config:
                payload["symbols"] = symbols_config
            
            response = requests.post(
                f"{self.base_url}/api/start",
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Start monitoring failed: {e}")
            return None
    
    def add_symbol(self, symbol, poll_seconds=5, strikes=10):
        """Add a symbol while monitoring is running."""
        try:
            headers = {"Content-Type": "application/json"}
            payload = {
                "symbol": symbol,
                "poll_seconds": poll_seconds,
                "strikes": strikes
            }
            
            response = requests.post(
                f"{self.base_url}/api/add-symbol",
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Add symbol failed: {e}")
            return None
    
    def stop_monitoring(self):
        """Stop all monitoring."""
        try:
            response = requests.post(f"{self.base_url}/api/stop", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Stop monitoring failed: {e}")
            return None


# Usage Example
if __name__ == "__main__":
    client = OptionChainClient()
    
    # 1. Check health
    print("=== Health Check ===")
    health = client.health_check()
    print(json.dumps(health, indent=2))
    print()
    
    # 2. Start monitoring with default config
    print("=== Start Monitoring ===")
    result = client.start_monitoring()
    print(json.dumps(result, indent=2))
    print()
    
    # 3. Get status
    print("=== Get Status ===")
    status = client.get_status()
    print(json.dumps(status, indent=2))
    print()
    
    # 4. Add a new symbol
    print("=== Add Symbol ===")
    add_result = client.add_symbol("NSE:FINNIFTY-INDEX", poll_seconds=8, strikes=8)
    print(json.dumps(add_result, indent=2))
    sleep(2)
    print()
    
    # 5. Check status again
    print("=== Get Status (After Adding Symbol) ===")
    status = client.get_status()
    print(json.dumps(status, indent=2))
    print()
    
    # 6. Stop monitoring
    print("=== Stop Monitoring ===")
    stop_result = client.stop_monitoring()
    print(json.dumps(stop_result, indent=2))
```

### JavaScript/Node.js - Using fetch

```javascript
const BASE_URL = "http://localhost:5000";

class OptionChainClient {
    constructor(baseUrl = BASE_URL) {
        this.baseUrl = baseUrl;
    }

    async healthCheck() {
        try {
            const response = await fetch(`${this.baseUrl}/api/health`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Health check failed:', error);
            return null;
        }
    }

    async getStatus() {
        try {
            const response = await fetch(`${this.baseUrl}/api/status`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Get status failed:', error);
            return null;
        }
    }

    async startMonitoring(symbolsConfig = null) {
        try {
            const payload = symbolsConfig ? { symbols: symbolsConfig } : {};
            
            const response = await fetch(`${this.baseUrl}/api/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Start monitoring failed:', error);
            return null;
        }
    }

    async addSymbol(symbol, pollSeconds = 5, strikes = 10) {
        try {
            const payload = {
                symbol,
                poll_seconds: pollSeconds,
                strikes
            };

            const response = await fetch(`${this.baseUrl}/api/add-symbol`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Add symbol failed:', error);
            return null;
        }
    }

    async stopMonitoring() {
        try {
            const response = await fetch(`${this.baseUrl}/api/stop`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Stop monitoring failed:', error);
            return null;
        }
    }
}

// Usage Example
(async () => {
    const client = new OptionChainClient();

    // 1. Check health
    console.log("=== Health Check ===");
    const health = await client.healthCheck();
    console.log(JSON.stringify(health, null, 2));
    console.log();

    // 2. Start monitoring
    console.log("=== Start Monitoring ===");
    const result = await client.startMonitoring();
    console.log(JSON.stringify(result, null, 2));
    console.log();

    // 3. Get status
    console.log("=== Get Status ===");
    const status = await client.getStatus();
    console.log(JSON.stringify(status, null, 2));
    console.log();

    // 4. Add a new symbol
    console.log("=== Add Symbol ===");
    const addResult = await client.addSymbol("NSE:FINNIFTY-INDEX", 8, 8);
    console.log(JSON.stringify(addResult, null, 2));
    await new Promise(resolve => setTimeout(resolve, 2000));
    console.log();

    // 5. Check status again
    console.log("=== Get Status (After Adding Symbol) ===");
    const newStatus = await client.getStatus();
    console.log(JSON.stringify(newStatus, null, 2));
    console.log();

    // 6. Stop monitoring
    console.log("=== Stop Monitoring ===");
    const stopResult = await client.stopMonitoring();
    console.log(JSON.stringify(stopResult, null, 2));
})();
```

### cURL Examples

```bash
# 1. Health check
curl -X GET http://localhost:5000/api/health

# 2. Get status
curl -X GET http://localhost:5000/api/status

# 3. Start monitoring (default config)
curl -X POST http://localhost:5000/api/start

# 4. Start monitoring (custom config)
curl -X POST http://localhost:5000/api/start \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": {
      "NSE:NIFTY50-INDEX": {"poll_seconds": 5, "strikes": 10},
      "NSE:FINNIFTY-INDEX": {"poll_seconds": 8, "strikes": 8}
    }
  }'

# 5. Add symbol while running
curl -X POST http://localhost:5000/api/add-symbol \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "NSE:FINNIFTY-INDEX",
    "poll_seconds": 8,
    "strikes": 8
  }'

# 6. Stop monitoring
curl -X POST http://localhost:5000/api/stop
```

### PowerShell Examples

```powershell
# 1. Health check
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -Method Get
$response.Content | ConvertFrom-Json

# 2. Get status
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/status" -Method Get
$response.Content | ConvertFrom-Json

# 3. Start monitoring
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/start" -Method Post -ContentType "application/json" -Body '{}'
$response.Content | ConvertFrom-Json

# 4. Add symbol
$body = @{
    symbol = "NSE:FINNIFTY-INDEX"
    poll_seconds = 8
    strikes = 8
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:5000/api/add-symbol" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
$response.Content | ConvertFrom-Json

# 5. Stop monitoring
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/stop" -Method Post
$response.Content | ConvertFrom-Json
```

## Logging

Logs are stored in rotating files:

**Location:** `logs/option_chain_monitor.log`

**Configuration:**
- **Max file size:** 10 MB
- **Backup files:** 5 backups retained
- **Format:** `%(asctime)s - %(levelname)s - %(message)s`
- **Level:** Configurable via `config.xml` (INFO, DEBUG, WARNING, ERROR)

**Example log output:**
```
2025-11-22 14:35:15,234 - INFO - Symbol NSE:NIFTY50-INDEX added successfully
2025-11-22 14:35:15,235 - INFO - Starting polling for NSE:NIFTY50-INDEX (poll every 5s)
2025-11-22 14:35:20,456 - INFO - [OK] Fetched 10 strikes for NSE:NIFTY50-INDEX
2025-11-22 14:35:25,678 - INFO - [OK] Fetched 10 strikes for NSE:NIFTY50-INDEX
2025-11-22 14:35:30,789 - ERROR - Failed to fetch data for NSE:NIFTY50-INDEX: Connection timeout
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process (Windows)
taskkill /PID <PID> /F

# Or change port in config.xml
<port>8000</port>
```

### SSL Certificate Errors

The application automatically handles SSL verification issues for certain APIs. If you encounter SSL errors:

1. Check your internet connection
2. Verify firewall settings
3. Ensure broker API endpoints are accessible

### Import Errors

```bash
# Verify all dependencies are installed
pip install -r requirements.txt

# Check Python path includes the project directory
python -c "import sys; print(sys.path)"
```

### Monitoring Not Starting

Check the logs:
```bash
# View recent logs
tail -f logs/option_chain_monitor.log

# On Windows PowerShell
Get-Content logs/option_chain_monitor.log -Tail 50 -Wait
```

Common issues:
- Invalid broker credentials in `config.xml`
- Unsupported symbol format
- Market not in trading hours

## Performance Considerations

- **Symbol limit:** Default 20 symbols (configurable)
- **Minimum poll interval:** 1 second (configurable per symbol)
- **Memory:** ~50-100 MB baseline + ~5 MB per active symbol
- **CPU:** Minimal impact, mostly idle waiting

## Security Notes

⚠️ **Important:**
- Never commit `config.xml` with real credentials to version control
- Use environment variables for sensitive data in production
- Change default API port if deploying on shared systems
- Restrict API access using firewall rules
- Use HTTPS reverse proxy for remote deployments

## Features

✅ **Core Features:**
- Real-time option chain monitoring
- Configurable polling intervals per symbol
- Multiple symbol support (up to 20 by default)
- Broker integration (Dhan, Fyers)
- Rest API for control and monitoring
- Automatic shutdown scheduling
- Rotating log files with configurable level

🔧 **Technical Features:**
- Thread-safe operation with locks
- Graceful signal handling (SIGINT, SIGTERM)
- Configuration from XML with env var overrides
- Modular architecture with separate utils package
- Comprehensive error handling and logging

## License

[Your License Here]

## Support

For issues or questions:
1. Check logs in `logs/option_chain_monitor.log`
2. Review configuration in `config.xml`
3. Verify broker credentials and API access
4. Check that symbols are in correct format for your broker

## Changelog

### Version 1.0.0 (2025-11-22)
- Initial release
- Modular architecture refactoring
- CutoffTimer for scheduled shutdown
- Comprehensive REST API
- Full documentation and examples
