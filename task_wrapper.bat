@echo off
REM =====================================================================
REM Task Scheduler Wrapper - Absolute Path Version
REM Place this in D:\Test\ and point Task Scheduler to it
REM =====================================================================

setlocal enabledelayedexpansion

REM Use full absolute path - DO NOT use relative paths
set BATCH_FILE=D:\Test\run_monitor.bat

REM Log file
set LOG_FILE=D:\Test\task_scheduler.log

echo. >> "%LOG_FILE%"
echo ===== TASK SCHEDULER STARTUP ===== >> "%LOG_FILE%"
echo Timestamp: %date% %time% >> "%LOG_FILE%"
echo User: %USERNAME% >> "%LOG_FILE%"
echo Computer: %COMPUTERNAME% >> "%LOG_FILE%"
echo Batch file: %BATCH_FILE% >> "%LOG_FILE%"

REM Check if batch file exists
if exist "%BATCH_FILE%" (
    echo [OK] Batch file found >> "%LOG_FILE%"
    echo Executing: %BATCH_FILE% >> "%LOG_FILE%"
    call "%BATCH_FILE%"
    echo Exit code: %ERRORLEVEL% >> "%LOG_FILE%"
) else (
    echo [ERROR] Batch file NOT found at: %BATCH_FILE% >> "%LOG_FILE%"
    exit /b 1
)

echo ===== END OF TASK SCHEDULER LOG ===== >> "%LOG_FILE%"
exit /b 0
