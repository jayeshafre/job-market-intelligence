@echo off

echo ========================================
echo Starting Frontend and Backend Servers...
echo ========================================

:: Start Backend
start cmd /k "cd backend && venv\Scripts\activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

:: Start Frontend
start cmd /k "cd frontend && npm run dev"

echo ========================================
echo Servers Started Successfully
echo ========================================

pause