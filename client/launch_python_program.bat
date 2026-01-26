@echo off
REM This batch file is copied to the .venv site-packages directory
REM So we use ABSOLUTE PATHS to the actual project directory (D:\NS\trading_api_client)
setlocal enabledelayedexpansion

REM Get the absolute directory where this batch file is located
set SCRIPT_DIR=%~dp0
REM Navigate to parent directory to get project root
cd /d "%SCRIPT_DIR%.."
set PROJECT_ROOT=%cd%
set CLIENT_DIR=%PROJECT_ROOT%\client
set LOGFILE=logs\launch_log.txt

REM Create logs directory if it doesn't exist
if not exist "logs" (
    mkdir "logs"
)

REM Log script start
echo [%date% %time%] Starting launch script >> "%LOGFILE%"
echo [%date% %time%] Client directory: %CLIENT_DIR% >> "%LOGFILE%"
echo [%date% %time%] SCRIPT_DIR: %SCRIPT_DIR% >> "%LOGFILE%"

REM Find Python executable - try multiple locations
set PYTHON_EXE=
for %%X in (python.exe pythonw.exe) do (
    for /f "delims=" %%Y in ('where %%X 2^>nul') do set PYTHON_EXE=%%Y
    if defined PYTHON_EXE goto :found_python
)

if not defined PYTHON_EXE (
    echo [%date% %time%] ERROR: Python executable not found in PATH >> "%LOGFILE%"
    echo ERROR: Python executable not found in PATH. Please ensure Python is installed and added to PATH.
    goto :end
)

:found_python
REM Use python.exe for better error reporting (not pythonw.exe which hides errors)
set PYTHON_EXE=python.exe

REM Change to project root directory
cd /d "D:\NS\trading_api_client"

REM Command to run the specific module
set COMMAND=-m client.live_data_fetch_controller

REM Log the command being executed
echo [%date% %time%] Python executable: %PYTHON_EXE% >> "%LOGFILE%"
echo [%date% %time%] Command: %COMMAND% >> "%LOGFILE%"
echo [%date% %time%] Expected working directory: D:\NS\trading_api_client >> "%LOGFILE%"
echo [%date% %time%] Launching %COMMAND% >> "%LOGFILE%"
echo Launching %COMMAND% with %PYTHON_EXE%...

REM Launch the Python module
call "%PYTHON_EXE%" %COMMAND% >> "%LOGFILE%" 2>&1
set ERRORLEVEL_VAL=%errorlevel%

REM Log the result
if %ERRORLEVEL_VAL% equ 0 (
    echo [%date% %time%] Module executed successfully >> "%LOGFILE%"
    echo Module executed successfully.
) else (
    echo [%date% %time%] ERROR: Module execution failed with exit code %ERRORLEVEL_VAL% >> "%LOGFILE%"
    echo ERROR: Module execution failed with exit code %ERRORLEVEL_VAL%. Check log file for details.
)

:end
echo [%date% %time%] Script finished >> "%LOGFILE%"
echo Log file: "%LOGFILE%"

endlocal