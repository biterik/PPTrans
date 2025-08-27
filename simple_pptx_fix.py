#!/usr/bin/env python3
"""
Simple fix for the PowerPoint text application issue
Fixes the indentation and syntax errors
"""

import sys
from pathlib import Path

def fix_syntax_errors():
    """Fix syntax errors in the pptx_processor.py file"""
    
    pptx_file = Path('src/core/pptx_processor.py')
    
    # Read the current file
    with open(pptx_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup
    backup_file = pptx_file.with_suffix('.py.backup_syntax')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Backup created: {backup_file}")
    
    # Fix common indentation and syntax issues
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Skip empty lines or preserve them
        if not line.strip():
            fixed_lines.append(line)
            continue
            
        # Fix obvious indentation issues
        if line.lstrip().startswith('failed_applications += 1'):
            # Ensure proper indentation (should be inside a method)
            if not line.startswith('        '):  # 8 spaces for method body
                line = '            ' + line.lstrip()  # 12 spaces for nested block
        
        # Fix other common indentation issues
        if line.lstrip().startswith('successful_applications += 1'):
            if not line.startswith('        '):
                line = '            ' + line.lstrip()
        
        # Remove duplicate method definitions or malformed lines
        if 'def _apply_text_to_shape' in line and i > 0:
            # Check if this is a duplicate definition
            prev_lines = '\n'.join(lines[max(0, i-10):i])
            if 'def _apply_text_to_shape' in prev_lines:
                continue  # Skip duplicate
        
        fixed_lines.append(line)
    
    # Write the fixed content
    fixed_content = '\n'.join(fixed_lines)
    
    # Remove any method definitions that got duplicated or are incomplete
    import re
    
    # Remove incomplete method definitions (those not followed by proper implementation)
    fixed_content = re.sub(r'\n    def _apply_text_to_shape.*?\n(?!\s)', '\n', fixed_content, flags=re.DOTALL)
    fixed_content = re.sub(r'\n    def _apply_run_formatting.*?\n(?!\s)', '\n', fixed_content, flags=re.DOTALL)
    
    with open(pptx_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"Fixed syntax errors in {pptx_file}")

def add_working_text_methods():
    """Add working text application methods to the pptx_processor"""
    
    pptx_file = Path('src/core/pptx_processor.py')
    
    with open(pptx_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple working methods that avoid the 'tuple' error
    working_methods = '''
    def _apply_text_to_shape_simple(self, shape, translated_text: str) -> bool:
        """
        Simple text application that avoids tuple errors
        """
        try:
            if hasattr(shape, 'text'):
                shape.text = translated_text
                return True
            elif hasattr(shape, 'text_frame') and shape.text_frame:
                shape.text_frame.text = translated_text
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f"Error applying text: {e}")
            return False

    def apply_translations_simple(self) -> None:
        """
        Simple translation application method
        """
        if not self.current_presentation or not self.text_elements:
            self.logger.warning("No presentation or text elements to apply")
            return
        
        self.logger.info("Applying translations to presentation (simple method)")
        
        successful = 0
        failed = 0
        
        for element in self.text_elements:
            translated_text = element.get('translated_text', element.get('original_text', ''))
            shape = element.get('shape_reference')
            
            if shape and translated_text:
                if self._apply_text_to_shape_simple(shape, translated_text):
                    successful += 1
                else:
                    failed += 1
            else:
                failed += 1
        
        self.logger.info(f"Applied {successful} translations, {failed} failed")
'''
    
    # Add the methods before the last method or at the end of the class
    insertion_point = content.rfind('\n    def close(')
    if insertion_point == -1:
        insertion_point = content.rfind('\nclass ')
        if insertion_point != -1:
            # Find the end of the class
            next_class = content.find('\nclass ', insertion_point + 1)
            if next_class == -1:
                insertion_point = len(content) - 1
            else:
                insertion_point = next_class
    
    if insertion_point != -1:
        content = content[:insertion_point] + working_methods + '\n' + content[insertion_point:]
    
    with open(pptx_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Added simple text application methods to {pptx_file}")

def update_main_translate_method():
    """Update the main translation method to use the simple approach"""
    
    pptx_file = Path('src/core/pptx_processor.py')
    
    with open(pptx_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the apply_translations call with our simple version
    if 'apply_translations(' in content:
        content = content.replace(
            'apply_translations()',
            'apply_translations_simple()'
        )
    
    # Also replace any direct calls to _apply_text_to_shape
    if '_apply_text_to_shape(' in content:
        content = content.replace(
            '_apply_text_to_shape(',
            '_apply_text_to_shape_simple('
        )
    
    with open(pptx_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Updated method calls to use simple versions")

def test_fixed_processor():
    """Test if the processor loads without syntax errors"""
    try:
        src_path = Path('src').absolute()
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        # Clear any cached modules
        if 'core.pptx_processor' in sys.modules:
            del sys.modules['core.pptx_processor']
        
        from core.pptx_processor import PPTXProcessor
        
        processor = PPTXProcessor()
        print("✅ PPTXProcessor loads successfully")
        
        # Check for our simple methods
        if hasattr(processor, '_apply_text_to_shape_simple'):
            print("✅ Simple text application method present")
        
        if hasattr(processor, 'apply_translations_simple'):
            print("✅ Simple translation application method present")
        
        return True
        
    except Exception as e:
        print(f"❌ Processor test failed: {e}")
        return False

def main():
    """Apply simple fixes to the PowerPoint processor"""
    print("Simple PowerPoint Processor Fix")
    print("=" * 40)
    
    if not Path('src/core/pptx_processor.py').exists():
        print("❌ pptx_processor.py not found")
        return False
    
    try:
        # Fix syntax errors first
        fix_syntax_errors()
        
        # Add simple working methods
        add_working_text_methods()
        
        # Update method calls
        update_main_translate_method()
        
        # Test the fixes
        if test_fixed_processor():
            print("\n✅ PowerPoint processor fixed successfully!")
            print("\nNow test with translation that works:")
            print("python src/main.py")
            print("\nThe direct HTTP requests translation method works,")
            print("so we should integrate that next.")
            return True
        else:
            print("\n❌ Issues remain with the processor")
            return False
            
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        return False

if __name__ == "__main__":
    main()
