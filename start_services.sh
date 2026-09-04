#!/bin/bash
# Starts Ollama and the ingestion+AI scheduler in the background.
# Safe to run every time you reopen this Codespace - the scheduler
# always checks for new/unprocessed records rather than duplicating
# work, so re-running this after a restart just resumes progress.

echo "Checking Ollama..."
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

echo "Checking scheduler..."
if pgrep -f "python3 scheduler.py" > /dev/null; then
    echo "Scheduler already running."
else
    echo "Starting scheduler..."
    cd /workspaces/ai-innovation-observatory/backend/app/ingestion
    nohup python3 -u scheduler.py > /tmp/scheduler.log 2>&1 &
    echo "Scheduler started with PID: $!"
fi

echo ""
echo "Done. To watch live progress: tail -f /tmp/scheduler.log"
