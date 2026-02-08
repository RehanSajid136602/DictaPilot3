#!/bin/bash
# DictaPilot One-Click Start for macOS
# This script can be copied anywhere and will run the app when double-clicked

set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Navigate to the project root (parent of portable-start folder)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if Python 3.10+ is available
if ! command -v python3 >/dev/null 2>&1; then
    echo "[ERROR] Python 3.10+ not found. Please install Python first."
    echo "Visit: https://www.python.org/downloads/"
    read -r -p "Press Enter to close..."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo "[ERROR] Python 3.10+ required, but found Python $PYTHON_VERSION"
    echo "Please install Python 3.10 or higher."
    read -r -p "Press Enter to close..."
    exit 1
fi

# Check if venv exists in the project root
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo "[ERROR] Virtual environment not found at: $PROJECT_ROOT/venv"
    echo ""
    echo "Please run the setup script first:"
    echo "  - On macOS: setup/setup_macos.command"
    echo ""
    read -r -p "Press Enter to close..."
    exit 1
fi

# Check if app.py exists
if [ ! -f "$PROJECT_ROOT/app.py" ]; then
    echo "[ERROR] app.py not found at: $PROJECT_ROOT/app.py"
    echo "Please ensure this portable-start folder is in the correct location."
    read -r -p "Press Enter to close..."
    exit 1
fi

# Activate venv and run the app
cd "$PROJECT_ROOT"
source "$PROJECT_ROOT/venv/bin/activate"

echo "Starting DictaPilot..."
python3 app.py

# If the app exits, keep window open briefly to see any errors
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "[ERROR] DictaPilot exited with error code: $EXIT_CODE"
    read -r -p "Press Enter to close..."
fi
