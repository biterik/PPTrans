"""
Translation Engine - Fixed to match GUI expectations
"""
import requests
import json
import time
import re
from typing import Optional
from urllib.parse import quote
from utils.logger import LoggerMixin
from utils.exceptions import TranslationError, NetworkError, RateLimitError


class PPTransTranslator(LoggerMixin):
    """Translation service that matches GUI expectations"""
    
    def __init__(self, translation_settings: dict):
        """Initialize with translation settings from config"""
        self.settings = translation_settings
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.last_request_time = 0
        self.min_request_interval = 0.5  # 500ms between requests
        
        self.logger.info("PPTransTranslator initialized")
        
    def _wait_for_rate_limit(self):
        """Implement rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    def _clean_text(self, text: str) -> str:
        """Clean text before translation"""
        if not text:
            return ""
        
        # Remove excessive whitespace but preserve single spaces
        cleaned = re.sub(r'\s+', ' ', text.strip())
        return cleaned
    
    def _translate_via_google_http(self, text: str, source_lang: str = 'auto', target_lang: str = 'en') -> str:
        """Direct HTTP translation using Google Translate"""
        try:
            self._wait_for_rate_limit()
            
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': source_lang,
                'tl': target_lang,
                'dt': 't',
                'q': text
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract translated text from response
            if result and len(result) > 0 and result[0]:
                translated_parts = []
                for part in result[0]:
                    if part and len(part) > 0:
                        translated_parts.append(part[0])
                
                translated_text = ''.join(translated_parts)
                if translated_text and translated_text.strip():
                    self.logger.debug(f"HTTP translation successful: '{text[:50]}...' -> '{translated_text[:50]}...'")
                    return translated_text.strip()
            
            raise TranslationError("Invalid response format from Google Translate")
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP translation failed: {e}")
            raise NetworkError(f"Network error: {e}", url=url)
        except Exception as e:
            self.logger.error(f"HTTP translation error: {e}")
            raise TranslationError(f"Translation failed: {e}")
    
    def _translate_via_mymemory(self, text: str, source_lang: str = 'auto', target_lang: str = 'en') -> str:
        """Fallback translation using MyMemory API"""
        try:
            self._wait_for_rate_limit()
            
            # Convert language codes if needed
            lang_pair = f"{source_lang}|{target_lang}" if source_lang != 'auto' else f"de|{target_lang}"
            
            url = "https://api.mymemory.translated.net/get"
            params = {
                'q': text,
                'langpair': lang_pair
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('responseStatus') == 200:
                translated_text = result.get('responseData', {}).get('translatedText', '')
                if translated_text and translated_text != text:
                    self.logger.debug(f"MyMemory translation successful: '{text[:50]}...' -> '{translated_text[:50]}...'")
                    return translated_text.strip()
            
            raise TranslationError("MyMemory API returned no translation")
            
        except Exception as e:
            self.logger.error(f"MyMemory translation error: {e}")
            raise TranslationError(f"MyMemory translation failed: {e}")
    
    def translate_text(self, text: str, source_lang: str = 'auto', target_lang: str = 'en') -> str:
        """
        Translate text with multiple fallback methods
        
        Args:
            text: Text to translate
            source_lang: Source language code (default 'auto')
            target_lang: Target language code (default 'en')
            
        Returns:
            str: Translated text
        """
        if not text or not text.strip():
            return text
        
        cleaned_text = self._clean_text(text)
        if not cleaned_text:
            return text
        
        self.logger.debug(f"Translating: '{cleaned_text[:100]}...'")
        
        # Try multiple translation methods
        translation_methods = [
            ("Google HTTP", self._translate_via_google_http),
            ("MyMemory", self._translate_via_mymemory)
        ]
        
        for method_name, method in translation_methods:
            try:
                self.logger.debug(f"Trying {method_name} translation...")
                result = method(cleaned_text, source_lang, target_lang)
                
                if result and result.strip() and result != cleaned_text:
                    self.logger.info(f"Translation successful using {method_name}")
                    return result
                else:
                    self.logger.warning(f"{method_name} returned same text or empty result")
                    
            except Exception as e:
                self.logger.warning(f"{method_name} failed: {e}")
                continue
        
        # If all methods fail, return original text
        self.logger.error(f"All translation methods failed for: '{cleaned_text[:50]}...'")
        return text  # Return original text rather than failing
    
    def test_connection(self) -> bool:
        """Test connection to translation service"""
        try:
            test_text = "Hello"
            result = self.translate_text(test_text, 'en', 'es')
            return result != test_text  # Should be different if working
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def detect_language(self, text: str) -> str:
        """Detect the language of the given text"""
        if not text or not text.strip():
            return 'unknown'
        
        try:
            self._wait_for_rate_limit()
            
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': 'auto',
                'tl': 'en',
                'dt': 't',
                'q': text[:100]  # Use first 100 chars for detection
            }
            
            response = self.session.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract detected language from response
            if result and len(result) > 2 and result[2]:
                detected_lang = result[2]
                self.logger.debug(f"Detected language: {detected_lang}")
                return detected_lang
            
            return 'unknown'
            
        except Exception as e:
            self.logger.error(f"Language detection failed: {e}")
            return 'unknown'