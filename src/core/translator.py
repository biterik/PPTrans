"""
Translation engine for PPTrans using Google Translate
"""

import time
import re
from typing import List, Dict, Optional, Tuple
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
    """Advanced translation engine with error handling and optimization"""
    
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
        if re.match(r'^[\d\s\-.,;:!?()[\]{}"\'/\\]*$', text.strip()):
            return False
        
        # Skip very short text (likely not meaningful)
        if len(text.strip()) < 2:
            return False
        
        # Skip URLs
        if re.match(r'^https?://', text.strip().lower()):
            return False
        
        # Skip email addresses
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', text.strip()):
            return False
        
        return True
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks for translation
        
        Args:
            text: Text to chunk
        
        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        self.logger.debug(f"Split text into {len(chunks)} chunks")
        return chunks
    
    def _translate_chunk_with_retry(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate a single chunk with retry logic
        
        Args:
            text: Text chunk to translate
            source_lang: Source language code
            target_lang: Target language code
        
        Returns:
            Translated text
        
        Raises:
            TranslationError: If translation fails after all retries
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    self.logger.debug(f"Retry attempt {attempt} for chunk translation")
                    self.stats['retries_performed'] += 1
                    time.sleep(self.retry_delay * attempt)  # Exponential backoff
                
                # Perform translation
                result = self.translator.translate(
                    text, 
                    src=source_lang if source_lang != 'auto' else None, 
                    dest=target_lang
                )
                
                if result and result.text:
                    self.stats['translations_performed'] += 1
                    self.stats['characters_translated'] += len(text)
                    return result.text
                else:
                    raise TranslationError("Empty translation result")
            
            except requests.exceptions.Timeout as e:
                last_error = NetworkError(
                    f"Translation request timed out after {self.timeout}s",
                    timeout=self.timeout,
                    original_error=e
                )
                self.logger.warning(f"Translation timeout on attempt {attempt + 1}")
            
            except requests.exceptions.ConnectionError as e:
                last_error = NetworkError(
                    "Network connection error during translation",
                    original_error=e
                )
                self.logger.warning(f"Connection error on attempt {attempt + 1}")
            
            except requests.exceptions.HTTPError as e:
                if hasattr(e.response, 'status_code'):
                    if e.response.status_code == 429:
                        last_error = RateLimitError(
                            "Translation service rate limit exceeded",
                            retry_after=60.0,
                            original_error=e
                        )
                    elif e.response.status_code in [401, 403]:
                        last_error = AuthenticationError(
                            "Translation service authentication failed",
                            original_error=e
                        )
                    else:
                        last_error = TranslationError(
                            f"HTTP error during translation: {e.response.status_code}",
                            original_error=e
                        )
                else:
                    last_error = TranslationError(
                        "HTTP error during translation",
                        original_error=e
                    )
                self.logger.warning(f"HTTP error on attempt {attempt + 1}: {last_error}")
            
            except Exception as e:
                last_error = TranslationError(
                    f"Unexpected error during translation: {str(e)}",
                    original_error=e
                )
                self.logger.warning(f"Unexpected error on attempt {attempt + 1}: {last_error}")
        
        # All retries failed
        self.stats['errors_encountered'] += 1
        self.logger.error(f"Translation failed after {self.max_retries + 1} attempts")
        raise last_error
    
    @log_performance
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text with advanced error handling and optimization
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
        
        Returns:
            Translated text
        
        Raises:
            TranslationError: If translation fails
            ValidationError: If input is invalid
        """
        start_time = time.time()
        
        try:
            # Validate input
            if not text or not text.strip():
                raise ValidationError("Text to translate is empty")
            
            # Validate language pair
            source_validated, target_validated = self.language_manager.validate_language_pair(
                source_lang, target_lang
            )
            
            # Check if translation is needed
            if not self._is_translatable_text(text):
                self.logger.debug(f"Skipping translation for non-translatable text: {text[:50]}...")
                return text
            
            self.logger.debug(f"Translating text: {source_validated} -> {target_validated}")
            
            # Split into chunks if necessary
            chunks = self._chunk_text(text)
            translated_chunks = []
            
            if self.parallel_processing and len(chunks) > 1:
                # Parallel processing for multiple chunks
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    future_to_chunk = {
                        executor.submit(
                            self._translate_chunk_with_retry, 
                            chunk, source_validated, target_validated
                        ): i for i, chunk in enumerate(chunks)
                    }
                    
                    # Collect results in order
                    results = [None] * len(chunks)
                    for future in as_completed(future_to_chunk):
                        chunk_index = future_to_chunk[future]
                        try:
                            results[chunk_index] = future.result()
                        except Exception as e:
                            self.logger.error(f"Error in parallel translation of chunk {chunk_index}: {e}")
                            raise
                    
                    translated_chunks = results
            else:
                # Sequential processing
                for chunk in chunks:
                    translated_chunk = self._translate_chunk_with_retry(
                        chunk, source_validated, target_validated
                    )
                    translated_chunks.append(translated_chunk)
            
            # Combine translated chunks
            translated_text = " ".join(translated_chunks)
            
            execution_time = time.time() - start_time
            self.stats['total_time'] += execution_time
            
            self.logger.debug(f"Translation completed in {execution_time:.2f}s")
            return translated_text
            
        except (TranslationError, NetworkError, RateLimitError, AuthenticationError, ValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Handle unexpected errors
            error_msg = f"Unexpected error during translation: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise TranslationError(
                error_msg,
                language_pair=(source_lang, target_lang),
                text_sample=text[:100] if text else None,
                original_error=e
            )
    
    def translate_text_list(self, texts: List[str], source_lang: str, target_lang: str) -> List[str]:
        """
        Translate a list of texts efficiently
        
        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code
        
        Returns:
            List of translated texts
        """
        self.logger.info(f"Starting batch translation of {len(texts)} texts")
        
        translated_texts = []
        for i, text in enumerate(texts):
            try:
                translated = self.translate_text(text, source_lang, target_lang)
                translated_texts.append(translated)
                
                if (i + 1) % 10 == 0:  # Log progress every 10 translations
                    self.logger.info(f"Progress: {i + 1}/{len(texts)} texts translated")
                    
            except Exception as e:
                self.logger.error(f"Error translating text {i}: {e}")
                translated_texts.append(text)  # Keep original text on error
        
        self.logger.info(f"Batch translation completed: {len(translated_texts)} texts processed")
        return translated_texts
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of given text
        
        Args:
            text: Text to analyze
        
        Returns:
            Detected language code
        
        Raises:
            TranslationError: If language detection fails
        """
        try:
            if not text or not text.strip():
                raise ValidationError("Text for language detection is empty")
            
            result = self.translator.detect(text)
            if result and result.lang:
                detected_lang = result.lang
                self.logger.debug(f"Detected language: {detected_lang} (confidence: {result.confidence})")
                return detected_lang
            else:
                raise TranslationError("Language detection returned no result")
                
        except Exception as e:
            error_msg = f"Language detection failed: {str(e)}"
            self.logger.error(error_msg)
            raise TranslationError(error_msg, original_error=e)
    
    def get_statistics(self) -> Dict:
        """Get translation statistics"""
        stats = self.stats.copy()
        if stats['translations_performed'] > 0:
            stats['average_chars_per_translation'] = (
                stats['characters_translated'] / stats['translations_performed']
            )
            stats['average_time_per_translation'] = (
                stats['total_time'] / stats['translations_performed']
            )
        return stats
    
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
    
    def test_connection(self) -> bool:
        """
        Test connection to translation service
        
        Returns:
            True if connection is working
        """
        try:
            test_result = self.translate_text("Hello", "en", "fr")
            return test_result is not None
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False