#!/bin/bash
# Renko Trading Bot - Complete Startup Script
# This script starts all services: Backend API, Frontend, and Trading Strategy

set -e

PROJECT_DIR="/home/username/renko"  # Change this to your VPS path
PYTHON_ENV="$PROJECT_DIR/.venv"
LOG_DIR="$PROJECT_DIR/logs"

# Create logs directory
mkdir -p "$LOG_DIR"

echo "🤖 Starting Renko Trading Bot..."
echo "================================"

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/startup.log"
}

# Check Python environment
if [ ! -f "$PYTHON_ENV/bin/activate" ]; then
    log "❌ Python environment not found at $PYTHON_ENV"
    exit 1
fi

# Activate Python environment
source "$PYTHON_ENV/bin/activate"
log "✅ Python environment activated"

# Change to project directory
cd "$PROJECT_DIR"

# Start Backend API
log "Starting Backend API on port 8000..."
nohup python -m uvicorn backend.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2 \
    > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
log "✅ Backend API started (PID: $BACKEND_PID)"

# Wait for backend to be ready
log "Waiting for backend to start..."
sleep 3

# Check if backend is running
if ! curl -s http://localhost:8000/api/tickers > /dev/null; then
    log "❌ Backend failed to start"
    exit 1
fi
log "✅ Backend API is responding"

# Start Trading Strategy (Worker)
log "Starting Trading Strategy Worker..."
nohup python backend/worker.py \
    > "$LOG_DIR/worker.log" 2>&1 &
WORKER_PID=$!
log "✅ Trading Worker started (PID: $WORKER_PID)"

# Start Frontend
log "Starting Frontend on port 5173..."
cd "$PROJECT_DIR/frontend"
nohup npm run preview \
    --host 0.0.0.0 \
    --port 5173 \
    > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
log "✅ Frontend started (PID: $FRONTEND_PID)"

# Save PIDs for shutdown script
echo $BACKEND_PID > "$LOG_DIR/backend.pid"
echo $WORKER_PID > "$LOG_DIR/worker.pid"
echo $FRONTEND_PID > "$LOG_DIR/frontend.pid"

log "================================"
log "✨ All services started successfully!"
log "Backend:  http://localhost:8000"
log "Frontend: http://localhost:5173"
log "================================"

# Keep script running
tail -f "$LOG_DIR/startup.log"
