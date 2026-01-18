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

REM Set bootstrap file from argument or default
if "%*"=="" (
    set bootstrap_file=option_chain_monitor_api_simple.py
) else (
    set bootstrap_file=%*
)

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
REM Step 5b: Install bundled custom packages
REM =====================================================================
echo [STEP 5b] Installing bundled custom packages ^(nslogger, trading_api^)...

REM Find where the package was installed and install bundled tar.gz files
call "%PYTHON%" -c "import sys; from pathlib import Path; import subprocess; import client; libs_dir = Path(client.__file__).parent / 'libs'; print(f'Found libs at: {libs_dir}'); packages = ['nslogger-1.0.0.tar.gz', 'trading_api-1.0.0.tar.gz']; [(print(f'\nInstalling {f}...'), subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--no-deps', str(libs_dir / f)])) for f in packages if (libs_dir / f).exists()]"

if errorlevel 1 (
    echo %RED%ERROR: Failed to install custom packages%RESET%
    exit /b 1
)

REM Verify custom packages installed
call "%PYTHON%" -c "import nslogger; import trading_api" >nul 2>&1
if errorlevel 1 (
    echo %RED%ERROR: Custom packages not installed correctly%RESET%
    exit /b 1
)
echo %GREEN%✓ Custom packages installed successfully%RESET%
echo.

REM =====================================================================
REM Step 6: Verify installation
REM =====================================================================
echo [STEP 6] Verifying installation...
call "%PYTHON%" -c "import client, nslogger, trading_api; print('All modules OK')" >nul 2>&1

if errorlevel 1 (
    echo %RED%ERROR: Module verification failed%RESET%
    exit /b 1
) else (
    echo %GREEN%✓ All modules verified successfully%RESET%
)
echo.

REM =====================================================================
REM Step 7: Copy configuration files
REM =====================================================================
echo [STEP 7] Checking configuration files...

REM Define files to copy from project directory
set files_to_copy=config.xml config.dir option_chain_monitor_api_simple.py

REM Loop through files and copy if they exist
for %%f in (%files_to_copy%) do (
    if exist "%SCRIPT_DIR%%%f" (        
        copy /Y "%SCRIPT_DIR%%%f" "%INSTALL_DIR%\%%f" >nul 2>&1
        if errorlevel 1 (
            echo %RED%✗ Failed to copy %SCRIPT_DIR%%%f - file in use to %INSTALL_DIR%\%%f - %RESET%
            echo Failed to copy from %SCRIPT_DIR%%%f to %INSTALL_DIR%\%%f >> "%LOG_FILE%"
        ) else (
            echo %GREEN%✓ Copied %SCRIPT_DIR%%%f from project to %INSTALL_DIR%\%%f - %RESET% 
            echo Copied %%f from %SCRIPT_DIR%%%f to %INSTALL_DIR%\%%f >> "%LOG_FILE%"
        )
    ) else (
        echo %YELLOW%⚠ %%f not found in project - using package defaults%RESET%
        echo %%f not found in project - using package defaults >> "%LOG_FILE%"
    )
)
echo.

REM =====================================================================
REM Step 8: Start Monitor
REM =====================================================================
REM echo [STEP 8] Starting monitor with bootstrap_file: %bootstrap_file%...
REM echo.
REM echo =====================================================================
REM echo STARTING APPLICATION
REM echo =====================================================================
REM echo.
REM 
REM cd /d "%INSTALL_DIR%"
REM if "%bootstrap_file:~0,2%"=="-m" (
REM     call "%PYTHON%" %bootstrap_file%
REM ) else (
REM     call "%PYTHON%" %bootstrap_file%
REM )
REM 
REM echo.
REM echo Application stopped.
exit /b 0