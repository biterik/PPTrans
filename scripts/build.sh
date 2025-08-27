#!/bin/bash

# PPTrans Build Script for Unix/macOS
# Usage: ./build.sh [mac|linux]

set -e  # Exit on error

PLATFORM=${1:-"auto"}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🚀 PPTrans Build Script"
echo "======================="
echo "Platform: $PLATFORM"
echo "Project root: $PROJECT_ROOT"

# Check if conda environment is active
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "❌ Error: Conda environment not active"
    echo "Please run: conda activate pptrans"
    exit 1
fi

echo "✅ Conda environment active: $CONDA_DEFAULT_ENV"
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Build script executed successfully!"
echo "ℹ️  Add PyInstaller specs and complete source code to enable full builds"