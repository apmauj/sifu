@echo off
echo Starting SIFU Server...
echo.

REM Set environment variables
set SIFU_SKIP_BOOTSTRAP=1

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Start the server
echo Starting FastAPI server on port 8003...
uvicorn main:app --host 127.0.0.1 --port 8003 --log-level info --reload

echo.
echo Server stopped.
pause
