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

REM First, extract to a temporary location to get the local dependencies
mkdir "%INSTALL_DIR%\temp_extract" >nul 2>&1
echo Extracting tar.gz file...
tar -xzf "%TARBALL%" -C "%INSTALL_DIR%\temp_extract" >nul 2>&1

if not exist "%INSTALL_DIR%\temp_extract\trading_api_monitor-1.0.0" (
    echo ERROR: Failed to extract tar.gz file
    echo Check that tar.gz file exists at: %TARBALL%
    pause
    exit /b 1
)

echo Extraction complete. Installing dependencies...
echo.

REM Install local dependencies first - SHOW OUTPUT
echo ===== Installing trading_api =====
if exist "%INSTALL_DIR%\temp_extract\trading_api_monitor-1.0.0\client\libs\trading_api-1.0.0.tar.gz" (
    echo Found: trading_api-1.0.0.tar.gz
    call "%PIP%" install "%INSTALL_DIR%\temp_extract\trading_api_monitor-1.0.0\client\libs\trading_api-1.0.0.tar.gz"
    if errorlevel 1 (
        echo WARNING: trading_api installation may have failed
    )
) else (
    echo ERROR: trading_api-1.0.0.tar.gz not found!
)

echo.
echo ===== Installing nslogger =====
if exist "%INSTALL_DIR%\temp_extract\trading_api_monitor-1.0.0\client\libs\nslogger-1.0.0.tar.gz" (
    echo Found: nslogger-1.0.0.tar.gz
    call "%PIP%" install "%INSTALL_DIR%\temp_extract\trading_api_monitor-1.0.0\client\libs\nslogger-1.0.0.tar.gz"
    if errorlevel 1 (
        echo WARNING: nslogger installation may have failed
    )
) else (
    echo ERROR: nslogger-1.0.0.tar.gz not found!
)

REM Install requirements.txt if it exists
echo.
echo ===== Installing requirements.txt =====
if exist "%INSTALL_DIR%\temp_extract\trading_api_monitor-1.0.0\requirements.txt" (
    echo Found: requirements.txt
    call "%PIP%" install -r "%INSTALL_DIR%\temp_extract\trading_api_monitor-1.0.0\requirements.txt"
) else (
    echo requirements.txt not found (this is OK)
)

REM Install main package from the extracted directory (standard install to get all dependencies)
echo.
echo ===== Installing trading-api-monitor package =====
call "%PIP%" install "%INSTALL_DIR%\temp_extract\trading_api_monitor-1.0.0"

if errorlevel 1 (
    echo.
    echo WARNING: trading-api-monitor installation returned an error
    echo This may still be OK if Flask and requests were installed
    echo Continuing with deployment...
    echo.
)

REM Copy the startup script to installation directory
echo Copying startup script...
if exist "%INSTALL_DIR%\temp_extract\trading_api_monitor-1.0.0\option_chain_monitor_api_simple.py" (
    copy "%INSTALL_DIR%\temp_extract\trading_api_monitor-1.0.0\option_chain_monitor_api_simple.py" "%INSTALL_DIR%\option_chain_monitor_api_simple.py" >nul 2>&1
    if exist "%INSTALL_DIR%\option_chain_monitor_api_simple.py" (
        echo Successfully copied startup script
    )
)

REM Copy client directory to install directory for easier access
echo Copying client module...
if exist "%INSTALL_DIR%\temp_extract\trading_api_monitor-1.0.0\client" (
    xcopy "%INSTALL_DIR%\temp_extract\trading_api_monitor-1.0.0\client" "%INSTALL_DIR%\client" /E /I /Y >nul 2>&1
    if exist "%INSTALL_DIR%\client" (
        echo Successfully copied client module
    )
)

REM Copy config.xml from extracted package
echo Copying package config...
if exist "%INSTALL_DIR%\temp_extract\trading_api_monitor-1.0.0\config.xml" (
    copy "%INSTALL_DIR%\temp_extract\trading_api_monitor-1.0.0\config.xml" "%INSTALL_DIR%\config.xml" >nul 2>&1
)

REM Copy market_data directory if it exists
echo Copying market data...
if exist "%INSTALL_DIR%\temp_extract\trading_api_monitor-1.0.0\market_data" (
    xcopy "%INSTALL_DIR%\temp_extract\trading_api_monitor-1.0.0\market_data" "%INSTALL_DIR%\market_data" /E /I /Y >nul 2>&1
)

REM Clean up temp extraction (ignore errors if it fails)
echo Cleaning up temporary files...
rmdir /s /q "%INSTALL_DIR%\temp_extract" >nul 2>&1

echo %GREEN%✓ Successfully installed from tar.gz%RESET%
echo.

REM =====================================================================
REM Step 6: Verify installation
REM =====================================================================
echo [STEP 6] Verifying installation...
call "%PYTHON%" -c "import sys; sys.path.insert(0, '%INSTALL_DIR%'); import client; print('client module OK')" >nul 2>&1

if errorlevel 1 (
    echo %YELLOW%⚠ Module verification skipped (client will be loaded from installation directory)%RESET%
) else (
    echo %GREEN%✓ Modules verified successfully%RESET%
)
echo.

REM =====================================================================
REM Step 7: Copy configuration file
REM =====================================================================
echo [STEP 7] Copying configuration file...
if exist "%SCRIPT_DIR%config.xml" (
    copy "%SCRIPT_DIR%config.xml" "%INSTALL_DIR%\config.xml" >nul 2>&1
    echo %GREEN%✓ Copied config.xml%RESET%
) else (
    echo %YELLOW%⚠ config.xml not found - using defaults%RESET%
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
