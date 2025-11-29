# Consuming tar.gz via Batch Files - Complete Guide

## Overview

Four batch files are provided to install and run the trading-api-monitor from the tar.gz distribution package:

1. **install_and_run.bat** - Full installation + immediate startup (RECOMMENDED)
2. **install_and_run_cli.bat** - Installation via CLI entry point + startup
3. **run_monitor.bat** - Run from existing installation
4. **run_monitor_hidden.bat** - Run hidden in background (Task Scheduler)

---

## Quick Start

### Method 1: Install & Run (Simplest)

```batch
install_and_run.bat
```

This single command will:
- ✓ Check tar.gz exists in `dist/` folder
- ✓ Create installation directory (`install_monitor/`)
- ✓ Create virtual environment
- ✓ Install from tar.gz file
- ✓ Verify installation
- ✓ Copy config.xml
- ✓ Start the Option Chain Monitor

**Output:**
```
=====================================================================
Trading API Monitor - Installation and Startup
=====================================================================

[STEP 1] Checking for distribution file...
✓ Found: d:\...\dist\trading-api-monitor-1.0.0.tar.gz

[STEP 2] Creating installation directory...
✓ Created: d:\...\install_monitor

[STEP 3] Creating virtual environment...
✓ Created virtual environment

[STEP 4] Upgrading pip...
✓ Upgraded pip

[STEP 5] Installing trading-api-monitor from tar.gz...
✓ Successfully installed from tar.gz

[STEP 6] Verifying installation...
✓ Modules verified successfully

[STEP 7] Copying configuration file...
✓ Copied config.xml

[STEP 8] Starting Option Chain Monitor...

=====================================================================
STARTING APPLICATION
=====================================================================

2025-11-22 14:30:45,123 - INFO - Option Chain Monitor API - Starting
2025-11-22 14:30:45,125 - INFO - Log file: logs/option_chain_monitor.log
2025-11-22 14:30:45,126 - INFO - API Host: localhost:5000
2025-11-22 14:30:45,142 - INFO - * Running on http://localhost:5000
```

---

## Batch File Details

### 1. install_and_run.bat

**Best for:** First-time installation and running

**What it does:**
1. Verifies tar.gz file exists in `dist/` directory
2. Creates `install_monitor/` directory
3. Creates virtual environment (`.venv`)
4. Upgrades pip, setuptools, wheel
5. Installs trading-api-monitor from tar.gz
6. Verifies all modules import correctly
7. Copies `config.xml` from project root
8. Starts the application with `python -m app`

**Installation structure created:**
```
install_monitor/
├── .venv/                    (isolated Python environment)
│   ├── Scripts/
│   │   ├── python.exe
│   │   ├── pip.exe
│   │   └── option-chain-monitor.exe
│   └── Lib/site-packages/
│       ├── client/           (installed package)
│       ├── Flask/
│       └── ...
└── config.xml               (copied from project root)
```

**Usage:**
```batch
cd d:\NSLearn\trading_api_client
install_and_run.bat
```

**Log output:** `install_monitor.log`

---

### 2. install_and_run_cli.bat

**Best for:** Using the CLI entry point (`option-chain-monitor` command)

**What it does:**
- Same as method 1 but uses CLI entry point if available
- Falls back to module execution if CLI not available
- More streamlined script

**Usage:**
```batch
install_and_run_cli.bat
```

**Log output:** `install_monitor_cli.log`

---

### 3. run_monitor.bat

**Best for:** Running after already installed

**What it does:**
1. Checks if installation already exists
2. Copies config.xml if missing
3. Starts the application from existing installation
4. Much faster (no re-installation)

**Prerequisites:** Must have run `install_and_run.bat` first

**Usage:**
```batch
REM First time (one-time setup)
install_and_run.bat

REM Subsequent runs
run_monitor.bat
```

---

### 4. run_monitor_hidden.bat

**Best for:** Windows Task Scheduler or background execution

**What it does:**
1. Uses `pythonw.exe` (no console window)
2. Redirects output to log file
3. Runs in background mode

**Log output:** `install_monitor/logs/monitor.log`

**Usage in Task Scheduler:**
```
Program: cmd.exe
Arguments: /c "d:\NSLearn\trading_api_client\run_monitor_hidden.bat"
Start in: d:\NSLearn\trading_api_client
```

---

## Installation Paths

### First-Time Installation

```batch
1. cd d:\NSLearn\trading_api_client
2. install_and_run.bat
   ↓
   Installation: install_monitor/
   Starts monitoring automatically
```

### Subsequent Runs

```batch
1. run_monitor.bat
   ↓
   Uses existing install_monitor/
   Fast startup (no re-installation)
```

### Background Execution (Task Scheduler)

```batch
1. Task Scheduler → Create Task
2. Program: cmd.exe
3. Arguments: /c "install_and_run.bat"  (first time)
   or        /c "run_monitor_hidden.bat" (subsequent)
4. Start in: d:\NSLearn\trading_api_client
5. Run user: System or specific user
6. Run with highest privileges: No
```

