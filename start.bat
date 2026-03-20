@echo off
echo Starting Resume Analyzer...

:: ── Backend ──────────────────────────────────────────────────────────────
start "Backend - FastAPI" cmd /k "cd /d "%~dp0backend" && uvicorn resume_analyzer:app --reload --port 8000"

:: Wait 3 seconds for backend to initialize before starting frontend
timeout /t 3 /nobreak >nul

:: ── Frontend ─────────────────────────────────────────────────────────────
start "Frontend - Vite" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo Both servers are starting:
echo   Backend  ^>  http://localhost:8000
echo   Frontend ^>  http://localhost:5173
echo.
echo Press any key to exit this window (servers will keep running)...
pause >nul
