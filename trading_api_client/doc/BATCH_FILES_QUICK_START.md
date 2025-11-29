# Batch File Setup - Quick Reference

## Four Batch Files Created

### 1. **install_and_run.bat** (4.9 KB) - RECOMMENDED
Installs tar.gz + starts monitor immediately
```batch
install_and_run.bat
```
**Does:**
- Checks tar.gz exists
- Creates installation directory
- Installs from tar.gz
- Verifies installation
- Copies config.xml
- **Starts the application**

**Installation location:** `install_monitor/`

---

### 2. **install_and_run_cli.bat** (2.4 KB)
Alternative using CLI entry point
```batch
install_and_run_cli.bat
```
**Does:** Same as above but uses `option-chain-monitor` CLI command

**Installation location:** `install_monitor_cli/`

---

### 3. **run_monitor.bat** (1.8 KB)
Run from existing installation (no re-install)
```batch
run_monitor.bat
```
**Use after:** First run of install_and_run.bat

**Advantages:**
- Fast startup (no installation)
- Updates config.xml if needed
- No need to re-extract/install

---

### 4. **run_monitor_hidden.bat** (1.0 KB)
Background execution without console window
```batch
run_monitor_hidden.bat
```
**Best for:**
- Windows Task Scheduler
- Running as background service
- No console window display

**Log location:** `install_monitor/logs/monitor.log`

---

## Quick Start

### Step 1: Build the Distribution (One-time)
```batch
python -m build
```
This creates: `dist/trading-api-monitor-1.0.0.tar.gz`

### Step 2: Install & Run
```batch
install_and_run.bat
```
This will:
- Install to `install_monitor/`
- Start the Option Chain Monitor
- Display API running on `http://localhost:5000`

### Step 3: Subsequent Runs
```batch
run_monitor.bat
```
Much faster - no reinstallation needed

---

## Installation Structure

After running `install_and_run.bat`:

```
trading_api_client/
├── install_monitor/          ← Created by batch file
│   ├── .venv/               ← Python virtual environment
│   │   └── Scripts/
│   │       └── python.exe   ← Python executable
│   ├── Lib/site-packages/
│   │   └── client/          ← Installed package from tar.gz
│   ├── config.xml           ← Copied from project root
│   └── logs/
│       └── option_chain_monitor.log
└── dist/
    └── trading-api-monitor-1.0.0.tar.gz  ← Source distribution
```

---

## Main Method Execution

### The Batch Files Execute:

```python
# install_and_run.bat runs:
python -m app

# Which imports and runs:
if __name__ == "__main__":
    main()  # Option Chain Monitor main method
```

### What Gets Started:

1. **Configuration Loading** - Reads config.xml
2. **Logger Initialization** - Sets up rotating file handler
3. **Global Instances** - Creates Config, Monitor, API
4. **Signal Handlers** - Graceful shutdown on SIGINT/SIGTERM
5. **Optional CutoffTimer** - Auto shutdown at specified time
6. **Flask API Server** - Starts REST API on port 5000
7. **Optional Auto-Start** - Begins monitoring if enabled

### API Endpoints Available:

```
✓ GET  http://localhost:5000/api/health
✓ GET  http://localhost:5000/api/status
✓ POST http://localhost:5000/api/start
✓ POST http://localhost:5000/api/add-symbol
✓ POST http://localhost:5000/api/stop
```

---

## Key Features

✅ **Fully Isolated** - Virtual environment in `install_monitor/`
✅ **No System Python Required** - Uses bundled Python
✅ **Configuration Support** - Copies config.xml automatically
✅ **Error Checking** - Validates each step
✅ **Logging** - Creates install_monitor.log and option_chain_monitor.log
✅ **Easy Management** - run_monitor.bat for quick restarts

---

## Troubleshooting

### tar.gz Not Found?
```batch
python -m build
install_and_run.bat
```

### Installation Failed?
```batch
REM Check the log
type install_monitor.log

REM Clean and retry
rmdir /s /q install_monitor
install_and_run.bat
```

### Application Won't Start?
```batch
REM Verify installation
install_monitor\.venv\Scripts\pip.exe show trading-api-monitor

REM Test imports
install_monitor\.venv\Scripts\python.exe -c "import client; print('OK')"

REM Check config.xml exists
dir install_monitor\config.xml
```

### Port Already in Use?
```batch
REM Edit config.xml to use different port
set OPTION_CHAIN_API_PORT=8000
install_and_run.bat
```

---

## Environment Variables (Optional)

Override configuration with environment variables before running:

```batch
set OPTION_CHAIN_API_PORT=8000
set OPTION_CHAIN_API_AUTO_START=true
set OPTION_CHAIN_CUTOFF_ENABLED=true
install_and_run.bat
```

---

## For Windows Task Scheduler

Create scheduled task to run at startup:

1. **Program:** `cmd.exe`
2. **Arguments:** `/c "D:\NSLearn\trading_api_client\install_and_run.bat"`
3. **Start in:** `D:\NSLearn\trading_api_client`
4. **Run with highest privileges:** `No`

Or use the hidden variant:

1. **Program:** `cmd.exe`
2. **Arguments:** `/c "D:\NSLearn\trading_api_client\run_monitor_hidden.bat"`
3. **Redirect output:** `install_monitor/logs/monitor.log`

---

## Complete Workflow

### Initial Setup
```
python -m build                    # Generate tar.gz (one-time)
install_and_run.bat               # Install & start (one-time)
```

### Daily Operations
```
run_monitor.bat                    # Quick start
```

### Scheduled (Automated)
```
Task Scheduler → install_and_run.bat or run_monitor_hidden.bat
```

---

## Files Reference

| File | Purpose | Size |
|------|---------|------|
| install_and_run.bat | Full setup + run | 4.9 KB |
| install_and_run_cli.bat | Alt setup using CLI | 2.4 KB |
| run_monitor.bat | Run existing install | 1.8 KB |
| run_monitor_hidden.bat | Background/Task Sched | 1.0 KB |

See `doc/BATCH_SETUP_GUIDE.md` for complete documentation.

