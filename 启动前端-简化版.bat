@echo off
echo ========================================
echo Starting Frontend Service...
echo ========================================
echo.

cd interfaces\client

if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
    echo.
)

echo Starting Vite dev server...
echo Frontend URL: http://localhost:5173
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

npm run dev

pause
