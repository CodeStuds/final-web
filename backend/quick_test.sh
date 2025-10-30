#!/bin/bash
# Quick test script to verify backend services

echo "======================================================"
echo "  HireSight Backend Services - Quick Test"
echo "======================================================"

# Kill any existing server
pkill -f "python.*api.py" 2>/dev/null
sleep 1

# Start server in background with API keys disabled
echo "Starting API server..."
export API_KEYS_ENABLED=false
cd "$(dirname "$0")"
python api.py > /dev/null 2>&1 &
SERVER_PID=$!

# Wait for server to start
echo "Waiting for server to start..."
sleep 3

# Check if server is running
if ! ps -p $SERVER_PID > /dev/null; then
    echo "❌ Server failed to start"
    exit 1
fi

echo "✅ Server started (PID: $SERVER_PID)"

# Run tests
echo ""
echo "Running tests..."
python test_api.py

TEST_RESULT=$?

# Cleanup
echo ""
echo "Stopping server..."
kill $SERVER_PID 2>/dev/null
sleep 1

if [ $TEST_RESULT -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    exit 0
else
    echo ""
    echo "⚠️  Some tests failed - check output above"
    exit 1
fi
