# Trading API Monitor - Documentation Index

## Overview

Complete documentation for installation, building, deployment, and usage of the trading-api-monitor application.

---

## 📋 Quick Start

### For End Users (Install & Run)
**Start here:** `README_OPTION_CHAIN_MONITOR.md`

```bash
# Option 1: Direct (simplest)
pip install -r requirements.txt
python option_chain_monitor_api_simple.py

# Option 2: Package (recommended)
python -m build
pip install dist/trading_api_monitor-1.0.0-py3-none-any.whl
```

### For Developers (Build & Develop)
**Start here:** `BUILD_INSTRUCTIONS.md`

```bash
pip install -e ".[dev]"
pytest tests/
black client/ app.py
```

### For System Administrators (Deploy)
**Start here:** `SELF_CONTAINED_BUNDLE_GUIDE.md` or `PYTHON_BUILD_DEPLOY_GUIDE.md`

```bash
python -m build
# Deploy dist/trading_api_monitor-1.0.0-py3-none-any.whl
```

---

## 📚 Documentation Files

### 1. **README_OPTION_CHAIN_MONITOR.md** (Main Documentation)
**Best for:** Installation, configuration, API usage, troubleshooting

**Sections:**
- Overview and architecture
- 3 installation options (direct, package, Docker)
- Configuration (XML structure, environment variables)
- 3 ways to run the application
- Build & deployment guide
- 5 REST API endpoints with examples
- API consumption examples (Python, JavaScript, cURL, PowerShell)
- Logging configuration
- Troubleshooting common issues
- Features and security notes

**Use this for:**
- Installing the application
- Configuring broker credentials
- Testing the API
- Troubleshooting issues

---

### 2. **BUILD_INSTRUCTIONS.md** (Comprehensive Build Guide)
**Best for:** Building packages, deployment, development tools

**Sections:**
- Quick start (development and production)
- Build system components explained:
  - pyproject.toml (modern standard)
  - setup.py (backward compatibility)
  - MANIFEST.in (package data)
  - requirements.txt (dependencies)
- 5-step building process
- 4 installation methods
- Development workflow with code quality tools
- Version management
- PyPI publishing (optional)
- Troubleshooting and best practices

**Use this for:**
- Understanding the build system
- Building distribution packages
- Setting up development environment
- Publishing to PyPI

---

### 3. **BUILD_COMMANDS_SUMMARY.md** (Quick Reference)
**Best for:** Quick lookup of common commands

**Contains:**
- Quick reference for dev and production builds
- Installation options overview
- Build configuration files summary
- Complete build process checklist
- Installation verification steps
- Development tools setup
- Distribution files for deployment

**Use this for:**
- Quick command reference
- Build process overview
- Common tasks quick lookup

---

### 4. **SELF_CONTAINED_BUNDLE_GUIDE.md** (Deployment Bundle)
**Best for:** Creating portable deployments

**Sections:**
- Bundle creation process
- Self-contained virtual environment setup
- Verification procedures
- Deployment instructions
- Bundle contents listing
- Requirements and prerequisites

**Use this for:**
- Creating portable bundles with embedded Python
- Deploying without Python pre-installed
- Air-gapped environments

---

### 5. **PYTHON_BUILD_DEPLOY_GUIDE.md** (Build & Deploy)
**Best for:** Complete workflow from source to production

**Sections:**
- Development setup
- Building the application
- Packaging for distribution
- Deployment strategies
- CI/CD integration
- Automation scripts

**Use this for:**
- Complete build workflow
- Automation and scripting
- Production deployment
- CI/CD setup

---

### 6. **OPTION_CHAIN_API_README.md** (API Reference)
**Best for:** Understanding and using the REST API

**Contains:**
- API endpoints documentation
- Request/response examples
- Authentication and security
- Error handling
- Rate limiting
- Code examples

**Use this for:**
- API integration
- Endpoint reference
- Example code snippets

---

