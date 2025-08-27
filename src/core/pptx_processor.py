"""
PowerPoint PPTX Processor Module
Handles loading, processing, and saving PowerPoint presentations
"""

import os
import sys
import shutil
import requests
from typing import Dict, List, Optional, Any
from pptx import Presentation

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from utils.logger import get_logger
    from utils.exceptions import PPTransError
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback logging
    import logging
    get_logger = lambda name: logging.getLogger(name)
    
    # Fallback exception
    class PPTransError(Exception):
        """Custom exception for PPTrans errors."""
        pass


class PPTXProcessor:
    """
    Handles PowerPoint presentation processing, text extraction, and modification.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize PPTX processor.
        
        Args:
            config (dict, optional): Configuration dictionary
        """
        self.config = config or {}
        self.logger = get_logger(__name__)
        self.presentation = None
        self.file_path = None
        self._current_text_elements = {}
        self._translations = {}
        self._stats = {'translated_elements': 0, 'processed_slides': 0}
        
        self.logger.info(f"PPTX Processor initialized with config: {self.config}")
    
    def load_presentation(self, file_path: str) -> bool:
        """
        Load PowerPoint presentation from file.
        
        Args:
            file_path (str): Path to the PPTX file
            
        Returns:
            bool: True if loaded successfully, False otherwise
            
        Raises:
            PPTransError: If file cannot be loaded
        """
        try:
            if not os.path.exists(file_path):
                raise PPTransError(f"File not found: {file_path}")
            
            if not file_path.lower().endswith('.pptx'):
                raise PPTransError(f"Invalid file type. Expected .pptx, got: {file_path}")
            
            # Create backup if configured
            if self.config.get('backup_original', True):
                backup_path = f"{file_path}.backup"
                shutil.copy2(file_path, backup_path)
                self.logger.info(f"Created backup: {backup_path}")
            
            # Load presentation
            self.presentation = Presentation(file_path)
            self.file_path = file_path
            
            slide_count = len(self.presentation.slides)
            self.logger.info(f"Presentation loaded successfully: {slide_count} slides")
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to load presentation: {str(e)}"
            self.logger.error(error_msg)
            raise PPTransError(error_msg) from e
    
    def parse_slide_range(self, slide_range_str: str, total_slides: int) -> List[int]:
        """
        Parse slide range string and return list of slide indices (0-based).
        BULLETPROOF VERSION - handles the '-' error and all edge cases
        
        Args:
            slide_range_str (str): Slide range like "1-5", "all", "3,7,9", etc.
            total_slides (int): Total number of slides in presentation
            
        Returns:
            list: List of 0-based slide indices (integers)
        """
        self.logger.debug(f"parse_slide_range called with: '{slide_range_str}' (type: {type(slide_range_str)}), total_slides: {total_slides}")
        
        # Handle None, empty, or "all"
        if not slide_range_str or str(slide_range_str).strip().lower() == "all":
            result = list(range(total_slides))
            self.logger.debug(f"Using all slides: {[i+1 for i in result]}")
            return result
        
        # Convert to string and clean
        slide_range_str = str(slide_range_str).strip()
        
        # Handle the specific cases that cause "invalid literal for int() with base 10: '-'"
        problematic_inputs = ["-", "--", ",-", "-,", ",", " ", ""]
        if slide_range_str in problematic_inputs:
            self.logger.warning(f"Invalid slide range '{slide_range_str}', defaulting to all slides")
            return list(range(total_slides))
        
        slide_indices = []
        
        try:
            # Handle comma-separated ranges/numbers
            parts = []
            raw_parts = slide_range_str.split(',')
            self.logger.debug(f"Raw parts after comma split: {raw_parts}")
            
            for part in raw_parts:
                clean_part = part.strip()
                if clean_part and clean_part not in ["-", ""]:  # Filter out problematic parts
                    parts.append(clean_part)
            
            self.logger.debug(f"Clean parts: {parts}")
            
            if not parts:
                self.logger.warning("No valid parts found after filtering, defaulting to all slides")
                return list(range(total_slides))
            
            for part in parts:
                self.logger.debug(f"Processing part: '{part}'")
                
                if '-' in part:
                    # Handle range like "1-5"
                    # But first check if it's just a standalone dash
                    if part == "-":
                        self.logger.warning("Skipping standalone dash")
                        continue
                        
                    dash_parts = part.split('-')
                    self.logger.debug(f"Dash split parts: {dash_parts}")
                    
                    # Filter out empty parts from dash split
                    range_parts = []
                    for dp in dash_parts:
                        clean_dp = dp.strip()
                        if clean_dp:  # Only add non-empty parts
                            range_parts.append(clean_dp)
                    
                    self.logger.debug(f"Clean range parts: {range_parts}")
                    
                    if len(range_parts) == 2:
                        try:
                            start_str, end_str = range_parts
                            self.logger.debug(f"Trying to convert: start_str='{start_str}', end_str='{end_str}'")
                            
                            start = int(start_str) - 1  # Convert to 0-based
                            end = int(end_str) - 1      # Convert to 0-based
                            
                            # Validate range
                            if 0 <= start <= end < total_slides:
                                range_indices = list(range(start, end + 1))
                                slide_indices.extend(range_indices)
                                self.logger.info(f"Added range {start+1}-{end+1}: slides {[i+1 for i in range_indices]}")
                            else:
                                self.logger.warning(f"Range {start+1}-{end+1} is invalid for {total_slides} slides, skipping")
                        except ValueError as ve:
                            self.logger.warning(f"Could not convert range parts '{start_str}'-'{end_str}' to integers: {ve}")
                    else:
                        self.logger.warning(f"Invalid range format '{part}' (expected 2 parts, got {len(range_parts)}), skipping")
                else:
                    # Handle single slide number
                    try:
                        self.logger.debug(f"Trying to convert single slide: '{part}'")
                        slide_num = int(part) - 1  # Convert to 0-based
                        if 0 <= slide_num < total_slides:
                            slide_indices.append(slide_num)
                            self.logger.info(f"Added single slide {slide_num + 1}")
                        else:
                            self.logger.warning(f"Slide {slide_num + 1} out of range (1-{total_slides}), skipping")
                    except ValueError as ve:
                        self.logger.warning(f"Could not convert '{part}' to integer: {ve}")
        
        except Exception as e:
            self.logger.error(f"Unexpected error parsing slide range: {e}")
            self.logger.warning("Defaulting to all slides due to parsing error")
            return list(range(total_slides))
        
        # If no valid indices found, default to all slides
        if not slide_indices:
            self.logger.warning("No valid slide numbers found, defaulting to all slides")
            return list(range(total_slides))
        
        # Remove duplicates and sort
        result = sorted(list(set(slide_indices)))
        self.logger.info(f"Final processed slides: {[i+1 for i in result]}")
        return result
    
    def extract_text_elements(self, slide_range_str: str = "all") -> Dict[int, List[Dict[str, Any]]]:
        """
        Extract text elements from specified slides and store for translation.
        
        Args:
            slide_range_str (str): Slide range specification
            
        Returns:
            dict: Text elements by slide index
        """
        try:
            if not self.presentation:
                raise PPTransError("No presentation loaded")
            
            total_slides = len(self.presentation.slides)
            self.logger.info(f"Total slides in presentation: {total_slides}")
            
            # Parse slide range - now bulletproof
            slide_indices = self.parse_slide_range(slide_range_str, total_slides)
            
            text_elements = {}
            
            for slide_idx in slide_indices:
                slide = self.presentation.slides[slide_idx]
                slide_texts = []
                
                # Extract text from shapes
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        slide_texts.append({
                            'text': shape.text,
                            'shape_id': getattr(shape, 'shape_id', None),
                            'type': 'shape',
                            'shape_ref': shape  # Keep reference for later
                        })
                    elif hasattr(shape, "text_frame"):
                        # Handle text frames with paragraphs
                        for paragraph in shape.text_frame.paragraphs:
                            para_text = "".join(run.text for run in paragraph.runs)
                            if para_text.strip():
                                slide_texts.append({
                                    'text': para_text,
                                    'shape_id': getattr(shape, 'shape_id', None),
                                    'paragraph_id': id(paragraph),
                                    'type': 'paragraph',
                                    'shape_ref': shape,  # Keep reference for later
                                    'paragraph_ref': paragraph  # Keep reference for later
                                })
                
                if slide_texts:
                    text_elements[slide_idx] = slide_texts
                    self.logger.info(f"Slide {slide_idx + 1}: Found {len(slide_texts)} text elements")
                else:
                    self.logger.warning(f"Slide {slide_idx + 1}: No text elements found")
            
            total_texts = sum(len(texts) for texts in text_elements.values())
            self.logger.info(f"Total text elements extracted: {total_texts}")
            
            # Store for later use by translate_text_elements
            self._current_text_elements = text_elements
            
            return text_elements
            
        except Exception as e:
            error_msg = f"Error extracting text elements: {str(e)}"
            self.logger.error(error_msg)
            raise PPTransError(error_msg) from e
    
    def translate_text_elements(self, progress_callback):
        """
        This method is called by GUI with a progress callback function.
        The callback function does the actual translation work.
        
        Args:
            progress_callback: Function that translates text and updates progress
        """
        try:
            self.logger.info("Starting translation with progress callback...")
            
            # Get text elements that were already extracted
            if not hasattr(self, '_current_text_elements') or not self._current_text_elements:
                # Extract text elements first
                self.logger.info("Extracting text elements...")
                self._current_text_elements = self.extract_text_elements("all")
            
            text_elements = self._current_text_elements
            self.logger.info(f"Processing {len(text_elements)} slides for translation")
            
            # Store translations
            self._translations = {}
            total_elements = 0
            
            for slide_idx, slide_texts in text_elements.items():
                slide_translations = []
                
                for j, text_element in enumerate(slide_texts):
                    original_text = text_element.get('text', '').strip()
                    
                    if original_text:
                        try:
                            # Call the progress callback - it handles translation AND progress
                            translated_text = progress_callback(original_text)
                            
                            slide_translations.append({
                                'original_text': original_text,
                                'translated_text': translated_text,
                                'text_element': text_element  # Keep reference
                            })
                            
                            total_elements += 1
                            self.logger.info(f"Slide {slide_idx+1}, Text {j+1}: '{original_text[:40]}...' -> '{translated_text[:40]}...'")
                            
                        except Exception as e:
                            self.logger.warning(f"Translation failed for '{original_text[:30]}...': {e}")
                            # Keep original text as fallback
                            slide_translations.append({
                                'original_text': original_text,
                                'translated_text': original_text,
                                'text_element': text_element
                            })
                    else:
                        # Empty text
                        slide_translations.append({
                            'original_text': original_text,
                            'translated_text': original_text,
                            'text_element': text_element
                        })
                
                self._translations[slide_idx] = slide_translations
                self.logger.info(f"Slide {slide_idx + 1}: Processed {len(slide_translations)} text elements")
            
            # Update stats
            self._stats['translated_elements'] = total_elements
            self._stats['processed_slides'] = len(self._translations)
            
            self.logger.info(f"Translation complete: {total_elements} elements in {len(self._translations)} slides")
            
        except Exception as e:
            error_msg = f"Error in translate_text_elements: {str(e)}"
            self.logger.error(error_msg)
            raise PPTransError(error_msg) from e
    
    def apply_translations(self):
        """
        Apply the stored translations back to the presentation.
        Called by GUI after translate_text_elements completes.
        """
        try:
            if not hasattr(self, '_translations') or not self._translations:
                raise PPTransError("No translations available. Run translate_text_elements first.")
            
            self.logger.info(f"Applying translations to {len(self._translations)} slides...")
            
            applied_count = 0
            for slide_idx, slide_translations in self._translations.items():
                if slide_idx >= len(self.presentation.slides):
                    continue
                    
                slide = self.presentation.slides[slide_idx]
                
                for translation in slide_translations:
                    translated_text = translation.get('translated_text', '')
                    text_element = translation.get('text_element', {})
                    
                    if translated_text and text_element:
                        try:
                            # Apply translation based on element type
                            if text_element.get('type') == 'shape' and 'shape_ref' in text_element:
                                shape = text_element['shape_ref']
                                if hasattr(shape, 'text'):
                                    shape.text = translated_text
                                    applied_count += 1
                                    self.logger.debug(f"Applied to shape in slide {slide_idx+1}")
                                    
                            elif text_element.get('type') == 'paragraph' and 'paragraph_ref' in text_element:
                                paragraph = text_element['paragraph_ref']
                                if paragraph and hasattr(paragraph, 'clear'):
                                    paragraph.clear()
                                    if paragraph.runs:
                                        paragraph.runs[0].text = translated_text
                                    else:
                                        run = paragraph.runs.add()
                                        run.text = translated_text
                                    applied_count += 1
                                    self.logger.debug(f"Applied to paragraph in slide {slide_idx+1}")
                        except Exception as e:
                            self.logger.warning(f"Failed to apply translation to slide {slide_idx+1}: {e}")
                            continue
            
            self.logger.info(f"Successfully applied {applied_count} translations to presentation")
            return True
            
        except Exception as e:
            error_msg = f"Error applying translations: {str(e)}"
            self.logger.error(error_msg)
            raise PPTransError(error_msg) from e
    
    def save_presentation(self, output_path: Optional[str] = None) -> str:
        """Save the presentation to file."""
        try:
            if not self.presentation:
                raise PPTransError("No presentation loaded")
            
            if not output_path:
                base, ext = os.path.splitext(self.file_path)
                output_path = f"{base}_translated{ext}"
            
            # Ensure directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            self.presentation.save(output_path)
            self.logger.info(f"Presentation saved: {output_path}")
            return output_path
            
        except Exception as e:
            error_msg = f"Error saving presentation: {str(e)}"
            self.logger.error(error_msg)
            raise PPTransError(error_msg) from e
    
    def get_presentation_info(self) -> Dict[str, Any]:
        """Get basic information about the loaded presentation."""
        if not self.presentation:
            return {"error": "No presentation loaded"}
        
        try:
            total_slides = len(self.presentation.slides)
            slide_info = []
            
            for i, slide in enumerate(self.presentation.slides):
                text_count = 0
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        text_count += 1
                    elif hasattr(shape, "text_frame"):
                        for paragraph in shape.text_frame.paragraphs:
                            if any(run.text.strip() for run in paragraph.runs):
                                text_count += 1
                
                slide_info.append({
                    'slide_number': i + 1,
                    'text_elements': text_count
                })
            
            return {
                'total_slides': total_slides,
                'slides': slide_info
            }
            
        except Exception as e:
            self.logger.error(f"Error getting presentation info: {str(e)}")
            return {"error": str(e)}
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get processing statistics.
        Called by GUI to show completion message.
        """
        return self._stats.copy()
    
    def close(self):
        """Clean up resources."""
        self.presentation = None
        self.file_path = None
        self._current_text_elements = {}
        self._translations = {}
        self.logger.info("PPTX Processor closed")