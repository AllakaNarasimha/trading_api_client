# run_monitor.bat - Smart Auto-Installation

## Feature: Intelligent Installation Detection

`run_monitor.bat` now automatically detects if the installation exists and handles both cases:

### Smart Logic Flow

```
User runs: run_monitor.bat
    ↓
Is installation already set up?
    ↓ YES
    └─→ Run from existing install
        (Fast, no re-installation)
    ↓ NO
    └─→ Auto-run install_and_run.bat
        (Complete setup + start)
```

---

## Before vs After

### Before (Manual)

```batch
REM First time (must remember to use install script)
install_and_run.bat

REM Subsequent runs (must remember correct script)
run_monitor.bat
```

❌ Users might forget and run wrong script
❌ Error message if installation missing
❌ Manual script selection needed

### After (Automatic)

```batch
REM Every time - just run this
run_monitor.bat
```

✅ Always works
✅ Auto-detects setup status
✅ Auto-installs if needed
✅ One command for everything

---

## Usage Scenarios

### Scenario 1: Fresh Start (First Run)

```batch
D:\NSLearn\trading_api_client> run_monitor.bat

Installation not found. Auto-installing...

[STEP 1] Checking for distribution file...
✓ Found: dist\trading-api-monitor-1.0.0.tar.gz

[STEP 2] Creating installation directory...
✓ Created: install_monitor

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
2025-11-22 14:30:45,142 - INFO - * Running on http://localhost:5000
```

---

### Scenario 2: Subsequent Runs

```batch
D:\NSLearn\trading_api_client> run_monitor.bat

Running from existing installation at: install_monitor

=====================================================================
STARTING OPTION CHAIN MONITOR
=====================================================================

2025-11-22 14:35:20,456 - INFO - Option Chain Monitor API - Starting
2025-11-22 14:35:20,789 - INFO - * Running on http://localhost:5000
```

Much faster! No re-installation.

---

## How It Works

### Installation Detection

```batch
REM Check if installation exists
if not exist "%VENV_DIR%" (
    REM Installation missing
    echo Installation not found. Auto-installing...
    call "%SCRIPT_DIR%install_and_run.bat"
    exit /b %errorlevel%
)

REM Installation exists
echo Running from existing installation at: %INSTALL_DIR%
```

Checks for: `install_monitor\.venv\`

**If found:** Uses existing installation (fast)
**If missing:** Runs full installation (complete setup)

---

## Key Features

✅ **One Command** - `run_monitor.bat` for everything
✅ **Smart Detection** - Automatically detects setup status
✅ **Auto-Install** - Installs if not already done
✅ **Fast Restarts** - Skips installation on subsequent runs
✅ **Auto-Config** - Updates config.xml if needed
✅ **Error Handling** - Clear messages at each step

---

## Workflow Examples

### Example 1: New Machine

```batch
REM Get the project
git clone <repo>
cd trading_api_client

REM Just run this - everything handled automatically
run_monitor.bat

REM First run installs, subsequent runs are fast
```

---

### Example 2: Scheduled Task (Windows Task Scheduler)

Create a scheduled task with:
- **Program:** `cmd.exe`
- **Arguments:** `/c "D:\NSLearn\trading_api_client\run_monitor.bat"`
- **Start in:** `D:\NSLearn\trading_api_client`

✅ First scheduled run: Auto-installs
✅ Subsequent runs: Fast startup from existing install

---

### Example 3: Development Cycle

```batch
REM Start development
run_monitor.bat          # Installs + starts

# Make changes to code...

REM Test changes
run_monitor.bat          # Uses existing install (fast)

# Test more...

REM Production deployment
run_monitor.bat          # Ready to go
```

---

## File Organization

### First Run
```
trading_api_client/
├── dist/
│   └── trading-api-monitor-1.0.0.tar.gz
├── run_monitor.bat              ← User runs this
├── config.xml
└── (no install_monitor yet)
```

### After First Run
```
trading_api_client/
├── dist/
│   └── trading-api-monitor-1.0.0.tar.gz
├── run_monitor.bat              ← User runs this again
├── config.xml
└── install_monitor/             ← Created automatically
    ├── .venv/
    ├── config.xml
    └── logs/
```

### Subsequent Runs
```
run_monitor.bat → Checks install_monitor/ exists
               → Runs from existing install (fast!)
```

---

## Benefits vs Old Approach

| Feature | Old | New |
|---------|-----|-----|
| First time setup | Use `install_and_run.bat` | Use `run_monitor.bat` ✅ |
| Subsequent runs | Use `run_monitor.bat` | Use `run_monitor.bat` ✅ |
| Auto-detect | ❌ Manual choice | ✅ Automatic |
| Installation | Manual script selection | Auto-installed if needed ✅ |
| Error handling | Error if not installed | Auto-installs ✅ |
| User experience | Multiple commands | Single command ✅ |

---

## Smart Logic

### Installation Check
```
%VENV_DIR% = install_monitor\.venv\

Does it exist?
├─ YES → Run from existing
└─ NO  → Auto-install via install_and_run.bat
```

---

## Return Codes

The script properly propagates return codes:

```batch
exit /b %errorlevel%
```

- `0` = Success
- `1` = Failure (shown in exit code)

Useful for:
- Task Scheduler error handling
- CI/CD pipeline integration
- Batch script chaining

---

## Configuration Auto-Update

Even on subsequent runs, the script:

```batch
REM Copy config if needed
if exist "%SCRIPT_DIR%config.xml" (
    if not exist "%INSTALL_DIR%\config.xml" (
        copy "%SCRIPT_DIR%config.xml" "%INSTALL_DIR%\config.xml"
        echo Updated configuration file
    )
)
```

Automatically copies `config.xml` from project root to installation if it's missing.

---

## No Manual Intervention Needed

```batch
run_monitor.bat
```

That's all you need! The script handles:
✅ Checking installation status
✅ Running installation if needed
✅ Updating configuration
✅ Starting the application
✅ Proper error handling

---

## Perfect For

- ✅ First-time users (no script selection confusion)
- ✅ Scheduled tasks (auto-install on first run)
- ✅ CI/CD pipelines (one command, intelligent behavior)
- ✅ Development (quick restarts)
- ✅ Production (reliable startup)
- ✅ Remote execution (no manual setup needed)

---

## Summary

**Old way:**
```batch
install_and_run.bat      # First time
run_monitor.bat          # Subsequent times
```

**New way:**
```batch
run_monitor.bat          # Always works!
```

The script intelligently handles everything!

