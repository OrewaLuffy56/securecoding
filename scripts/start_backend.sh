#!/bin/bash
# Start the FastAPI backend

cd /app/backend

echo "🚀 Starting SecureScan.ai Backend..."
echo "Port: 8000"
echo "Supabase: Connected"
echo "Redis: Synchronous mode (no Redis available)"
echo ""

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
