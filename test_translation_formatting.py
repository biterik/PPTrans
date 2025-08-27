#!/usr/bin/env python3
"""
Test script to verify translation and formatting preservation
Run this to test the fixes before using the GUI
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.translator import Translator
from core.pptx_processor import PPTXProcessor


def test_translator():
    """Test the fixed translator"""
    print("🔤 Testing Translator...")
    
    translator = Translator()
    
    test_texts = [
        "Hallo, wie geht es dir?",
        "Dies ist ein Test.",
        "Guten Morgen, Deutschland!"
    ]
    
    for text in test_texts:
        try:
            result = translator.translate_text(text, source_lang='de', target_lang='en')
            print(f"✓ '{text}' -> '{result}'")
        except Exception as e:
            print(f"✗ Translation failed for '{text}': {e}")
    
    print()


def test_pptx_processor(pptx_file_path: str, slide_range: str = "1-3"):
    """Test the fixed PPTX processor"""
    print(f"📄 Testing PPTX Processor with {pptx_file_path}...")
    
    if not os.path.exists(pptx_file_path):
        print(f"✗ PowerPoint file not found: {pptx_file_path}")
        return
    
    try:
        # Initialize processor
        processor = PPTXProcessor(pptx_file_path)
        processor.load_presentation()
        
        print(f"✓ Loaded presentation with {processor.processing_stats['total_slides']} slides")
        
        # Extract text elements
        processor.extract_text_elements(slide_range)
        print(f"✓ Extracted {len(processor.text_elements)} text elements")
        
        # Show preview
        preview = processor.get_text_elements_preview(5)
        print("\n📋 Text Elements Preview:")
        for item in preview:
            print(f"  Element {item['id']} (Slide {item['slide']}):")
            print(f"    Text: {item['original_text']}")
            print(f"    Font: {item['formatting']['font_name']} ({item['formatting']['font_size']}pt)")
            print(f"    Alignment: {item['formatting']['alignment']}")
            print()
        
        # Translate elements
        print("🔄 Translating elements...")
        processor.translate_text_elements()
        
        stats = processor.get_processing_stats()
        print(f"✓ Translation completed:")
        print(f"    Translated: {stats['translated_elements']}")
        print(f"    Skipped: {stats['skipped_elements']}")
        print(f"    Errors: {stats['error_count']}")
        
        # Show translated preview
        print("\n📋 Translated Elements Preview:")
        preview = processor.get_text_elements_preview(5)
        for item in preview:
            if item['translated_text']:
                print(f"  Element {item['id']}: '{item['original_text'][:50]}...' -> '{item['translated_text'][:50]}...'")
        
        # Apply translations
        print("\n✏️ Applying translations...")
        processor.apply_translations()
        
        # Save test file
        output_file = pptx_file_path.replace('.pptx', '_translated_test.pptx')
        processor.save_presentation(output_file)
        print(f"✓ Test file saved: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"✗ PPTX processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("🚀 PPTrans Translation & Formatting Test")
    print("=" * 50)
    
    # Test translator
    test_translator()
    
    # Test PPTX processor
    pptx_file = input("📁 Enter path to your PowerPoint file (or press Enter to skip): ").strip()
    if pptx_file and os.path.exists(pptx_file):
        slide_range = input("📋 Enter slide range to test (e.g., '1-3' or press Enter for '1-3'): ").strip() or "1-3"
        success = test_pptx_processor(pptx_file, slide_range)
        
        if success:
            print("\n✅ All tests passed! The fixes should work in your GUI.")
        else:
            print("\n❌ Tests failed. Please check the error messages above.")
    else:
        print("⚠️ Skipping PPTX test - no file provided")
    
    print("\n🎯 Next steps:")
    print("1. If tests passed, copy the fixed files to your project")
    print("2. Test with your GUI: python src/main.py")
    print("3. Try translating slides 16-18 of your presentation")


if __name__ == "__main__":
    main()