#!/usr/bin/env bash
#
# Build script for macOS
# Creates a single-file DictaPilot binary using PyInstaller spec file
#

set -e

echo "=== DictaPilot macOS Build ==="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found. Please install Python 3.10+"
    exit 1
fi

# Install PyInstaller if needed
echo "Ensuring PyInstaller is installed..."
python3 -m pip install pyinstaller --quiet 2>/dev/null || true

# Clean previous build
if [ -d "dist" ]; then
    echo "Cleaning previous build..."
    rm -rf dist build
fi

# Build using spec file
echo "Building DictaPilot..."
python3 -m PyInstaller packaging/DictaPilot.spec --clean --noconfirm

if [ $? -eq 0 ]; then
    echo ""
    echo "=== Build Complete ===" 
    echo "Output: dist/DictaPilot"
    echo ""
    echo "To create release zip:"
    echo "  cd dist && zip -r DictaPilot-macos-x64.zip DictaPilot && cd .."
else
    echo "Build failed!"
    exit 1
fi