@echo off
REM =====================================================================
REM Trading API Monitor - Hidden Background Runner
REM For use with Windows Task Scheduler (starts without console window)
REM =====================================================================

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set INSTALL_DIR=%SCRIPT_DIR%install_monitor
set VENV_DIR=%INSTALL_DIR%\.venv
set PYTHON=%VENV_DIR%\Scripts\pythonw.exe
set LOG_DIR=%INSTALL_DIR%\logs
set LOG_FILE=%LOG_DIR%\monitor.log

REM Create logs directory if it doesn't exist
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Change to installation directory
cd /d "%INSTALL_DIR%"

REM Run Python with pythonw (no console window)
REM Redirect output to log file
if exist "%PYTHON%" (
    start "" "%PYTHON%" -m app >>"%LOG_FILE%" 2>&1
) else (
    REM Fallback if pythonw not available
    "%VENV_DIR%\Scripts\python.exe" -m app >>"%LOG_FILE%" 2>&1
)

exit /b 0
