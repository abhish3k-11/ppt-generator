@echo off
echo 🐋 PPT Generator - PostgreSQL Setup

REM Check if Docker is running
call "%~dp0wait-for-docker.bat"
if %errorlevel% neq 0 (
    echo ❌ Cannot proceed without Docker Desktop
    pause
    exit /b 1
)

REM Navigate to postgres config directory
cd /d "%~dp0..\infrastructure\postgres"

echo 📦 Starting PostgreSQL and pgAdmin containers...
docker compose -f docker-compose.postgres.yml up -d

if %errorlevel% neq 0 (
    echo ❌ Failed to start containers
    echo 🔍 Checking Docker logs...
    docker compose -f docker-compose.postgres.yml logs
    pause
    exit /b 1
)

echo ⏳ Waiting for services to initialize...
timeout /t 15

echo 📊 Container Status:
docker compose -f docker-compose.postgres.yml ps

echo.
echo 🎉 PostgreSQL Setup Complete!
echo.
echo 🌐 pgAdmin Web Interface:
echo    URL: http://localhost:5050
echo    Email: admin@pptgen.com
echo    Password: AdminPass123!
echo.
echo 🗄️ Database Connection:
echo    Host: localhost
echo    Port: 5432
echo    Database: ppt_generator
echo    Username: ppt_admin
echo    Password: SecurePass123!
echo.
echo 🔍 Commands:
echo    View logs: docker compose -f docker-compose.postgres.yml logs
echo    Stop services: docker compose -f docker-compose.postgres.yml down

pause