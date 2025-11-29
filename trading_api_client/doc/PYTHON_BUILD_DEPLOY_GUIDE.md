# 🏗️ Python Build & Deploy - Complete Guide

## Standard Python Workflow

```
┌─────────────────────────────────────┐
│ 1. DEVELOPMENT                      │
│ • Edit code in .venv                │
│ • Test: python app.py               │
│ • Update requirements.txt            │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│ 2. PREPARE FOR RELEASE              │
│ • Update version                    │
│ • pip freeze > requirements.lock    │
│ • Create git tag                    │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│ 3. BUILD (Create Distribution)      │
│ python publish_project.py --clean   │
│ Creates: publish/ + ZIP file        │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│ 4. TEST BUILD                       │
│ • Fresh .venv                       │
│ • pip install -r requirements.txt   │
│ • python option_chain_*.py          │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│ 5. DISTRIBUTE                       │
│ • Email / USB / Cloud               │
│ • Send publish/ folder or ZIP       │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│ 6. DEPLOY (On Target Machine)       │
│ • Extract/copy publish/ folder      │
│ • Update config.xml                 │
│ • Run run_api.bat                   │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│ 7. VERIFY                           │
│ • curl /api/health                  │
│ • Check logs                        │
│ • Monitor performance               │
└─────────────────────────────────────┘
```

## 🔧 Three Standard Approaches

### Approach 1: PyPI Package Manager
**When:** Building a reusable library
```bash
pip install flask  # Installing from PyPI
```
**Setup:** setup.py / pyproject.toml

### Approach 2: Virtual Environment (Recommended for Apps) ✅
**When:** Building an application
```bash
python -m venv .venv
pip install -r requirements.txt
python app.py
```
**Your project:** ✅ Uses this approach

### Approach 3: Docker Containerization
**When:** Cloud deployment, scaling
```dockerfile
FROM python:3.13
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

## 📋 Standard Project Structure

```
project/
├── .venv/                    ← Virtual environment
├── src/ or app/              ← Application code
├── tests/                    ← Unit tests
├── docs/                     ← Documentation
├── requirements.txt          ← Dependencies (pinned versions)
├── setup.py                  ← Package metadata (if distributing)
├── .gitignore               ← Git ignore rules
├── README.md                ← Project documentation
└── config.yaml              ← Configuration
```

## 🔄 Full Build & Deploy Workflow

### Step 1: Prepare Dependencies
```bash
# Install what you need
pip install Flask requests dhanhq fyers-apiv3

# Document it
pip freeze > requirements.txt
```

### Step 2: Test Before Release
```bash
# Create fresh environment
python -m venv test_env
test_env\Scripts\activate
pip install -r requirements.txt
python app.py
deactivate
```

### Step 3: Package for Distribution
```bash
# Create self-contained bundle
python publish_project.py --clean
# Result: publish/ folder ready for deployment
```

### Step 4: Verify the Package
```bash
ls -la publish/
cat publish/DEPLOYMENT_GUIDE.md
```

### Step 5: Test Deployment
```bash
cd publish
.\run_api.bat
# Verify: curl http://localhost:5000/api/health
```

## 🛠️ Build Tools & Files

| Tool/File | Purpose | Example |
|-----------|---------|---------|
| `venv` | Virtual environment | `python -m venv .venv` |
| `pip` | Package manager | `pip install -r requirements.txt` |
| `requirements.txt` | Dependency list | `Flask==2.3.0` |
| `requirements.lock` | Pinned versions | Auto-generated |
| `setup.py` | Package metadata | For PyPI distribution |
| `pyproject.toml` | Modern config | Replaces setup.py |
| `Dockerfile` | Container definition | For Docker |
| `docker-compose.yml` | Multi-container setup | For orchestration |

## 📋 requirements.txt Best Practices

### Bad Practice ❌
```
Flask
requests
dhanhq
fyers-apiv3
```

### Good Practice ✅
```
# Core dependencies
Flask==2.3.0
requests>=2.28.0,<3.0.0
python-dotenv>=0.21.0

# Broker APIs
dhanhq==2.0.2
fyers-apiv3==3.1.7

