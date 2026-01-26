@echo off
setlocal

set "DEPLOY_DIR=D:\OCCollector"
set "TEMP_FOLDER=%USERPROFILE%\.trading_api_client_temp"
set "files=dist\trading_api_monitor-1.0.0.tar.gz run_monitor.bat install_and_run.bat launch_monitor.bat args.txt config.dir config.xml option_chain_monitor_api_simple.py"

echo Cleaning up temp folder...
if exist "%TEMP_FOLDER%" (
    echo Deleting temp folder: %TEMP_FOLDER%
    rmdir /s /q "%TEMP_FOLDER%"
    echo Temp folder deleted.
) else (
    echo Temp folder does not exist: %TEMP_FOLDER%
)

if not exist "%DEPLOY_DIR%" (
    mkdir "%DEPLOY_DIR%"
    echo Created %DEPLOY_DIR%
) else (
    echo Clearing existing files in %DEPLOY_DIR%...
    del "%DEPLOY_DIR%\*.log"
    for %%f in (%files%) do (
        del "%DEPLOY_DIR%\%%~nxf"
    )
    echo delete completed.
)

echo Copying distribution files to %DEPLOY_DIR%...
for %%f in (%files%) do (
    copy "%%f" "%DEPLOY_DIR%\"
)
echo Copy complete.

icacls "%DEPLOY_DIR%" | find "Everyone:(F)" >nul
if errorlevel 1 (
    echo Setting full permissions on %DEPLOY_DIR%...
    icacls "%DEPLOY_DIR%" /grant Everyone:F /T
)

echo Killing any existing pythonw.exe processes...
taskkill /f /im python.exe /t 2>nul
taskkill /f /im pythonw.exe /t 2>nul
echo Existing processes killed (if any).

echo Running run_monitor.bat...
powershell -Command "Start-Process '%DEPLOY_DIR%\run_monitor.bat' -Verb RunAs -WindowStyle Hidden"

endlocal
echo Done.