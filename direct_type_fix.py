#!/usr/bin/env python3
"""
Direct fix for the string/int type error in slide range processing
"""

from pathlib import Path

def fix_slide_range_processing():
    """Fix the slide range processing to ensure integers are returned"""
    
    pptx_file = Path('src/core/pptx_processor.py')
    
    with open(pptx_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup
    backup_file = pptx_file.with_suffix('.py.backup_direct_fix')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Backup created: {backup_file}")
    
    # Find and replace the entire parse_slide_range method with a working version
    method_start = content.find('    def parse_slide_range(self, range_str: str) -> List[int]:')
    
    if method_start == -1:
        print("Could not find parse_slide_range method")
        return False
    
    # Find the end of the method (next method or end of class)
    method_end = content.find('\n    def ', method_start + 1)
    if method_end == -1:
        method_end = len(content)
    
    # Working replacement method
    new_method = '''    def parse_slide_range(self, range_str: str) -> List[int]:
        """Parse slide range string and return list of slide indices (0-based)"""
        if not range_str or not range_str.strip():
            raise ValueError("Empty slide range specification")
        
        range_str = range_str.strip().lower()
        max_slides = self.get_slide_count()
        
        if max_slides == 0:
            raise ValueError("No presentation loaded")
        
        # Handle "all" keyword
        if range_str == "all":
            return list(range(max_slides))
        
        # Clean up the input - remove non-digit, non-dash, non-comma characters
        import re
        cleaned = re.sub(r'[^0-9-,]', '', range_str)
        
        if not cleaned:
            raise ValueError(f"Invalid slide range specification: '{range_str}'")
        
        slide_indices = set()
        
        try:
            parts = [part.strip() for part in cleaned.split(',') if part.strip()]
            
            for part in parts:
                if '-' in part:
                    range_parts = part.split('-')
                    if len(range_parts) != 2:
                        raise ValueError(f"Invalid range format: '{part}'")
                    
                    start_str, end_str = range_parts
                    if not start_str or not end_str:
                        raise ValueError(f"Invalid range format: '{part}'")
                    
                    start = int(start_str)
                    end = int(end_str)
                    
                    if start < 1 or end < 1:
                        raise ValueError(f"Slide numbers must be positive")
                    
                    if start > end:
                        raise ValueError(f"Invalid range: start > end")
                    
                    if start > max_slides or end > max_slides:
                        raise ValueError(f"Slide range exceeds available slides")
                    
                    # Add slides in range (convert to 0-based indexing)
                    for i in range(start - 1, end):
                        slide_indices.add(i)
                    
                else:
                    slide_num = int(part)
                    if slide_num < 1:
                        raise ValueError(f"Slide number must be positive")
                    if slide_num > max_slides:
                        raise ValueError(f"Slide exceeds available slides")
                    
                    # Convert to 0-based indexing
                    slide_indices.add(slide_num - 1)
        
        except ValueError as e:
            raise ValueError(f"Invalid slide range: {str(e)}")
        
        if not slide_indices:
            raise ValueError(f"No valid slides specified")
        
        # Ensure we return a list of integers
        result = sorted(list(slide_indices))
        return result
'''
    
    # Replace the method
    new_content = content[:method_start] + new_method + content[method_end:]
    
    # Write the fixed content
    with open(pptx_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Replaced parse_slide_range method in {pptx_file}")
    return True

def test_slide_range_parsing():
    """Test the slide range parsing"""
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
        
        # Mock a presentation with slides
        class MockPresentation:
            def __init__(self, slide_count):
                self.slides = [None] * slide_count
        
        processor.current_presentation = MockPresentation(10)
        
        # Test various slide range formats
        test_cases = [
            "1",
            "1-3", 
            "5-7",
            "1,3,5",
            "1-3,5-7"
        ]
        
        for test_case in test_cases:
            try:
                result = processor.parse_slide_range(test_case)
                print(f"Test '{test_case}': {result}")
                print(f"  Types: {[type(x) for x in result]}")
                
                # Check all results are integers
                if all(isinstance(x, int) for x in result):
                    print(f"  ✅ All integers")
                else:
                    print(f"  ❌ Contains non-integers")
                    return False
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
                return False
        
        print("\n✅ All slide range parsing tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        return False

def main():
    """Main function"""
    print("Direct Fix for Slide Range Type Error")
    print("=" * 40)
    
    # Fix the method
    if fix_slide_range_processing():
        # Test the fix
        if test_slide_range_parsing():
            print("\n🎉 SUCCESS! Slide range parsing fixed")
            print("Now test: python src/main.py")
            print("The type error should be resolved.")
        else:
            print("\n❌ Fix applied but tests failed")
    else:
        print("\n❌ Could not apply fix")

if __name__ == "__main__":
    main()
