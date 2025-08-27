#!/usr/bin/env python3
"""
Direct fix for the syntax error at line 277
"""

from pathlib import Path

def fix_line_277_directly():
    """Fix the specific syntax error at line 277"""
    
    pptx_file = Path('src/core/pptx_processor.py')
    
    # Read the file
    with open(pptx_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Create backup
    backup_file = pptx_file.with_suffix('.py.backup_direct')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"Backup created: {backup_file}")
    
    # Show the problematic area
    if len(lines) > 277:
        print(f"Line 276: {repr(lines[275])}")
        print(f"Line 277: {repr(lines[276])}")  # This is the problem line
        print(f"Line 278: {repr(lines[277])}")
        print(f"Line 279: {repr(lines[278])}")
    
    # Find and fix the indentation issues around line 277
    fixed_lines = []
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Fix the specific problematic line and surrounding area
        if 270 <= line_num <= 290:  # Focus on the problem area
            # Remove any malformed method insertions or duplicate content
            if ('failed_applications += 1' in line or 
                'successful_applications += 1' in line or
                'def _apply_text_to_shape' in line or
                'def _apply_run_formatting' in line or
                'def apply_translations' in line):
                
                # Skip lines that seem to be incorrectly inserted method fragments
                if not line.strip().startswith('def ') and ('failed_applications' in line or 'successful_applications' in line):
                    print(f"Removing problematic line {line_num}: {repr(line)}")
                    continue
                    
                # Skip duplicate method definitions
                if line.strip().startswith('def ') and any(method in line for method in ['_apply_text_to_shape', '_apply_run_formatting', 'apply_translations']):
                    # Check if this method already exists earlier in the file
                    method_name = line.strip().split('(')[0].replace('def ', '')
                    earlier_occurrence = any(method_name in earlier_line for earlier_line in lines[:i])
                    if earlier_occurrence:
                        print(f"Removing duplicate method definition at line {line_num}: {repr(line)}")
                        continue
        
        fixed_lines.append(line)
    
    # Write the fixed file
    with open(pptx_file, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"Fixed syntax errors in {pptx_file}")
    
    # Check if the file is now syntactically valid
    try:
        with open(pptx_file, 'r', encoding='utf-8') as f:
            content = f.read()
        compile(content, str(pptx_file), 'exec')
        print("✅ File is now syntactically valid")
        return True
    except SyntaxError as e:
        print(f"❌ Still has syntax error: Line {e.lineno}: {e.msg}")
        return False

def test_import():
    """Test if we can import the processor now"""
    try:
        import sys
        src_path = Path('src').absolute()
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        # Clear cached module
        if 'core.pptx_processor' in sys.modules:
            del sys.modules['core.pptx_processor']
        
        from core.pptx_processor import PPTXProcessor
        processor = PPTXProcessor()
        print("✅ PPTXProcessor imports and initializes successfully")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    """Main fix function"""
    print("Direct Syntax Error Fix for pptx_processor.py")
    print("=" * 50)
    
    if not Path('src/core/pptx_processor.py').exists():
        print("❌ File not found")
        return False
    
    # Fix the syntax error
    if fix_line_277_directly():
        # Test if it works now
        if test_import():
            print("\n🎉 SUCCESS! The syntax error is fixed.")
            print("Now test the application:")
            print("python src/main.py")
            return True
        else:
            print("\n⚠️  Syntax is valid but import still fails")
            return False
    else:
        print("\n❌ Could not fix the syntax error")
        return False

if __name__ == "__main__":
    main()
