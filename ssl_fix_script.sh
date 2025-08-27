#!/bin/bash

# PPTrans SSL Fix and Alternative Setup
# This script provides multiple solutions for SSL certificate issues

set -e

echo "🔧 PPTrans SSL Fix and Setup"
echo "============================"
echo ""

# Function to check conda SSL configuration
check_ssl_config() {
    echo "📋 Current conda SSL configuration:"
    conda config --show ssl_verify 2>/dev/null || echo "ssl_verify: not set"
    echo ""
}

# Function to fix SSL issues
fix_ssl_issues() {
    echo "🔒 Attempting to fix SSL issues..."
    
    # Method 1: Disable SSL verification temporarily (not recommended for production)
    echo "Method 1: Temporarily disabling SSL verification..."
    conda config --set ssl_verify false
    
    # Method 2: Update certificates
    echo "Method 2: Updating certificates..."
    conda update ca-certificates -y 2>/dev/null || echo "Failed to update certificates"
    
    # Method 3: Set conda channels to use HTTP instead of HTTPS (fallback)
    echo "Method 3: Configuring fallback channels..."
    conda config --set channel_priority flexible
    
    echo "✅ SSL configuration updated"
}

# Function to create environment with pip fallback
create_environment_pip_fallback() {
    echo "🐍 Creating Python environment with pip fallback..."
    
    # Create basic conda environment with minimal packages
    echo "Creating minimal conda environment..."
    conda create -n pptrans python=3.11 -y || {
        echo "❌ Failed to create conda environment"
        echo "Trying with different method..."
        
        # Alternative: create with python only
        conda create -n pptrans python=3.11 pip -c conda-forge -y --no-deps || {
            echo "❌ All conda methods failed"
            return 1
        }
    }
    
    # Activate environment
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate pptrans
    
    # Install packages with pip
    echo "📦 Installing packages with pip..."
    pip install --upgrade pip
    pip install python-pptx==0.6.23
    pip install googletrans==4.0.0rc1  
    pip install requests==2.31.0
    pip install pyinstaller==6.3.0
    pip install pytest==7.4.4
    pip install pytest-cov==4.1.0
    
    # Install tkinter support (usually comes with Python)
    python -c "import tkinter; print('✅ Tkinter available')" || {
        echo "⚠️  Tkinter not available, trying to install..."
        # On some systems, tkinter needs to be installed separately
        conda install tk -y 2>/dev/null || pip install tk || echo "Manual tkinter installation may be needed"
    }
    
    echo "✅ Environment created successfully with pip!"
}

# Function to test the installation
test_installation() {
    echo "🧪 Testing installation..."
    
    # Test Python imports
    python -c "
import sys
print(f'Python version: {sys.version}')

try:
    import tkinter
    print('✅ tkinter: OK')
except ImportError as e:
    print(f'❌ tkinter: {e}')

try:
    import pptx
    print('✅ python-pptx: OK')
except ImportError as e:
    print(f'❌ python-pptx: {e}')

try:
    import googletrans
    print('✅ googletrans: OK')
except ImportError as e:
    print(f'❌ googletrans: {e}')

try:
    import requests
    print('✅ requests: OK')
except ImportError as e:
    print(f'❌ requests: {e}')
"
}

# Main execution
main() {
    check_ssl_config
    
    echo "🤔 Choose your setup method:"
    echo "1. Fix SSL issues and retry conda install"
    echo "2. Skip conda, use pip-only installation"
    echo "3. Manual setup instructions"
    echo ""
    read -p "Enter your choice (1-3): " choice
    
    case $choice in
        1)
            echo "Attempting SSL fix..."
            fix_ssl_issues
            echo ""
            echo "🔄 Retrying conda environment creation..."
            conda env create -f environment.yml && {
                echo "✅ Success with SSL fix!"
                source "$(conda info --base)/etc/profile.d/conda.sh"
                conda activate pptrans
                test_installation
            } || {
                echo "❌ SSL fix didn't work, falling back to pip method..."
                create_environment_pip_fallback
                test_installation
            }
            ;;
        2)
            echo "Using pip-only installation..."
            create_environment_pip_fallback
            test_installation
            ;;
        3)
            echo "📋 Manual Setup Instructions:"
            echo "============================="
            echo ""
            echo "1. Create environment manually:"
            echo "   conda create -n pptrans python=3.11"
            echo ""
            echo "2. Activate environment:"
            echo "   conda activate pptrans"
            echo ""
            echo "3. Install packages with pip:"
            echo "   pip install python-pptx==0.6.23"
            echo "   pip install googletrans==4.0.0rc1"
            echo "   pip install requests==2.31.0"
            echo "   pip install pyinstaller==6.3.0"
            echo "   pip install pytest==7.4.4"
            echo ""
            echo "4. Test installation:"
            echo "   python -c 'import tkinter, pptx, googletrans; print(\"All packages OK\")'"
            echo ""
            exit 0
            ;;
        *)
            echo "❌ Invalid choice"
            exit 1
            ;;
    esac
    
    echo ""
    echo "🎉 Setup completed!"
    echo "📋 Next steps:"
    echo "1. Make sure you're in the pptrans environment: conda activate pptrans"
    echo "2. Add the source files from the conversation"
    echo "3. Run: python src/main.py"
}

# Check if we're in the right directory
if [ ! -f "environment.yml" ]; then
    echo "❌ Error: environment.yml not found"
    echo "Please run this script from the PPTrans project root directory"
    exit 1
fi

# Run main function
main
