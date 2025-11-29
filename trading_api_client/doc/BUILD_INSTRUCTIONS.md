# Trading API Monitor - Build Instructions

## Overview

This document provides complete instructions for building and distributing the trading-api-monitor package.

## Quick Start

### For Development

```bash
# Install in development mode with tools
pip install -e ".[dev]"

# Run tests
pytest tests/

# Format code
black client/ app.py

# Check code quality
flake8 client/ app.py
```

### For Production

```bash
# Install build tools
pip install build twine

# Clean previous builds
rm -r dist build *.egg-info

# Build distributions
python -m build

# Result: dist/trading_api_monitor-1.0.0-py3-none-any.whl
#         dist/trading-api-monitor-1.0.0.tar.gz
```

## Build System Components

### 1. pyproject.toml
**Purpose:** Modern Python packaging configuration (PEP 517/518)

**Key Sections:**
```toml
[build-system]
requires = ["setuptools>=65.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "trading-api-monitor"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [...]

[project.optional-dependencies]
dev = ["pytest", "black", "flake8", "mypy"]

[project.scripts]
option-chain-monitor = "app:main"
```

### 2. setup.py
**Purpose:** Backward compatibility and setuptools configuration

**Features:**
- Entry point for CLI: `option-chain-monitor=app:main`
- Package discovery via `find_packages()`
- Package data inclusion for tar.gz files
- Metadata and classifiers for PyPI

### 3. MANIFEST.in
**Purpose:** Specify additional files to include in distribution

**Contents:**
```
include README_OPTION_CHAIN_MONITOR.md
include OPTION_CHAIN_API_README.md
include requirements.txt
include config.xml
recursive-include client/libs *.tar.gz
recursive-include market_data *.csv
recursive-include doc *
```

### 4. requirements.txt
**Purpose:** Runtime dependencies specification

**Contents:**
- Custom libraries (local tar.gz files)
- External dependencies (Flask, requests, fyers-apiv3, dhanhq, etc.)

## Building Process

### Step 1: Prepare Environment

```bash
# Navigate to project
cd d:\NSLearn\trading_api_client

# Ensure Python 3.11+ is available
python --version

# Create virtual environment (if needed)
python -m venv .venv
.venv\Scripts\activate.bat  # Windows
# or
source .venv/bin/activate   # Linux/macOS
```

### Step 2: Install Build Dependencies

```bash
# Install build tools
pip install --upgrade pip setuptools wheel
pip install build twine

# Verify installation
python -m build --version
twine --version
```

### Step 3: Clean Previous Builds

```bash
# Windows (PowerShell)
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue

# Windows (CMD)
rmdir /s /q dist build 2>nul
del /s *.egg-info 2>nul

# Linux/macOS
rm -rf dist build *.egg-info
```

### Step 4: Build Distribution Packages

```bash
# Build wheel and source distribution
python -m build

# Output:
# Successfully built trading_api_monitor-1.0.0.tar.gz
# trading_api_monitor-1.0.0-py3-none-any.whl
```

### Step 5: Verify Build (Optional)

```bash
# Check wheel contents
unzip -l dist/trading_api_monitor-1.0.0-py3-none-any.whl

# Verify with twine
twine check dist/*

# Check metadata
python -c "import wheel.metadata; print(wheel.metadata.distribution('trading-api-monitor'))"
```

## Installation Methods

### Method 1: Install from Wheel (Recommended)

**Fastest and most reliable method:**

```bash
# In a clean virtual environment
python -m venv test_install
test_install\Scripts\activate.bat  # Windows

# Install wheel
pip install dist/trading_api_monitor-1.0.0-py3-none-any.whl

# Verify
option-chain-monitor --help
```

### Method 2: Install from Source Distribution

**For users who want to compile:**

```bash
# Install source distribution
pip install dist/trading-api-monitor-1.0.0.tar.gz

# Verify
option-chain-monitor --help
```

### Method 3: Development Installation

**For development with live code changes:**

```bash
# Install in editable mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Changes to code are immediately available
```

### Method 4: Direct Installation from dist/

```bash
# After building, install from dist folder
pip install dist/trading_api_monitor-1.0.0-py3-none-any.whl

# Or
pip install dist/trading-api-monitor-1.0.0.tar.gz
```

## Distribution Files

### Wheel File
**Name:** `trading_api_monitor-1.0.0-py3-none-any.whl`

**Advantages:**
- Fastest installation (no compilation)
- No build dependencies required on target system
- Pre-built binary package
- Recommended for production

**Contents:**
- Compiled Python bytecode
- All dependencies listed in metadata
- Entry points configured
- Metadata and licenses

### Source Distribution
**Name:** `trading-api-monitor-1.0.0.tar.gz`

**Advantages:**
- Smaller file size (if uncompressed individually)
- Allows inspection of source code
- Can be built on target system
- Better for archival

**Contents:**
- Complete source code
- All configuration files
- Tests and documentation
- Build metadata

## Package Contents

After installation, the package provides:

