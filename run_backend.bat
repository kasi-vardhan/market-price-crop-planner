@echo off
title Market Price & Crop Planner - Backend
echo ========================================================
echo Starting Market Price & Crop Planner - FastAPI Backend
echo ========================================================
cd /d "%~dp0backend"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000
pause
