#!/usr/bin/env python3
"""
PPTrans Translation Fix Script
Fixes the current translation issues and tests the fixes
"""

import sys
import os
from pathlib import Path

def backup_file(file_path):
    """Create a backup of the original file"""
    backup_path = Path(str(file_path) + '.backup')
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Backup created: {backup_path}")
    return backup_path

def fix_language_manager():
    """Fix the LanguageManager class"""
    print("\n=== Fixing Language Manager ===")
    
    lang_mgr_path = Path('src/core/language_manager.py')
    if not lang_mgr_path.exists():
        print(f"❌ File not found: {lang_mgr_path}")
        return False
    
    backup_file(lang_mgr_path)
    
    # Updated LanguageManager with is_valid_language_code method
    fixed_content = '''"""
Language manager for PPTrans with validation methods
"""

from typing import Dict, List, Optional
from googletrans import LANGUAGES
from utils.logger import LoggerMixin

class LanguageManager(LoggerMixin):
    """Manages language codes and validation for translation"""
    
    def __init__(self):
        """Initialize language manager with Google Translate languages"""
        # Use Google Translate's language dictionary
        self.languages = LANGUAGES.copy()
        
        # Add some common aliases and variations
        self.language_aliases = {
            'zh': 'zh-cn',  # Chinese simplified
            'zh-hans': 'zh-cn',
            'zh-hant': 'zh-tw',
            'pt': 'pt',     # Portuguese
            'pt-br': 'pt',  # Brazilian Portuguese -> Portuguese
        }
        
        self.logger.info(f"Language manager initialized with {len(self.languages)} languages")
    
    def is_valid_language_code(self, code: str) -> bool:
        """
        Check if a language code is valid
        
        Args:
            code: Language code to validate (e.g., 'en', 'de', 'zh-cn')
            
        Returns:
            True if code is valid, False otherwise
        """
        if not code:
            return False
        
        code = code.lower().strip()
        
        # Check direct match
        if code in self.languages:
            return True
        
        # Check aliases
        if code in self.language_aliases:
            return True
        
        # Check if it's a variant (like 'en-US' for 'en')
        if '-' in code:
            base_code = code.split('-')[0]
            if base_code in self.languages:
                return True
        
        return False
    
    def normalize_language_code(self, code: str) -> str:
        """
        Normalize a language code to the standard format
        
        Args:
            code: Language code to normalize
            
        Returns:
            Normalized language code
        """
        if not code:
            return code
        
        code = code.lower().strip()
        
        # Check aliases first
        if code in self.language_aliases:
            return self.language_aliases[code]
        
        # Check if it's a variant
        if '-' in code:
            base_code = code.split('-')[0]
            if base_code in self.languages:
                return base_code
        
        return code
    
    def get_all_languages(self) -> Dict[str, str]:
        """
        Get all available languages
        
        Returns:
            Dictionary mapping language codes to language names
        """
        return self.languages.copy()
    
    def get_language_name(self, code: str) -> Optional[str]:
        """
        Get the name of a language from its code
        
        Args:
            code: Language code
            
        Returns:
            Language name or None if not found
        """
        if not code:
            return None
        
        code = self.normalize_language_code(code)
        return self.languages.get(code)
    
    def get_common_languages(self) -> Dict[str, str]:
        """
        Get a curated list of commonly used languages
        
        Returns:
            Dictionary of common language codes and names
        """
        common_codes = [
            'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh-cn', 
            'ar', 'hi', 'tr', 'pl', 'nl', 'sv', 'da', 'no', 'fi', 'el'
        ]
        
        return {code: self.languages[code] for code in common_codes if code in self.languages}
    
    def search_languages(self, query: str) -> Dict[str, str]:
        """
        Search for languages by name or code
        
        Args:
            query: Search query
            
        Returns:
            Dictionary of matching languages
        """
        query = query.lower().strip()
        if not query:
            return {}
        
        matches = {}
        
        # Search by code
        for code, name in self.languages.items():
            if query in code.lower() or query in name.lower():
                matches[code] = name
        
        return matches
    
    def get_language_choices_for_gui(self) -> List[tuple]:
        """
        Get language choices formatted for GUI dropdown
        
        Returns:
            List of tuples (display_name, language_code)
        """
        choices = []
        
        # Add auto-detect option
        choices.append(("Auto-detect", "auto"))
        
        # Add all languages sorted by name
        sorted_languages = sorted(self.languages.items(), key=lambda x: x[1])
        for code, name in sorted_languages:
            display_name = f"{name.title()} ({code})"
            choices.append((display_name, code))
        
        return choices
    
    def get_common_language_choices_for_gui(self) -> List[tuple]:
        """
        Get common language choices formatted for GUI dropdown
        
        Returns:
            List of tuples (display_name, language_code) for common languages
        """
        choices = []
        
        # Add auto-detect option
        choices.append(("Auto-detect", "auto"))
        
        # Add common languages
        common = self.get_common_languages()
        sorted_common = sorted(common.items(), key=lambda x: x[1])
        
        for code, name in sorted_common:
            display_name = f"{name.title()} ({code})"
            choices.append((display_name, code))
        
        return choices
    
    def validate_language_pair(self, source: str, target: str) -> tuple:
        """
        Validate a source-target language pair
        
        Args:
            source: Source language code
            target: Target language code
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Source can be 'auto'
        if source != 'auto' and not self.is_valid_language_code(source):
            return False, f"Invalid source language code: {source}"
        
        if not self.is_valid_language_code(target):
            return False, f"Invalid target language code: {target}"
        
        # Normalize codes for comparison
        norm_source = self.normalize_language_code(source) if source != 'auto' else 'auto'
        norm_target = self.normalize_language_code(target)
        
        # Check if source and target are the same (unless auto-detect)
        if norm_source != 'auto' and norm_source == norm_target:
            source_name = self.get_language_name(norm_source)
            return False, f"Source and target language are the same ({source_name})"
        
        return True, ""
'''
    
    try:
        with open(lang_mgr_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"✅ Fixed {lang_mgr_path}")
        return True
    except Exception as e:
        print(f"❌ Error fixing language manager: {e}")
        return False

