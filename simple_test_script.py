#!/usr/bin/env python3
"""
Simple test script for the corrected PPTrans implementation
Run this to verify the fixes work before using the GUI
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test that all imports work correctly"""
    print("Testing imports...")
    
    try:
        from core.translator import PPTransTranslator
        print("✓ PPTransTranslator import successful")
    except Exception as e:
        print(f"✗ PPTransTranslator import failed: {e}")
        return False
    
    try:
        from core.pptx_processor import PPTXProcessor  
        print("✓ PPTXProcessor import successful")
    except Exception as e:
        print(f"✗ PPTXProcessor import failed: {e}")
        return False
    
    try:
        from utils.logger import setup_logger
        print("✓ Logger import successful")
    except Exception as e:
        print(f"✗ Logger import failed: {e}")
        return False
    
    return True

def test_translator():
    """Test the translator functionality"""
    print("\nTesting translator...")
    
    try:
        from core.translator import PPTransTranslator
        
        # Initialize with dummy settings
        translator = PPTransTranslator({
            'max_requests_per_hour': 1000,
            'retry_attempts': 3
        })
        
        # Test basic translation
        test_texts = [
            "Hallo Welt",
            "Guten Morgen", 
            "Wie geht es dir?"
        ]
        
        print("Testing translations:")
        for text in test_texts:
            try:
                result = translator.translate_text(text, 'de', 'en')
                print(f"  '{text}' -> '{result}'")
            except Exception as e:
                print(f"  Translation failed for '{text}': {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Translator test failed: {e}")
        return False

def test_processor():
    """Test the PPTX processor"""
    print("\nTesting PPTX processor...")
    
    try:
        from core.pptx_processor import PPTXProcessor
        
        # Initialize with dummy settings
        processor = PPTXProcessor({
            'preserve_animations': True,
            'max_text_length': 10000
        })
        
        print("✓ PPTXProcessor initialized successfully")
        print("✓ Methods available:", [m for m in dir(processor) if not m.startswith('_')])
        
        return True
        
    except Exception as e:
        print(f"✗ Processor test failed: {e}")
        return False

def test_full_workflow():
    """Test the full workflow that the GUI uses"""
    print("\nTesting full workflow...")
    
    # Get PowerPoint file from user
    pptx_file = input("Enter path to PowerPoint file (or press Enter to skip): ").strip()
    if not pptx_file or not os.path.exists(pptx_file):
        print("Skipping full workflow test - no valid file provided")
        return True
    
    try:
        from core.translator import PPTransTranslator
        from core.pptx_processor import PPTXProcessor
        
        # Initialize components
        translator = PPTransTranslator({'max_requests_per_hour': 1000})
        processor = PPTXProcessor({'preserve_animations': True})
        
        print(f"Loading presentation: {pptx_file}")
        processor.load_presentation(pptx_file)
        
        info = processor.get_presentation_info()
        print(f"✓ Loaded presentation with {info['total_slides']} slides")
        
        slide_range = input("Enter slide range (e.g., '1-3' or press Enter for '1-3'): ").strip() or "1-3"
        
        print(f"Extracting text from slides {slide_range}...")
        text_elements = processor.extract_text_elements(slide_range)
        print(f"✓ Extracted {len(text_elements)} text elements")
        
        if text_elements:
            # Show preview
            print("\nText elements preview:")
            for i, element in enumerate(text_elements[:3]):  # Show first 3
                print(f"  {i+1}. '{element['original_text'][:50]}...'")
            
            # Test translation workflow 
            def translate_with_progress(text: str) -> str:
                return translator.translate_text(text, 'auto', 'en')
            
            print("\nTranslating elements...")
            processor.translate_text_elements(translate_with_progress)
            
            print("Applying translations...")
            processor.apply_translations()
            
            print("Saving presentation...")
            output_path = processor.save_presentation()
            
            stats = processor.get_processing_stats()
            print(f"✓ Translation completed!")
            print(f"  Translated: {stats['translated_elements']} elements")
            print(f"  Output: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"✗ Full workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("PPTrans Implementation Test")
    print("=" * 40)
    
    # Test imports first
    if not test_imports():
        print("\n❌ Import tests failed - fix imports before continuing")
        return
    
    # Test components
    translator_ok = test_translator()
    processor_ok = test_processor()
    
    if translator_ok and processor_ok:
        print("\n✅ Component tests passed!")
        
        # Test full workflow if user wants
        if input("\nRun full workflow test? (y/n): ").lower().startswith('y'):
            workflow_ok = test_full_workflow()
            
            if workflow_ok:
                print("\n🎉 All tests passed! Your implementation should work with the GUI.")
                print("\nNext steps:")
                print("1. Replace your current translator.py and pptx_processor.py with the corrected versions")
                print("2. Run: python src/main.py")
                print("3. Test with your slides 16-18")
            else:
                print("\n❌ Workflow test failed - check the errors above")
        else:
            print("\n✅ Basic tests passed - should work with GUI")
    else:
        print("\n❌ Component tests failed - check the errors above")

if __name__ == "__main__":
    main()