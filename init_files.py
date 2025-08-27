# src/__init__.py
"""
PPTrans - PowerPoint Translation Tool
A cross-platform desktop application for translating PowerPoint presentations
while preserving all formatting, fonts, images, and layout.
"""

__version__ = "1.0.0"
__author__ = "PPTrans Team"
__email__ = "contact@pptrans.com"

---

# src/gui/__init__.py
"""
GUI components for PPTrans application
"""

---

# src/core/__init__.py
"""
Core functionality for PPTrans application
"""

---

# src/utils/__init__.py
"""
Utility modules for PPTrans application
"""

---

# tests/__init__.py
"""
Test suite for PPTrans application
"""

---

# tests/test_translator.py
"""
Tests for the translation engine
"""

import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.translator import PPTransTranslator
from core.language_manager import LanguageManager
from utils.exceptions import TranslationError, ValidationError


class TestPPTransTranslator(unittest.TestCase):
    """Test cases for PPTransTranslator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'chunk_size': 1000,
            'max_retries': 2,
            'retry_delay': 0.1,
            'timeout': 5
        }
        self.translator = PPTransTranslator(self.config)
    
    def test_init(self):
        """Test translator initialization"""
        self.assertEqual(self.translator.chunk_size, 1000)
        self.assertEqual(self.translator.max_retries, 2)
        self.assertEqual(self.translator.retry_delay, 0.1)
        self.assertEqual(self.translator.timeout, 5)
    
    def test_is_translatable_text(self):
        """Test text translatability detection"""
        # Should translate
        self.assertTrue(self.translator._is_translatable_text("Hello world"))
        self.assertTrue(self.translator._is_translatable_text("This is a sentence."))
        
        # Should not translate
        self.assertFalse(self.translator._is_translatable_text(""))
        self.assertFalse(self.translator._is_translatable_text("   "))
        self.assertFalse(self.translator._is_translatable_text("123"))
        self.assertFalse(self.translator._is_translatable_text(".,;!?"))
        self.assertFalse(self.translator._is_translatable_text("https://example.com"))
        self.assertFalse(self.translator._is_translatable_text("test@example.com"))
    
    def test_chunk_text(self):
        """Test text chunking"""
        short_text = "Short text"
        chunks = self.translator._chunk_text(short_text)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], short_text)
        
        # Test with long text
        long_text = "This is a sentence. " * 100
        self.translator.chunk_size = 100
        chunks = self.translator._chunk_text(long_text)
        self.assertGreater(len(chunks), 1)
    
    @patch('core.translator.Translator')
    def test_translate_text_validation(self, mock_translator_class):
        """Test input validation for translate_text"""
        mock_translator = Mock()
        mock_translator_class.return_value = mock_translator
        
        translator = PPTransTranslator(self.config)
        
        # Test empty text
        with self.assertRaises(ValidationError):
            translator.translate_text("", "en", "fr")
        
        # Test invalid language codes  
        with self.assertRaises(Exception):  # Should raise LanguageNotSupportedError
            translator.translate_text("Hello", "invalid", "fr")
    
    def test_get_statistics(self):
        """Test statistics retrieval"""
        stats = self.translator.get_statistics()
        
        expected_keys = [
            'translations_performed',
            'characters_translated', 
            'errors_encountered',
            'retries_performed',
            'total_time'
        ]
        
        for key in expected_keys:
            self.assertIn(key, stats)
            self.assertIsInstance(stats[key], (int, float))
    
    def test_reset_statistics(self):
        """Test statistics reset"""
        # Modify some stats
        self.translator.stats['translations_performed'] = 5
        self.translator.stats['characters_translated'] = 100
        
        # Reset
        self.translator.reset_statistics()
        
        # Check reset
        self.assertEqual(self.translator.stats['translations_performed'], 0)
        self.assertEqual(self.translator.stats['characters_translated'], 0)


class TestLanguageManager(unittest.TestCase):
    """Test cases for LanguageManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.language_manager = LanguageManager()
    
    def test_supported_languages(self):
        """Test supported languages retrieval"""
        languages = self.language_manager.get_supported_languages()
        
        # Check common languages are present
        self.assertIn('en', languages)
        self.assertIn('es', languages)
        self.assertIn('fr', languages)
        self.assertIn('de', languages)
        self.assertIn('auto', languages)
        
        # Check language names
        self.assertEqual(languages['en'], 'English')
        self.assertEqual(languages['auto'], 'Auto-detect')
    
    def test_language_validation(self):
        """Test language code validation"""
        # Valid languages
        self.assertEqual(self.language_manager.validate_language_code('en'), 'en')
        self.assertEqual(self.language_manager.validate_language_code('EN'), 'en')
        self.assertEqual(self.language_manager.validate_language_code('  fr  '), 'fr')
        
        # Invalid languages
        with self.assertRaises(Exception):  # Should raise LanguageNotSupportedError
            self.language_manager.validate_language_code('invalid')
    
    def test_language_pair_validation(self):
        """Test language pair validation"""
        # Valid pairs
        source, target = self.language_manager.validate_language_pair('en', 'fr')
        self.assertEqual(source, 'en')
        self.assertEqual(target, 'fr')
        
        # Auto-detect as source
        source, target = self.language_manager.validate_language_pair('auto', 'fr')
        self.assertEqual(source, 'auto')
        self.assertEqual(target, 'fr')
        
        # Invalid: auto as target
        with self.assertRaises(Exception):  # Should raise ValidationError
            self.language_manager.validate_language_pair('en', 'auto')
        
        # Invalid: same languages
        with self.assertRaises(Exception):  # Should raise ValidationError
            self.language_manager.validate_language_pair('en', 'en')
    
    def test_language_search(self):
        """Test language search functionality"""
        # Search by name
        results = self.language_manager.search_languages('English')
        self.assertTrue(any(code == 'en' for code, name in results))
        
        # Search by code
        results = self.language_manager.search_languages('fr')
        self.assertTrue(any(code == 'fr' for code, name in results))
        
        # Partial search
        results = self.language_manager.search_languages('span')
        self.assertTrue(any('Spanish' in name for code, name in results))
    
    def test_popular_languages(self):
        """Test popular languages list"""
        popular = self.language_manager.get_popular_languages()
        
        # Should be a list of tuples
        self.assertIsInstance(popular, list)
        self.assertTrue(all(isinstance(item, tuple) and len(item) == 2 
                          for item in popular))
        
        # Should include common languages
        codes = [code for code, name in popular]
        self.assertIn('en', codes)
        self.assertIn('es', codes)
        self.assertIn('fr', codes)


