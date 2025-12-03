@echo off
REM Quick start script for Legal Act Tracker

echo.
echo ================================================================================
echo LEGAL ACT TRACKER - QUICK START
echo ================================================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found
    echo Run INSTALL.bat first
    pause
    exit /b 1
)

REM Run main tests
echo Running tests and validation...
echo.
python main.py

if %errorlevel% neq 0 (
    echo ERROR: Tests failed
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo STARTING API SERVER
echo ================================================================================
echo.
echo Server starting on http://localhost:8000/docs
echo Press Ctrl+C to stop
echo.

python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload

pause
