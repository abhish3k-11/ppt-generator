@echo off
echo 🚀 Starting PPT Generator API Gateway

REM Check if infrastructure is running
echo Checking infrastructure...
docker ps | findstr ppt-postgres >nul
if %errorlevel% neq 0 (
    echo ❌ PostgreSQL not running. Starting infrastructure...
    call "%~dp0setup-infrastructure.bat"
)

docker ps | findstr ppt-redis >nul
if %errorlevel% neq 0 (
    echo ❌ Redis not running. Starting infrastructure...
    call "%~dp0setup-infrastructure.bat"
)

echo ✅ Infrastructure is running

REM Navigate to gateway directory
cd /d "%~dp0..\backend\gateway"

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    copy ".env.example" ".env"
)

echo.
echo 🌟 Starting FastAPI Gateway...
echo 📍 API Documentation: http://localhost:8000/docs
echo 🏥 Health Check: http://localhost:8000/health
echo 🔐 Auth Endpoints: http://localhost:8000/api/auth
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
