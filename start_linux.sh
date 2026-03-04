#!/bin/bash
(set -o igncr) 2>/dev/null && set -o igncr; # Fix for potential Windows line endings

echo "========================================================"
echo "  PENGUIN CLASSIFIER APP - LAUNCHER"
echo "========================================================"

# 1. Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "[ERROR] Docker is not running. Please start Docker Desktop."
  exit 1
fi

# 2. Check if App is already running
if [ "$(docker ps -q -f name=penguin-running)" ]; then
  echo "[INFO] The application is already running!"
  echo "[INFO] Opening a new browser window..."
  open "http://localhost:8050"
  exit 0
fi

# 3. Build Image
echo "[INFO] Building Docker Image..."
docker build -t penguin-app .

# 4. Open Browser (background wait)
(sleep 5 && open "http://localhost:8050") &

# 5. Run Container
echo "[INFO] App running at http://localhost:8050"
echo "[INFO] Press CTRL+C to stop."

docker run -p 8050:8050 \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/metrics:/app/metrics" \
  --rm \
  --name penguin-running \
  penguin-app
