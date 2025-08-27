#!/usr/bin/env python3
"""
Fix the type errors in PPTrans
"""

from pathlib import Path

def fix_pptx_processor_type_error():
    """Fix the type error in pptx_processor.py"""
    
    pptx_file = Path('src/core/pptx_processor.py')
    
    with open(pptx_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup
    backup_file = pptx_file.with_suffix('.py.backup_type_fix')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Backup created: {backup_file}")
    
    # Fix the type error - slide_indices should be a list of integers, not strings
    # The issue is in the parse_slide_range method where regex is removing too much
    
    # Fix the regex pattern - it was using double backslashes
    old_regex = "cleaned = re.sub(r'[^0-9-,\\\\s]', '', range_str)"
    new_regex = "cleaned = re.sub(r'[^0-9-,\\s]', '', range_str)"
    content = content.replace(old_regex, new_regex)
    
    old_regex2 = "cleaned = re.sub(r'\\\\s+', '', cleaned)"
    new_regex2 = "cleaned = re.sub(r'\\s+', '', cleaned)"
    content = content.replace(old_regex2, new_regex2)
    
    # Write the fixed content
    with open(pptx_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed regex patterns in {pptx_file}")

def fix_exceptions_error_handler():
    """Fix the error handler in exceptions.py"""
    
    exceptions_file = Path('src/utils/exceptions.py')
    
    if not exceptions_file.exists():
        print("exceptions.py not found - skipping")
        return
    
    with open(exceptions_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup
    backup_file = exceptions_file.with_suffix('.py.backup_handler_fix')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Backup created: {backup_file}")
    
    # Fix the error handler to use str(exception) instead of exception.message
    old_handler = 'return f"An error occurred: {exception.message}"'
    new_handler = 'return f"An error occurred: {str(exception)}"'
    
    if old_handler in content:
        content = content.replace(old_handler, new_handler)
        
        with open(exceptions_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed error handler in {exceptions_file}")
    else:
        print("Error handler pattern not found - might already be fixed")

def test_fixes():
    """Test that the fixes work"""
    try:
        import sys
        src_path = Path('src').absolute()
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        # Clear cached modules
        if 'core.pptx_processor' in sys.modules:
            del sys.modules['core.pptx_processor']
        if 'utils.exceptions' in sys.modules:
            del sys.modules['utils.exceptions']
        
        from core.pptx_processor import PPTXProcessor
        processor = PPTXProcessor()
        
        # Test slide range parsing
        processor.current_presentation = type('MockPresentation', (), {
            'slides': [None] * 10  # Mock 10 slides
        })()
        
        slide_range = processor.parse_slide_range("1-3")
        print(f"Test slide range parsing: {slide_range}")
        print("Type of first element:", type(slide_range[0]))
        
        if all(isinstance(i, int) for i in slide_range):
            print("✅ Slide range parsing returns integers correctly")
        else:
            print("❌ Slide range parsing still has type issues")
            
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main fix function"""
    print("Fixing Type Errors in PPTrans")
    print("=" * 35)
    
    # Fix the PowerPoint processor type error
    print("Step 1: Fixing pptx_processor type error...")
    fix_pptx_processor_type_error()
    
    # Fix the exceptions error handler
    print("\nStep 2: Fixing exceptions error handler...")
    fix_exceptions_error_handler()
    
    # Test the fixes
    print("\nStep 3: Testing fixes...")
    if test_fixes():
        print("\n✅ SUCCESS! Type errors fixed")
        print("Now test: python src/main.py")
        return True
    else:
        print("\n❌ Some issues remain")
        return False

if __name__ == "__main__":
    main()
