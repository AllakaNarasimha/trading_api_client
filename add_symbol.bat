@echo off
REM =====================================================================
REM Add Symbol to Option Chain Monitor
REM =====================================================================

setlocal enabledelayedexpansion

set API_URL=http://localhost:5000/api/add-symbol

echo.
echo =====================================================================
echo Adding Symbol to Option Chain Monitor
echo =====================================================================
echo API URL: %API_URL%
echo.

REM Add NSE:NIFTY50-INDEX
echo Adding NSE:NIFTY50-INDEX...
curl -X POST %API_URL% ^
  -H "Content-Type: application/json" ^
  -d "{\"symbol\": \"NSE:NIFTY50-INDEX\", \"poll_seconds\": [0, 30], \"strikes\": 15}"
echo.

echo =====================================================================
echo Symbol addition complete
echo =====================================================================
echo.

exit /b 0
