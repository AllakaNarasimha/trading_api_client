# Batch Files - Flexible tar.gz Location Support

## Feature: Auto-Detection of tar.gz File

All batch files now automatically detect and use the tar.gz file from **either location**:

1. **dist/ folder** (recommended) - `dist/trading-api-monitor-1.0.0.tar.gz`
2. **Project root folder** (fallback) - `trading-api-monitor-1.0.0.tar.gz`

---

## How It Works

The batch files use intelligent file detection:

```batch
REM Find tar.gz file (check both dist/ and project root)
set TARBALL=
if exist "%DIST_DIR%\trading-api-monitor-1.0.0.tar.gz" (
    set TARBALL=%DIST_DIR%\trading-api-monitor-1.0.0.tar.gz
) else if exist "%SCRIPT_DIR%trading-api-monitor-1.0.0.tar.gz" (
    set TARBALL=%SCRIPT_DIR%trading-api-monitor-1.0.0.tar.gz
)
```

**Search Order:**
1. First checks: `dist/trading-api-monitor-1.0.0.tar.gz`
2. Then checks: `trading-api-monitor-1.0.0.tar.gz` (same folder as batch file)
3. If found in either location, uses it automatically

---

## Usage Scenarios

### Scenario 1: tar.gz in dist/ folder (Standard)

```
project_root/
├── dist/
│   └── trading-api-monitor-1.0.0.tar.gz    ← Found here
├── install_and_run.bat
└── config.xml
```

**Command:**
```batch
install_and_run.bat
```

**Result:** ✓ Uses file from `dist/`

---

### Scenario 2: tar.gz in project root (Fallback)

```
project_root/
├── trading-api-monitor-1.0.0.tar.gz       ← Found here
├── install_and_run.bat
└── config.xml
```

**Command:**
```batch
install_and_run.bat
```

**Result:** ✓ Uses file from project root

---

### Scenario 3: tar.gz in both locations (dist takes priority)

```
project_root/
├── dist/
│   └── trading-api-monitor-1.0.0.tar.gz   ← Uses this (priority)
├── trading-api-monitor-1.0.0.tar.gz       ← Ignored
├── install_and_run.bat
└── config.xml
```

**Command:**
```batch
install_and_run.bat
```

**Result:** ✓ Uses `dist/` version (standard best practice)

---

### Scenario 4: tar.gz not found anywhere

```
project_root/
├── dist/                                   ← Empty
├── install_and_run.bat
└── config.xml
```

**Command:**
```batch
install_and_run.bat
```

**Output:**
```
ERROR: tar.gz file not found!
Searched in:
  - D:\...\dist\trading-api-monitor-1.0.0.tar.gz
  - D:\...\trading-api-monitor-1.0.0.tar.gz
Run: python -m build
```

---

## Building the Distribution

### Method 1: Build to dist/ (Recommended)

```batch
python -m build
```

**Creates:**
- `dist/trading-api-monitor-1.0.0.tar.gz` ← Preferred location
- `dist/trading_api_monitor-1.0.0-py3-none-any.whl`

**Then run:**
```batch
install_and_run.bat
```

---

### Method 2: Manual file placement

If tar.gz is generated elsewhere, move it to project root:

```batch
REM Copy tar.gz to project root
copy "C:\other\path\trading-api-monitor-1.0.0.tar.gz" .

REM Now run
install_and_run.bat
```

---

## Updated Batch Files

All batch files now support both locations:

| File | Support |
|------|---------|
| **install_and_run.bat** | ✓ dist/ and project root |
| **install_and_run_cli.bat** | ✓ dist/ and project root |
| **run_monitor.bat** | Uses existing install |
| **run_monitor_hidden.bat** | Uses existing install |

---

## Error Messages (Improved)

### Before (Old)
```
ERROR: tar.gz file not found!
Expected location: D:\path\to\dist\trading-api-monitor-1.0.0.tar.gz
```

### After (New - Shows both locations)
```
ERROR: tar.gz file not found!
Searched in:
  - D:\path\to\dist\trading-api-monitor-1.0.0.tar.gz
  - D:\path\to\trading-api-monitor-1.0.0.tar.gz
Run: python -m build
```

---

## Practical Examples

### Example 1: Development Workflow

```batch
REM Step 1: Build distribution
D:\NSLearn\trading_api_client> python -m build

REM Creates dist/trading-api-monitor-1.0.0.tar.gz

REM Step 2: Install and run
D:\NSLearn\trading_api_client> install_and_run.bat

REM Works! Uses file from dist/
```

---

### Example 2: Moved Distribution File

```batch
REM tar.gz is in project root (not in dist/)
D:\NSLearn\trading_api_client> dir trading-api-monitor-1.0.0.tar.gz
trading-api-monitor-1.0.0.tar.gz

REM Still works!
D:\NSLearn\trading_api_client> install_and_run.bat

REM Batch file finds it automatically
```

---

### Example 3: CI/CD Pipeline

```bash
# Pipeline generates tar.gz anywhere
python -m build

# Rename or move file if needed
mv dist/trading-api-monitor-1.0.0.tar.gz .

# Deploy using batch file - still works!
install_and_run.bat
```

---

## Benefits

✅ **Flexible** - Works with tar.gz in either location
✅ **Robust** - Automatic fallback if file moved
✅ **Smart** - Prefers dist/ (standard practice)
✅ **Helpful** - Shows both search locations in error
✅ **No Changes Needed** - Just run the batch file

---

## File Search Logic Flow

```
User runs: install_and_run.bat
    ↓
Check if dist/trading-api-monitor-1.0.0.tar.gz exists?
    ↓ YES
    └─→ Use dist/ version
        (Continue installation)
    ↓ NO
Check if trading-api-monitor-1.0.0.tar.gz exists (project root)?
    ↓ YES
    └─→ Use project root version
        (Continue installation)
    ↓ NO
    └─→ Show error: Not found in either location
        (Ask user to run: python -m build)
```

---

## Summary

**The batch files now:**
- ✅ Search `dist/` folder first (standard)
- ✅ Fall back to project root folder
- ✅ Use whichever file is found
- ✅ Show helpful error if not found anywhere
- ✅ Require no configuration changes

**Just run:**
```batch
install_and_run.bat
```

**And it will find the tar.gz file automatically!**

