@echo off
REM =====================================================================
REM Trading API Monitor - Quick Install and Run
REM =====================================================================

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set DIST_DIR=%SCRIPT_DIR%dist
set INSTALL_DIR=%SCRIPT_DIR%install_monitor_cli
set VENV_DIR=%INSTALL_DIR%\.venv
set PYTHON=%VENV_DIR%\Scripts\python.exe
set PIP=%VENV_DIR%\Scripts\pip.exe
set LOG_FILE=%SCRIPT_DIR%install_monitor_cli.log

REM Find tar.gz file (check both dist/ and project root)
set TARBALL=
if exist "%DIST_DIR%\trading_api_monitor-1.0.0.tar.gz" (
    set TARBALL=%DIST_DIR%\trading_api_monitor-1.0.0.tar.gz
) else if exist "%SCRIPT_DIR%trading_api_monitor-1.0.0.tar.gz" (
    set TARBALL=%SCRIPT_DIR%trading_api_monitor-1.0.0.tar.gz
)

echo.
echo =====================================================================
echo Trading API Monitor - CLI Entry Point Installation
echo =====================================================================
echo.

REM Check tar.gz exists
if "%TARBALL%"=="" (
    echo ERROR: tar.gz file not found!
    echo Searched in:
    echo   - %DIST_DIR%\trading_api_monitor-1.0.0.tar.gz
    echo   - %SCRIPT_DIR%trading_api_monitor-1.0.0.tar.gz
    echo Run: python -m build
    exit /b 1
)
echo [✓] Found distribution: %TARBALL%

REM Clean and create installation directory
if exist "%INSTALL_DIR%" (
    rmdir /s /q "%INSTALL_DIR%" >nul 2>&1
)
mkdir "%INSTALL_DIR%" >nul 2>&1
echo [✓] Created installation directory

REM Create virtual environment
cd /d "%INSTALL_DIR%"
python -m venv .venv >nul 2>&1
if not exist "%PYTHON%" (
    echo ERROR: Failed to create virtual environment
    exit /b 1
)
echo [✓] Created virtual environment

REM Upgrade pip
"%PIP%" install --upgrade pip >nul 2>&1
echo [✓] Upgraded pip

REM Install from tar.gz
echo Installing from tar.gz...

REM First, extract to a temporary location to get the local dependencies
mkdir "%INSTALL_DIR%\temp_extract" >nul 2>&1
tar -xzf "%TARBALL%" -C "%INSTALL_DIR%\temp_extract" >nul 2>&1

REM Install local dependencies first
echo Installing local dependencies...
"%PIP%" install "%INSTALL_DIR%\temp_extract\trading_api_monitor-1.0.0\client\libs\trading_api-1.0.0.tar.gz" >>"%LOG_FILE%" 2>&1
"%PIP%" install "%INSTALL_DIR%\temp_extract\trading_api_monitor-1.0.0\client\libs\nslogger-1.0.0.tar.gz" >>"%LOG_FILE%" 2>&1

REM Install main package from the extracted directory
"%PIP%" install "%INSTALL_DIR%\temp_extract\trading_api_monitor-1.0.0" >>"%LOG_FILE%" 2>&1

REM Copy the startup script to installation directory
copy "%INSTALL_DIR%\temp_extract\trading_api_monitor-1.0.0\option_chain_monitor_api_simple.py" "%INSTALL_DIR%\option_chain_monitor_api_simple.py" >nul 2>&1

REM Clean up temp extraction
rmdir /s /q "%INSTALL_DIR%\temp_extract" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Installation failed. Check %LOG_FILE%
    exit /b 1
)
echo [✓] Installed successfully

REM Copy config if exists
if exist "%SCRIPT_DIR%config.xml" (
    copy "%SCRIPT_DIR%config.xml" "%INSTALL_DIR%\config.xml" >nul 2>&1
    echo [✓] Copied configuration
)

REM Start application
echo.
echo =====================================================================
echo STARTING APPLICATION
echo =====================================================================
echo.

cd /d "%INSTALL_DIR%"
call "%PYTHON%" option_chain_monitor_api_simple.py

exit /b 0