if __name__ == '__main__':
    unittest.main()

---

# tests/test_pptx_processor.py
"""
Tests for the PowerPoint processor
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.pptx_processor import PPTXProcessor, TextElement
from utils.exceptions import PPTXProcessingError, SlideRangeError


class TestPPTXProcessor(unittest.TestCase):
    """Test cases for PPTXProcessor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = PPTXProcessor()
        
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_parse_slide_range(self):
        """Test slide range parsing"""
        # Test "all"
        result = self.processor._parse_slide_range("all", 10)
        self.assertEqual(result, list(range(1, 11)))
        
        # Test single slide
        result = self.processor._parse_slide_range("5", 10)
        self.assertEqual(result, [5])
        
        # Test range
        result = self.processor._parse_slide_range("2-5", 10)
        self.assertEqual(result, [2, 3, 4, 5])
        
        # Test comma-separated
        result = self.processor._parse_slide_range("1,3,5", 10)
        self.assertEqual(result, [1, 3, 5])
        
        # Test mixed
        result = self.processor._parse_slide_range("1,3-5,8", 10)
        self.assertEqual(result, [1, 3, 4, 5, 8])
        
        # Test invalid ranges
        with self.assertRaises(SlideRangeError):
            self.processor._parse_slide_range("0-5", 10)
        
        with self.assertRaises(SlideRangeError):
            self.processor._parse_slide_range("5-15", 10)
        
        with self.assertRaises(SlideRangeError):
            self.processor._parse_slide_range("invalid", 10)
    
    def test_text_element_creation(self):
        """Test TextElement creation"""
        element = TextElement(
            text="Hello World",
            slide_number=1,
            shape_index=0,
            paragraph_index=0,
            font_name="Arial",
            font_size=12,
            font_bold=True
        )
        
        self.assertEqual(element.text, "Hello World")
        self.assertEqual(element.original_text, "Hello World")
        self.assertEqual(element.slide_number, 1)
        self.assertEqual(element.font_name, "Arial")
        self.assertEqual(element.font_size, 12)
        self.assertTrue(element.font_bold)
        self.assertFalse(element.translated)
        
        # Test translation
        element.text = "Hola Mundo"
        element.translated = True
        self.assertEqual(element.text, "Hola Mundo")
        self.assertEqual(element.original_text, "Hello World")
        self.assertTrue(element.translated)
    
    def test_load_nonexistent_file(self):
        """Test loading a nonexistent file"""
        nonexistent_file = os.path.join(self.test_dir, "nonexistent.pptx")
        
        with self.assertRaises(Exception):  # Should raise FileOperationError
            self.processor.load_presentation(nonexistent_file)
    
    def test_invalid_file_extension(self):
        """Test loading file with invalid extension"""
        invalid_file = os.path.join(self.test_dir, "test.txt")
        
        # Create the file
        with open(invalid_file, 'w') as f:
            f.write("test")
        
        with self.assertRaises(Exception):  # Should raise ValidationError
            self.processor.load_presentation(invalid_file)
    
    def test_get_processing_stats(self):
        """Test processing statistics"""
        stats = self.processor.get_processing_stats()
        
        expected_keys = [
            'total_slides',
            'processed_slides',
            'total_text_elements',
            'translated_elements',
            'skipped_elements',
            'errors'
        ]
        
        for key in expected_keys:
            self.assertIn(key, stats)
            self.assertIsInstance(stats[key], int)


