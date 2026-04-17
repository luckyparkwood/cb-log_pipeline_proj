#!/bin/bash

echo "Starting log pipeline..."

# activate venv
source venv/bin/activate

# start Redis (ignore error if already running)
brew services start redis >/dev/null 2>&1

# start API
echo "Starting API..."
uvicorn app.api:app --reload &
API_PID=$!

# start worker
echo "Starting worker..."
python -m app.worker &
WORKER_PID=$!

# start generator
echo "Starting generator..."
python -m app.generator &
GEN_PID=$!

echo "All services started."
echo "API PID: $API_PID"
echo "Worker PID: $WORKER_PID"
echo "Generator PID: $GEN_PID"

echo "Press Ctrl+C to stop everything."

# wait for user interrupt
trap "echo 'Stopping...'; kill $API_PID $WORKER_PID $GEN_PID; exit" INT

wait