### 7. **BUNDLE_QUICK_START.md** (Quick Start for Bundles)
**Best for:** Quick deployment reference

**Contains:**
- Quick start instructions
- Essential commands
- Verification checklist
- Common issues

**Use this for:**
- Quick reference for bundle deployment
- First-time setup

---

### 8. **README_UPDATES_SUMMARY.md** (What's New)
**Best for:** Understanding documentation updates

**Contains:**
- Summary of all updates
- File changes overview
- Quick command reference
- Verification checklist

**Use this for:**
- Understanding what changed
- Verification of updates

---

## 🛠 Build System Files

### Configuration Files

**pyproject.toml** - Modern Python packaging (PEP 517/518)
- Build system configuration
- Project metadata
- Dependency specifications
- Development tools configuration
- Entry points for CLI

**setup.py** - Backward compatibility script
- Legacy setuptools configuration
- Package discovery
- Entry point setup
- Metadata fallback

**MANIFEST.in** - Package data inclusion
- Specifies additional files to include
- Configuration, documentation, data files
- Custom library tar.gz files

**requirements.txt** - Runtime dependencies
- Flask, requests, and other external packages
- Custom libraries (local paths)

---

## 📦 Distribution Packages

Generated from `python -m build`:

```
dist/
├── trading_api_monitor-1.0.0-py3-none-any.whl     (67 KB) ← Recommended
└── trading-api-monitor-1.0.0.tar.gz               (1.6 MB)
```

**Wheel (.whl):** Fast, no-compilation installation (recommended)
**Source (.tar.gz):** Full source code with buildinfo

---

## 🚀 Installation Methods

### Method 1: Direct from Requirements (Simplest)
```bash
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

### Method 2: From Package (Recommended)
```bash
pip install build
python -m build
pip install dist/trading_api_monitor-1.0.0-py3-none-any.whl
```

### Method 3: Editable Development
```bash
pip install -e ".[dev]"
```

### Method 4: Docker
```bash
docker build -t trading-api-monitor:1.0.0 .
docker run -p 5000:5000 trading-api-monitor:1.0.0
```

---

## 🏃 Running the Application

### After Installation

```bash
# Method 1: CLI command (if installed as package)
option-chain-monitor

# Method 2: Python module
python -m app

# Method 3: Direct script
python option_chain_monitor_api_simple.py

# Method 4: Direct execution
python app.py
```

---

## 👨‍💻 Development Workflow

### Setup Development Environment
```bash
pip install -e ".[dev]"
```

### Code Quality Tools
```bash
# Format code
black client/ app.py

# Check code style
flake8 client/ app.py

# Type checking
mypy client/

# Run tests
pytest tests/

# All checks combined
black client/ app.py && flake8 client/ app.py && mypy client/ && pytest tests/
```

---

## 🔨 Build Process

### Step-by-Step Build

```bash
# 1. Install tools
pip install build twine

# 2. Clean previous builds
rm -r dist build *.egg-info

# 3. Build packages
python -m build

