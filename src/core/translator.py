"""
Enhanced Translation Engine using Google Cloud Translation API (Paid Tier)
Preserves all existing content filtering, academic context, and post-processing
"""
import os
import time
import re
from typing import Optional, Dict, List, Tuple, Set
from pathlib import Path
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account

# Handle imports for both test context (from project root) and app context (from src/)
try:
    from src.utils.logger import LoggerMixin
    from src.utils.exceptions import TranslationError, NetworkError, RateLimitError
except ImportError:
    from utils.logger import LoggerMixin
    from utils.exceptions import TranslationError, NetworkError, RateLimitError


class PPTransTranslator(LoggerMixin):
    """Enhanced translation service using Google Cloud API with reliable batch processing"""
    
    def __init__(self, translation_settings: dict):
        """Initialize with translation settings from config"""
        self.settings = translation_settings
        
        # Initialize Google Cloud Translation client
        self.client = self._initialize_google_client()
        
        # Content filtering (preserved from your original)
        self.skip_patterns = self._compile_skip_patterns()
        self.context_terms = self._load_enhanced_context_terms()
        
        # Load external glossary for academic terms
        self.glossary_terms = self._load_glossary_from_file()
        
        # With paid API, we can safely enable batch processing again!
        self.use_batching = translation_settings.get('use_batching', True)
        self.batch_size = translation_settings.get('batch_size', 50)  # Can handle larger batches now
        
        # Rate limiting (much more generous with paid API)
        self.request_count = 0
        self.hour_start_time = time.time()
        
        self.logger.info("PPTransTranslator initialized with Google Cloud API (paid tier)")
        
    def _initialize_google_client(self):
        """Initialize Google Translate client with credentials from local directory."""
        try:
            credentials_path = None
            
            # Method 1: Try local credentials directory FIRST (for PPTrans project)
            project_root = Path(__file__).parent.parent.parent
            potential_paths = [
                project_root / "credentials" / "google-translate-key.json",
                project_root / "credentials" / "service-account-key.json", 
                project_root / "credentials" / "google-cloud-key.json",
            ]
            
            for path in potential_paths:
                if path.exists():
                    credentials_path = str(path.absolute())
                    self.logger.info(f"Using local credentials: {credentials_path}")
                    break
            
            if credentials_path:
                # Load credentials explicitly from local file
                credentials = service_account.Credentials.from_service_account_file(credentials_path)
                client = translate.Client(credentials=credentials)
            else:
                # Fallback: try environment variable (but warn about it)
                env_var = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
                if env_var:
                    self.logger.warning(f"No local credentials found, falling back to environment variable: {env_var}")
                    client = translate.Client()
                else:
                    raise FileNotFoundError("No credentials found")
            
            # Test the connection
            self._test_api_connection(client)
            
            self.logger.info("Google Cloud Translation API initialized successfully")
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Cloud Translation API: {e}")
            
            error_msg = (f"API initialization failed: {e}\n"
                       "Please ensure:\n"
                       "1. Place your PPTrans JSON key in credentials/google-translate-key.json\n"
                       "2. The service account has 'Cloud Translation API User' role\n"
                       "3. The Cloud Translation API is enabled in your Google Cloud project")
            
            raise TranslationError(error_msg)
    
    def _test_api_connection(self, client):
        """Test API connection with a simple translation."""
        try:
            result = client.translate("test", target_language="de")
            translated_text = result.get('translatedText', '').lower()
            
            # Check if we got a valid translation (should be "Test" or "testen" in German)
            if translated_text and translated_text != "test":
                self.logger.debug(f"API connection test successful: 'test' -> '{translated_text}'")
                return True
            else:
                raise ConnectionError("API test returned empty or unchanged result")
                
        except Exception as e:
            raise ConnectionError(f"Google Cloud Translation API connection failed: {e}")
        
    def _compile_skip_patterns(self) -> List[re.Pattern]:
        """Patterns for content that shouldn't be translated (preserved from original)"""
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
        """Enhanced context-specific terms with better German academic vocabulary (preserved from original)"""
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
        """Check if text should be skipped entirely (preserved from original)"""
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
    
    def _load_glossary_from_file(self) -> Dict[str, str]:
        """Load academic glossary from external file"""
        glossary = {}
        
        # Try to find glossary file
        project_root = Path(__file__).parent.parent.parent
        glossary_paths = [
            project_root / "academic_glossary.txt",
            project_root / "config" / "academic_glossary.txt",
            project_root / "resources" / "academic_glossary.txt",
        ]
        
        glossary_file = None
        for path in glossary_paths:
            if path.exists():
                glossary_file = path
                break
        
        if not glossary_file:
            self.logger.warning("No external glossary file found, using built-in terms")
            return self._get_fallback_glossary()
        
        try:
            with open(glossary_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse format: source_term = target_translation
                    if '=' in line:
                        source, target = line.split('=', 1)
                        source = source.strip().lower()  # Case-insensitive matching
                        target = target.strip()
                        
                        if source and target:
                            glossary[source] = target
                            
            self.logger.info(f"Loaded {len(glossary)} terms from glossary file: {glossary_file}")
            return glossary
            
        except Exception as e:
            self.logger.error(f"Error loading glossary file {glossary_file}: {e}")
            return self._get_fallback_glossary()
    
    def _get_fallback_glossary(self) -> Dict[str, str]:
        """Fallback glossary if external file not available"""
        return {
            'students': 'students',
            'student': 'student',
            'location': 'campus',
            'site': 'campus',
            'first semester day': 'First Semester Orientation Day',
            'university of applied sciences': 'University of Applied Sciences',
            'college': 'University of Applied Sciences',
        }
    
    def _apply_glossary_fixes(self, translated_text: str) -> str:
        """Apply academic term glossary fixes after Google translation"""
        if not translated_text:
            return translated_text
            
        fixed = translated_text
        
        # Apply glossary fixes loaded from external file
        for source_term, target_term in self.glossary_terms.items():
            if source_term in fixed.lower():
                # Use regex for case-insensitive replacement while preserving case context
                pattern = re.compile(re.escape(source_term), re.IGNORECASE)
                fixed = pattern.sub(target_term, fixed)
                self.logger.debug(f"Glossary fix: {source_term} -> {target_term}")
        
        return fixed
    
    def _postprocess_translation(self, original: str, translated: str) -> str:
        """Post-process translation to fix common issues (preserved from original)"""
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
    
    def _track_api_usage(self):
        """Track API usage (much more generous limits with paid API)"""
        current_time = time.time()
        
        # Reset hourly counter
        if current_time - self.hour_start_time > 3600:
            self.request_count = 0
            self.hour_start_time = current_time
        
        self.request_count += 1
        
        # Log usage but don't enforce strict limits (paid API is very generous)
        if self.request_count % 100 == 0:
            self.logger.info(f"API usage: {self.request_count} requests in current hour")
    
    def translate_text(self, text: str, source_lang: str = 'de', target_lang: str = 'en') -> str:
        """
        Single text translation - simplified for German->English PowerPoint slides
        """
        if not text or not text.strip():
            return text
        
        if self._should_skip_translation(text):
            return text
        
        try:
            self._track_api_usage()
            
            # Send directly to Google Translate with explicit German source
            result = self.client.translate(
                text,
                source_language=source_lang,
                target_language=target_lang
            )
            
            translated = result['translatedText']
            
            # Apply your post-processing fixes
            final_translation = self._postprocess_translation(text, translated)
            
            # Apply glossary substitutions after Google translation
            final_translation = self._apply_glossary_fixes(final_translation)
            
            if final_translation != text:
                self.logger.debug(f"Translated: '{text}' -> '{final_translation}'")
            
            return final_translation
            
        except Exception as e:
            self.logger.error(f"Translation failed for '{text[:30]}...': {e}")
            return text  # Return original on error
    
    def translate_text_batch(self, text_items: List[str], source_lang: str = 'de', target_lang: str = 'en') -> List[str]:
        """
        Translate multiple text items using reliable batch processing
        Now enabled again with paid Google Cloud API!
        """
        if not text_items:
            return []
        
        if not self.use_batching:
            # Fall back to individual translation if batching disabled
            self.logger.info("Batch processing disabled, using individual translation")
            return [self.translate_text(text, source_lang, target_lang) for text in text_items]
        
        self.logger.info(f"Batch translating {len(text_items)} items with Google Cloud API")
        
        # Separate items that need translation from those that should be skipped
        translatable_items = []
        skipped_indices = set()
        translated_items = [''] * len(text_items)
        
        for i, text in enumerate(text_items):
            if self._should_skip_translation(text):
                skipped_indices.add(i)
                translated_items[i] = text  # Keep original
                self.logger.debug(f"Skipped item {i+1}: '{text[:30]}...'")
            else:
                translatable_items.append((i, text))
        
        if not translatable_items:
            self.logger.info("No items to translate (all skipped)")
            return translated_items
        
        # Process in batches
        for batch_start in range(0, len(translatable_items), self.batch_size):
            batch_end = min(batch_start + self.batch_size, len(translatable_items))
            batch = translatable_items[batch_start:batch_end]
            
            try:
                self._track_api_usage()
                
                # Extract texts for batch translation
                batch_texts = [item[1] for item in batch]  # original text
                
                # Batch translate using Google Cloud API
                results = self.client.translate(
                    batch_texts,
                    source_language=source_lang,
                    target_language=target_lang
                )
                
                # Apply translations back to original positions
                for (original_index, original_text), result in zip(batch, results):
                    translated = result['translatedText']
                    
                    # Post-process and apply glossary fixes
                    final_translation = self._postprocess_translation(original_text, translated)
                    final_translation = self._apply_glossary_fixes(final_translation)
                    translated_items[original_index] = final_translation
                    
                    if final_translation != original_text:
                        self.logger.debug(f"Batch translated item {original_index+1}: '{original_text[:30]}...' -> '{final_translation[:30]}...'")
                
                self.logger.info(f"Batch {batch_start//self.batch_size + 1}: Processed {len(batch)} items")
                
            except Exception as e:
                self.logger.error(f"Batch translation failed for batch {batch_start//self.batch_size + 1}: {e}")
                # Fallback to individual translation for this batch
                for original_index, original_text in batch:
                    try:
                        individual_result = self.translate_text(original_text, source_lang, target_lang)
                        translated_items[original_index] = individual_result
                    except Exception as individual_error:
                        self.logger.error(f"Individual fallback failed for item {original_index+1}: {individual_error}")
                        translated_items[original_index] = original_text  # Keep original
        
        # Calculate success statistics
        successful_translations = sum(1 for i, item in enumerate(translated_items) 
                                    if i not in skipped_indices and item != text_items[i])
        
        self.logger.info(f"Batch translation completed: {successful_translations}/{len(text_items) - len(skipped_indices)} items translated, {len(skipped_indices)} skipped")
        
        return translated_items
    
    def test_connection(self) -> bool:
        """Test connection to Google Cloud Translation service"""
        try:
            test_result = self.translate_text("Studierende besuchen Vorlesungen", source_lang='de', target_lang='en')
            success = test_result.lower() != "studierende besuchen vorlesungen" and test_result.strip() != ""
            if success:
                self.logger.info(f"Connection test successful: 'Studierende besuchen Vorlesungen' -> '{test_result}'")
            else:
                self.logger.error(f"Connection test failed - got: '{test_result}'")
            return success
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def get_translation_stats(self) -> Dict[str, int]:
        """Get translation statistics"""
        current_time = time.time()
        time_in_current_hour = current_time - self.hour_start_time
        
        return {
            'requests_made': self.request_count,
            'time_in_current_hour': int(time_in_current_hour),
            'time_until_reset': max(0, int(3600 - time_in_current_hour)),
            'api_type': 'Google Cloud Translation API (Paid)',
            'batch_processing_enabled': self.use_batching,
            'batch_size': self.batch_size
        }
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages from Google Cloud API"""
        try:
            languages = self.client.get_languages()
            return [{'code': lang['language'], 'name': lang.get('name', lang['language'])} 
                   for lang in languages]
        except Exception as e:
            self.logger.error(f"Failed to get supported languages: {e}")
            return []