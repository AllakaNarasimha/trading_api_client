@echo off
REM =====================================================================
REM Trading API Monitor - Installation and Startup Batch Script
REM This script installs the tar.gz distribution and starts the monitor
REM =====================================================================

setlocal enabledelayedexpansion

REM Get script directory
set SCRIPT_DIR=%~dp0
set DIST_DIR=%SCRIPT_DIR%dist
set INSTALL_DIR=%SCRIPT_DIR%install_monitor
set VENV_DIR=%INSTALL_DIR%\.venv
set PYTHON=%VENV_DIR%\Scripts\python.exe
set PIP=%VENV_DIR%\Scripts\pip.exe
set LOG_FILE=%SCRIPT_DIR%install_monitor.log

REM Find tar.gz file (check both dist/ and project root)
set TARBALL=
if exist "%DIST_DIR%\trading_api_monitor-1.0.0.tar.gz" (
    set TARBALL=%DIST_DIR%\trading_api_monitor-1.0.0.tar.gz
) else if exist "%SCRIPT_DIR%trading_api_monitor-1.0.0.tar.gz" (
    set TARBALL=%SCRIPT_DIR%trading_api_monitor-1.0.0.tar.gz
)

REM Colors (using ANSI codes in Windows 10+)
set "GREEN="
set "RED="
set "YELLOW="
set "RESET="

echo.
echo =====================================================================
echo Trading API Monitor - Installation and Startup
echo =====================================================================
echo Timestamp: %date% %time%
echo Script Directory: %SCRIPT_DIR%
echo.

REM =====================================================================
REM Step 1: Check if tar.gz file exists
REM =====================================================================
echo [STEP 1] Checking for distribution file...
if "%TARBALL%"=="" (
    echo %RED%ERROR: tar.gz file not found!%RESET%
    echo Searched in:
    echo   - %DIST_DIR%\trading_api_monitor-1.0.0.tar.gz
    echo   - %SCRIPT_DIR%trading_api_monitor-1.0.0.tar.gz
    echo.
    echo Please run: python -m build
    echo to generate the distribution package first.
    exit /b 1
)
echo %GREEN%✓ Found: %TARBALL%%RESET%
echo.

REM =====================================================================
REM Step 2: Create installation directory
REM =====================================================================
echo [STEP 2] Creating installation directory...
if exist "%INSTALL_DIR%" (
    echo Removing existing virtual environment ^(preserving user data^)...
    if exist "%VENV_DIR%" (
        rmdir /s /q "%VENV_DIR%" >nul 2>&1
    )
) else (
    mkdir "%INSTALL_DIR%" >nul 2>&1
)
echo %GREEN%✓ Ready: %INSTALL_DIR%%RESET%
echo.

REM =====================================================================
REM Step 3: Create virtual environment
REM =====================================================================
echo [STEP 3] Creating virtual environment...
echo This may take a few minutes...
call %SystemRoot%\System32\cmd.exe /c "cd /d "%INSTALL_DIR%" && python -m venv .venv" >nul 2>&1

if not exist "%PYTHON%" (
    echo %RED%ERROR: Failed to create virtual environment%RESET%
    exit /b 1
)
echo %GREEN%✓ Created virtual environment%RESET%
echo.

REM =====================================================================
REM Step 4: Upgrade pip
REM =====================================================================
echo [STEP 4] Upgrading pip...
call "%PIP%" install --upgrade pip setuptools wheel >nul 2>&1
echo %GREEN%✓ Upgraded pip%RESET%
echo.

REM =====================================================================
REM Step 5: Install from tar.gz
REM =====================================================================
echo [STEP 5] Installing trading-api-monitor from tar.gz...
echo This may take a minute...
echo.

REM Install the main package - this will install public dependencies automatically
echo ===== Installing trading-api-monitor package =====
call "%PIP%" install "%TARBALL%"

if errorlevel 1 (
    echo %RED%ERROR: Failed to install trading-api-monitor%RESET%
    exit /b 1
)

