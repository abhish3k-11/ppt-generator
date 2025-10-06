@echo off
echo Checking Docker Desktop status...

:CHECK_DOCKER
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Desktop is not running.
    echo.
    echo 🔧 Please start Docker Desktop:
    echo    1. Open Start Menu
    echo    2. Search "Docker Desktop"
    echo    3. Right-click and "Run as Administrator"
    echo    4. Wait for the whale icon in system tray
    echo.
    echo ⏳ Waiting for Docker Desktop to start...
    timeout /t 10
    goto CHECK_DOCKER
)

echo ✅ Docker Desktop is running!
goto :EOF