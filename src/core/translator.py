"""
Fixed Batch Translation Engine with improved splitting and context awareness
"""
import requests
import json
import time
import re
from typing import Optional, Dict, List, Tuple, Set
from urllib.parse import quote
from utils.logger import LoggerMixin
from utils.exceptions import TranslationError, NetworkError, RateLimitError


class PPTransTranslator(LoggerMixin):
    """Fixed batch translation service with reliable splitting and enhanced context"""
    
    def __init__(self, translation_settings: dict):
        """Initialize with translation settings from config"""
        self.settings = translation_settings
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Conservative rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.5  # Slower but more reliable
        self.request_count = 0
        self.hourly_limit = 200  # Very conservative
        self.hour_start_time = time.time()
        
        # Content filtering
        self.skip_patterns = self._compile_skip_patterns()
        self.context_terms = self._load_enhanced_context_terms()
        
        # Use individual translation instead of batching due to API unreliability
        self.use_batching = False  # Disable problematic batching
        
        self.logger.info("Fixed PPTransTranslator initialized (individual translation mode)")
        
    def _compile_skip_patterns(self) -> List[re.Pattern]:
        """Patterns for content that shouldn't be translated"""
        patterns = [
            re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),  # Email
            re.compile(r'^[\+\d\s\-\(\)☎📧]{6,}$'),  # Phone numbers and symbols
            re.compile(r'^https?://'),  # URLs
            re.compile(r'^[^\w\s]{1,3}$'),  # Single symbols/punctuation
            re.compile(r'^\d+$'),  # Numbers only
            re.compile(r'^[A-Z][a-z]+ [A-Z][a-z]+$'),  # Names (First Last)
            re.compile(r'^\s*[\.,;:!\?|►▪•♦<>]+\s*$'),  # Punctuation/symbols
            re.compile(r'^.{1,2}$'),  # Very short content
        ]
        return patterns
    
    def _load_enhanced_context_terms(self) -> Dict[str, str]:
        """Enhanced context-specific terms with better German academic vocabulary"""
        return {
            # University/Academic terms
            'Erstsemestertag': 'First Semester Orientation Day',
            'Studierende': 'students',
            'Studierenden': 'students',  # Different case
            'Studiengang': 'degree program',
            'Hochschule Heilbronn': 'Heilbronn University of Applied Sciences',
            'Heilbronn': 'Heilbronn',
            'Standort': 'location',  # This was causing the repetition
            'Standortes': 'location',
            'des Standortes': 'of the campus',  # Better contextual translation
            'am Standort': 'at the campus',
            'für den Standort': 'for the campus',
            
            # Student organization terms
            'Vertritt die Interessen': 'Represents the interests',
            'Plant Veranstaltungen': 'Plans events',
            'Seien Sie aktiv': 'Be active',
            'engagieren Sie sich': 'get involved',
            
            # Academic activities
            'Veranstaltungen': 'events',
            'Vorlesung': 'lecture',
            'Seminar': 'seminar',
            'Übung': 'tutorial',
            'Prüfung': 'exam',
            'Semester': 'semester',
            'Campus': 'campus',
            
            # General German terms that are often mistranslated
            'aller Art': 'of all kinds',
            'sich engagieren': 'get involved',
            'aktiv sein': 'be active',
            
            # Keep German place names
            'Deutschland': 'Germany',
            'Baden-Württemberg': 'Baden-Württemberg',
            
            # Names and titles that shouldn't be translated
            'GDM': 'GDM',
            'Ani Antonyan': 'Ani Antonyan',
            'mv-international': 'mv-international',
            'hs-heilbronn.de': 'hs-heilbronn.de',
        }
    
    def _should_skip_translation(self, text: str) -> bool:
        """Check if text should be skipped entirely"""
        if not text or not text.strip():
            return True
            
        text_clean = text.strip()
        
        # Check skip patterns
        for pattern in self.skip_patterns:
            if pattern.match(text_clean):
                self.logger.debug(f"Skipping translation (pattern match): '{text_clean}'")
                return True
        
        # Skip if only whitespace or punctuation
        if not re.search(r'\w', text_clean):
            self.logger.debug(f"Skipping translation (no words): '{text_clean}'")
            return True
            
        return False
    
    def _preprocess_text(self, text: str) -> str:
        """Apply enhanced context-aware preprocessing"""
        processed = text
        
        # Apply context term replacements for better translation
        for german_term, english_term in self.context_terms.items():
            # Use word boundaries to avoid partial replacements
            pattern = r'\b' + re.escape(german_term) + r'\b'
            if re.search(pattern, processed, re.IGNORECASE):
                processed = re.sub(pattern, english_term, processed, flags=re.IGNORECASE)
                self.logger.debug(f"Context preprocessing: {german_term} -> {english_term}")
        
        return processed
    
    def _postprocess_translation(self, original: str, translated: str) -> str:
        """Post-process translation to fix common issues"""
        if not translated or translated == original:
            return translated
        
        fixed = translated
        
        # Fix common repetition patterns
        repetition_fixes = {
            'of the location of the location': 'of the campus',
            'the location of the location': 'the campus',
            'for the location': 'for the campus',
            'at the location': 'at the campus',
            'students of the location': 'students at the campus',
        }
        
        for bad_phrase, good_phrase in repetition_fixes.items():
            if bad_phrase in fixed.lower():
                fixed = re.sub(re.escape(bad_phrase), good_phrase, fixed, flags=re.IGNORECASE)
                self.logger.debug(f"Post-processing fix: {bad_phrase} -> {good_phrase}")
        
        return fixed
    
    def _check_rate_limits(self):
        """Enhanced rate limiting"""
        current_time = time.time()
        
        # Reset hourly counter
        if current_time - self.hour_start_time > 3600:
            self.request_count = 0
            self.hour_start_time = current_time
        
        if self.request_count >= self.hourly_limit:
            wait_time = 3600 - (current_time - self.hour_start_time)
            self.logger.warning(f"Hourly rate limit reached. Waiting {wait_time:.0f} seconds")
            raise RateLimitError(f"Hourly rate limit exceeded. Try again in {wait_time:.0f} seconds", retry_after=wait_time)
        
        # Per-request interval
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            self.logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def _translate_single_via_google(self, text: str, source_lang: str = 'auto', target_lang: str = 'en') -> str:
        """Translate single text via Google Translate - more reliable than batching"""
        try:
            self._check_rate_limits()
            
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': source_lang,
                'tl': target_lang,
                'dt': 't',
                'ie': 'UTF-8',
                'oe': 'UTF-8',
                'q': text
            }
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 429:
                raise RateLimitError("Google Translate rate limit exceeded", retry_after=120)
            elif response.status_code == 403:
                raise RateLimitError("Google Translate access forbidden", retry_after=3600)
            
            response.raise_for_status()
            result = response.json()
            
            if result and len(result) > 0 and result[0]:
                translated_parts = []
                for part in result[0]:
                    if part and len(part) > 0:
                        translated_parts.append(part[0])
                
                translated_text = ''.join(translated_parts)
                if translated_text and translated_text.strip():
                    return translated_text.strip()
            
            raise TranslationError("Empty response from Google Translate")
            
        except requests.exceptions.Timeout:
            raise NetworkError("Translation request timed out", timeout=15)
        except requests.exceptions.RequestException as e:
            if "429" in str(e) or "rate" in str(e).lower():
                raise RateLimitError("Rate limit exceeded", retry_after=120)
            raise NetworkError(f"Network error: {e}")
    
    def translate_text_batch(self, text_items: List[str], source_lang: str = 'auto', target_lang: str = 'en') -> List[str]:
        """
        Translate multiple text items using reliable individual translation
        (Batching disabled due to API splitting issues)
        """
        if not text_items:
            return []
        
        self.logger.info(f"Translating {len(text_items)} items individually (batching disabled)")
        
        translated_items = []
        
        for i, text in enumerate(text_items):
            try:
                if self._should_skip_translation(text):
                    translated_items.append(text)  # Keep original
                    self.logger.debug(f"Skipped item {i+1}: '{text[:30]}...'")
                else:
                    # Preprocess
                    preprocessed = self._preprocess_text(text)
                    
                    # Translate
                    translated = self._translate_single_via_google(preprocessed, source_lang, target_lang)
                    
                    # Post-process
                    final_translation = self._postprocess_translation(text, translated)
                    
                    translated_items.append(final_translation)
                    
                    if final_translation != text:
                        self.logger.debug(f"Translated item {i+1}: '{text[:30]}...' -> '{final_translation[:30]}...'")
                    else:
                        self.logger.debug(f"No change item {i+1}: '{text[:30]}...'")
                        
            except Exception as e:
                self.logger.error(f"Translation failed for item {i+1}: {e}")
                translated_items.append(text)  # Keep original on error
        
        success_count = sum(1 for i, item in enumerate(translated_items) if item != text_items[i])
        self.logger.info(f"Individual translation completed: {success_count}/{len(text_items)} items translated")
        
        return translated_items
    
    def translate_text(self, text: str, source_lang: str = 'auto', target_lang: str = 'en') -> str:
        """
        Single text translation with enhanced preprocessing and postprocessing
        """
        if not text or not text.strip():
            return text
        
        if self._should_skip_translation(text):
            return text
        
        try:
            # Preprocess
            preprocessed = self._preprocess_text(text)
            
            # Translate
            translated = self._translate_single_via_google(preprocessed, source_lang, target_lang)
            
            # Post-process
            final_translation = self._postprocess_translation(text, translated)
            
            return final_translation
            
        except Exception as e:
            self.logger.error(f"Translation failed for '{text[:30]}...': {e}")
            return text  # Return original on error
    
    def test_connection(self) -> bool:
        """Test connection to translation service"""
        try:
            test_result = self.translate_text("Hallo Welt", 'de', 'en')
            return test_result.lower() != "hallo welt"
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def get_translation_stats(self) -> Dict[str, int]:
        """Get translation statistics"""
        return {
            'requests_made': self.request_count,
            'requests_remaining': max(0, self.hourly_limit - self.request_count),
            'time_until_reset': max(0, int(3600 - (time.time() - self.hour_start_time)))
        }