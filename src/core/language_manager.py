"""
Language management for PPTrans
Handles language codes, names, and validation
"""

from typing import Dict, List, Optional, Tuple
from utils.logger import LoggerMixin
from utils.exceptions import LanguageNotSupportedError

class LanguageManager(LoggerMixin):
    """Manages supported languages and language operations"""
    
    # Google Translate supported languages (ISO 639-1 codes)
    SUPPORTED_LANGUAGES = {
        'auto': 'Auto-detect',
        'af': 'Afrikaans',
        'ak': 'Akan',
        'sq': 'Albanian',
        'am': 'Amharic',
        'ar': 'Arabic',
        'hy': 'Armenian',
        'as': 'Assamese',
        'ay': 'Aymara',
        'az': 'Azerbaijani',
        'bm': 'Bambara',
        'ba': 'Bashkir',
        'eu': 'Basque',
        'be': 'Belarusian',
        'bn': 'Bengali',
        'bho': 'Bhojpuri',
        'bs': 'Bosnian',
        'bg': 'Bulgarian',
        'ca': 'Catalan',
        'ceb': 'Cebuano',
        'ny': 'Chichewa',
        'zh-cn': 'Chinese (Simplified)',
        'zh-tw': 'Chinese (Traditional)',
        'co': 'Corsican',
        'hr': 'Croatian',
        'cs': 'Czech',
        'da': 'Danish',
        'dv': 'Dhivehi',
        'doi': 'Dogri',
        'nl': 'Dutch',
        'en': 'English',
        'eo': 'Esperanto',
        'et': 'Estonian',
        'ee': 'Ewe',
        'tl': 'Filipino',
        'fi': 'Finnish',
        'fr': 'French',
        'fy': 'Frisian',
        'gl': 'Galician',
        'ka': 'Georgian',
        'de': 'German',
        'el': 'Greek',
        'gn': 'Guarani',
        'gu': 'Gujarati',
        'ht': 'Haitian Creole',
        'ha': 'Hausa',
        'haw': 'Hawaiian',
        'iw': 'Hebrew',
        'hi': 'Hindi',
        'hmn': 'Hmong',
        'hu': 'Hungarian',
        'is': 'Icelandic',
        'ig': 'Igbo',
        'ilo': 'Ilocano',
        'id': 'Indonesian',
        'ga': 'Irish',
        'it': 'Italian',
        'ja': 'Japanese',
        'jw': 'Javanese',
        'kn': 'Kannada',
        'kk': 'Kazakh',
        'km': 'Khmer',
        'rw': 'Kinyarwanda',
        'gom': 'Konkani',
        'ko': 'Korean',
        'kri': 'Krio',
        'ku': 'Kurdish (Kurmanji)',
        'ckb': 'Kurdish (Sorani)',
        'ky': 'Kyrgyz',
        'lo': 'Lao',
        'la': 'Latin',
        'lv': 'Latvian',
        'ln': 'Lingala',
        'lt': 'Lithuanian',
        'lg': 'Luganda',
        'lb': 'Luxembourgish',
        'mk': 'Macedonian',
        'mai': 'Maithili',
        'mg': 'Malagasy',
        'ms': 'Malay',
        'ml': 'Malayalam',
        'mt': 'Maltese',
        'mi': 'Maori',
        'mr': 'Marathi',
        'mni-mtei': 'Meiteilon (Manipuri)',
        'lus': 'Mizo',
        'mn': 'Mongolian',
        'my': 'Myanmar (Burmese)',
        'ne': 'Nepali',
        'no': 'Norwegian',
        'or': 'Odia (Oriya)',
        'om': 'Oromo',
        'ps': 'Pashto',
        'fa': 'Persian',
        'pl': 'Polish',
        'pt': 'Portuguese',
        'pa': 'Punjabi',
        'qu': 'Quechua',
        'ro': 'Romanian',
        'ru': 'Russian',
        'sm': 'Samoan',
        'sa': 'Sanskrit',
        'gd': 'Scots Gaelic',
        'nso': 'Sepedi',
        'sr': 'Serbian',
        'st': 'Sesotho',
        'sn': 'Shona',
        'sd': 'Sindhi',
        'si': 'Sinhala',
        'sk': 'Slovak',
        'sl': 'Slovenian',
        'so': 'Somali',
        'es': 'Spanish',
        'su': 'Sundanese',
        'sw': 'Swahili',
        'sv': 'Swedish',
        'tg': 'Tajik',
        'ta': 'Tamil',
        'tt': 'Tatar',
        'te': 'Telugu',
        'th': 'Thai',
        'ti': 'Tigrinya',
        'ts': 'Tsonga',
        'tr': 'Turkish',
        'tk': 'Turkmen',
        'ak': 'Twi',
        'uk': 'Ukrainian',
        'ur': 'Urdu',
        'ug': 'Uyghur',
        'uz': 'Uzbek',
        'vi': 'Vietnamese',
        'cy': 'Welsh',
        'xh': 'Xhosa',
        'yi': 'Yiddish',
        'yo': 'Yoruba',
        'zu': 'Zulu'
    }
    
    # Popular languages for quick access
    POPULAR_LANGUAGES = [
        'auto', 'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 
        'zh-cn', 'zh-tw', 'ar', 'hi', 'tr', 'nl', 'sv', 'da', 'no', 'fi'
    ]
    
    def __init__(self):
        """Initialize language manager"""
        self.logger.info(f"Language manager initialized with {len(self.SUPPORTED_LANGUAGES)} languages")
    
    def get_supported_languages(self, include_auto_detect: bool = True) -> Dict[str, str]:
        """
        Get dictionary of supported languages
        
        Args:
            include_auto_detect: Whether to include auto-detect option
        
        Returns:
            Dictionary mapping language codes to language names
        """
        languages = self.SUPPORTED_LANGUAGES.copy()
        if not include_auto_detect and 'auto' in languages:
            del languages['auto']
        return languages
    
    def get_language_list(self, include_auto_detect: bool = True, popular_first: bool = False) -> List[Tuple[str, str]]:
        """
        Get list of supported languages as (code, name) tuples
        
        Args:
            include_auto_detect: Whether to include auto-detect option
            popular_first: Whether to sort popular languages first
        
        Returns:
            List of (language_code, language_name) tuples
        """
        languages = self.get_supported_languages(include_auto_detect)
        
        if popular_first:
            # Sort with popular languages first, then alphabetically
            popular = [(code, languages[code]) for code in self.POPULAR_LANGUAGES if code in languages]
            others = [(code, name) for code, name in sorted(languages.items()) 
                     if code not in self.POPULAR_LANGUAGES]
            return popular + others
        else:
            return sorted(languages.items(), key=lambda x: x[1])  # Sort by name
    
    def is_language_supported(self, language_code: str) -> bool:
        """
        Check if a language code is supported
        
        Args:
            language_code: Language code to check
        
        Returns:
            True if language is supported
        """
        return language_code.lower() in self.SUPPORTED_LANGUAGES
    
    def validate_language_code(self, language_code: str) -> str:
        """
        Validate and normalize language code
        
        Args:
            language_code: Language code to validate
        
        Returns:
            Normalized language code
        
        Raises:
            LanguageNotSupportedError: If language is not supported
        """
        normalized_code = language_code.lower().strip()
        
        if not self.is_language_supported(normalized_code):
            raise LanguageNotSupportedError(
                f"Language '{language_code}' is not supported",
                language_code=language_code
            )
        
        return normalized_code
    
    def get_language_name(self, language_code: str) -> str:
        """
        Get language name from code
        
        Args:
            language_code: Language code
        
        Returns:
            Language name
        
        Raises:
            LanguageNotSupportedError: If language is not supported
        """
        normalized_code = self.validate_language_code(language_code)
        return self.SUPPORTED_LANGUAGES[normalized_code]
    
    def get_language_code(self, language_name: str) -> Optional[str]:
        """
        Get language code from name (case-insensitive)
        
        Args:
            language_name: Language name
        
        Returns:
            Language code or None if not found
        """
        name_lower = language_name.lower().strip()
        
        for code, name in self.SUPPORTED_LANGUAGES.items():
            if name.lower() == name_lower:
                return code
        
        return None
    
    def validate_language_pair(self, source_lang: str, target_lang: str) -> Tuple[str, str]:
        """
        Validate a language pair for translation
        
        Args:
            source_lang: Source language code
            target_lang: Target language code
        
        Returns:
            Tuple of (validated_source_code, validated_target_code)
        
        Raises:
            LanguageNotSupportedError: If either language is not supported
            ValidationError: If language pair is invalid
        """
        # Validate individual languages
        source_validated = self.validate_language_code(source_lang)
        target_validated = self.validate_language_code(target_lang)
        
        # Check if target is auto-detect (not allowed for target)
        if target_validated == 'auto':
            from utils.exceptions import ValidationError
            raise ValidationError(
                "Auto-detect cannot be used as target language",
                field_name="target_language",
                field_value=target_lang
            )
        
        # Check if source and target are the same (except auto-detect)
        if source_validated == target_validated and source_validated != 'auto':
            from utils.exceptions import ValidationError
            raise ValidationError(
                f"Source and target languages cannot be the same: {source_validated}",
                field_name="language_pair"
            )
        
        self.logger.debug(f"Validated language pair: {source_validated} -> {target_validated}")
        return source_validated, target_validated
    
    def get_popular_languages(self) -> List[Tuple[str, str]]:
        """
        Get list of popular languages
        
        Returns:
            List of (language_code, language_name) tuples for popular languages
        """
        return [(code, self.SUPPORTED_LANGUAGES[code]) 
                for code in self.POPULAR_LANGUAGES 
                if code in self.SUPPORTED_LANGUAGES]
    
    def search_languages(self, query: str) -> List[Tuple[str, str]]:
        """
        Search languages by name or code
        
        Args:
            query: Search query
        
        Returns:
            List of matching (language_code, language_name) tuples
        """
        query_lower = query.lower().strip()
        matches = []
        
        for code, name in self.SUPPORTED_LANGUAGES.items():
            if (query_lower in code.lower() or 
                query_lower in name.lower()):
                matches.append((code, name))
        
        # Sort by relevance (exact matches first, then name matches, then code matches)
        def sort_key(item):
            code, name = item
            if code.lower() == query_lower or name.lower() == query_lower:
                return (0, name.lower())  # Exact match
            elif name.lower().startswith(query_lower):
                return (1, name.lower())  # Name starts with query
            elif query_lower in name.lower():
                return (2, name.lower())  # Name contains query
            else:
                return (3, name.lower())  # Code contains query
        
        matches.sort(key=sort_key)
        return matches