echo %GREEN%✓ Successfully installed main package%RESET%
echo.

REM =====================================================================
REM Step 5b: Run post-installation script
REM =====================================================================
echo [STEP 5b] Running post-installation script...
echo This will install custom packages and dependencies...

REM Try to run the post-install script (it's installed as a module)
call "%PYTHON%" -m post_install 2>&1

if errorlevel 1 (
    echo %YELLOW%⚠ Warning: post_install module failed, trying direct installation...%RESET%
    
    REM Fallback: Install dependencies explicitly
    echo Installing dependencies from requirements.txt...
    call "%PIP%" install Flask>=2.3.0 requests>=2.28.0 python-dotenv>=0.21.0 certifi>=2023.0.0 fyers-apiv3>=2.0.0 dhanhq>=2.0.0
    
    REM Install custom packages
    echo Installing custom packages...
    call "%PYTHON%" -c "import sys; from pathlib import Path; import subprocess; import client; libs_dir = Path(client.__file__).parent / 'libs'; packages = ['nslogger-1.0.0.tar.gz', 'trading_api-1.0.0.tar.gz']; [(print(f'Installing {f}...'), subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--no-deps', str(libs_dir / f)])) for f in packages if (libs_dir / f).exists()]"
)

REM Verify custom packages installed
call "%PYTHON%" -c "import nslogger; import trading_api" >nul 2>&1
if errorlevel 1 (
    echo %RED%ERROR: Custom packages not installed correctly%RESET%
    exit /b 1
)
echo %GREEN%✓ Post-installation complete%RESET%
echo.

REM =====================================================================
REM Step 6: Verify installation
REM =====================================================================
echo [STEP 6] Verifying installation...

REM Verify all required modules can be imported
call "%PYTHON%" -c "import client, nslogger, trading_api, Flask, requests; print('All modules OK')" >nul 2>&1

if errorlevel 1 (
    echo %RED%ERROR: Module verification failed%RESET%
    echo Checking which modules are missing...
    call "%PYTHON%" -c "import sys; modules=['client', 'nslogger', 'trading_api', 'Flask', 'requests', 'fyers_apiv3', 'dhanhq']; [print(f'{m}: OK') if __import__(m) else None for m in modules]" 2>&1
    exit /b 1
) else (
    echo %GREEN%✓ All modules verified successfully%RESET%
)
echo.

REM =====================================================================
REM Step 7: Copy configuration files
REM =====================================================================
echo [STEP 7] Checking configuration files...

REM Copy config.xml from project directory if it exists
if exist "%SCRIPT_DIR%config.xml" (
    copy "%SCRIPT_DIR%config.xml" "%INSTALL_DIR%\config.xml" >nul 2>&1
    echo %GREEN%✓ Copied config.xml from project%RESET%
) else (
    echo %YELLOW%⚠ config.xml not found in project - using package defaults%RESET%
)

REM Find and copy the main script from installed package
call "%PYTHON%" -c "import os, shutil; from pathlib import Path; import option_chain_monitor_api_simple; script_path = Path(option_chain_monitor_api_simple.__file__); install_dir = Path(r'%INSTALL_DIR%'); shutil.copy2(script_path, install_dir / 'option_chain_monitor_api_simple.py') if script_path.exists() else None" 2>nul
if exist "%INSTALL_DIR%\option_chain_monitor_api_simple.py" (
    echo %GREEN%✓ Startup script ready%RESET%
) else (
    echo %YELLOW%⚠ Warning: Could not locate startup script%RESET%
)
echo.

REM =====================================================================
REM Step 8: Start Option Chain Monitor
REM =====================================================================
echo [STEP 8] Starting Option Chain Monitor...
echo.
echo =====================================================================
echo STARTING APPLICATION
echo =====================================================================
echo.

REM Run the option chain monitor
cd /d "%INSTALL_DIR%"
call "%PYTHON%" option_chain_monitor_api_simple.py

REM If execution reaches here, application was stopped
echo.
echo Application stopped.
exit /b 0