def test_translation_api():
    """Test the translation API with proper error handling"""
    print("\n=== Testing Translation API ===")
    
    try:
        # Add src to path
        src_path = Path('src').absolute()
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        from core.translator import PPTransTranslator
        from core.language_manager import LanguageManager
        
        # Test language manager first
        lang_mgr = LanguageManager()
        print(f"✅ LanguageManager loaded with {len(lang_mgr.get_all_languages())} languages")
        print(f"✅ is_valid_language_code method: {hasattr(lang_mgr, 'is_valid_language_code')}")
        print(f"✅ English valid: {lang_mgr.is_valid_language_code('en')}")
        print(f"✅ German valid: {lang_mgr.is_valid_language_code('de')}")
        
        # Test translator
        translator = PPTransTranslator({'max_retries': 2})
        
        # Test simple translation
        test_text = "Hallo Welt"
        result = translator.translate_text(test_text, 'de', 'en')
        print(f"✅ Test translation: '{test_text}' → '{result}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Translation API test failed: {e}")
        return False

def test_pptx_processing():
    """Test PowerPoint processing with better error handling"""
    print("\n=== Testing PowerPoint Processing ===")
    
    try:
        # Add src to path
        src_path = Path('src').absolute()
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        from core.pptx_processor import PPTXProcessor
        
        processor = PPTXProcessor()
        print("✅ PPTXProcessor created successfully")
        
        # Check if key methods exist
        required_methods = [
            '_apply_text_to_shape',
            '_extract_text_formatting',
            'extract_text_elements',
            'apply_translations'
        ]
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(processor, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"⚠️  Missing methods in PPTXProcessor: {missing_methods}")
            print("   You'll need to add the fixed methods from the PowerPoint fix artifact")
        else:
            print("✅ All required methods present")
        
        return len(missing_methods) == 0
        
    except Exception as e:
        print(f"❌ PowerPoint processing test failed: {e}")
        return False

def main():
    """Main fix and test function"""
    print("PPTrans Translation Fix Script")
    print("=" * 50)
    
    # Check we're in the right directory
    if not Path('src').exists():
        print("❌ Please run this script from the PPTrans project root directory")
        return False
    
    success = True
    
    # Fix language manager
    success &= fix_language_manager()
    
    # Test the fixes
    success &= test_translation_api()
    success &= test_pptx_processing()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All fixes applied and tests passed!")
        print("\nNext steps:")
        print("1. If PPTXProcessor methods are missing, copy them from the PowerPoint fix artifact")
        print("2. Test with: python src/main.py")
        print("3. Try translating a small slide range (e.g., just '1' or '1-2')")
    else:
        print("❌ Some issues remain. Check the output above for details.")
    
    print(f"\n📋 Summary of what was fixed:")
    print(f"   - Added is_valid_language_code() method to LanguageManager")
    print(f"   - Improved language validation and normalization")
    print(f"   - Enhanced error handling in language operations")
    print(f"   - Better type hints and return values")
    
    return success

if __name__ == "__main__":
    main()
