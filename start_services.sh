#!/bin/bash
# Starts everything needed for the full system: Ollama, the ingestion
# scheduler, the backend API, and the frontend dev server.
# Safe to run every time you reopen this Codespace - each check
# detects if a service is already running before starting a new one,
# so re-running this never creates duplicates or loses progress.

echo "=== Checking Ollama ==="
if curl -s http://localhost:11434 > /dev/null; then
    echo "Ollama already running."
else
    echo "Starting Ollama..."
    ollama serve > /tmp/ollama.log 2>&1 &
    sleep 3
    if curl -s http://localhost:11434 > /dev/null; then
        echo "Ollama started successfully."
    else
        echo "WARNING: Ollama did not start correctly - check /tmp/ollama.log"
    fi
fi

echo ""
echo "=== Checking ingestion + AI scheduler ==="
if pgrep -f "python3 -u scheduler.py" > /dev/null; then
    echo "Scheduler already running."
else
    echo "Starting scheduler..."
    cd /workspaces/ai-innovation-observatory/backend/app/ingestion
    nohup python3 -u scheduler.py > /tmp/scheduler.log 2>&1 &
    echo "Scheduler started with PID: $!"
fi

echo ""
echo "=== Checking backend API (port 8000) ==="
if curl -s http://localhost:8000/ > /dev/null; then
    echo "Backend API already running."
else
    echo "Starting backend API..."
    cd /workspaces/ai-innovation-observatory
    nohup uvicorn backend.app.api.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/api.log 2>&1 &
    sleep 2
    if curl -s http://localhost:8000/ > /dev/null; then
        echo "Backend API started successfully."
    else
        echo "WARNING: Backend API did not start correctly - check /tmp/api.log"
    fi
fi

echo ""
echo "=== Checking frontend (port 5173) ==="
if curl -s http://localhost:5173/ > /dev/null; then
    echo "Frontend already running."
else
    echo "Starting frontend..."
    cd /workspaces/ai-innovation-observatory/frontend
    nohup npm run dev -- --host 0.0.0.0 > /tmp/frontend.log 2>&1 &
    sleep 3
    if curl -s http://localhost:5173/ > /dev/null; then
        echo "Frontend started successfully."
    else
        echo "WARNING: Frontend did not start correctly - check /tmp/frontend.log"
    fi
fi

echo ""
echo "=== All checks complete ==="
echo "Logs: /tmp/ollama.log  /tmp/scheduler.log  /tmp/api.log  /tmp/frontend.log"
echo "Use: tail -f /tmp/<name>.log   to watch any of them live"
