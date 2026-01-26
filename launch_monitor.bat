@echo off
REM =====================================================================
REM Monitor Process Launcher
REM Starts bootstrap processes sequentially, then launches live processes
REM in parallel
REM =====================================================================

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
if "%SCRIPT_DIR:~-1%"=="\" set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

set INSTALL_DIR=%SCRIPT_DIR%\install_monitor
set VENV_DIR=%INSTALL_DIR%\.venv
set PYTHON=%VENV_DIR%\Scripts\python.exe
set PYTHONW=%VENV_DIR%\Scripts\pythonw.exe
set LOG_FILE=%SCRIPT_DIR%\install_monitor.log
set CONFIG_FILE=%SCRIPT_DIR%\args.txt

echo [%date% %time%] Launch monitor started
cd /d "%INSTALL_DIR%"

if not exist "%PYTHON%" (
    echo [ERROR %date% %time%] Python not found at: %PYTHON%
    exit /b 1
)

set BOOTSTRAP_LIST=
set LIVE_LIST=

if exist "%CONFIG_FILE%" (
    for /f "tokens=*" %%a in ('findstr "BOOTSTRAP_LIST=" "%CONFIG_FILE%"') do (
        set "LINE=%%a"
        for /f "tokens=2 delims==" %%x in ("!LINE!") do (
            set "BOOTSTRAP_LIST=%%x"
        )
    )
    for /f "tokens=*" %%b in ('findstr "LIVE_LIST=" "%CONFIG_FILE%"') do (
        set "LINE=%%b"
        for /f "tokens=2 delims==" %%y in ("!LINE!") do (
            set "LIVE_LIST=%%y"
        )
    )
)

REM Parse lists into arrays by semicolon delimiter
set "bootstrap_count=0"
set "live_count=0"
set "bootstrap_item="
set "live_item="

REM Parse BOOTSTRAP_LIST
if not "!BOOTSTRAP_LIST!"=="" (
    for /l %%i in (0,1,255) do (
        set "char=!BOOTSTRAP_LIST:~%%i,1!"
        if "!char!"=="" goto :BOOTSTRAP_DONE
        if "!char!"==";" (
            if defined bootstrap_item (
                set /a "bootstrap_count+=1"
                set "bootstrap_list[!bootstrap_count!]=!bootstrap_item!"
                set "bootstrap_item="
            )
        ) else if "!bootstrap_item!"=="" (
            if not "!char!"==" " set "bootstrap_item=!char!"
        ) else (
            set "bootstrap_item=!bootstrap_item!!char!"
        )
    )
    :BOOTSTRAP_DONE
    if defined bootstrap_item (
        set /a "bootstrap_count+=1"
        set "bootstrap_list[!bootstrap_count!]=!bootstrap_item!"
    )
)

REM Parse LIVE_LIST
if not "!LIVE_LIST!"=="" (
    for /l %%j in (0,1,255) do (
        set "char=!LIVE_LIST:~%%j,1!"
        if "!char!"=="" goto :LIVE_DONE
        if "!char!"==";" (
            if defined live_item (
                set /a "live_count+=1"
                set "live_list[!live_count!]=!live_item!"
                set "live_item="
            )
        ) else if "!live_item!"=="" (
            if not "!char!"==" " set "live_item=!char!"
        ) else (
            set "live_item=!live_item!!char!"
        )
    )
    :LIVE_DONE
    if defined live_item (
        set /a "live_count+=1"
        set "live_list[!live_count!]=!live_item!"
    )
)

echo [%date% %time%] Bootstrap processes: !bootstrap_count!
echo [%date% %time%] Live processes: !live_count!

timeout /t 10 /nobreak >nul

REM =====================================================================
REM Start BOOTSTRAP processes SEQUENTIALLY (wait for each one)
REM =====================================================================
for /l %%i in (1,1,!bootstrap_count!) do (
    echo [%date% %time%] Bootstrap %%i/!bootstrap_count!: !bootstrap_list[%%i]!
    "%PYTHONW%" !bootstrap_list[%%i]!
    echo [%date% %time%] Bootstrap %%i completed
)

REM =====================================================================
REM Start LIVE processes IN PARALLEL (no waiting)
REM =====================================================================
if !live_count! gtr 0 (
    echo [%date% %time%] Starting live processes in parallel
    for /l %%j in (1,1,!live_count!) do (
        echo [%date% %time%] Launching live %%j/!live_count!: !live_list[%%j]!
        start "" /b "%PYTHONW%" !live_list[%%j]!
    )
)

echo [%date% %time%] All processes launched
exit /b 0