@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
  set "PYTHON=.venv\Scripts\python.exe"
) else if exist "venv\Scripts\python.exe" (
  set "PYTHON=venv\Scripts\python.exe"
) else (
  set "PYTHON=python"
)

echo Starting API on http://127.0.0.1:8000
echo Starting frontend on http://127.0.0.1:5173
echo Close each window to stop that process.

start "TCG API" cmd /k ""%PYTHON%" -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000"

pushd frontend
start "TCG Frontend" cmd /k "npm run dev"
popd
endlocal