if __name__ == '__main__':
    unittest.main()

---

# scripts/install_dev.sh
#!/bin/bash

# Development setup script for PPTrans
# This script sets up the development environment

set -e  # Exit on error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🛠️  PPTrans Development Setup"
echo "============================"
echo "Project root: $PROJECT_ROOT"
echo ""

cd "$PROJECT_ROOT"

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed or not in PATH"
    echo "Please install Miniconda or Anaconda first"
    exit 1
fi

echo "✅ Conda found: $(conda --version)"

# Create conda environment
echo "🔧 Creating conda environment from environment.yml..."
if conda env list | grep -q "pptrans"; then
    echo "⚠️  Environment 'pptrans' already exists"
    read -p "Do you want to remove it and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        conda env remove -n pptrans -y
    else
        echo "Using existing environment"
        conda activate pptrans
        pip install -r requirements.txt
        echo "✅ Dependencies updated"
        exit 0
    fi
fi

conda env create -f environment.yml

echo "✅ Conda environment created successfully"

# Activate environment and install additional dev dependencies
echo "🔧 Installing additional development dependencies..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate pptrans

# Install development dependencies
pip install -e ".[dev]"

echo "✅ Development dependencies installed"

# Create necessary directories
echo "🗂️  Creating project directories..."
mkdir -p logs
mkdir -p assets
mkdir -p docs

# Create sample icon if it doesn't exist
if [ ! -f "assets/icon.png" ]; then
    echo "🎨 Creating sample icon..."
    # Create a simple colored square as placeholder icon
    python -c "
try:
    from PIL import Image, ImageDraw
    import os
    
    # Create a simple icon
    size = (64, 64)
    image = Image.new('RGBA', size, (70, 130, 180, 255))  # Steel blue
    draw = ImageDraw.Draw(image)
    
    # Draw a simple 'T' for Translation
    draw.rectangle([20, 10, 44, 20], fill='white')  # Top bar
    draw.rectangle([28, 10, 36, 50], fill='white')  # Vertical bar
    
    # Save as PNG and ICO
    image.save('assets/icon.png')
    image.save('assets/icon.ico')
    print('Sample icons created')
except ImportError:
    print('PIL not available, skipping icon creation')
    # Create empty files as placeholders
    open('assets/icon.png', 'a').close()
    open('assets/icon.ico', 'a').close()
"
fi

# Run tests to verify setup
echo "🧪 Running tests to verify setup..."
python -m pytest tests/ -v || {
    echo "⚠️  Some tests failed, but setup is complete"
    echo "This is normal if you don't have test PowerPoint files"
}

# Setup git hooks if .git directory exists
if [ -d ".git" ]; then
    echo "🔧 Setting up git hooks..."
    mkdir -p .git/hooks
    
    # Create pre-commit hook for code formatting
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Run black code formatter before commit
black --check src/ tests/ || {
    echo "Code formatting issues found. Run 'black src/ tests/' to fix."
    exit 1
}
EOF
    chmod +x .git/hooks/pre-commit
    echo "✅ Git hooks installed"
fi

echo ""
echo "🎉 Development setup completed successfully!"
echo ""
echo "To get started:"
echo "1. Activate the environment: conda activate pptrans"
echo "2. Run the application: python src/main.py"
echo "3. Run tests: python -m pytest tests/"
echo "4. Build executable: bash scripts/build.sh"
echo ""
echo "Development tools available:"
echo "- Code formatting: black src/ tests/"
echo "- Linting: flake8 src/ tests/"
echo "- Type checking: mypy src/"
echo "- Testing: pytest tests/ -v --cov"