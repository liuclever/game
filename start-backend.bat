@echo off
echo ========================================
echo    Game Backend Server
echo ========================================
echo.

echo [1/2] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)
python --version
echo.

echo [2/2] Starting Flask backend...
echo Backend URL: http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

python -m interfaces.web_api.app

pause
