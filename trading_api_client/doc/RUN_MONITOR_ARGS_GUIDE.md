# Run Monitor - Args Configuration Guide

## Overview

The updated `run_monitor.bat` script now supports configuration files and command-line arguments to control installation behavior. This is useful when you have updated the tar.gz file and need to reinstall the application.

## Quick Start

### Default Behavior (No Changes)
```bash
run_monitor.bat
```
- Uses settings from `args.txt`
- Only installs if not already installed
- Otherwise runs existing installation

### Force Reinstall
```bash
run_monitor.bat --force-reinstall
```
- Uninstalls existing installation
- Reinstalls from tar.gz
- Starts the application

### Clean Install
```bash
run_monitor.bat --clean-install
```
- Same as `--force-reinstall`

### Skip Installation Check
```bash
run_monitor.bat --no-install
```
- Skips installation verification
- Runs existing installation directly
- Useful if you know installation is good

### Show Help
```bash
run_monitor.bat --help
```
- Displays usage information

## Configuration File: args.txt

The `args.txt` file contains default settings that are applied when running `run_monitor.bat` without command-line arguments.

### Available Options

#### FORCE_REINSTALL
- **Default**: `false`
- **Values**: `true` or `false`
- **Purpose**: Force reinstall on every run
- **When to use**: Set to `true` if you want automatic reinstalls on each run

```batch
set FORCE_REINSTALL=true
```

#### UNINSTALL_BEFORE_INSTALL
- **Default**: `true`
- **Values**: `true` or `false`
- **Purpose**: Uninstall before reinstalling
- **When to use**: Keep as `true` for clean installs

```batch
set UNINSTALL_BEFORE_INSTALL=true
```

#### TAR_GZ_PATH
- **Default**: Empty (auto-detect)
- **Values**: Full path to tar.gz file
- **Purpose**: Specify custom tar.gz location
- **When to use**: If tar.gz is in non-standard location

```batch
set TAR_GZ_PATH=D:\custom\path\trading_api_monitor-1.0.0.tar.gz
```

#### VENV_AUTO_DELETE
- **Default**: `true`
- **Values**: `true` or `false`
- **Purpose**: Auto-delete virtual environment before install
- **When to use**: Keep as `true` (recommended)

```batch
set VENV_AUTO_DELETE=true
```

#### SHOW_LOGS
- **Default**: `false`
- **Values**: `true` or `false`
- **Purpose**: Show installation log after completion
- **When to use**: Set to `true` for troubleshooting

```batch
set SHOW_LOGS=true
```

## Typical Workflows

### Workflow 1: Updated Tar.gz - Force Reinstall
```bash
# Edit args.txt and set:
set FORCE_REINSTALL=true

# Then run:
run_monitor.bat
```
Or use command-line instead:
```bash
run_monitor.bat --force-reinstall
```

### Workflow 2: Keep Installation, Update Config
```bash
# Leave FORCE_REINSTALL=false in args.txt
# Just run (existing install is used, config.xml is copied):
run_monitor.bat
```

### Workflow 3: Custom Tar.gz Location
```bash
# Edit args.txt:
set TAR_GZ_PATH=D:\builds\trading_api_monitor-1.0.0.tar.gz
set FORCE_REINSTALL=true

# Then run:
run_monitor.bat
```

### Workflow 4: Development - Frequent Reinstalls
```bash
# Edit args.txt:
set FORCE_REINSTALL=true
set SHOW_LOGS=true

# Then run:
run_monitor.bat
```

## How It Works

1. **Load Configuration**
   - Reads `args.txt` file
   - Sets default values if file missing

2. **Parse Arguments**
   - Command-line arguments override `args.txt`
   - Supported: `--force-reinstall`, `--clean-install`, `--no-install`, `--help`

3. **Check Installation**
   - Determines if reinstall is needed
   - Uninstalls if `FORCE_REINSTALL=true`

4. **Install if Needed**
   - Calls `install_and_run.bat`
   - Installs from tar.gz
   - Verifies installation

5. **Run Application**
   - Changes to installation directory
   - Copies config.xml if updated
   - Starts the monitor application

## Troubleshooting

### Installation Fails
1. Set `SHOW_LOGS=true` in args.txt
2. Run: `run_monitor.bat --force-reinstall`
3. Check `install_monitor.log` for details

### Can't Find Tar.gz
1. Verify tar.gz exists in `dist/` or project root
2. Set `TAR_GZ_PATH` in args.txt to full path
3. Run: `run_monitor.bat --force-reinstall`

### Venv Corrupted
1. Set `VENV_AUTO_DELETE=true`
2. Run: `run_monitor.bat --force-reinstall`
3. Reinstall will delete and recreate venv

### Stuck in Loop
1. Run: `run_monitor.bat --no-install`
2. Manually check `install_monitor/` directory
3. Delete `install_monitor/` if corrupted
4. Run: `run_monitor.bat --force-reinstall`

## Environment Locations

- **Source Directory**: Current directory (project root)
- **Install Directory**: `install_monitor/`
- **Virtual Environment**: `install_monitor/.venv/`
- **Log File**: `install_monitor.log`
- **Config File**: `config.xml` (copied from project root)

## Best Practices

1. **Use Command-Line for One-Off Actions**
   ```bash
   run_monitor.bat --force-reinstall
   ```

2. **Use args.txt for Permanent Defaults**
   - Edit once, affects all runs
   - Keep version control friendly

3. **Always Backup config.xml Before Reinstall**
   - Script copies it automatically if present
   - Verify it's in project root

4. **Monitor Installation Logs**
   - Set `SHOW_LOGS=true` during development
   - Check `install_monitor.log` on errors

5. **Version Control**
   - Keep `args.txt` in version control
   - Update with each release

## Examples

### Example 1: Production Setup
```batch
REM args.txt
set FORCE_REINSTALL=false
set UNINSTALL_BEFORE_INSTALL=true
set TAR_GZ_PATH=
set VENV_AUTO_DELETE=true
set SHOW_LOGS=false
```

### Example 2: Development Setup
```batch
REM args.txt
set FORCE_REINSTALL=true
set UNINSTALL_BEFORE_INSTALL=true
set TAR_GZ_PATH=D:\builds\latest\trading_api_monitor-1.0.0.tar.gz
set VENV_AUTO_DELETE=true
set SHOW_LOGS=true
```

### Example 3: Testing Setup
```batch
REM args.txt
set FORCE_REINSTALL=false
set UNINSTALL_BEFORE_INSTALL=true
set TAR_GZ_PATH=D:\test\trading_api_monitor-1.0.0.tar.gz
set VENV_AUTO_DELETE=true
set SHOW_LOGS=true
```

## Summary

| Method | Use Case | Command |
|--------|----------|---------|
| Default | Run as-is | `run_monitor.bat` |
| Force Reinstall | New tar.gz | `run_monitor.bat --force-reinstall` |
| Config File | Permanent settings | Edit `args.txt` then `run_monitor.bat` |
| Custom Path | Different tar.gz location | Edit `TAR_GZ_PATH` in `args.txt` |
| Troubleshoot | Installation issues | Set `SHOW_LOGS=true`, use `--force-reinstall` |
