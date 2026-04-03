@echo off
title Penguin Classifier Launcher
cd /d "%~dp0"
cls

echo ========================================================
echo   PENGUIN CLASSIFIER APP - LAUNCHER
echo ========================================================

REM 1. Check if Docker is running
docker info >nul 2>&1
if %ERRORLEVEL% neq 0 (
  echo [ERROR] Docker is not running. Please start Docker Desktop.
  pause
  exit /b 1
)

REM 2. Check if App is already running
set "APP_RUNNING="
for /f %%i in ('docker ps -q -f name^=penguin-running') do set APP_RUNNING=%%i
if defined APP_RUNNING (
  echo [INFO] The application is already running!
  echo [INFO] Opening browser...
  start "" "http://localhost:8050"
  echo.
  echo ========================================================
  echo   App is running at http://localhost:8050
  echo   To stop the app, run: docker stop penguin-running
  echo ========================================================
  set /p "DUMMY=Press Enter to close this window..."
  exit /b 0
)

REM 3. Clean up old container
docker rm -f penguin-running >nul 2>&1

REM 4. Build Image
echo [INFO] Building Docker Image...
docker build -t penguin-app .
if %ERRORLEVEL% neq 0 (
  echo [ERROR] Docker build failed.
  pause
  exit /b 1
)

REM 5. Wait for app in background, then open browser
REM Executes an asynchronous sub-process to poll the server
start /b cmd /c "for /l %%x in (1, 1, 60) do (curl -s http://localhost:8050 >nul 2>&1 && (start """" "http://localhost:8050" & exit) || timeout /t 2 >nul)"

REM 6. Run Container
echo [INFO] App starting at http://localhost:8050
echo [INFO] Press CTRL+C to stop.

docker run ^
  -p 8050:8050 ^
  -v "%cd%\data\raw:/app/data/raw" ^
  -v "%cd%\data\processed:/app/data/processed" ^
  -v "%cd%\models:/app/models" ^
  -v "%cd%\metrics:/app/metrics" ^
  --rm ^
  --name penguin-running ^
  penguin-app