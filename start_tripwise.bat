@echo off
title TripWise - Smart Travel Planner Server
echo ========================================================
echo   TripWise - Smart Travel Planner
echo ========================================================
echo.

cd /d "%~dp0backend"

REM Check if Python virtual environment exists
if exist ".venv\Scripts\python.exe" (
    echo [OK] Using virtual environment in backend\.venv
    set "PY_CMD=.venv\Scripts\python.exe"
) else (
    echo [*] Checking global Python...
    where python >nul 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] Python was not found on your system!
        echo Please install Python 3.10+ from https://www.python.org/
        pause
        exit /b 1
    )
    set "PY_CMD=python"
)

echo [*] Starting TripWise server on http://localhost:8080...
echo [*] Press Ctrl+C in this window anytime to stop the server.
echo.

REM Automatically open browser after 2 seconds
start "" cmd /c "timeout /t 2 >nul & start http://localhost:8080/app"

REM Run the FastAPI server
"%PY_CMD%" run.py

pause
