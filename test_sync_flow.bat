@echo off
echo.
echo =====================================================================
echo TESTING COMPLETE DEPENDENCY SYNC FLOW
echo =====================================================================
echo.

echo [TEST 1] Checking current state...
echo.

dir /b "client\libs\*.tar.gz" 2>nul
if errorlevel 1 (
    echo No tar.gz files found in client\libs
) else (
    echo Current tar.gz files in client\libs:
    for %%f in ("client\libs\*.tar.gz") do (
        echo   %%~nxf - %%~zf bytes
    )
)

echo.
echo [TEST 2] Running dependency sync...
echo.

call sync_dependencies.bat

echo.
echo [TEST 3] Verifying results...
echo.

echo Libraries in client\libs after sync:
dir /b "client\libs\*.tar.gz" 2>nul
if errorlevel 1 (
    echo [ERROR] No tar.gz files found after sync!
) else (
    echo.
    echo File details:
    for %%f in ("client\libs\*.tar.gz") do (
        echo   %%~nxf - %%~zf bytes - %%~tf
    )
)

echo.
echo [TEST 4] Checking pyproject.toml updates...
echo.

findstr /C:"protobuf" pyproject.toml >nul
if errorlevel 1 (
    echo [WARNING] protobuf dependency not found in pyproject.toml
) else (
    echo [OK] protobuf dependency found in pyproject.toml
)

findstr /C:"googleapis-common-protos" pyproject.toml >nul
if errorlevel 1 (
    echo [WARNING] googleapis-common-protos dependency not found in pyproject.toml
) else (
    echo [OK] googleapis-common-protos dependency found in pyproject.toml
)

echo.
echo =====================================================================
echo TEST COMPLETE
echo =====================================================================
echo.
pause