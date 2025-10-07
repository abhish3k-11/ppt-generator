@echo off
echo 🏗️ Setting up Complete PPT Generator Infrastructure

REM Create directory structure
echo Creating directory structure...
mkdir "%~dp0..\infrastructure\redis" >nul 2>&1

REM Check Docker
echo Checking Docker Desktop...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Desktop is not running
    echo Please start Docker Desktop first
    pause
    exit /b 1
)

echo ✅ Docker is running!

REM Navigate to infrastructure
cd /d "%~dp0..\infrastructure"

echo 🐋 Starting complete infrastructure...
docker compose -f docker-compose.infrastructure.yml down >nul 2>&1
docker compose -f docker-compose.infrastructure.yml up -d

if %errorlevel% neq 0 (
    echo ❌ Failed to start infrastructure
    pause
    exit /b 1
)

echo ⏳ Waiting for all services to be ready (30 seconds)...
timeout /t 30

echo 📊 Infrastructure Status:
docker compose -f docker-compose.infrastructure.yml ps

echo.
echo 🎉 Complete Infrastructure Ready!
echo.
echo 🗄️ PostgreSQL:
echo    📍 Host: localhost:5432
echo    🗃️  Database: ppt_generator
echo    👤 User: ppt_admin
echo    🔑 Pass: SecurePass123!
echo.
echo 🚀 Redis:
echo    📍 Host: localhost:6379
echo    🔧 No password (development)
echo.
echo 🌐 Management Interfaces:
echo    📊 pgAdmin: http://localhost:5050
echo       👤 admin@pptgen.com / AdminPass123!
echo    🔧 Redis Commander: http://localhost:8081  
echo       👤 admin / RedisAdmin123!
echo.
echo 🧪 Test Commands:
echo    PostgreSQL: docker exec ppt-postgres pg_isready -U ppt_admin -d ppt_generator
echo    Redis: docker exec ppt-redis redis-cli ping
echo.

REM Test connections
echo 🔍 Testing connections...
docker exec ppt-postgres pg_isready -U ppt_admin -d ppt_generator
if %errorlevel% equ 0 (echo ✅ PostgreSQL is ready!) else (echo ⚠️ PostgreSQL might still be starting...)

docker exec ppt-redis redis-cli ping
if %errorlevel% equ 0 (echo ✅ Redis is ready!) else (echo ⚠️ Redis might still be starting...)

pause