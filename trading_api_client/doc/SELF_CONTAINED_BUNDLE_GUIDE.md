# 📦 Self-Contained Bundle - Complete How-To Guide

## What is a Self-Contained Bundle?

A complete, portable deployment package containing:
```
publish/
├── .venv/                          ← Virtual environment (Python + all dependencies)
├── client/                         ← Your application code
│   ├── libs/
│   │   ├── trading_api-1.0.0.tar.gz
│   │   └── nslogger-1.0.0.tar.gz
│   └── utils/
├── option_chain_monitor_api_simple.py
├── config.xml                      ← Only thing to edit
├── requirements.txt                ← For reference
└── run_api.bat                     ← Just click this!
```

**NO INSTALLATION NEEDED on target machine!** Just copy and run.

---

## Step-by-Step: Create Your Bundle

### Step 1: Prepare the Virtual Environment

You already have `.venv/` in publish folder. Verify it:

```batch
D:\NSLearn\trading_api_client\publish> .venv\Scripts\python.exe --version
Python 3.13.x
```

### Step 2: Ensure All Dependencies Are Installed

```batch
cd D:\NSLearn\trading_api_client\publish

# Activate the virtual environment
.venv\Scripts\activate.bat

# Install/upgrade all dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

### Step 3: Test Everything Works

```batch
# Still in publish folder with .venv activated
python option_chain_monitor_api_simple.py
```

You should see:
```
[INFO] Starting Option Chain Monitor...
[INFO] API Server running on http://localhost:5000
```

Press `Ctrl+C` to stop.

### Step 4: Create the Smart Launcher

The `run_api.bat` file should look like this:

```batch
@echo off
REM Self-contained deployment launcher
REM No Python installation required - uses bundled .venv

cd /d %~dp0
call .venv\Scripts\activate.bat
python option_chain_monitor_api_simple.py
pause
```

This is already in your publish folder! ✅

### Step 5: Package Everything

Now you have a complete, self-contained bundle:

```
publish/                           ← This entire folder
├── .venv/                         ← 200-300 MB (all Python + dependencies)
├── client/                        ← Your app code
├── config.xml                     ← Edit this with credentials
├── requirements.txt               ← Reference only
├── run_api.bat                    ← Run this!
└── ... other files
```

---

## How to Deploy This Bundle

### Option A: Copy Entire Folder

```batch
# On your development machine
xcopy D:\NSLearn\trading_api_client\publish D:\Deploy\MyAPI /E /I /Y

# Then on target machine, just run:
D:\Deploy\MyAPI\run_api.bat
```

### Option B: Create ZIP File for Easy Transfer

```batch
# On development machine
cd D:\NSLearn\trading_api_client
powershell -Command "Compress-Archive -Path publish -DestinationPath publish-bundle.zip"

# Transfer publish-bundle.zip to target machine
# On target machine, extract and run:
# Extract-Archive publish-bundle.zip
# cd publish
# run_api.bat
```

### Option C: Use publish_project.py (Automated)

```bash
python publish_project.py --clean
# Creates: publish-YYYYMMDD-HHMMSS.zip with everything
```

---

## What Happens When You Run It

### First Time (After Copying)
```
D:\Deploy\MyAPI> run_api.bat

[Activating virtual environment from .venv...]
[Python found from .venv\Scripts\python.exe]
[Loading modules from client/]
[Loading custom libs: trading_api, nslogger]
[Starting Flask API server...]
[INFO] API listening on http://localhost:5000
```

### Subsequent Times
Same thing - instant startup because everything is already there!

---

## What's Inside .venv/ (The Magic)

Your virtual environment contains:
```
.venv/
├── Scripts/
│   ├── python.exe                ← Python executable
│   ├── pip.exe                   ← Package manager
│   ├── activate.bat              ← Activation script
│   └── ... other tools
├── Lib/
│   └── site-packages/
│       ├── requests/             ← All installed packages
│       ├── fyers_api/
│       ├── dhanhq/
│       ├── flask/
│       ├── trading_api/          ← Your custom lib
│       └── nslogger/             ← Your custom lib
└── pyvenv.cfg                    ← Configuration
```

When you run `run_api.bat`:
1. It activates `.venv/`
2. Sets PATH to use `.venv\Scripts\python.exe`
3. Runs your app with all dependencies available
4. **No need for system Python!**

---

## Why This Works

### Self-Contained Benefits ✅

| Benefit | Explanation |
|---------|-------------|
| **No Installation** | `.venv` has everything - Python + all packages |
| **Portable** | Copy folder anywhere - works on any Windows machine |
| **Isolated** | Doesn't interfere with system Python or other projects |
| **Reproducible** | Same code, same environment, same results everywhere |
| **No Admin Rights** | Can run without administrator privileges |
| **Version Control** | Exact same versions everywhere (trading_api-1.0.0, etc) |

### What You Need on Target Machine

```
✅ Windows OS (XP SP3 or later)
❌ Python NOT needed (embedded in .venv)
❌ pip NOT needed (embedded in .venv)
❌ Administrator rights NOT needed
✅ Just the publish/ folder
✅ Write access to folder location
```

---

## Verification Checklist

Before packaging, verify everything:

```batch
cd D:\NSLearn\trading_api_client\publish