---

## Prerequisites

### Before Running

Ensure these are in place:

1. **tar.gz file exists:**
   ```
   d:\NSLearn\trading_api_client\dist\trading-api-monitor-1.0.0.tar.gz
   ```
   
   If missing, generate it:
   ```batch
   python -m build
   ```

2. **Python 3.11+ installed:**
   ```batch
   python --version
   ```

3. **config.xml exists** (optional, will use defaults if missing):
   ```
   d:\NSLearn\trading_api_client\config.xml
   ```

---

## Configuration

### Using config.xml

Place your configuration file before running:

```batch
1. Edit config.xml with your broker credentials
2. Place in: d:\NSLearn\trading_api_client\config.xml
3. Run: install_and_run.bat
4. Script automatically copies config.xml to install_monitor/
```

### Using Environment Variables

Override config.xml settings:

```batch
set OPTION_CHAIN_API_PORT=8000
set OPTION_CHAIN_API_AUTO_START=true
install_and_run.bat
```

---

## Troubleshooting

### Error: tar.gz file not found

**Problem:**
```
ERROR: tar.gz file not found!
Expected location: D:\...\dist\trading-api-monitor-1.0.0.tar.gz
```

**Solution:**
```batch
REM Build distribution packages
python -m build

REM Then try again
install_and_run.bat
```

---

### Error: Failed to create virtual environment

**Problem:**
```
ERROR: Failed to create virtual environment
```

**Solution:**
```batch
REM Ensure Python is in PATH
python --version

REM Try again, or manually create venv
python -m venv install_monitor\.venv
```

---

### Error: Installation failed

**Problem:**
```
ERROR: Failed to install from tar.gz
Check log file: install_monitor.log
```

**Solution:**
```batch
REM Check the log file
type install_monitor.log

REM Delete installation and retry
rmdir /s /q install_monitor
install_and_run.bat
```

---

### Application won't start

**Problem:**
```
ERROR: [Error] Config file not found: config.xml
```

**Solution:**
```batch
REM Copy config.xml to installation directory
copy config.xml install_monitor\config.xml

REM Or use run_monitor.bat which copies it automatically
run_monitor.bat
```

---

## Verification

### Test Installation

After running `install_and_run.bat`, check:

```batch
REM 1. Check if installation directory exists
dir install_monitor\

REM 2. Check if virtual environment created
dir install_monitor\.venv\Scripts\

REM 3. Check if package installed
install_monitor\.venv\Scripts\pip.exe show trading-api-monitor

REM 4. Test imports
install_monitor\.venv\Scripts\python.exe -c "import client; print('OK')"

REM 5. Check if CLI command exists
dir install_monitor\.venv\Scripts\option-chain-monitor.exe
```

---

## File Organization

### Before Installation
```
trading_api_client/
├── dist/
│   ├── trading-api-monitor-1.0.0.tar.gz       ← Your distribution
│   └── trading_api_monitor-1.0.0-py3-none-any.whl
├── config.xml
├── install_and_run.bat                        ← Run this first
├── install_and_run_cli.bat
├── run_monitor.bat                            ← Run this later
└── run_monitor_hidden.bat
```

### After Running install_and_run.bat
```
trading_api_client/
├── dist/
├── install_monitor/                           ← NEW
│   ├── .venv/                                ← Virtual environment
│   │   ├── Scripts/
│   │   │   ├── python.exe
│   │   │   ├── option-chain-monitor.exe
│   │   │   └── ...
│   │   └── Lib/site-packages/
│   │       └── client/                       ← Installed package
│   ├── config.xml                            ← Copied
│   └── logs/
│       └── option_chain_monitor.log
├── config.xml
└── install_and_run.bat
```

---

## Advanced Usage

### Custom Installation Directory

Modify the batch file to use a custom installation path:

```batch
REM Edit install_and_run.bat
set INSTALL_DIR=C:\Apps\trading-monitor   ← Change this
```

### Multiple Installations

Run separate installations:

```batch
REM First installation
install_and_run.bat                    → install_monitor\

REM Second installation (edit batch to use different dir)
REM Then run again                     → install_monitor_2\
```

### Uninstall

Remove installation:

```batch
rmdir /s /q install_monitor
rmdir /s /q install_monitor_cli
```

---

## Summary

| File | Purpose | When to Use |
|------|---------|------------|
| install_and_run.bat | Full installation + run | First time setup |
| install_and_run_cli.bat | Install via CLI + run | Alternative method |
| run_monitor.bat | Run from existing install | Subsequent runs |
| run_monitor_hidden.bat | Background execution | Task Scheduler |

**Recommended workflow:**
1. **First time:** `install_and_run.bat` (handles everything)
2. **Daily runs:** `run_monitor.bat` (fast, no re-installation)
3. **Scheduled task:** `run_monitor_hidden.bat` (no console window)

