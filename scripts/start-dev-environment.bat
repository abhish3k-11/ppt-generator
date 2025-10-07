@echo off
echo 🚀 PPT Generator - Complete Development Environment Setup

echo.
echo 📋 Starting development environment in order:
echo    1. Infrastructure (PostgreSQL + Redis)
echo    2. API Gateway (FastAPI)
echo    3. Frontend (Next.js)
echo.

REM Start infrastructure
echo 🏗️ Step 1: Starting Infrastructure...
call "%~dp0setup-infrastructure.bat"
if %errorlevel% neq 0 (
    echo ❌ Infrastructure startup failed
    pause
    exit /b 1
)

echo.
echo ⏳ Waiting for infrastructure to be ready...
timeout /t 10

REM Start API Gateway in background
echo 🚪 Step 2: Starting API Gateway...
start "PPT Generator - API Gateway" cmd /k "cd /d %~dp0..\backend\gateway && call venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo ⏳ Waiting for API Gateway to start...
timeout /t 5

REM Start Frontend
echo 🌐 Step 3: Starting Frontend...
cd /d "%~dp0..\frontend"
start "PPT Generator - Frontend" cmd /k "npm run dev"

echo.
echo 🎉 Development Environment Started!
echo.
echo 🌐 Services Running:
echo    💾 PostgreSQL:     localhost:5432
echo    🚀 Redis:          localhost:6379  
echo    🚪 API Gateway:    http://localhost:8000
echo    🌐 Frontend:       http://localhost:3000
echo.
echo 📊 Management Interfaces:
echo    📊 pgAdmin:        http://localhost:5050
echo    🔧 Redis Commander: http://localhost:8081
echo    📚 API Docs:       http://localhost:8000/docs
echo.

pause
