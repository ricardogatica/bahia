#!/bin/bash
# Quick start script - minimal version

echo "Starting Ports App..."
echo ""

# Try different ways to run Python
if command -v python3 &> /dev/null; then
    python3 ports_app.py
elif command -v python &> /dev/null; then
    python ports_app.py
else
    echo "Error: Python not found"
    exit 1
fi