REM Check Python is accessible
.venv\Scripts\python.exe --version
REM Expected: Python 3.13.x

REM Check pip works
.venv\Scripts\pip.exe list
REM Expected: See all packages listed

REM Check imports work
.venv\Scripts\python.exe -c "import trading_api; import nslogger; print('OK')"
REM Expected: OK

REM Check app structure
dir client
REM Expected: __init__.py, auth.py, libs/, utils/, etc.

REM Quick app test
.venv\Scripts\python.exe option_chain_monitor_api_simple.py
REM Expected: Runs for a few seconds, then Ctrl+C to stop
```

---

## Common Issues & Solutions

### Issue: "Python is not recognized"

**Problem:** Target machine doesn't have Python in PATH

**Solution:** NOT a problem! Your `.venv` has its own Python.
```batch
# Instead of:
python script.py          ← Looks for system Python (fails)

# Do this:
.venv\Scripts\python.exe script.py   ← Uses bundled Python (works)
```

Our `run_api.bat` already does this! ✅

### Issue: ".venv folder is huge (300 MB)"

**Problem:** Yes, that's normal. Includes Python + all packages.

**Solution:** Accept it - that's the tradeoff for "no installation needed"

**Alternative:** If size matters:
- Use PyInstaller (creates single .exe, smaller)
- Use Docker (completely different approach)

### Issue: "Port 5000 already in use"

**Problem:** Another app using port 5000

**Solution:** Edit `config.xml`:
```xml
<api>
    <port>5001</port>  ← Change from 5000 to 5001
</api>
```

### Issue: "Can't write to folder"

**Problem:** Folder is read-only or no write permission

**Solution:**
```batch
# Right-click folder → Properties → Security
# Ensure "Modify" permission is granted
# Or copy to different location with write access
```

---

## File Sizes Reference

For planning storage/transfer:

```
.venv/                    ~250-350 MB  ← Depends on packages
config.xml                ~2 KB
client/                   ~10 MB       ← Your code
requirements.txt          ~200 B
run_api.bat              ~1 KB
TOTAL:                    ~260-360 MB

Compressed ZIP:           ~80-120 MB   ← Much smaller!
```

---

## Deployment Process Summary

### Scenario: Deploy to New Machine

```
DEVELOPMENT MACHINE:
1. cd D:\NSLearn\trading_api_client
2. python publish_project.py --clean
   → Creates: publish-20251122-143000.zip (300-400 MB)

TRANSFER TO TARGET:
3. Email/USB/Cloud: Send publish-20251122-143000.zip to target machine

TARGET MACHINE:
4. Extract: publish-20251122-143000.zip
5. cd publish
6. Edit config.xml with your credentials
   <client_id>YOUR_ID</client_id>
   <access_token>YOUR_TOKEN</access_token>
7. Double-click run_api.bat
8. Done! API is running! 🎉
```

---

## Quick Command Reference

```batch
REM Prepare bundle
cd D:\NSLearn\trading_api_client\publish
.venv\Scripts\activate.bat
pip install -r requirements.txt

REM Test locally
python option_chain_monitor_api_simple.py

REM Create ZIP package
cd D:\NSLearn\trading_api_client
python publish_project.py --clean

REM Deploy on target
# 1. Extract ZIP
# 2. Edit config.xml
# 3. Run: run_api.bat
```

---

## Summary

### What You Have Now
- ✅ Virtual environment with Python in `publish/.venv/`
- ✅ All dependencies installed (trading_api, nslogger, etc.)
- ✅ Smart launcher script: `run_api.bat`
- ✅ Application code in `client/`

### What This Means
- 📦 **Complete bundle** - ready to copy and run
- 🚀 **No installation** - target machine just runs it
- 🔒 **Isolated** - doesn't interfere with system
- 📝 **Portable** - works on any Windows machine

### How to Deploy
1. Copy `publish/` folder (or ZIP it)
2. Edit `config.xml` on target machine
3. Run `run_api.bat`
4. Done! ✅

---

**Your self-contained bundle is ready to use! 🎉**
