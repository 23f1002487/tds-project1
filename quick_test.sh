#!/bin/bash
# Quick restart and test script

echo "🔄 Starting server restart and test sequence..."

# Kill any existing uvicorn processes
echo "🔪 Killing existing uvicorn processes..."
pkill -f "uvicorn.*app:app" || echo "No existing uvicorn processes found"
sleep 2

# Start the server in background
echo "🚀 Starting server..."
cd /home/vSaketh/TDS/Project/tds-p1-web-app-generator
nohup python -m uvicorn src.app:app --host 0.0.0.0 --port 7860 > server.log 2>&1 &
SERVER_PID=$!
echo "Server started with PID: $SERVER_PID"

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 5

# Test health endpoint
echo "🏥 Testing health endpoint..."
curl -s http://localhost:7860/health | python -m json.tool

# Test simple task
echo -e "\n🧪 Testing simple task..."
curl -s -X POST "http://localhost:7860/process_task" \
  -H "Content-Type: application/json" \
  -d @simple_test.json

echo -e "\n📝 Recent server logs:"
tail -10 server.log

echo -e "\n📋 Recent task logs:"
tail -5 task_log.txt