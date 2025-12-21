@echo off
REM =====================================================================
REM Trading API Monitor - Simple Runner (Task Scheduler Compatible)
REM =====================================================================
REM This script works with Windows Task Scheduler even when logged out
REM Logs all activity to install_monitor.log for debugging
REM =====================================================================

setlocal enabledelayedexpansion

REM Get the directory where this batch file is located (works from Task Scheduler)
set SCRIPT_DIR=%~dp0
if "%SCRIPT_DIR:~-1%"=="\" set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

set INSTALL_DIR=%SCRIPT_DIR%\install_monitor
set VENV_DIR=%INSTALL_DIR%\.venv
set PYTHON=%VENV_DIR%\Scripts\python.exe
set PYTHONW=%VENV_DIR%\Scripts\pythonw.exe
set PIP=%VENV_DIR%\Scripts\pip.exe
set REINSTALL=false
set LOG_FILE=%SCRIPT_DIR%\install_monitor.log

REM Create log directory if it doesn't exist
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM =====================================================================
REM Logging function - append to log file with timestamp
REM =====================================================================
setlocal enabledelayedexpansion

REM Log startup information
echo. >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"
echo [%date% %time%] Task Scheduler startup initiated >> "%LOG_FILE%"
echo Script Directory: %SCRIPT_DIR% >> "%LOG_FILE%"
echo Install Directory: %INSTALL_DIR% >> "%LOG_FILE%"
echo Log File: %LOG_FILE% >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"

REM Load REINSTALL from args.txt
if exist "%SCRIPT_DIR%\args.txt" (
    findstr /I "REINSTALL=true" "%SCRIPT_DIR%\args.txt" >nul 2>&1
    if not errorlevel 1 (
        set REINSTALL=true
        echo [%date% %time%] REINSTALL=true detected in args.txt >> "%LOG_FILE%"
    ) else (
        echo [%date% %time%] REINSTALL=false (not in args.txt) >> "%LOG_FILE%"
    )
) else (
    echo [%date% %time%] args.txt not found >> "%LOG_FILE%"
)

REM If REINSTALL is true, uninstall package first
if "%REINSTALL%"=="true" (
    echo [%date% %time%] Starting reinstall process >> "%LOG_FILE%"
    if exist "%VENV_DIR%" (
        echo [%date% %time%] Found existing venv at: %VENV_DIR% >> "%LOG_FILE%"
        if exist "%PIP%" (
            echo [%date% %time%] Uninstalling trading-api-monitor... >> "%LOG_FILE%"
            call "%PIP%" uninstall trading-api-monitor -y >> "%LOG_FILE%" 2>&1
            echo [%date% %time%] Uninstall completed >> "%LOG_FILE%"
        ) else (
            echo [%date% %time%] ERROR: pip not found at %PIP% >> "%LOG_FILE%"
        )
    ) else (
        echo [%date% %time%] No existing venv found >> "%LOG_FILE%"
    )
    echo [%date% %time%] Calling install_and_run.bat >> "%LOG_FILE%"
    call "%SCRIPT_DIR%\install_and_run.bat" >> "%LOG_FILE%" 2>&1
    set EXIT_CODE=!ERRORLEVEL!
    echo [%date% %time%] install_and_run.bat completed with exit code: !EXIT_CODE! >> "%LOG_FILE%"
    exit /b !EXIT_CODE!
)

REM Check if installation exists
if not exist "%VENV_DIR%" (
    echo [%date% %time%] Installation not found at: %VENV_DIR% >> "%LOG_FILE%"
    echo [%date% %time%] Running installer >> "%LOG_FILE%"
    call "%SCRIPT_DIR%\install_and_run.bat" >> "%LOG_FILE%" 2>&1
    set EXIT_CODE=!ERRORLEVEL!
    echo [%date% %time%] install_and_run.bat completed with exit code: !EXIT_CODE! >> "%LOG_FILE%"
    exit /b !EXIT_CODE!
) else (
    echo [%date% %time%] Installation found at: %VENV_DIR% >> "%LOG_FILE%"
)

REM Copy config if needed
if exist "%SCRIPT_DIR%\config.xml" (
    if not exist "%INSTALL_DIR%\config.xml" (
        copy "%SCRIPT_DIR%\config.xml" "%INSTALL_DIR%\config.xml" >nul 2>&1
        echo [%date% %time%] Copied config.xml from %SCRIPT_DIR% >> "%LOG_FILE%"
    ) else (
        echo [%date% %time%] config.xml already exists >> "%LOG_FILE%"
    )
) else (
    echo [%date% %time%] WARNING: config.xml not found in %SCRIPT_DIR% >> "%LOG_FILE%"
)

REM Check if the main script exists
if not exist "%INSTALL_DIR%\option_chain_monitor_api_simple.py" (
    echo [ERROR %date% %time%] option_chain_monitor_api_simple.py not found in %INSTALL_DIR% >> "%LOG_FILE%"
    exit /b 1
) else (
    echo [%date% %time%] Found option_chain_monitor_api_simple.py >> "%LOG_FILE%"
)

cd /d "%INSTALL_DIR%"
echo [%date% %time%] Changed directory to: %CD% >> "%LOG_FILE%"

REM Verify Python exists before running
if not exist "%PYTHON%" (
    echo [ERROR %date% %time%] Python executable not found at: %PYTHON% >> "%LOG_FILE%"
    echo [ERROR %date% %time%] Venv may not be properly installed >> "%LOG_FILE%"
    exit /b 1
) else (
    echo [%date% %time%] Python found at: %PYTHON% >> "%LOG_FILE%"
)

echo [%date% %time%] Starting monitor process >> "%LOG_FILE%"

if exist "%PYTHONW%" (
    echo [%date% %time%] Using pythonw.exe for silent background execution >> "%LOG_FILE%"
    start "" /min /b "%PYTHONW%" "%INSTALL_DIR%\option_chain_monitor_api_simple.py"
    echo [%date% %time%] Process started with pythonw.exe (PID will be in background) >> "%LOG_FILE%"
) else (
    echo [%date% %time%] pythonw.exe not found at: %PYTHONW% >> "%LOG_FILE%"
    echo [%date% %time%] Using python.exe instead >> "%LOG_FILE%"
    start "" /b "%PYTHON%" "%INSTALL_DIR%\option_chain_monitor_api_simple.py"
    echo [%date% %time%] Process started with python.exe >> "%LOG_FILE%"
)

echo [%date% %time%] Monitor process started successfully >> "%LOG_FILE%"
echo [%date% %time%] Application log file: %INSTALL_DIR%\monitor_output.log >> "%LOG_FILE%"
echo [%date% %time%] Script execution complete >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"

exit /b 0
