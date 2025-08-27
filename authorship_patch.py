#!/usr/bin/env python3
"""
Update authorship information across all PPTrans files
Replace "PPTrans Team" with "Erik Bitzek"
"""

import os
import re
from pathlib import Path

def update_file_authorship(file_path: Path):
    """Update authorship in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace variations of PPTrans Team with Erik Bitzek
        replacements = [
            (r'PPTrans Team', 'Erik Bitzek'),
            (r'"PPTrans Team"', '"Erik Bitzek"'),
            (r'PPTransTeam', 'Erik Bitzek'),
            (r'contact@pptrans\.com', 'erik.bitzek@fau.de'),
            (r'__author__ = "PPTrans Team"', '__author__ = "Erik Bitzek"'),
            (r'author="PPTrans Team"', 'author="Erik Bitzek"'),
            (r'author_email="contact@pptrans\.com"', 'author_email="erik.bitzek@fau.de"'),
            (r'Copyright \(c\) 2025 PPTrans Team', 'Copyright (c) 2025 Erik Bitzek'),
        ]
        
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        if content != original_content:
            # Create backup
            backup_path = file_path.with_suffix(file_path.suffix + '.backup_auth')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Updated: {file_path}")
            return True
        else:
            print(f"📋 No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    """Update authorship in all relevant files"""
    print("🔧 Updating Authorship to Erik Bitzek")
    print("=" * 40)
    
    # Files to update
    files_to_update = [
        "README.md",
        "LICENSE",
        "setup.py",
        "src/__init__.py",
        "src/main.py",
        "src/gui/__init__.py",
        "src/core/__init__.py", 
        "src/utils/__init__.py",
        "src/utils/logger.py",
        "src/utils/config.py",
        "src/utils/exceptions.py",
        "src/core/language_manager.py",
        "src/core/translator.py",
        "src/core/pptx_processor.py",
        "src/gui/main_window.py",
        "src/gui/widgets.py",
        "src/gui/dialogs.py",
        "tests/__init__.py",
    ]
    
    updated_count = 0
    
    for file_path_str in files_to_update:
        file_path = Path(file_path_str)
        if file_path.exists():
            if update_file_authorship(file_path):
                updated_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print(f"\n📊 Updated {updated_count} files with new authorship")
    print("✅ Authorship update completed!")

if __name__ == "__main__":
    main()
