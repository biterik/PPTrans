#!/usr/bin/env python3
"""
Final LanguageManager fix with correct method parameters that match GUI expectations
"""

import sys
import os
from pathlib import Path

def fix_get_language_list_method():
    """Fix the get_language_list method to match GUI expectations"""
    
    lang_mgr_path = Path('src/core/language_manager.py')
    if not lang_mgr_path.exists():
        print(f"❌ File not found: {lang_mgr_path}")
        return False
    
    # Read current content
    with open(lang_mgr_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the get_language_list method
    old_method = '''    def get_language_list(self, popular_first: bool = False) -> List[Tuple[str, str]]:
        """
        Get list of languages formatted for GUI dropdowns
        This is the method the GUI is looking for!
        
        Args:
            popular_first: If True, put popular languages first
            
        Returns:
            List of tuples (language_code, language_name)
        """'''
    
    new_method = '''    def get_language_list(self, include_auto_detect: bool = True, popular_first: bool = False) -> List[Tuple[str, str]]:
        """
        Get list of languages formatted for GUI dropdowns
        This is the method the GUI is looking for!
        
        Args:
            include_auto_detect: If True, include "Auto-detect" option at the top
            popular_first: If True, put popular languages first
            
        Returns:
            List of tuples (language_code, language_name)
        """
        result = []
        
        # Add auto-detect option if requested
        if include_auto_detect:
            result.append(("auto", "Auto-detect"))'''
    
    # Replace the method definition
    if old_method in content:
        # Replace method signature and add the auto-detect logic
        content = content.replace(old_method, new_method)
        
        # Also need to update the method body to handle the auto-detect logic
        old_body_start = '''        if popular_first:'''
        new_body_start = '''        
        if popular_first:'''
        
        content = content.replace(old_body_start, new_body_start)
        
        # Update the return statements to use result list
        content = content.replace(
            'return popular_langs + remaining_langs',
            'result.extend(popular_langs + remaining_langs)\n            return result'
        )
        content = content.replace(
            'return all_langs',
            'result.extend(all_langs)\n            return result'
        )
        
        try:
            with open(lang_mgr_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed get_language_list method in {lang_mgr_path}")
            return True
        except Exception as e:
            print(f"❌ Error writing file: {e}")
            return False
    else:
        print("❌ Could not find method to replace")
        return False

def create_quick_complete_fix():
    """Create a complete working language manager with the correct method signature"""
    
    content = '''"""
Complete Language manager for PPTrans with all GUI-required methods
Final version with correct method signatures
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
        
        # Handle auto-detect
        if code == 'auto':
            return True
        
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
        
        # Handle auto-detect
        if code == 'auto':
            return 'auto'
        
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
        
        if code == 'auto':
            return 'Auto-detect'
        
        code = self.normalize_language_code(code)
        return self.languages.get(code)
    
    def get_common_languages(self) -> Dict[str, str]:
        """
        Get a curated list of commonly used languages
        
        Returns:
            Dictionary of common language codes and names
        """
        return {code: self.languages[code] for code in self.popular_languages if code in self.languages}
    
    def get_language_list(self, include_auto_detect: bool = True, popular_first: bool = False) -> List[Tuple[str, str]]:
        """
        Get list of languages formatted for GUI dropdowns
        This is the method the GUI is looking for with correct parameters!
        
        Args:
            include_auto_detect: If True, include "Auto-detect" option at the top
            popular_first: If True, put popular languages first
            
        Returns:
            List of tuples (language_code, language_name)
        """
        result = []
        
        # Add auto-detect option if requested
        if include_auto_detect:
            result.append(("auto", "Auto-detect"))
        
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
            
            result.extend(popular_langs + remaining_langs)
        else:
            # Return all languages sorted by name
            all_langs = [(code, name) for code, name in self.languages.items()]
            all_langs.sort(key=lambda x: x[1])  # Sort by name
            result.extend(all_langs)
        
        return result
    
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
        language_list = self.get_language_list(include_auto_detect=False, popular_first=True)
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

def apply_final_fix():
    """Apply the final complete fix"""
    print("\n=== Applying Final LanguageManager Fix ===")
    
    lang_mgr_path = Path('src/core/language_manager.py')
    if not lang_mgr_path.exists():
        print(f"❌ File not found: {lang_mgr_path}")
        return False
    
    # Create backup
    backup_path = Path(str(lang_mgr_path) + '.backup_final')
    if lang_mgr_path.exists():
        with open(lang_mgr_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Backup created: {backup_path}")
    
    try:
        # Write the complete final language manager
        final_content = create_quick_complete_fix()
        with open(lang_mgr_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"✅ Applied final LanguageManager fix to {lang_mgr_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error applying final fix: {e}")
        return False

def test_final_language_manager():
    """Test the final language manager"""
    print("\n=== Testing Final LanguageManager ===")
    
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
        
        # Test the method with the correct parameters that the GUI uses
        source_languages = lang_mgr.get_language_list(include_auto_detect=True, popular_first=True)
        print(f"✅ get_language_list(include_auto_detect=True, popular_first=True): {len(source_languages)} languages")
        print(f"   First few: {source_languages[:3]}")
        
        target_languages = lang_mgr.get_language_list(include_auto_detect=False, popular_first=True)  
        print(f"✅ get_language_list(include_auto_detect=False, popular_first=True): {len(target_languages)} languages")
        print(f"   First few: {target_languages[:3]}")
        
        # Test validation
        print(f"✅ is_valid_language_code('auto'): {lang_mgr.is_valid_language_code('auto')}")
        print(f"✅ is_valid_language_code('en'): {lang_mgr.is_valid_language_code('en')}")
        print(f"✅ is_valid_language_code('de'): {lang_mgr.is_valid_language_code('de')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Final LanguageManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to apply and test the final fix"""
    print("Final LanguageManager Fix for PPTrans GUI")
    print("=" * 50)
    
    # Check we're in the right directory
    if not Path('src').exists():
        print("❌ Please run this script from the PPTrans project root directory")
        return False
    
    success = True
    
    # Apply the final fix
    success &= apply_final_fix()
    
    # Test the final fix
    if success:
        success &= test_final_language_manager()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Final LanguageManager fix applied and tested!")
        print("\n✨ Fixed method signature:")
        print("   get_language_list(include_auto_detect=True, popular_first=False)")
        print("\n🔧 Next step:")
        print("   Test the GUI: python src/main.py")
        print("   Should launch without LanguageManager errors!")
    else:
        print("❌ Some issues remain. Please check the output above.")
    
    return success

if __name__ == "__main__":
    main()
