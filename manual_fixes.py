#!/usr/bin/env python3
"""
PPTrans Manual Fixes
Python-based fixes for common issues (alternative to patch command)
"""

import os
import sys
import re
from pathlib import Path

def fix_pptx_processor_syntax():
    """Fix the syntax error in pptx_processor.py"""
    file_path = Path("src/core/pptx_processor.py")
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"🔧 Fixing syntax error in {file_path}")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the error exists
    error_pattern = r'self\.logger\.info\("PPTX Processor closed"\)_post_init__\(self\):'
    
    if re.search(error_pattern, content):
        print("🔍 Found syntax error, fixing...")
        
        # Fix the error
        fixed_content = re.sub(
            error_pattern,
            'self.logger.info("PPTX Processor closed")',
            content
        )
        
        # Create backup
        backup_path = file_path.with_suffix('.py.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📦 Created backup: {backup_path}")
        
        # Write fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print("✅ Fixed pptx_processor.py syntax error")
        return True
    else:
        print("✅ No syntax error found in pptx_processor.py")
        return True

def fix_missing_imports():
    """Fix any missing import issues"""
    fixes_applied = []
    
    # Check main.py for proper imports
    main_file = Path("src/main.py")
    if main_file.exists():
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ensure proper sys.path setup
        if 'sys.path.insert(0, str(Path(__file__).parent))' not in content:
            print("🔧 Adding sys.path fix to main.py")
            
            # Find the imports section and add path fix
            lines = content.split('\n')
            import_index = -1
            
            for i, line in enumerate(lines):
                if line.startswith('from utils.logger import'):
                    import_index = i
                    break
            
            if import_index > 0:
                # Insert sys.path fix before utils imports
                lines.insert(import_index, '')
                lines.insert(import_index, '# Add src directory to path for imports')
                lines.insert(import_index, 'sys.path.insert(0, str(Path(__file__).parent))')
                lines.insert(import_index, '')
                
                with open(main_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                
                fixes_applied.append("Added sys.path fix to main.py")
    
    return fixes_applied

def test_imports():
    """Test if all imports work"""
    print("🧪 Testing imports...")
    
    # Add src to path
    src_path = str(Path("src").absolute())
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    test_modules = [
        ("utils.logger", "Logger utilities"),
        ("utils.config", "Configuration management"),
        ("utils.exceptions", "Custom exceptions"),
        ("core.language_manager", "Language manager"),
        ("core.translator", "Translation engine"),
        ("core.pptx_processor", "PowerPoint processor"),
        ("gui.main_window", "Main GUI window"),
        ("gui.widgets", "GUI widgets"),
        ("gui.dialogs", "GUI dialogs"),
    ]
    
    success_count = 0
    for module_name, description in test_modules:
        try:
            __import__(module_name)
            print(f"✅ {description}: OK")
            success_count += 1
        except ImportError as e:
            print(f"❌ {description}: {e}")
        except SyntaxError as e:
            print(f"❌ {description}: Syntax Error - {e}")
        except Exception as e:
            print(f"❌ {description}: {e}")
    
    print(f"\n📊 Import test results: {success_count}/{len(test_modules)} modules OK")
    return success_count == len(test_modules)

def main():
    """Main function to apply all fixes"""
    print("🔧 PPTrans Manual Fixes")
    print("=" * 30)
    
    # Check if we're in the right directory
    if not Path("src").exists():
        print("❌ Error: 'src' directory not found")
        print("Please run this script from the PPTrans project root directory")
        return False
    
    # Apply fixes
    fixes_successful = True
    
    # Fix syntax errors
    if not fix_pptx_processor_syntax():
        fixes_successful = False
    
    # Fix import issues
    import_fixes = fix_missing_imports()
    for fix in import_fixes:
        print(f"✅ {fix}")
    
    # Test everything
    print("\n" + "=" * 30)
    if test_imports():
        print("🎉 All fixes applied successfully!")
        print("You can now run: python src/main.py")
    else:
        print("⚠️  Some issues remain. Check the error messages above.")
        fixes_successful = False
    
    return fixes_successful

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
