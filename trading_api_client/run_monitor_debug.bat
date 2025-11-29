@echo off
REM =====================================================================
REM Debug version - logs everything for troubleshooting
REM =====================================================================

setlocal enabledelayedexpansion

REM Log to a file in the same directory
set DEBUG_LOG=%~dp0debug_startup.log

echo. >> "%DEBUG_LOG%"
echo ===== START OF DEBUG LOG ===== >> "%DEBUG_LOG%"
echo Timestamp: %date% %time% >> "%DEBUG_LOG%"
echo Script location: %~f0 >> "%DEBUG_LOG%"
echo Current directory: %CD% >> "%DEBUG_LOG%"

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0
if "%SCRIPT_DIR:~-1%"=="\" set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

echo Script directory: %SCRIPT_DIR% >> "%DEBUG_LOG%"

set INSTALL_DIR=%SCRIPT_DIR%\install_monitor
set VENV_DIR=%INSTALL_DIR%\.venv
set PYTHON=%VENV_DIR%\Scripts\python.exe
set PYTHONW=%VENV_DIR%\Scripts\pythonw.exe

echo Install directory: %INSTALL_DIR% >> "%DEBUG_LOG%"
echo Venv directory: %VENV_DIR% >> "%DEBUG_LOG%"
echo Python path: %PYTHON% >> "%DEBUG_LOG%"

REM Check if paths exist
if exist "%SCRIPT_DIR%" (
    echo [OK] Script directory exists >> "%DEBUG_LOG%"
) else (
    echo [ERROR] Script directory NOT found >> "%DEBUG_LOG%"
)

if exist "%INSTALL_DIR%" (
    echo [OK] Install directory exists >> "%DEBUG_LOG%"
) else (
    echo [ERROR] Install directory NOT found >> "%DEBUG_LOG%"
)

if exist "%VENV_DIR%" (
    echo [OK] Venv directory exists >> "%DEBUG_LOG%"
) else (
    echo [ERROR] Venv directory NOT found >> "%DEBUG_LOG%"
)

if exist "%PYTHON%" (
    echo [OK] Python executable found >> "%DEBUG_LOG%"
) else (
    echo [ERROR] Python executable NOT found >> "%DEBUG_LOG%"
)

if exist "%INSTALL_DIR%\option_chain_monitor_api_simple.py" (
    echo [OK] Main script found >> "%DEBUG_LOG%"
) else (
    echo [ERROR] Main script NOT found >> "%DEBUG_LOG%"
)

echo. >> "%DEBUG_LOG%"
echo Now calling run_monitor.bat... >> "%DEBUG_LOG%"
echo. >> "%DEBUG_LOG%"

REM Call the main script
call "%SCRIPT_DIR%\run_monitor.bat" >> "%DEBUG_LOG%" 2>&1

echo. >> "%DEBUG_LOG%"
echo Run completed with exit code: %ERRORLEVEL% >> "%DEBUG_LOG%"
echo ===== END OF DEBUG LOG ===== >> "%DEBUG_LOG%"

exit /b %ERRORLEVEL%
