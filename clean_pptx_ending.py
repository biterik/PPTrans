#!/usr/bin/env python3
"""
Clean fix for pptx_processor.py - replace the problematic ending
"""

from pathlib import Path

def fix_pptx_processor_clean():
    """Replace the ending of pptx_processor.py with a clean version"""
    file_path = Path("src/core/pptx_processor.py")
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"🔧 Cleaning up {file_path}")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup
    backup_path = file_path.with_suffix('.py.backup3')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📦 Created backup: {backup_path}")
    
    # Find the last good method before the problems start
    lines = content.split('\n')
    
    # Find where the apply_translations method ends
    last_good_line = -1
    for i, line in enumerate(lines):
        if 'self.logger.info("Translations applied successfully")' in line:
            last_good_line = i
            break
    
    if last_good_line == -1:
        # Fallback: find the save_presentation method
        for i, line in enumerate(lines):
            if 'def save_presentation(self' in line:
                last_good_line = i - 1
                break
    
    if last_good_line == -1:
        print("❌ Could not find a good insertion point")
        return False
    
    # Keep everything up to the last good line
    clean_lines = lines[:last_good_line + 1]
    
    # Add the missing methods with clean implementations
    missing_methods = '''
    
    def translate_text_elements(self, translator_func: Callable[[str], str], 
                               progress_callback: Optional[Callable[[int, int], None]] = None) -> None:
        """
        Translate text elements using provided translation function
        
        Args:
            translator_func: Function that takes text and returns translation
            progress_callback: Optional callback for progress updates (current, total)
        
        Raises:
            PPTXProcessingError: If translation fails
        """
        if not self.text_elements:
            raise PPTXProcessingError("No text elements to translate")
        
        try:
            self.logger.info(f"Starting translation of {len(self.text_elements)} text elements")
            
            for i, element in enumerate(self.text_elements):
                try:
                    if element.text.strip():  # Only translate non-empty text
                        translated_text = translator_func(element.text)
                        element.text = translated_text
                        element.translated = True
                        self.stats.translated_elements += 1
                    else:
                        self.stats.skipped_elements += 1
                        
                except Exception as e:
                    self.logger.warning(f"Failed to translate element {i}: {e}")
                    self.stats.errors += 1
                
                # Progress callback
                if progress_callback:
                    progress_callback(i + 1, len(self.text_elements))
                
                # Log progress periodically
                if (i + 1) % 50 == 0:
                    self.logger.info(f"Translation progress: {i + 1}/{len(self.text_elements)}")
            
            self.logger.info(f"Translation completed: {self.stats.translated_elements} elements translated, "
                           f"{self.stats.skipped_elements} skipped, {self.stats.errors} errors")
                           
        except Exception as e:
            error_msg = f"Translation process failed: {str(e)}"
            self.logger.error(error_msg)
            raise PPTXProcessingError(error_msg, original_error=e)

    @log_performance
    def save_presentation(self, output_path: Optional[str] = None) -> str:
        """
        Save the modified presentation
        
        Args:
            output_path: Optional output path. If not provided, adds "_translated" suffix
        
        Returns:
            Path to saved file
        
        Raises:
            PPTXProcessingError: If save operation fails
        """
        if not self.current_presentation:
            raise PPTXProcessingError("No presentation to save")
        
        try:
            if output_path is None:
                input_path = Path(self.current_file_path)
                output_path = input_path.parent / f"{input_path.stem}_translated{input_path.suffix}"
            else:
                output_path = Path(output_path)
            
            self.logger.info(f"Saving presentation to: {output_path}")
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save presentation
            self.current_presentation.save(str(output_path))
            
            self.logger.info(f"Presentation saved successfully: {output_path}")
            return str(output_path)
            
        except Exception as e:
            error_msg = f"Failed to save presentation: {str(e)}"
            self.logger.error(error_msg)
            raise PPTXProcessingError(
                error_msg,
                file_path=str(output_path) if output_path else None,
                original_error=e
            )
    
    def get_presentation_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded presentation
        
        Returns:
            Dictionary with presentation information
        """
        if not self.current_presentation:
            return {}
        
        info = {
            'file_path': self.current_file_path,
            'total_slides': len(self.current_presentation.slides),
            'slide_dimensions': {
                'width': self.current_presentation.slide_width,
                'height': self.current_presentation.slide_height
            }
        }
        
        # Add slide layout information
        slide_layouts = {}
        for i, slide in enumerate(self.current_presentation.slides, 1):
            layout_name = slide.slide_layout.name if hasattr(slide.slide_layout, 'name') else f"Layout_{i}"
            if layout_name not in slide_layouts:
                slide_layouts[layout_name] = 0
            slide_layouts[layout_name] += 1
        
        info['slide_layouts'] = slide_layouts
        
        return info
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            'total_slides': self.stats.total_slides,
            'processed_slides': self.stats.processed_slides,
            'total_text_elements': self.stats.total_text_elements,
            'translated_elements': self.stats.translated_elements,
            'skipped_elements': self.stats.skipped_elements,
            'errors': self.stats.errors,
            'processing_time': self.stats.processing_time
        }
    
    def close(self) -> None:
        """Clean up resources"""
        self.current_presentation = None
        self.current_file_path = None
        self.text_elements = []
        self.stats = ProcessingStats()
        self.logger.info("PPTX Processor closed")
'''
    
    # Combine the clean content
    clean_content = '\n'.join(clean_lines) + missing_methods
    
    # Write the clean file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(clean_content)
    
    print("✅ Applied clean fix to pptx_processor.py")
    return True

def validate_and_test():
    """Validate syntax and test import"""
    try:
        with open("src/core/pptx_processor.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        compile(content, "src/core/pptx_processor.py", 'exec')
        print("✅ Syntax validation passed")
        
        # Test import
        import sys
        sys.path.insert(0, 'src')
        from core.pptx_processor import PPTXProcessor
        print("✅ Import test successful")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error: Line {e.lineno}: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Clean PPTX Processor Fix")
    print("=" * 30)
    
    if fix_pptx_processor_clean():
        print("\n🧪 Testing the fix...")
        if validate_and_test():
            print("🎉 pptrans_processor.py is now fixed and working!")
            print("🚀 Try running: python src/main.py")
            return True
    
    print("❌ Fix failed")
    return False

if __name__ == "__main__":
    main()