```
trading_api_monitor/
├── client/
│   ├── auth.py              # Broker authentication
│   ├── orders.py            # Order management
│   ├── portfolio.py         # Portfolio management
│   ├── watchlist.py         # Real-time data streaming
│   ├── utils/
│   │   ├── config.py        # Configuration management
│   │   ├── monitor.py       # Monitoring core
│   │   ├── api.py           # Flask REST API
│   │   ├── cutoff_timer.py  # Scheduled shutdown
│   │   └── __init__.py
│   ├── libs/
│   │   ├── nslogger-1.0.0.tar.gz
│   │   └── trading_api-1.0.0.tar.gz
│   └── __init__.py
├── doc/                     # Documentation
├── market_data/             # NSE market data
└── [config files]
```

## Entry Points

### CLI Command

After installation, a command-line entry point is available:

```bash
# Direct command
option-chain-monitor

# This runs: python -m app (via setup.py entry_points)
```

### Module Import

```python
# As a Python package
from client.utils import config, monitor, api

# Direct app execution
from app import main
main()
```

## Development Workflow

### Code Quality Tools

All configured in `pyproject.toml`:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Black: Code formatting
black client/ app.py

# Flake8: Code style checks
flake8 client/ app.py

# MyPy: Type checking
mypy client/

# Pytest: Unit testing
pytest tests/ -v --cov=client

# Combined: Run all checks
black client/ app.py && flake8 client/ app.py && mypy client/ && pytest tests/
```

### Version Updates

When updating version:

1. Update in `pyproject.toml`:
   ```toml
   [project]
   version = "1.0.1"
   ```

2. Update in `setup.py` (if present):
   ```python
   version='1.0.1'
   ```

3. Git tag (optional):
   ```bash
   git tag -a v1.0.1 -m "Version 1.0.1"
   git push origin v1.0.1
   ```

4. Rebuild:
   ```bash
   rm -rf dist build *.egg-info
   python -m build
   ```

## Publishing to PyPI

**For public distribution (optional):**

```bash
# Create PyPI account at https://pypi.org

# Install twine
pip install twine

# Build packages (if not already built)
python -m build

# Test upload (testpypi)
twine upload --repository testpypi dist/*

# Production upload
twine upload dist/*

# Install from PyPI
pip install trading-api-monitor
```

## Troubleshooting

### Build Errors

**Error:** `error: metadata must be valid TOML`
- **Solution:** Check `pyproject.toml` for syntax errors

**Error:** `unknown file type in files list`
- **Solution:** Verify `MANIFEST.in` file paths exist

**Error:** `'setuptools_scm' not found`
- **Solution:** Install: `pip install setuptools_scm`

### Installation Errors

**Error:** `No module named 'client'`
- **Solution:** Ensure installation completed: `pip show trading-api-monitor`

**Error:** `command 'option-chain-monitor' not found`
- **Solution:** Check entry point installation: `pip show -f trading-api-monitor`

**Error:** `wheel file is not a zip file`
- **Solution:** Download wheel again, may be corrupted

### Import Errors

```bash
# After installation, verify imports
python -c "import client; import client.utils; print('OK')"

# Check package location
python -c "import client; print(client.__file__)"
```

## Testing the Build

### Verification Script

```bash
# Create test_installation.py
python -c "
import sys
import client
from client.utils import config, monitor, api

print(f'✓ Python {sys.version_info.major}.{sys.version_info.minor}')
print(f'✓ Client module: {client.__file__}')
print(f'✓ Config module: {config.__file__}')
print(f'✓ All imports successful')
"
```

### Functional Test

```bash
# In a fresh virtual environment
python -m venv test_fresh
test_fresh\Scripts\activate.bat

# Install from wheel
pip install dist/trading_api_monitor-1.0.0-py3-none-any.whl

# Run app
option-chain-monitor

# Test API
curl http://localhost:5000/api/health
```

## Best Practices

1. **Always build in clean environment**
   - Remove previous dist/, build/, *.egg-info
   - Use clean virtual environment for testing

2. **Test after building**
   - Verify wheel installation in fresh venv
   - Test all entry points
   - Check imports

3. **Use semantic versioning**
   - MAJOR.MINOR.PATCH (1.0.0)
   - Update consistently across files

4. **Include changelog**
   - Document changes between versions
   - Update README with new features

5. **Sign releases (optional)**
   - GPG sign wheel files
   - Use twine for trusted uploads

## File References

- **Build System:** `pyproject.toml`
- **Setup Script:** `setup.py`
- **Manifest:** `MANIFEST.in`
- **Dependencies:** `requirements.txt`
- **Configuration:** `config.xml`
- **Documentation:** `README_OPTION_CHAIN_MONITOR.md`

## Related Documentation

- [Python Packaging Guide](https://packaging.python.org/)
- [setuptools Documentation](https://setuptools.pypa.io/)
- [PEP 517/518](https://www.python.org/dev/peps/pep-0517/)
- [wheel Documentation](https://wheel.readthedocs.io/)

## Support

For build-related issues:

1. Check `pyproject.toml` syntax
2. Verify all dependencies installed
3. Clear build artifacts
4. Rebuild from scratch
5. Check Python version (requires 3.11+)
