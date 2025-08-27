@echo off
REM PPTrans Build Script for Windows

echo 🚀 PPTrans Build Script for Windows
echo ===================================

if "%CONDA_DEFAULT_ENV%"=="" (
    echo ❌ Error: Conda environment not active
    echo Please run: conda activate pptrans
    exit /b 1
)

echo ✅ Conda environment active: %CONDA_DEFAULT_ENV%
echo 📦 Installing dependencies...
pip install -r requirements.txt

echo ✅ Build script executed successfully!
echo ℹ️  Add PyInstaller specs and complete source code to enable full builds
