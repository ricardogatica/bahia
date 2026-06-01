#!/bin/bash
# Installation script for Ports App - macOS port monitor

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "╔═══════════════════════════════════╗"
echo "║   PORTS APP - Installation        ║"
echo "║   macOS Port Monitor TUI          ║"
echo "╚═══════════════════════════════════╝"
echo ""

# Detect Python
echo -n "🔍 Detecting Python... "
if command -v python3 &> /dev/null; then
    PYTHON=$(command -v python3)
    PYTHON_VERSION=$($PYTHON --version 2>&1)
    echo -e "${GREEN}✓${NC}"
    echo "   Found: $PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON=$(command -v python)
    PYTHON_VERSION=$($PYTHON --version 2>&1)
    echo -e "${GREEN}✓${NC}"
    echo "   Found: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC}"
    echo ""
    echo -e "${RED}ERROR: Python 3 not found!${NC}"
    echo ""
    echo "Install Python 3 from: https://www.python.org/downloads/"
    echo "Or using Homebrew:"
    echo "  brew install python3"
    echo ""
    exit 1
fi

# Check pip
echo -n "🔍 Detecting pip... "
if $PYTHON -m pip --version &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "Trying to install pip..."
    $PYTHON -m ensurepip --upgrade
fi

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo ""
echo "📦 Installing dependencies..."
echo "   Installing: textual"

if $PYTHON -m pip install -q textual; then
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    echo -e "${RED}✗${NC} Failed to install dependencies"
    echo "Try manually:"
    echo "  $PYTHON -m pip install textual"
    exit 1
fi

# Make scripts executable
echo ""
echo "🔐 Setting permissions..."
chmod +x "$SCRIPT_DIR/ports_app.py" 2>/dev/null || true
chmod +x "$SCRIPT_DIR/ports-app" 2>/dev/null || true
chmod +x "$SCRIPT_DIR/install.sh" 2>/dev/null || true
echo -e "${GREEN}✓${NC} Made scripts executable"

# Try to install globally
echo ""
echo -n "🌍 Installing globally... "
if cd "$SCRIPT_DIR" && $PYTHON -m pip install -e . -q 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    GLOBAL_INSTALL=true
else
    echo -e "${YELLOW}⚠${NC} (optional, can still run locally)"
    GLOBAL_INSTALL=false
fi

# Summary
echo ""
echo "╔═══════════════════════════════════╗"
echo "║   Installation Complete! ✓        ║"
echo "╚═══════════════════════════════════╝"
echo ""

if [ "$GLOBAL_INSTALL" = true ]; then
    echo "Run from anywhere:"
    echo -e "  ${GREEN}ports-app${NC}"
else
    echo "Run from project directory:"
    echo -e "  ${GREEN}$PYTHON ports_app.py${NC}"
    echo ""
    echo "Or:"
    echo -e "  ${GREEN}./ports-app${NC}"
fi

echo ""
echo "Controls in app:"
echo "  ↑↓   Navigate"
echo "  k    Kill process"
echo "  r    Refresh"
echo "  q    Quit"
echo ""
echo -e "${GREEN}Happy monitoring!${NC}"
echo ""
