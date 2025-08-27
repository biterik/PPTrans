"""
Custom exceptions for PPTrans application
"""

class PPTransError(Exception):
    """Base exception class for PPTrans"""
    
    def __init__(self, message: str, error_code: str = None, original_error: Exception = None):
        """
        Initialize PPTrans exception
        
        Args:
            message: Error message
            error_code: Optional error code for categorization
            original_error: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.original_error = original_error
    
    def __str__(self):
        error_str = self.message
        if self.error_code:
            error_str = f"[{self.error_code}] {error_str}"
        if self.original_error:
            error_str = f"{error_str} (caused by: {self.original_error})"
        return error_str

class TranslationError(PPTransError):
    """Exception raised during translation operations"""
    
    def __init__(self, message: str, language_pair: tuple = None, text_sample: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.language_pair = language_pair
        self.text_sample = text_sample

class PPTXProcessingError(PPTransError):
    """Exception raised during PowerPoint file processing"""
    
    def __init__(self, message: str, file_path: str = None, slide_number: int = None, **kwargs):
        super().__init__(message, **kwargs)
        self.file_path = file_path
        self.slide_number = slide_number

class APIError(PPTransError):
    """Exception raised for API-related errors"""
    
    def __init__(self, message: str, api_name: str = None, status_code: int = None, **kwargs):
        super().__init__(message, **kwargs)
        self.api_name = api_name
        self.status_code = status_code

class ConfigurationError(PPTransError):
    """Exception raised for configuration-related errors"""
    
    def __init__(self, message: str, config_key: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.config_key = config_key

class FileOperationError(PPTransError):
    """Exception raised for file operation errors"""
    
    def __init__(self, message: str, operation: str = None, file_path: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.operation = operation
        self.file_path = file_path

class LanguageNotSupportedError(PPTransError):
    """Exception raised when a language is not supported"""
    
    def __init__(self, message: str, language_code: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.language_code = language_code

class ValidationError(PPTransError):
    """Exception raised for validation errors"""
    
    def __init__(self, message: str, field_name: str = None, field_value = None, **kwargs):
        super().__init__(message, **kwargs)
        self.field_name = field_name
        self.field_value = field_value

class SlideRangeError(ValidationError):
    """Exception raised for invalid slide range specifications"""
    
    def __init__(self, message: str, range_spec: str = None, max_slides: int = None, **kwargs):
        super().__init__(message, **kwargs)
        self.range_spec = range_spec
        self.max_slides = max_slides

class NetworkError(APIError):
    """Exception raised for network-related errors"""
    
    def __init__(self, message: str, url: str = None, timeout: float = None, **kwargs):
        super().__init__(message, **kwargs)
        self.url = url
        self.timeout = timeout

class RateLimitError(APIError):
    """Exception raised when API rate limits are exceeded"""
    
    def __init__(self, message: str, retry_after: float = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after

class AuthenticationError(APIError):
    """Exception raised for authentication failures"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="AUTH_FAILED", **kwargs)

# Utility functions for exception handling

def handle_and_log_exception(logger, exception: Exception, context: str = "") -> PPTransError:
    """
    Handle and log an exception, converting it to a PPTransError if necessary
    
    Args:
        logger: Logger instance
        exception: The exception to handle
        context: Additional context information
    
    Returns:
        PPTransError instance
    """
    context_msg = f" in {context}" if context else ""
    
    if isinstance(exception, PPTransError):
        logger.error(f"PPTrans error{context_msg}: {exception}")
        return exception
    else:
        error_msg = f"Unexpected error{context_msg}: {exception}"
        logger.error(error_msg, exc_info=True)
        return PPTransError(error_msg, original_error=exception)

def create_user_friendly_message(exception: PPTransError) -> str:
    """
    Create a user-friendly error message from a PPTransError
    
    Args:
        exception: PPTransError instance
    
    Returns:
        User-friendly error message
    """
    if isinstance(exception, TranslationError):
        return f"Translation failed: {exception.message}"
    elif isinstance(exception, PPTXProcessingError):
        return f"PowerPoint processing error: {exception.message}"
    elif isinstance(exception, NetworkError):
        return "Network connection error. Please check your internet connection and try again."
    elif isinstance(exception, RateLimitError):
        return "Translation service temporarily unavailable due to high usage. Please try again later."
    elif isinstance(exception, AuthenticationError):
        return "Authentication failed. Please check your API credentials."
    elif isinstance(exception, FileOperationError):
        return f"File operation failed: {exception.message}"
    elif isinstance(exception, LanguageNotSupportedError):
        return f"Language not supported: {exception.language_code}"
    else:
        return f"An error occurred: {exception.message}"