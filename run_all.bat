@echo off
title Market Price & Crop Planner - Runner
echo ========================================================
echo Starting Market Price & Crop Planner (Backend + Frontend)
echo ========================================================

start "Backend Server" cmd /k "cd /d %~dp0 && call run_backend.bat"
timeout /t 3 /nobreak >nul
start "Frontend Dev" cmd /k "cd /d %~dp0 && call run_frontend.bat"

echo.
echo Both servers are launching in separate windows:
echo - Backend API:  http://127.0.0.1:8000
echo - Frontend App: http://localhost:5173
echo.
pause