# 4. Verify (optional)
twine check dist/*

# 5. Install and test
pip install dist/trading_api_monitor-1.0.0-py3-none-any.whl
option-chain-monitor --help
```

---

## 📋 Configuration

### Main Configuration File: config.xml

Structure:
```xml
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

### Environment Variable Overrides

Format: `OPTION_CHAIN_{SECTION}_{KEY}=value`

Examples:
```bash
set OPTION_CHAIN_API_PORT=8000
set OPTION_CHAIN_API_AUTO_START=true
set OPTION_CHAIN_CUTOFF_ENABLED=true
```

---

## 🔍 Verification

### Installation Verification
```bash
# Check package installation
pip show trading-api-monitor

# Test imports
python -c "import client; from client.utils import config, monitor, api; print('OK')"

# Test CLI command
option-chain-monitor --help
```

### API Health Check
```bash
# After starting the application
curl http://localhost:5000/api/health

# With Python
curl -X GET http://localhost:5000/api/health
```

---

## 🆘 Troubleshooting

### Common Issues

**Port already in use:**
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Import errors:**
```bash
pip install -r requirements.txt
python -c "import sys; print(sys.path)"
```

**SSL certificate errors:**
- Check internet connection
- Verify firewall settings
- Ensure API endpoints are accessible

**Module not found:**
```bash
# Reinstall
pip uninstall trading-api-monitor
pip install dist/trading_api_monitor-1.0.0-py3-none-any.whl
```

See full troubleshooting in:
- `README_OPTION_CHAIN_MONITOR.md` - Troubleshooting section
- `BUILD_INSTRUCTIONS.md` - Troubleshooting guide

---

## 📖 Documentation Structure

```
Documentation/
├── README_OPTION_CHAIN_MONITOR.md    ← Main documentation
├── BUILD_INSTRUCTIONS.md              ← Build guide
├── BUILD_COMMANDS_SUMMARY.md          ← Quick reference
├── SELF_CONTAINED_BUNDLE_GUIDE.md     ← Bundle creation
├── PYTHON_BUILD_DEPLOY_GUIDE.md       ← Build workflow
├── OPTION_CHAIN_API_README.md         ← API reference
├── BUNDLE_QUICK_START.md              ← Quick start
├── README_UPDATES_SUMMARY.md          ← Update summary
└── DOCUMENTATION_INDEX.md             ← This file
```

---

## 🔗 Related Files

### Build Configuration
- `pyproject.toml` - Modern packaging standard
- `setup.py` - Legacy packaging script
- `MANIFEST.in` - Package data specification
- `requirements.txt` - Dependencies

### Source Code
- `app.py` - Main application entry point
- `option_chain_monitor_api_simple.py` - Alternative entry point
- `client/` - Client package
  - `utils/` - Core modules (config, monitor, api, cutoff_timer)
  - `libs/` - Custom libraries (tar.gz files)

### Configuration
- `config.xml` - Application configuration

### Distribution
- `dist/trading_api_monitor-1.0.0-py3-none-any.whl` - Recommended wheel
- `dist/trading-api-monitor-1.0.0.tar.gz` - Source distribution

---

## 📞 Support

### Documentation Organization

1. **For Installation:** `README_OPTION_CHAIN_MONITOR.md`
2. **For Building:** `BUILD_INSTRUCTIONS.md`
3. **For Quick Reference:** `BUILD_COMMANDS_SUMMARY.md`
4. **For Deployment:** `SELF_CONTAINED_BUNDLE_GUIDE.md` or `PYTHON_BUILD_DEPLOY_GUIDE.md`
5. **For API:** `OPTION_CHAIN_API_README.md`
6. **For Issues:** See Troubleshooting sections in main README

---

## ✅ Checklist for New Users

- [ ] Read `README_OPTION_CHAIN_MONITOR.md` for overview
- [ ] Choose installation method (Option 1, 2, or 3)
- [ ] Follow installation instructions
- [ ] Configure `config.xml` with credentials
- [ ] Run application using preferred method
- [ ] Test API endpoints with health check
- [ ] Review logging in `logs/` directory

---

## 🎓 Learning Path

**Beginner (Just Run It):**
1. README_OPTION_CHAIN_MONITOR.md → Installation → Option 1
2. Configure config.xml
3. Run application

**Developer (Build & Extend):**
1. BUILD_INSTRUCTIONS.md → Development Build
2. Install dev dependencies
3. Review code in `client/utils/`
4. Run tests with pytest

**DevOps (Deploy & Automate):**
1. PYTHON_BUILD_DEPLOY_GUIDE.md → Complete workflow
2. BUILD_INSTRUCTIONS.md → Production Build
3. Deploy wheel file to production
4. Set up monitoring and logging

---

**Last Updated:** 2025-11-22
**Version:** 1.0.0
**Status:** ✅ Complete Documentation
