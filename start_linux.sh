#!/bin/bash
cd "$(dirname "$0")" || exit 1
(set -o igncr) 2>/dev/null && set -o igncr;

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
  echo "[INFO] Opening browser..."
  open "http://localhost:8050"
  echo ""
  echo "========================================================"
  echo "  App is running at http://localhost:8050"
  echo "  To stop the app, run: docker stop penguin-running"
  echo "========================================================"
  read -r -p "Press Enter to close this window..."
  exit 0
fi

# 3. Clean up old container
docker rm -f penguin-running 2>/dev/null

# 4. Build Image
echo "[INFO] Building Docker Image..."
if ! docker build -t penguin-app .; then
  echo "[ERROR] Docker build failed."
  exit 1
fi

# 5. Wait for app in background, then open browser
(
  for i in {1..60}; do
    if curl -s http://localhost:8050 > /dev/null 2>&1; then
      open "http://localhost:8050"
      break
    fi
    sleep 2
  done
) &

# 6. Run Container
echo "[INFO] App starting at http://localhost:8050"
echo "[INFO] Press CTRL+C to stop."

docker run \
  -p 8050:8050 \
  -v "$(pwd)/data/raw:/app/data/raw" \
  -v "$(pwd)/data/processed:/app/data/processed" \
  -v "$(pwd)/models:/app/models" \
  -v "$(pwd)/metrics:/app/metrics" \
  --rm \
  --name penguin-running \
  penguin-app
