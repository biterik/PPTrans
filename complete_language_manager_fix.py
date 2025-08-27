#!/usr/bin/env python3
"""
Complete LanguageManager fix with all methods needed by the GUI
"""

import sys
import os
from pathlib import Path

def backup_file(file_path):
    """Create a backup of the original file"""
    backup_path = Path(str(file_path) + '.backup3')
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Backup created: {backup_path}")
    return backup_path

def create_complete_language_manager():
    """Create a complete LanguageManager with all GUI-required methods"""
    
    content = '''"""
Complete Language manager for PPTrans with all GUI-required methods
"""

from typing import Dict, List, Optional, Tuple
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
        
        # Popular languages (most commonly used)
        self.popular_languages = [
            'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh-cn',
            'ar', 'hi', 'tr', 'pl', 'nl', 'sv', 'da', 'no', 'fi', 'el',
            'cs', 'hu', 'ro', 'sk', 'bg', 'hr', 'sl', 'et', 'lv', 'lt'
        ]
        
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
        return {code: self.languages[code] for code in self.popular_languages if code in self.languages}
    
    def get_language_list(self, popular_first: bool = False) -> List[Tuple[str, str]]:
        """
        Get list of languages formatted for GUI dropdowns
        This is the method the GUI is looking for!
        
        Args:
            popular_first: If True, put popular languages first
            
        Returns:
            List of tuples (language_code, language_name)
        """
        if popular_first:
            # Get popular languages first
            popular_langs = [(code, self.languages[code]) 
                           for code in self.popular_languages 
                           if code in self.languages]
            
            # Get remaining languages sorted by name
            remaining_codes = [code for code in self.languages.keys() 
                             if code not in self.popular_languages]
            remaining_langs = [(code, self.languages[code]) for code in remaining_codes]
            remaining_langs.sort(key=lambda x: x[1])  # Sort by name
            
            return popular_langs + remaining_langs
        else:
            # Return all languages sorted by name
            all_langs = [(code, name) for code, name in self.languages.items()]
            all_langs.sort(key=lambda x: x[1])  # Sort by name
            return all_langs
    
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
        
        # Search by code and name
        for code, name in self.languages.items():
            if query in code.lower() or query in name.lower():
                matches[code] = name
        
        return matches
    
    def get_language_choices_for_gui(self, include_auto: bool = True) -> List[Tuple[str, str]]:
        """
        Get language choices formatted for GUI dropdown with display names
        
        Args:
            include_auto: Whether to include auto-detect option
            
        Returns:
            List of tuples (display_name, language_code)
        """
        choices = []
        
        # Add auto-detect option if requested
        if include_auto:
            choices.append(("Auto-detect", "auto"))
        
        # Add all languages with formatted display names
        language_list = self.get_language_list(popular_first=True)
        for code, name in language_list:
            display_name = f"{name.title()} ({code})"
            choices.append((display_name, code))
        
        return choices
    
    def get_common_language_choices_for_gui(self, include_auto: bool = True) -> List[Tuple[str, str]]:
        """
        Get common language choices formatted for GUI dropdown
        
        Args:
            include_auto: Whether to include auto-detect option
            
        Returns:
            List of tuples (display_name, language_code) for common languages
        """
        choices = []
        
        # Add auto-detect option if requested
        if include_auto:
            choices.append(("Auto-detect", "auto"))
        
        # Add common languages
        common = self.get_common_languages()
        sorted_common = sorted(common.items(), key=lambda x: x[1])
        
        for code, name in sorted_common:
            display_name = f"{name.title()} ({code})"
            choices.append((display_name, code))
        
        return choices
    
    def validate_language_pair(self, source: str, target: str) -> Tuple[bool, str]:
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
    
    def get_language_code_from_display_name(self, display_name: str) -> Optional[str]:
        """
        Extract language code from display name used in GUI
        
        Args:
            display_name: Display name like "English (en)" or "Auto-detect"
            
        Returns:
            Language code or None if not found
        """
        if not display_name:
            return None
        
        # Handle auto-detect
        if display_name.strip().lower() == "auto-detect":
            return "auto"
        
        # Extract code from parentheses
        if '(' in display_name and ')' in display_name:
            start = display_name.rfind('(')
            end = display_name.rfind(')')
            if start < end:
                code = display_name[start+1:end].strip()
                if self.is_valid_language_code(code) or code == "auto":
                    return code
        
        # Fallback: search by name
        name_part = display_name.split('(')[0].strip().lower()
        for code, name in self.languages.items():
            if name.lower() == name_part:
                return code
        
        return None
    
    def format_language_display_name(self, code: str) -> str:
        """
        Format a language code into a display name for the GUI
        
        Args:
            code: Language code
            
        Returns:
            Formatted display name
        """
        if code == "auto":
            return "Auto-detect"
        
        name = self.get_language_name(code)
        if name:
            return f"{name.title()} ({code})"
        else:
            return code  # Fallback to just the code
'''
    
    return content

