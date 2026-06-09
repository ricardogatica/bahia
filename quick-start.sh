#!/bin/bash
# Quick start script - minimal version

echo "Starting Bahia..."
echo ""

# Try different ways to run Python
if command -v python3 &> /dev/null; then
    python3 bahia.py
elif command -v python &> /dev/null; then
    python bahia.py
else
    echo "Error: Python not found"
    exit 1
fi
