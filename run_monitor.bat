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

REM Check for lock file to prevent concurrent runs
if exist "%SCRIPT_DIR%\run_monitor.lock" (
    echo [%date% %time%] Another instance is running, killing processes and removing lock >> "%LOG_FILE%"
    taskkill /f /im pythonw.exe /t 2>nul
    taskkill /f /im python.exe /t 2>nul
    del "%SCRIPT_DIR%\run_monitor.lock" >nul 2>&1
)
echo [%date% %time%] Creating lock file >> "%LOG_FILE%"
echo %date% %time% > "%SCRIPT_DIR%\run_monitor.lock"

echo run monitor log="%LOG_FILE%"

REM Bootstrap files will be read from args.txt by launch_monitor.bat
REM No need to set bootstrap_file here

REM Create log directory if it doesn't exist
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM =====================================================================
REM Logging function - append to log file with timestamp
REM =====================================================================

REM Log startup information
echo. >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"
echo [%date% %time%] Task Scheduler startup initiated >> "%LOG_FILE%"
echo Script Directory: %SCRIPT_DIR% >> "%LOG_FILE%"
echo Install Directory: %INSTALL_DIR% >> "%LOG_FILE%"
echo Log File: %LOG_FILE% >> "%LOG_FILE%"
echo ========================================== >> "%LOG_FILE%"

REM =====================================================================
REM Kill any existing Python processes (runs every time)
REM =====================================================================
echo [%date% %time%] Stopping any running Python processes >> "%LOG_FILE%"
taskkill /f /im pythonw.exe /t 2>nul
taskkill /f /im python.exe /t 2>nul
echo [%date% %time%] Process termination completed >> "%LOG_FILE%"

REM =====================================================================
REM Determine if installation/reinstall is needed
REM =====================================================================

REM Load REINSTALL flag from args.txt with retry mechanism for file locking
set REINSTALL_REQUESTED=false
if exist "%SCRIPT_DIR%\args.txt" (
    echo [%date% %time%] Reading REINSTALL flag from args.txt >> "%LOG_FILE%"
    
    REM Try to copy file to temp and read from temp to avoid locking issues
    set "TEMP_ARGS=%TEMP%\args_temp_%RANDOM%.txt"
    copy /Y "%SCRIPT_DIR%\args.txt" "%TEMP_ARGS%" >nul 2>&1
    if exist "%TEMP_ARGS%" (
        for /f "delims=" %%a in ('powershell -Command "try { Get-Content '%TEMP_ARGS%' | Select-String 'REINSTALL=' | ForEach-Object { ($_.Line.Split('=')[1]).Trim() } } catch { exit 1 }" 2^>nul') do (
            set "REINSTALL_REQUESTED=%%a"
            goto :READ_REINSTALL_SUCCESS
        )
        del "%TEMP_ARGS%" >nul 2>&1
    )
    
    :READ_REINSTALL_SUCCESS
    echo [%date% %time%] Successfully read REINSTALL flag >> "%LOG_FILE%"
)
echo [%date% %time%] REINSTALL requested from args.txt: !REINSTALL_REQUESTED! >> "%LOG_FILE%"

REM Check if venv exists
set VENV_EXISTS=false
if exist "%VENV_DIR%" (
    set VENV_EXISTS=true
    echo [%date% %time%] Virtual environment found at: %VENV_DIR% >> "%LOG_FILE%"
) else (
    echo [%date% %time%] Virtual environment not found at: %VENV_DIR% >> "%LOG_FILE%"
)

REM Determine if we need to install/reinstall
set NEED_INSTALL=false
if "!REINSTALL_REQUESTED!"=="true" (
    set NEED_INSTALL=true
    echo [%date% %time%] Install triggered: REINSTALL flag set to true >> "%LOG_FILE%"
)
if "!VENV_EXISTS!"=="false" (
    set NEED_INSTALL=true
    echo [%date% %time%] Install triggered: Virtual environment not found >> "%LOG_FILE%"
)

REM Handle installation/reinstall if needed
if "!NEED_INSTALL!"=="true" (
    echo [%date% %time%] ========== STARTING INSTALLATION ========== >> "%LOG_FILE%"
    
    REM Uninstall package if venv exists and reinstall was requested
    if "!REINSTALL_REQUESTED!"=="true" (
        if "!VENV_EXISTS!"=="true" (
            if exist "%PIP%" (
                echo [%date% %time%] Uninstalling trading-api-monitor... >> "%LOG_FILE%"
                call "%PIP%" uninstall trading-api-monitor -y >> "%LOG_FILE%" 2>&1
                echo [%date% %time%] Uninstall completed >> "%LOG_FILE%"
            ) else (
                echo [%date% %time%] WARNING: pip not found at %PIP%, skipping uninstall >> "%LOG_FILE%"
            )
        )
    )
    
    REM Run installer
    echo [%date% %time%] Executing install_and_run.bat >> "%LOG_FILE%"
    call "%SCRIPT_DIR%\install_and_run.bat" >> "%LOG_FILE%" 2>&1
    set EXIT_CODE=!ERRORLEVEL!
    echo [%date% %time%] Installation completed with exit code: !EXIT_CODE! >> "%LOG_FILE%"
    REM exit /b !EXIT_CODE!
)

echo [%date% %time%] Installation not required, proceeding with monitor startup >> "%LOG_FILE%"

REM Define files to copy from project directory
set files_to_copy=config.xml config.dir

REM Loop through files and copy if they exist
for %%f in (%files_to_copy%) do (
    if exist "%SCRIPT_DIR%%%f" (        
        copy /Y "%SCRIPT_DIR%%%f" " %INSTALL_DIR%\%%f" >nul 2>&1
        if errorlevel 1 (
            echo %RED%✗ Failed to copy %%f - file in use to %INSTALL_DIR%\%%f - %RESET%
            echo Failed to copy %%f to %INSTALL_DIR%\%%f >> "%LOG_FILE%"
        ) else (
            echo %GREEN%✓ Copied %%f from project to %INSTALL_DIR%\%%f - %RESET% 
            echo Copied %%f from %SCRIPT_DIR%%%f to %INSTALL_DIR%\%%f >> "%LOG_FILE%"
        )
    ) else (
        echo %YELLOW%⚠ %%f not found in project - using package defaults%RESET%
        echo %%f not found in project - using package defaults >> "%LOG_FILE%"
    )
)
echo.

cd /d "%INSTALL_DIR%"
echo [%date% %time%] Changed directory to: %CD% >> "%LOG_FILE%"

REM Wait before launching monitor
echo [%date% %time%] Waiting 20 seconds before launching monitor process >> "%LOG_FILE%"
timeout /t 10 /nobreak >nul
echo [%date% %time%] Delay completed, launching monitor >> "%LOG_FILE%"

REM Launch the monitor process
echo [%date% %time%] Calling launch_monitor.bat >> "%LOG_FILE%"
call "%SCRIPT_DIR%\launch_monitor.bat" >> "%LOG_FILE%" 2>&1
set EXIT_CODE=!ERRORLEVEL!
echo [%date% %time%] launch_monitor.bat completed with exit code: !EXIT_CODE! >> "%LOG_FILE%"

REM Remove lock file
del "%SCRIPT_DIR%\run_monitor.lock" >nul 2>&1

exit /b !EXIT_CODE!
