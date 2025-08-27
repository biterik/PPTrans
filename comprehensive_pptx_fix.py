#!/usr/bin/env python3
"""
Comprehensive fix for pptx_processor.py
This will check and fix all syntax issues in the file
"""

import re
from pathlib import Path

def fix_pptx_processor_comprehensive():
    """Comprehensive fix for pptx_processor.py"""
    file_path = Path("src/core/pptx_processor.py")
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"🔧 Comprehensive fix for {file_path}")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup
    backup_path = file_path.with_suffix('.py.backup2')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📦 Created backup: {backup_path}")
    
    # Fix common issues
    original_content = content
    
    # Fix 1: Remove any stray _post_init__ references
    content = re.sub(r'_post_init__\(self\):\s*', '', content)
    
    # Fix 2: Ensure proper method endings
    content = re.sub(r'self\.logger\.info\("PPTX Processor closed"\)[^"]*$', 
                     'self.logger.info("PPTX Processor closed")', content, flags=re.MULTILINE)
    
    # Fix 3: Remove any incomplete or malformed function definitions at the end
    # Look for lines that start with def but don't have proper syntax
    lines = content.split('\n')
    cleaned_lines = []
    
    for i, line in enumerate(lines):
        # Skip obviously malformed lines that look like function definitions but aren't
        if re.match(r'^\s*def\s+\w+.*[^:]\s*$', line):  # def without proper ending
            print(f"🔧 Removing malformed line {i+1}: {line.strip()}")
            continue
        
        # Skip lines that look like they're part of broken syntax
        if '_post_init__' in line and 'def' in line:
            print(f"🔧 Removing broken _post_init__ line {i+1}: {line.strip()}")
            continue
            
        cleaned_lines.append(line)
    
    content = '\n'.join(cleaned_lines)
    
    # Fix 4: Ensure the file ends properly
    if not content.endswith('\n'):
        content += '\n'
    
    # Fix 5: Remove any duplicate class definitions or method definitions
    # This is a more aggressive fix - remove any lines after the last proper method
    lines = content.split('\n')
    last_good_line = -1
    
    for i, line in enumerate(lines):
        if line.strip() == 'self.logger.info("PPTX Processor closed")':
            last_good_line = i
            break
    
    if last_good_line != -1:
        # Keep only up to the last good line
        lines = lines[:last_good_line + 1]
        content = '\n'.join(lines)
    
    # Write the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    if content != original_content:
        print("✅ Applied comprehensive fixes to pptx_processor.py")
    else:
        print("✅ No changes needed")
    
    return True

def validate_python_syntax(file_path):
    """Validate Python syntax of a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        compile(content, file_path, 'exec')
        print(f"✅ Syntax validation passed for {file_path}")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in {file_path}:")
        print(f"   Line {e.lineno}: {e.text.strip() if e.text else 'Unknown'}")
        print(f"   Error: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Error validating {file_path}: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Comprehensive PPTX Processor Fix")
    print("=" * 40)
    
    # Apply comprehensive fix
    fix_pptx_processor_comprehensive()
    
    # Validate syntax
    print("\n🧪 Validating syntax...")
    if validate_python_syntax("src/core/pptx_processor.py"):
        print("🎉 pptx_processor.py is now syntactically correct!")
        
        # Test import
        import sys
        sys.path.insert(0, 'src')
        try:
            from core.pptx_processor import PPTXProcessor
            print("✅ Import test successful!")
            return True
        except Exception as e:
            print(f"❌ Import test failed: {e}")
            return False
    else:
        print("❌ Syntax issues remain")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 Try running: python src/main.py")
    else:
        print("\n📝 You may need to manually check the file for issues")
