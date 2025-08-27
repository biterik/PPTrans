#!/bin/bash

# PPTrans Build Script for Unix/macOS
# Usage: ./build.sh [mac|linux]

set -e  # Exit on error

PLATFORM=${1:-"auto"}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist"
BUILD_DIR="$PROJECT_ROOT/build"

echo "🚀 PPTrans Build Script"
echo "======================="
echo "Platform: $PLATFORM"
echo "Project root: $PROJECT_ROOT"
echo ""

# Detect platform if auto
if [ "$PLATFORM" = "auto" ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        PLATFORM="mac"
    else
        PLATFORM="linux"
    fi
    echo "Auto-detected platform: $PLATFORM"
fi

# Check if conda environment is active
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "❌ Error: Conda environment not active"
    echo "Please run: conda activate pptrans"
    exit 1
fi

echo "✅ Conda environment active: $CONDA_DEFAULT_ENV"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf "$DIST_DIR" "$BUILD_DIR"
mkdir -p "$DIST_DIR"

# Change to project directory
cd "$PROJECT_ROOT"

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run tests
echo "🧪 Running tests..."
if [ -d "tests" ]; then
    python -m pytest tests/ -v || {
        echo "❌ Tests failed"
        exit 1
    }
    echo "✅ Tests passed"
else
    echo "⚠️  No tests directory found, skipping tests"
fi

# Select spec file based on platform
if [ "$PLATFORM" = "mac" ]; then
    SPEC_FILE="pyinstaller_spec/pptrans_mac.spec"
elif [ "$PLATFORM" = "linux" ]; then
    SPEC_FILE="pyinstaller_spec/pptrans_linux.spec"
else
    echo "❌ Unsupported platform: $PLATFORM"
    exit 1
fi

if [ ! -f "$SPEC_FILE" ]; then
    echo "❌ Spec file not found: $SPEC_FILE"
    exit 1
fi

echo "🔨 Building with PyInstaller..."
echo "Using spec file: $SPEC_FILE"

# Build with PyInstaller
pyinstaller --clean --noconfirm "$SPEC_FILE"

# Check if build was successful
if [ ! -d "$DIST_DIR/PPTrans" ]; then
    echo "❌ Build failed - output directory not found"
    exit 1
fi

echo "✅ Build completed successfully!"
echo "📁 Output directory: $DIST_DIR/PPTrans"

# Create a zip archive
echo "📦 Creating distribution archive..."
cd "$DIST_DIR"

if [ "$PLATFORM" = "mac" ]; then
    ARCHIVE_NAME="PPTrans-macOS-$(uname -m).zip"
    zip -r "$ARCHIVE_NAME" PPTrans/
elif [ "$PLATFORM" = "linux" ]; then
    ARCHIVE_NAME="PPTrans-Linux-$(uname -m).tar.gz"
    tar -czf "$ARCHIVE_NAME" PPTrans/
fi

echo "✅ Archive created: $DIST_DIR/$ARCHIVE_NAME"

# Display build information
echo ""
echo "🎉 Build Summary"
echo "================"
echo "Platform: $PLATFORM"
echo "Archive: $ARCHIVE_NAME"
echo "Size: $(du -h "$ARCHIVE_NAME" | cut -f1)"
echo "Location: $DIST_DIR"
echo ""

# Test the executable
echo "🧪 Testing executable..."
if [ "$PLATFORM" = "mac" ]; then
    "$DIST_DIR/PPTrans/PPTrans" --version || echo "⚠️  Version test failed, but executable exists"
elif [ "$PLATFORM" = "linux" ]; then
    "$DIST_DIR/PPTrans/PPTrans" --version || echo "⚠️  Version test failed, but executable exists"
fi

echo "✅ Build process completed successfully!"
echo ""
echo "To test the application:"
if [ "$PLATFORM" = "mac" ]; then
    echo "  cd '$DIST_DIR/PPTrans' && ./PPTrans"
elif [ "$PLATFORM" = "linux" ]; then
    echo "  cd '$DIST_DIR/PPTrans' && ./PPTrans"
fi