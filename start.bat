@echo off
echo Starting Pitch Deck Analyzer...
echo.

echo [1/2] Starting Backend Server...
start "Backend" cmd /k "python -m uvicorn app.main:app --reload"

timeout /t 3 /nobreak > nul

echo [2/2] Starting Frontend Server...
cd frontend
start "Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo   Pitch Deck Analyzer is starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to stop all servers...
pause > nul

taskkill /FI "WindowTitle eq Backend*" /T /F
taskkill /FI "WindowTitle eq Frontend*" /T /F
