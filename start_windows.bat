@echo off
title Penguin Classifier Launcher
cls
echo ========================================================
echo   PENGUIN CLASSIFIER APP - LAUNCHER
echo ========================================================
echo.

REM 1. Check if Docker is running
docker info >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker Desktop is not running!
    echo Please start Docker Desktop and run this script again.
    echo.
    pause
    exit /b
)

REM 2. Check if App is ALREADY running
docker ps -q -f name=penguin-running | findstr . >nul
IF %ERRORLEVEL% EQU 0 (
    echo [INFO] The application is already running!
    echo [INFO] Opening a new browser window...
    start "" "http://localhost:8050"
    REM end script here as app is already running
    exit /b
)

REM 3. Build Docker Image
echo [INFO] Building Docker Image (ensuring latest code)...
docker build -t penguin-app .

REM 4. Start Container
echo.
echo [INFO] App is starting...
echo [INFO] Opening browser...

start "" "http://localhost:8050"

REM Run Command (mounts data folder)
docker run -p 8050:8050 -v "%cd%/data:/app/data" -v "%cd%/metrics:/app/metrics" --rm --name penguin-running penguin-app

pause
