#!/usr/bin/env python3
"""
PPTrans - PowerPoint Translation Tool
Main application entry point
"""

import sys
import os
import traceback
from pathlib import Path

import logging
logging.getLogger().setLevel(logging.DEBUG)

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import setup_logger, get_logger
from utils.config import Config
from gui.main_window import PPTransMainWindow

def main():
    """Main application entry point"""
    try:
        # Setup logging
        setup_logger()
        logger = get_logger(__name__)
        
        logger.info("=" * 60)
        logger.info("PPTrans Application Starting")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Platform: {sys.platform}")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info("=" * 60)
        
        # Load configuration
        config = Config()
        logger.info(f"Configuration loaded: {config.get_all()}")
        
        # Create and run main window
        app = PPTransMainWindow()
        logger.info("Main window created successfully")
        
        # Start the application
        logger.info("Starting GUI event loop")
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Critical error in main application: {e}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        sys.exit(1)
    finally:
        logger.info("PPTrans Application Shutting Down")
        logger.info("=" * 60)

if __name__ == "__main__":
    main()
