@echo off
echo Starting AI Safety Platform...

echo Starting Backend Server (Port 8001)...
start "Backend Server" cmd /k "cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001"

echo Starting Frontend Server (Port 5173)...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo Done! Servers are launching in separate windows.
echo Frontend: http://localhost:5173
echo Backend: http://localhost:8001/docs
pause
