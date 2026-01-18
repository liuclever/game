@echo off
echo ========================================
echo    Game Frontend Server
echo ========================================
echo.

echo [1/3] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)
node --version
echo.

echo [2/3] Checking frontend directory...
if not exist "interfaces\client" (
    echo [ERROR] Frontend directory not found: interfaces\client
    pause
    exit /b 1
)
echo Frontend directory: interfaces\client
echo.

echo [3/3] Starting Vite dev server...
echo Frontend URL: http://localhost:5173
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

cd interfaces\client
npm run dev

pause
