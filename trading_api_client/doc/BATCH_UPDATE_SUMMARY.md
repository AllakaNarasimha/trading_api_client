# Batch Files - Flexible tar.gz Location Update Summary

## ✅ Update Complete

All batch files now support **flexible tar.gz file location detection**.

---

## What Changed

### Before (Rigid)
Batch files looked for tar.gz **only** in `dist/` folder:
```batch
set TARBALL=%DIST_DIR%\trading-api-monitor-1.0.0.tar.gz
```

❌ Failed if file was in project root
❌ Limited flexibility

### After (Flexible)
Batch files search **both locations** automatically:
```batch
REM Find tar.gz file (check both dist/ and project root)
set TARBALL=
if exist "%DIST_DIR%\trading-api-monitor-1.0.0.tar.gz" (
    set TARBALL=%DIST_DIR%\trading-api-monitor-1.0.0.tar.gz
) else if exist "%SCRIPT_DIR%trading-api-monitor-1.0.0.tar.gz" (
    set TARBALL=%SCRIPT_DIR%trading-api-monitor-1.0.0.tar.gz
)
```

✅ Works with tar.gz in `dist/`
✅ Works with tar.gz in project root
✅ Prefers `dist/` (standard practice)
✅ Shows both locations in error message

---

## Supported Scenarios

| Scenario | Before | After |
|----------|--------|-------|
| tar.gz in `dist/` | ✅ Works | ✅ Works (preferred) |
| tar.gz in project root | ❌ Fails | ✅ Works (fallback) |
| tar.gz in both | ✅ Works (uses dist/) | ✅ Works (uses dist/) |
| tar.gz in neither | ❌ Fails | ❌ Fails (helpful error) |

---

## Files Updated

✅ **install_and_run.bat** (4.9 KB)
- Added dual-location detection
- Improved error messaging
- Shows both search paths

✅ **install_and_run_cli.bat** (2.4 KB)
- Added dual-location detection
- Improved error messaging
- Alternative CLI entry point

ℹ️ **run_monitor.bat** (1.8 KB)
- No changes needed (uses existing installation)

ℹ️ **run_monitor_hidden.bat** (1.0 KB)
- No changes needed (uses existing installation)

---

## New Documentation

📄 **doc/BATCH_TAR_GZ_LOCATION_GUIDE.md**
- Comprehensive guide
- Usage scenarios with examples
- Error messages
- File search logic
- CI/CD pipeline examples

---

## Quick Usage

The batch files work the same way, but are now more flexible:

```batch
REM Generate distribution
python -m build

REM Run (works regardless of tar.gz location)
install_and_run.bat
```

### Scenario A: tar.gz in dist/ (Standard)
```batch
install_and_run.bat
```
✅ Finds and uses: `dist/trading-api-monitor-1.0.0.tar.gz`

### Scenario B: tar.gz in project root
```batch
install_and_run.bat
```
✅ Finds and uses: `trading-api-monitor-1.0.0.tar.gz`

### Scenario C: tar.gz moved or deleted
```batch
install_and_run.bat
```
❌ Error message showing both expected locations

---

## Error Message Improvement

### Before
```
ERROR: tar.gz file not found!
Expected location: D:\...\dist\trading-api-monitor-1.0.0.tar.gz
```

### After
```
ERROR: tar.gz file not found!
Searched in:
  - D:\...\dist\trading-api-monitor-1.0.0.tar.gz
  - D:\...\trading-api-monitor-1.0.0.tar.gz
Run: python -m build
```

Clearer error showing both locations searched.

---

## Search Order

When you run a batch file:

1. **Check dist/ folder first**
   - `dist/trading-api-monitor-1.0.0.tar.gz`
   - Preferred location (standard Python practice)

2. **Fall back to project root**
   - `trading-api-monitor-1.0.0.tar.gz`
   - Backup location

3. **If found, use it**
   - Continue with installation

4. **If not found anywhere**
   - Show error with both paths
   - Ask user to run: `python -m build`

---

## Use Cases

### Use Case 1: Standard Development
```
Directory: d:\NSLearn\trading_api_client
python -m build              # Creates dist/
install_and_run.bat         # Uses dist/ version
```

### Use Case 2: Moved Distribution File
```
Directory: d:\NSLearn\trading_api_client
Copy file to project root (manually)
install_and_run.bat         # Still works! Uses root version
```

### Use Case 3: CI/CD Pipeline
```bash
python -m build                              # Generates distribution
# File might be in dist/ or elsewhere
install_and_run.bat                         # Auto-detects location
```

### Use Case 4: Multiple Machines
```
Machine A: tar.gz in dist/
Machine B: tar.gz in project root
install_and_run.bat         # Works on both! Flexible detection
```

---

## Technical Details

### How Detection Works

```batch
REM Initialize TARBALL as empty
set TARBALL=

REM Test dist/ location
if exist "%DIST_DIR%\trading-api-monitor-1.0.0.tar.gz" (
    set TARBALL=%DIST_DIR%\trading-api-monitor-1.0.0.tar.gz
) else if exist "%SCRIPT_DIR%trading-api-monitor-1.0.0.tar.gz" (
    set TARBALL=%SCRIPT_DIR%trading-api-monitor-1.0.0.tar.gz
)

REM Check if found
if "%TARBALL%"=="" (
    REM Not found anywhere - show error
) else (
    REM Found - use it
    pip install "%TARBALL%"
)
```

---

## No Configuration Needed

✅ No environment variables to set
✅ No config file modifications
✅ No batch file edits needed
✅ Just run the batch file

The detection is **automatic and transparent**.

---

## Backward Compatibility

✅ All existing workflows still work
✅ Files in `dist/` folder work (preferred)
✅ Files in project root also work
✅ No breaking changes

If you've been running:
```batch
install_and_run.bat
```

It continues to work exactly the same way!

---

## Summary

| Feature | Before | After |
|---------|--------|-------|
| Location Detection | dist/ only | dist/ + root |
| Flexibility | Limited | Flexible |
| Error Messages | Single path | Both paths |
| Backward Compat. | N/A | ✅ Full |
| Configuration | N/A | None needed |

---

## Implementation

The change is implemented as a simple but effective search pattern:

```
if <location 1> exists
    use location 1
else if <location 2> exists
    use location 2
else
    show helpful error
```

This provides:
- **Predictable behavior** - dist/ has priority
- **Fallback support** - project root as backup
- **Clear errors** - shows both paths searched
- **No complexity** - simple batch script logic

---

## No Breaking Changes

If you're currently using:
```batch
install_and_run.bat
```

With tar.gz in `dist/`, everything continues to work exactly as before. The new code is backward compatible.

---

## Files Ready

✅ install_and_run.bat - Updated with dual-location detection
✅ install_and_run_cli.bat - Updated with dual-location detection
✅ run_monitor.bat - No changes needed
✅ run_monitor_hidden.bat - No changes needed
✅ doc/BATCH_TAR_GZ_LOCATION_GUIDE.md - New comprehensive guide

All batch files are **flexible and production-ready**!