def apply_complete_language_manager_fix():
    """Apply the complete language manager fix"""
    print("\n=== Applying Complete LanguageManager Fix ===")
    
    lang_mgr_path = Path('src/core/language_manager.py')
    if not lang_mgr_path.exists():
        print(f"❌ File not found: {lang_mgr_path}")
        return False
    
    # Create backup
    backup_file(lang_mgr_path)
    
    try:
        # Write the complete language manager
        complete_content = create_complete_language_manager()
        with open(lang_mgr_path, 'w', encoding='utf-8') as f:
            f.write(complete_content)
        
        print(f"✅ Applied complete LanguageManager fix to {lang_mgr_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error applying LanguageManager fix: {e}")
        return False

def test_complete_language_manager():
    """Test the complete language manager"""
    print("\n=== Testing Complete LanguageManager ===")
    
    try:
        # Add src to path
        src_path = Path('src').absolute()
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        # Reimport to get the new version
        import importlib
        if 'core.language_manager' in sys.modules:
            importlib.reload(sys.modules['core.language_manager'])
        
        from core.language_manager import LanguageManager
        
        # Test the language manager
        lang_mgr = LanguageManager()
        print(f"✅ LanguageManager loaded with {len(lang_mgr.get_all_languages())} languages")
        
        # Test the method the GUI needs
        language_list = lang_mgr.get_language_list(popular_first=True)
        print(f"✅ get_language_list() works: {len(language_list)} languages")
        print(f"   First few: {language_list[:3]}")
        
        # Test other GUI methods
        choices = lang_mgr.get_language_choices_for_gui()
        print(f"✅ get_language_choices_for_gui() works: {len(choices)} choices")
        print(f"   First choice: {choices[0]}")
        
        # Test validation methods
        print(f"✅ is_valid_language_code('en'): {lang_mgr.is_valid_language_code('en')}")
        print(f"✅ is_valid_language_code('de'): {lang_mgr.is_valid_language_code('de')}")
        
        # Test display name extraction
        test_display = "English (en)"
        extracted_code = lang_mgr.get_language_code_from_display_name(test_display)
        print(f"✅ get_language_code_from_display_name('{test_display}'): {extracted_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Complete LanguageManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to apply and test the complete fix"""
    print("Complete LanguageManager Fix for PPTrans GUI")
    print("=" * 55)
    
    # Check we're in the right directory
    if not Path('src').exists():
        print("❌ Please run this script from the PPTrans project root directory")
        return False
    
    success = True
    
    # Apply the complete fix
    success &= apply_complete_language_manager_fix()
    
    # Test the complete fix
    if success:
        success &= test_complete_language_manager()
    
    print("\n" + "=" * 55)
    if success:
        print("🎉 Complete LanguageManager fix applied and tested!")
        print("\n✨ Added methods:")
        print("   - get_language_list(popular_first=False)")
        print("   - get_language_choices_for_gui(include_auto=True)")
        print("   - get_language_code_from_display_name(display_name)")
        print("   - format_language_display_name(code)")
        print("   - get_common_language_choices_for_gui()")
        print("   - All validation and normalization methods")
        print("\n🔧 Next step:")
        print("   Test the GUI: python src/main.py")
    else:
        print("❌ Some issues remain. Please check the output above.")
    
    return success

if __name__ == "__main__":
    main()
