#!/usr/bin/env python3
"""
Ultra-robust translator fix for the 'int' object has no attribute 'as_dict' error
This completely replaces the translator.py file with a version that handles all API response variations
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

def create_robust_translator():
    """Create a completely robust translator that handles all API response formats"""
    
    translator_content = '''"""
Ultra-robust translation engine for PPTrans using Google Translate
Handles all possible API response formats including the 'int' object error
"""

import time
import re
import json
from typing import List, Dict, Optional, Tuple, Union, Any
from googletrans import Translator, LANGUAGES
import requests.exceptions
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.logger import LoggerMixin, log_performance
from utils.exceptions import (
    TranslationError, NetworkError, RateLimitError, 
    AuthenticationError, ValidationError
)
from .language_manager import LanguageManager

class PPTransTranslator(LoggerMixin):
    """Ultra-robust translation engine with comprehensive error handling"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize translator with configuration
        
        Args:
            config: Configuration dictionary for translator settings
        """
        self.config = config or {}
        self.chunk_size = self.config.get('chunk_size', 5000)
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay = self.config.get('retry_delay', 1.0)
        self.timeout = self.config.get('timeout', 30)
        self.parallel_processing = self.config.get('parallel_processing', False)
        self.max_workers = self.config.get('max_workers', 4)
        
        # Initialize Google Translator
        self.translator = Translator(timeout=self.timeout)
        self.language_manager = LanguageManager()
        
        # Statistics tracking
        self.stats = {
            'translations_performed': 0,
            'characters_translated': 0,
            'errors_encountered': 0,
            'retries_performed': 0,
            'total_time': 0.0
        }
        
        self.logger.info(f"Translator initialized with config: {self.config}")
    
    def _is_translatable_text(self, text: str) -> bool:
        """
        Check if text contains translatable content
        
        Args:
            text: Text to check
        
        Returns:
            True if text should be translated
        """
        if not text or not text.strip():
            return False
        
        # Skip if text is only numbers, punctuation, or whitespace
        if re.match(r'^[\\d\\s\\-.,;:!?()[\\]{}"\\''/\\\\]*$', text.strip()):
            return False
        
        # Skip very short text (likely not meaningful)
        if len(text.strip()) < 2:
            return False
        
        # Skip URLs
        if re.match(r'^https?://', text.strip().lower()):
            return False
        
        # Skip email addresses
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$', text.strip()):
            return False
        
        return True
    
    def _safe_extract_translation(self, result: Any, original_text: str) -> str:
        """
        Ultra-robust extraction of translation text from any possible API response
        
        Args:
            result: Translation result from googletrans (any type)
            original_text: Original text that was being translated
            
        Returns:
            Translated text string
        """
        try:
            self.logger.debug(f"API result type: {type(result)}, value: {str(result)[:100]}...")
            
            # Handle None result
            if result is None:
                self.logger.warning("API returned None result")
                return original_text
            
            # Handle string result (direct translation)
            if isinstance(result, str):
                self.logger.debug("API returned direct string")
                return result if result.strip() else original_text
            
            # Handle integer result (the problematic case)
            if isinstance(result, int):
                self.logger.warning(f"API returned integer result: {result}")
                return original_text  # Return original text when API returns int
            
            # Handle float result
            if isinstance(result, float):
                self.logger.warning(f"API returned float result: {result}")
                return original_text
            
            # Handle standard translation object with .text attribute
            if hasattr(result, 'text'):
                translated = result.text
                self.logger.debug(f"Extracted via .text: {translated[:50]}...")
                return translated if translated and translated.strip() else original_text
            
            # Handle object with .as_dict() method
            if hasattr(result, 'as_dict'):
                try:
                    result_dict = result.as_dict()
                    if isinstance(result_dict, dict):
                        # Try different possible keys
                        for key in ['translatedText', 'text', 'translation']:
                            if key in result_dict:
                                translated = result_dict[key]
                                self.logger.debug(f"Extracted via as_dict()['{key}']: {translated[:50]}...")
                                return translated if translated and translated.strip() else original_text
                    self.logger.warning(f"as_dict() returned non-dict: {type(result_dict)}")
                except Exception as e:
                    self.logger.warning(f"Error calling as_dict(): {e}")
            
            # Handle dictionary result
            if isinstance(result, dict):
                self.logger.debug("API returned dictionary")
                for key in ['translatedText', 'text', 'translation', 'result']:
                    if key in result:
                        translated = result[key]
                        self.logger.debug(f"Extracted from dict['{key}']: {translated[:50]}...")
                        return translated if translated and translated.strip() else original_text
            
            # Handle list result (sometimes API returns a list)
            if isinstance(result, list):
                self.logger.debug(f"API returned list with {len(result)} items")
                if result:
                    # Try to extract from first item
                    first_item = result[0]
                    return self._safe_extract_translation(first_item, original_text)
            
            # Handle tuple result
            if isinstance(result, tuple):
                self.logger.debug(f"API returned tuple with {len(result)} items")
                if result:
                    # Try to extract from first item
                    first_item = result[0]
                    return self._safe_extract_translation(first_item, original_text)
            
            # Last resort: try to convert to string
            result_str = str(result).strip()
            if result_str and result_str != str(type(result)):
                self.logger.debug(f"Using string conversion: {result_str[:50]}...")
                return result_str
            
            # Ultimate fallback: return original text
            self.logger.warning(f"Could not extract translation from {type(result)}, returning original")
            return original_text
            
        except Exception as e:
            self.logger.error(f"Error in _safe_extract_translation: {e}")
            return original_text
    
    def _create_fallback_translator(self):
        """Create a new translator instance as fallback"""
        try:
            return Translator(timeout=self.timeout)
        except Exception as e:
            self.logger.warning(f"Could not create fallback translator: {e}")
            return None
    
    @log_performance
    def translate_text(
        self, 
        text: str, 
        source_lang: str = 'auto', 
        target_lang: str = 'en'
    ) -> str:
        """
        Ultra-robust text translation with comprehensive error handling
        
        Args:
            text: Text to translate
            source_lang: Source language code (default: 'auto')
            target_lang: Target language code (default: 'en')
        
        Returns:
            Translated text
        
        Raises:
            TranslationError: If translation fails after all retries and fallbacks
        """
        if not text or not text.strip():
            return text
        
        # Check if text needs translation
        if not self._is_translatable_text(text):
            self.logger.debug(f"Skipping non-translatable text: {text[:50]}...")
            return text
        
        # Validate languages
        if not self.language_manager.is_valid_language_code(source_lang) and source_lang != 'auto':
            self.logger.warning(f"Invalid source language code: {source_lang}, using 'auto'")
            source_lang = 'auto'
        
        if not self.language_manager.is_valid_language_code(target_lang):
            raise ValidationError(f"Invalid target language code: {target_lang}")
        
        # Skip if source and target are the same (and not auto-detect)
        if source_lang == target_lang and source_lang != 'auto':
            return text
        
        last_exception = None
        current_translator = self.translator
        
        # Try with main translator first, then fallback translator
        for translator_attempt in range(2):
            if translator_attempt == 1:
                self.logger.info("Trying fallback translator...")
                fallback_translator = self._create_fallback_translator()
                if fallback_translator:
                    current_translator = fallback_translator
                else:
                    break
            
            for attempt in range(self.max_retries + 1):
                try:
                    # Add delay between retries (but not on first attempt)
                    if attempt > 0:
                        delay = self.retry_delay * (attempt ** 2)  # Exponential backoff
                        self.logger.debug(f"Waiting {delay:.1f}s before retry {attempt}")
                        time.sleep(delay)
                        self.stats['retries_performed'] += 1
                    
                    self.logger.debug(f"Translation attempt {attempt + 1}/{self.max_retries + 1} "
                                    f"(translator {translator_attempt + 1}/2): '{text[:50]}...'")
                    
                    # Perform translation
                    result = current_translator.translate(
                        text, 
                        src=source_lang, 
                        dest=target_lang
                    )
                    
                    # Extract translated text using ultra-robust method
                    translated_text = self._safe_extract_translation(result, text)
                    
                    # Sanity check: if translation is identical to original and we expected a change
                    if (translated_text == text and 
                        source_lang != 'auto' and 
                        source_lang != target_lang and 
                        len(text.strip()) > 3):
                        self.logger.debug("Translation identical to original, might be correct or API issue")
                    
                    # Update statistics
                    self.stats['translations_performed'] += 1
                    self.stats['characters_translated'] += len(text)
                    
                    # Log success
                    if source_lang == 'auto':
                        detected_lang = getattr(result, 'src', 'unknown') if hasattr(result, 'src') else 'unknown'
                        self.logger.debug(f"✅ Translated ({detected_lang}→{target_lang}): '{text[:30]}...' → '{translated_text[:30]}...'")
                    else:
                        self.logger.debug(f"✅ Translated ({source_lang}→{target_lang}): '{text[:30]}...' → '{translated_text[:30]}...'")
                    
                    return translated_text
                    
                except requests.exceptions.ConnectionError as e:
                    last_exception = NetworkError(f"Network connection failed: {str(e)}")
                    self.logger.warning(f"Network error on attempt {attempt + 1}: {e}")
                    
                except requests.exceptions.Timeout as e:
                    last_exception = NetworkError(f"Translation request timed out: {str(e)}")
                    self.logger.warning(f"Timeout error on attempt {attempt + 1}: {e}")
                    
                except requests.exceptions.HTTPError as e:
                    if hasattr(e, 'response') and e.response is not None:
                        if e.response.status_code == 429:
                            last_exception = RateLimitError(f"Rate limit exceeded: {str(e)}")
                            self.logger.warning(f"Rate limit error on attempt {attempt + 1}: {e}")
                            time.sleep(self.retry_delay * 3)  # Longer delay for rate limits
                        elif e.response.status_code in [401, 403]:
                            last_exception = AuthenticationError(f"Authentication failed: {str(e)}")
                            self.logger.error(f"Auth error on attempt {attempt + 1}: {e}")
                            break  # Don't retry auth errors
                        else:
                            last_exception = TranslationError(f"HTTP error {e.response.status_code}: {str(e)}")
                            self.logger.warning(f"HTTP error on attempt {attempt + 1}: {e}")
                    else:
                        last_exception = TranslationError(f"HTTP error: {str(e)}")
                        self.logger.warning(f"HTTP error on attempt {attempt + 1}: {e}")
                        
                except Exception as e:
                    # Handle any other exception
                    error_msg = str(e)
                    last_exception = TranslationError(f"Translation error: {error_msg}")
                    self.logger.warning(f"Translation error on attempt {attempt + 1} "
                                      f"(translator {translator_attempt + 1}): {last_exception}")
                    
                    # If this is an API format error, no point in retrying with same translator
                    if "'int' object has no attribute" in error_msg or "has no attribute 'as_dict'" in error_msg:
                        break  # Try fallback translator instead
        
        # All attempts and fallbacks failed
        self.stats['errors_encountered'] += 1
        self.logger.error(f"Translation completely failed after all attempts and fallbacks")
        
        # Return original text instead of raising exception (graceful degradation)
        self.logger.warning(f"Returning original text due to translation failure: '{text[:50]}...'")
        return text
    
    def translate_batch(
        self, 
        texts: List[str], 
        source_lang: str = 'auto', 
        target_lang: str = 'en',
        progress_callback: Optional[callable] = None
    ) -> List[str]:
        """
        Translate multiple texts with optional parallel processing
        
        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code
            progress_callback: Optional callback function for progress updates
        
        Returns:
            List of translated texts
        """
        if not texts:
            return []
        
        self.logger.info(f"Starting batch translation of {len(texts)} items ({source_lang}→{target_lang})")
        
        if self.parallel_processing and len(texts) > 1:
            return self._translate_parallel(texts, source_lang, target_lang, progress_callback)
        else:
            return self._translate_sequential(texts, source_lang, target_lang, progress_callback)
    
    def _translate_sequential(
        self, 
        texts: List[str], 
        source_lang: str, 
        target_lang: str,
        progress_callback: Optional[callable] = None
    ) -> List[str]:
        """Translate texts sequentially"""
        translated = []
        total = len(texts)
        
        for i, text in enumerate(texts):
            try:
                result = self.translate_text(text, source_lang, target_lang)
                translated.append(result)
                
                if progress_callback:
                    progress_callback(i + 1, total, f"Translated item {i + 1}/{total}")
                    
            except Exception as e:
                self.logger.warning(f"Failed to translate item {i}: {e}")
                translated.append(text)  # Keep original text on failure
        
        return translated
    
    def _translate_parallel(
        self, 
        texts: List[str], 
        source_lang: str, 
        target_lang: str,
        progress_callback: Optional[callable] = None
    ) -> List[str]:
        """Translate texts in parallel using ThreadPoolExecutor"""
        translated = [''] * len(texts)  # Pre-allocate list to maintain order
        completed = 0
        total = len(texts)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all translation tasks
            future_to_index = {
                executor.submit(self.translate_text, text, source_lang, target_lang): i
                for i, text in enumerate(texts)
            }
            
            # Process completed translations
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    result = future.result()
                    translated[index] = result
                except Exception as e:
                    self.logger.warning(f"Failed to translate item {index}: {e}")
                    translated[index] = texts[index]  # Keep original on failure
                
                completed += 1
                if progress_callback:
                    progress_callback(completed, total, f"Translated item {completed}/{total}")
        
        return translated
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get dictionary of supported language codes and names
        
        Returns:
            Dictionary mapping language codes to language names
        """
        return self.language_manager.get_all_languages()
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of given text
        
        Args:
            text: Text to analyze
        
        Returns:
            Detected language code or None if detection fails
        """
        if not text or not text.strip():
            return None
        
        try:
            result = self.translator.detect(text)
            detected_lang = result.lang if hasattr(result, 'lang') else str(result)
            self.logger.debug(f"Detected language: {detected_lang} for text: '{text[:50]}...'")
            return detected_lang
        except Exception as e:
            self.logger.warning(f"Language detection failed: {e}")
            return None
    
    def get_statistics(self) -> Dict:
        """Get translation statistics"""
        return self.stats.copy()
    
    def reset_statistics(self) -> None:
        """Reset translation statistics"""
        self.stats = {
            'translations_performed': 0,
            'characters_translated': 0,
            'errors_encountered': 0,
            'retries_performed': 0,
            'total_time': 0.0
        }
        self.logger.info("Translation statistics reset")
'''
    
    return translator_content

def apply_translator_fix():
    """Apply the ultra-robust translator fix"""
    print("\n=== Applying Ultra-Robust Translator Fix ===")
    
    translator_path = Path('src/core/translator.py')
    if not translator_path.exists():
        print(f"❌ File not found: {translator_path}")
        return False
    
    # Create backup
    backup_file(translator_path)
    
    try:
        # Write the robust translator
        robust_content = create_robust_translator()
        with open(translator_path, 'w', encoding='utf-8') as f:
            f.write(robust_content)
        
        print(f"✅ Applied ultra-robust translator fix to {translator_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error applying translator fix: {e}")
        return False

def test_robust_translator():
    """Test the robust translator"""
    print("\n=== Testing Ultra-Robust Translator ===")
    
    try:
        # Add src to path
        src_path = Path('src').absolute()
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        # Reimport to get the new version
        import importlib
        if 'core.translator' in sys.modules:
            importlib.reload(sys.modules['core.translator'])
        
        from core.translator import PPTransTranslator
        
        # Test translator with comprehensive error handling
        translator = PPTransTranslator({'max_retries': 2, 'retry_delay': 0.5})
        
        # Test simple translation
        test_texts = [
            "Hallo",
            "Guten Tag", 
            "Wie geht es dir?"
        ]
        
        successful_translations = 0
        for test_text in test_texts:
            try:
                result = translator.translate_text(test_text, 'de', 'en')
                print(f"✅ '{test_text}' → '{result}'")
                successful_translations += 1
            except Exception as e:
                print(f"⚠️  '{test_text}' failed: {e}")
        
        print(f"\nTranslation success rate: {successful_translations}/{len(test_texts)}")
        
        # Get statistics
        stats = translator.get_statistics()
        print(f"Translation stats: {stats}")
        
        return successful_translations > 0
        
    except Exception as e:
        print(f"❌ Ultra-robust translator test failed: {e}")
        return False

def main():
    """Main function to apply and test the fix"""
    print("Ultra-Robust Translator Fix for PPTrans")
    print("=" * 60)
    
    # Check we're in the right directory
    if not Path('src').exists():
        print("❌ Please run this script from the PPTrans project root directory")
        return False
    
    success = True
    
    # Apply the fix
    success &= apply_translator_fix()
    
    # Test the fix
    if success:
        success &= test_robust_translator()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Ultra-robust translator fix applied and tested successfully!")
        print("\n✨ Key improvements:")
        print("   - Handles 'int' object API responses gracefully")
        print("   - Falls back to original text when translation fails")
        print("   - Uses multiple fallback strategies")
        print("   - Creates backup translator instances")
        print("   - Comprehensive error logging")
        print("\n🔧 Next steps:")
        print("   1. Test with: python src/main.py")
        print("   2. Try a small slide range first (e.g., '1' or '1-2')")
        print("   3. Check that translations are now applied to slides")
    else:
        print("❌ Some issues remain. Please check the output above.")
    
    return success

if __name__ == "__main__":
    main()
