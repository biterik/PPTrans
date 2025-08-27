#!/bin/bash

# Development setup script for PPTrans

set -e  # Exit on error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🛠️  PPTrans Development Setup"
echo "============================"
echo "Project root: $PROJECT_ROOT"

cd "$PROJECT_ROOT"

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed or not in PATH"
    echo "Please install Miniconda or Anaconda first"
    exit 1
fi

echo "✅ Conda found: $(conda --version)"

# Create conda environment
echo "🔧 Creating conda environment from environment.yml..."
if conda env list | grep -q "pptrans"; then
    echo "⚠️  Environment 'pptrans' already exists"
    read -p "Do you want to remove it and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        conda env remove -n pptrans -y
    else
        echo "Using existing environment"
        exit 0
    fi
fi

conda env create -f environment.yml

echo "✅ Development environment setup completed!"
echo "🚀 Next steps:"
echo "1. conda activate pptrans"
echo "2. Add the remaining source files"
echo "3. python src/main.py"