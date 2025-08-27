#!/usr/bin/env python3
"""
PPTrans Debug Script
Helps diagnose and fix common issues with the PPTrans application
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    print("=== Python Version Check ===")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major != 3 or version.minor < 8:
        print("❌ Error: Python 3.8+ is required")
        return False
    else:
        print("✅ Python version is compatible")
        return True

def check_dependencies():
    """Check if required packages are installed"""
    print("\n=== Dependency Check ===")
    required_packages = [
        ('tkinter', 'tkinter'),
        ('python-pptx', 'pptx'),
        ('googletrans', 'googletrans'),
        ('requests', 'requests'),
    ]
    
    missing = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name}: OK")
        except ImportError:
            print(f"❌ {package_name}: MISSING")
            missing.append(package_name)
    
    if missing:
        print(f"\nTo install missing packages:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True

def check_project_structure():
    """Check if project structure is correct"""
    print("\n=== Project Structure Check ===")
    
    required_dirs = [
        'src',
        'src/core',
        'src/gui', 
        'src/utils'
    ]
    
    required_files = [
        'src/main.py',
        'src/core/translator.py',
        'src/core/pptx_processor.py',
        'src/core/language_manager.py',
        'src/gui/main_window.py',
        'src/gui/widgets.py',
        'src/gui/dialogs.py',
        'src/utils/logger.py',
        'src/utils/config.py',
        'src/utils/exceptions.py'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            print(f"❌ Directory missing: {dir_path}")
            missing_dirs.append(dir_path)
        else:
            print(f"✅ Directory: {dir_path}")
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ File missing: {file_path}")
            missing_files.append(file_path)
        else:
            print(f"✅ File: {file_path}")
    
    return len(missing_dirs) == 0 and len(missing_files) == 0

def test_imports():
    """Test importing all modules"""
    print("\n=== Import Test ===")
    
    # Add src to path
    src_path = Path('src').absolute()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    modules_to_test = [
        'utils.logger',
        'utils.config',
        'utils.exceptions',
        'core.language_manager',
        'core.translator',
        'core.pptx_processor',
        'gui.widgets',
        'gui.dialogs',
        'gui.main_window'
    ]
    
    failed_imports = []
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ Import {module}: OK")
        except Exception as e:
            print(f"❌ Import {module}: FAILED - {e}")
            failed_imports.append((module, str(e)))
    
    if failed_imports:
        print(f"\n=== Import Errors Details ===")
        for module, error in failed_imports:
            print(f"\n{module}:")
            print(f"  Error: {error}")
            
            # Try to give specific fix suggestions
            if "SyntaxError" in error:
                print(f"  Fix: Check syntax in {module.replace('.', '/')}.py")
            elif "ModuleNotFoundError" in error:
                print(f"  Fix: Install missing dependency or check file exists")
    
    return len(failed_imports) == 0

def test_translator_api():
    """Test Google Translate API access"""
    print("\n=== Translator API Test ===")
    
    try:
        # Add src to path
        src_path = Path('src').absolute()
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        from googletrans import Translator
        translator = Translator()
        
        # Test simple translation
        result = translator.translate("Hello", dest='de')
        translated_text = result.text if hasattr(result, 'text') else str(result)
        print(f"✅ Test translation: 'Hello' → '{translated_text}'")
        return True
        
    except Exception as e:
        print(f"❌ Translation test failed: {e}")
        print("  This might be due to:")
        print("  - Network connectivity issues")
        print("  - Google Translate API changes")
        print("  - Rate limiting")
        return False

def check_file_syntax(file_path):
    """Check Python file for syntax errors"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Try to compile the source
        compile(source, file_path, 'exec')
        return True, None
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)

def fix_common_issues():
    """Attempt to fix common issues automatically"""
    print("\n=== Auto-Fix Attempts ===")
    
    fixes_applied = []
    
    # Fix 1: Check for common syntax error in pptx_processor.py
    pptx_file = Path('src/core/pptx_processor.py')
    if pptx_file.exists():
        is_valid, error = check_file_syntax(pptx_file)
        if not is_valid and "invalid syntax" in error:
            print(f"🔧 Found syntax error in {pptx_file}: {error}")
            
            # Try to read and identify the specific issue
            with open(pptx_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for the specific error pattern from the logs
            if 'self.logger.info("PPTX Processor closed")_post_init__(self):' in content:
                print("🔧 Found the specific syntax error - missing newline")
                fixed_content = content.replace(
                    'self.logger.info("PPTX Processor closed")_post_init__(self):',
                    'self.logger.info("PPTX Processor closed")'
                )
                
                # Create backup
                backup_file = pptx_file.with_suffix('.py.backup')
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Write fixed version
                with open(pptx_file, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                print(f"✅ Fixed syntax error in {pptx_file}")
                print(f"   Backup saved as {backup_file}")
                fixes_applied.append("Fixed pptx_processor.py syntax error")
    
    if fixes_applied:
        print(f"\n🎉 Applied {len(fixes_applied)} fixes:")
        for fix in fixes_applied:
            print(f"  - {fix}")
    else:
        print("No automatic fixes needed or available")

def main():
    """Main diagnostic function"""
    print("PPTrans Diagnostic Tool")
    print("=" * 50)
    
    # Check current directory
    cwd = Path.cwd()
    print(f"Current directory: {cwd}")
    
    if not (cwd / 'src').exists():
        print("❌ Error: Please run this script from the PPTrans project root directory")
        print("   (The directory containing the 'src' folder)")
        return False
    
    all_ok = True
    
    # Run all checks
    all_ok &= check_python_version()
    all_ok &= check_dependencies()
    all_ok &= check_project_structure()
    
    # Try auto-fixes before import test
    fix_common_issues()
    
    all_ok &= test_imports()
    
    # Only test translator if imports work
    if all_ok:
        test_translator_api()
    
    print("\n" + "=" * 50)
    if all_ok:
        print("🎉 All basic checks passed! Try running: python src/main.py")
    else:
        print("❌ Some issues found. Please fix them before running the application.")
    
    return all_ok

if __name__ == "__main__":
    main()
