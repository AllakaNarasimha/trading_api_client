@echo off
REM =====================================================================
REM IMPORTANT: Start the Trading API Monitor from HERE
REM =====================================================================

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set INSTALL_DIR=%SCRIPT_DIR%install_monitor

echo.
echo =====================================================================
echo TRADING API MONITOR - START HERE
echo =====================================================================
echo.
echo Current Directory: %CD%
echo Script Location: %SCRIPT_DIR%
echo Install Location: %INSTALL_DIR%
echo.

REM Check if already installed
if exist "%INSTALL_DIR%\option_chain_monitor_api_simple.py" (
    echo Starting existing installation...
    cd /d "%INSTALL_DIR%"
    call "%INSTALL_DIR%\.venv\Scripts\python.exe" option_chain_monitor_api_simple.py
    exit /b 0
)

REM If not installed, check for args.txt and reinstall flag
if exist "%SCRIPT_DIR%args.txt" (
    for /f "tokens=2 delims==" %%A in (findstr /I "REINSTALL" "%SCRIPT_DIR%args.txt") do (
        set REINSTALL=%%A
    )
)

if /i "%REINSTALL%"=="true" (
    echo REINSTALL flag detected. Running full installation...
    call "%SCRIPT_DIR%install_and_run.bat"
    exit /b !ERRORLEVEL!
) else (
    echo.
    echo ERROR: Application not yet installed!
    echo.
    echo To install, either:
    echo 1. Set REINSTALL=true in args.txt and run this script again
    echo 2. Run: install_and_run.bat
    echo.
    pause
    exit /b 1
)