# Custom libraries
./client/libs/trading_api-1.0.0.tar.gz
./client/libs/nslogger-1.0.0.tar.gz
```

**Rules:**
- Pin major versions for stability
- Use >= for secure updates
- Group by category
- Use >= for security patches
- Use == for exact reproducibility

## 🚀 Automation: CI/CD Pipelines

### GitHub Actions Example
```yaml
name: Build & Deploy

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.13'
      - run: |
          python -m venv venv
          source venv/bin/activate
          pip install -r requirements.txt
          pytest
```

## 🐳 Docker Best Practices

### Dockerfile Example
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Copy only requirements first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "option_chain_monitor_api_simple.py"]
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - BROKER_NAME=dhan
      - CONFIG_PATH=/app/config.xml
    volumes:
      - ./config.xml:/app/config.xml
```

## 📊 Deployment Environments

### Development
```bash
export ENV=development
python -m venv .venv
pip install -r requirements.txt
python option_chain_monitor_api_simple.py
```

### Staging
```bash
# Uses Docker
docker build -t api:latest .
docker run -p 5000:5000 api:latest
```

### Production
```bash
# Windows Task Scheduler or Linux cron
# Runs: publish\run_api.bat or python app.py
# With environment variables for credentials
```

## 🔒 Secrets Management

### Development ❌ (Don't do this)
```python
ACCESS_TOKEN = "abc123xyz"  # NEVER commit this!
```

### Using .env ✅
```bash
# .env file (in .gitignore)
BROKER_ACCESS_TOKEN=your_token_here
BROKER_CLIENT_ID=your_id_here

# Python code
from dotenv import load_dotenv
import os
load_dotenv()
access_token = os.getenv('BROKER_ACCESS_TOKEN')
```

### Using Environment Variables ✅
```bash
# Before running
export BROKER_ACCESS_TOKEN=your_token
python app.py
```

### Using XML Config ✅ (Your approach)
```xml
<config>
    <broker>
        <access_token>${BROKER_TOKEN}</access_token>
    </broker>
</config>
```

## ✅ Deployment Checklist

- [x] Virtual environment created (.venv)
- [x] Dependencies listed (requirements.txt)
- [x] Code tested locally
- [x] Application entry point defined
- [x] Configuration system in place
- [x] Build process automated
- [x] Build tested
- [x] Deployment package created
- [x] Deployment tested on fresh machine
- [ ] Production credentials configured
- [ ] Monitoring set up
- [ ] Backup strategy in place
- [ ] Rollback procedure documented

## 🔄 Rollback Strategy

### If Deployment Fails
```bash
# 1. Stop current version
taskkill /F /IM python.exe

# 2. Restore previous version
copy backup\publish-20251121.zip .
unzip publish-20251121.zip

# 3. Update config and restart
cd publish
run_api.bat
```

### Version Control
```bash
# Keep dated backups
publish-20251121.zip
publish-20251122.zip
publish-20251123.zip
```

## 🎯 Recommendation for Your Project

### Short-term (What You Have Now) ✅
```
Use: Virtual environment + requirements.txt
Command: python publish_project.py --clean
Result: publish/ folder ready for deployment
```

### Medium-term (Growth Phase)
```
Add: Docker support
Add: CI/CD pipeline  
Add: Better file structure
```

### Long-term (Scale Phase)
```
Add: Kubernetes
Add: Monitoring
Add: Package distribution
```

## 📚 Key Takeaways

1. **Virtual Environment** - Isolates dependencies
2. **requirements.txt** - Reproduces exact environment
3. **Automated Build** - publish_project.py handles packaging
4. **Self-Contained Bundle** - publish/ has everything needed
5. **No Installation Required** - Target machine just runs it
6. **Industry Standard** - This is how Python apps are deployed

## ✨ Summary

Your project correctly implements **Approach 2: Virtual Environment**, which is:
- ✅ Industry standard for applications
- ✅ Simple and reproducible
- ✅ Perfect for your use case
- ✅ Production-ready right now

**Next Step:** Deploy with `python publish_project.py --clean`
