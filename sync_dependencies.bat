@echo off
setlocal enabledelayedexpansion

echo.
echo =====================================================================
echo Dependency Synchronization and Rebuild Tool
echo =====================================================================
echo.

set "PROJECT_ROOT=%~dp0"
set "LIBS_DIR=%PROJECT_ROOT%client\libs"
set "MAIN_PYPROJECT=%PROJECT_ROOT%pyproject.toml"
set "PYTHON_CMD=python"

%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH
    pause
    exit /b 1
)

echo [STEP 1] Analyzing bundled library dependencies...
echo.

if not exist "%LIBS_DIR%" (
    echo [WARNING] No libs directory found at: %LIBS_DIR%
    mkdir "%LIBS_DIR%"
)

echo [STEP 2] Running dependency analysis and sync...
%PYTHON_CMD% "%PROJECT_ROOT%analyze_and_sync_deps.py" "%LIBS_DIR%" "%MAIN_PYPROJECT%"

if errorlevel 1 (
    echo [ERROR] Dependency analysis failed
    pause
    exit /b 1
)

echo.
echo =====================================================================
echo Synchronization Complete!
echo =====================================================================
echo.
pause