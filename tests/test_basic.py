"""
Basic tests for PPTrans application
"""

import unittest
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

class TestBasic(unittest.TestCase):
    """Basic test cases"""

    def test_imports(self):
        """Test that basic imports work"""
        # This will work once the source files are added
        try:
            # These will fail until source files are added
            # from core.language_manager import LanguageManager
            # from utils.config import Config
            pass
        except ImportError:
            self.skipTest("Source files not yet added")

    def test_project_structure(self):
        """Test project structure exists"""
        project_root = Path(__file__).parent.parent

        # Check key directories exist
        self.assertTrue((project_root / "src").exists())
        self.assertTrue((project_root / "src/gui").exists())
        self.assertTrue((project_root / "src/core").exists())
        self.assertTrue((project_root / "src/utils").exists())

        # Check key files exist
        self.assertTrue((project_root / "README.md").exists())
        self.assertTrue((project_root / "environment.yml").exists())
        self.assertTrue((project_root / "requirements.txt").exists())

if __name__ == '__main__':
    unittest.main()