"""
Slide range parsing utility with robust validation
Add this to your pptx_processor.py or create as a separate utility
"""

import re
from typing import List, Tuple, Union

def parse_slide_range(range_str: str, max_slides: int) -> List[int]:
    """
    Parse slide range string and return list of slide indices (0-based)
    
    Supported formats:
    - Single slide: "5"
    - Range: "5-10" 
    - Multiple ranges: "1-3,5,7-9"
    - "all" for all slides
    
    Args:
        range_str: Range specification string
        max_slides: Maximum number of slides available
        
    Returns:
        List of 0-based slide indices
        
    Raises:
        ValueError: If range specification is invalid
    """
    if not range_str or not range_str.strip():
        raise ValueError("Empty slide range specification")
    
    range_str = range_str.strip().lower()
    
    # Handle "all" keyword
    if range_str == "all":
        return list(range(max_slides))
    
    # Clean up the input - remove any non-digit, non-dash, non-comma characters
    # This fixes issues like "16-18l" -> "16-18"
    cleaned = re.sub(r'[^0-9\-,\s]', '', range_str)
    cleaned = re.sub(r'\s+', '', cleaned)  # Remove whitespace
    
    if not cleaned:
        raise ValueError(f"Invalid slide range specification: '{range_str}' contains no valid numbers")
    
    slide_indices = set()
    
    try:
        # Split by commas for multiple ranges/single slides
        parts = [part.strip() for part in cleaned.split(',') if part.strip()]
        
        for part in parts:
            if '-' in part:
                # Handle range like "5-10"
                range_parts = part.split('-')
                if len(range_parts) != 2:
                    raise ValueError(f"Invalid range format: '{part}' (should be 'start-end')")
                
                start_str, end_str = range_parts
                if not start_str or not end_str:
                    raise ValueError(f"Invalid range format: '{part}' (missing start or end)")
                
                start = int(start_str)
                end = int(end_str)
                
                if start < 1 or end < 1:
                    raise ValueError(f"Slide numbers must be positive (got {start}-{end})")
                
                if start > end:
                    raise ValueError(f"Invalid range: start ({start}) > end ({end})")
                
                if start > max_slides or end > max_slides:
                    raise ValueError(f"Slide range {start}-{end} exceeds available slides (1-{max_slides})")
                
                # Add all slides in range (convert to 0-based indexing)
                slide_indices.update(range(start - 1, end))
                
            else:
                # Handle single slide
                slide_num = int(part)
                if slide_num < 1:
                    raise ValueError(f"Slide number must be positive (got {slide_num})")
                if slide_num > max_slides:
                    raise ValueError(f"Slide {slide_num} exceeds available slides (1-{max_slides})")
                
                # Convert to 0-based indexing
                slide_indices.add(slide_num - 1)
    
    except ValueError as e:
        # Re-raise ValueError with original input for context
        raise ValueError(f"Invalid slide range specification: {range_str}. Error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Invalid slide range specification: {range_str}. Error: {str(e)}")
    
    if not slide_indices:
        raise ValueError(f"No valid slides specified in range: {range_str}")
    
    # Return sorted list
    return sorted(list(slide_indices))

def validate_slide_range_input(range_str: str) -> Tuple[bool, str]:
    """
    Validate slide range input without knowing max_slides
    
    Args:
        range_str: Range specification string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not range_str or not range_str.strip():
        return False, "Please enter a slide range"
    
    range_str = range_str.strip().lower()
    
    if range_str == "all":
        return True, ""
    
    # Clean up the input
    cleaned = re.sub(r'[^0-9\-,\s]', '', range_str)
    cleaned = re.sub(r'\s+', '', cleaned)
    
    if not cleaned:
        return False, f"Invalid characters in range specification: '{range_str}'"
    
    try:
        parts = [part.strip() for part in cleaned.split(',') if part.strip()]
        
        for part in parts:
            if '-' in part:
                range_parts = part.split('-')
                if len(range_parts) != 2:
                    return False, f"Invalid range format: '{part}' (should be 'start-end')"
                
                start_str, end_str = range_parts
                if not start_str or not end_str:
                    return False, f"Invalid range format: '{part}' (missing start or end)"
                
                start = int(start_str)
                end = int(end_str)
                
                if start < 1 or end < 1:
                    return False, f"Slide numbers must be positive (got {start}-{end})"
                
                if start > end:
                    return False, f"Invalid range: start ({start}) > end ({end})"
            else:
                slide_num = int(part)
                if slide_num < 1:
                    return False, f"Slide number must be positive (got {slide_num})"
        
        return True, ""
        
    except ValueError as e:
        return False, f"Invalid numbers in range: {str(e)}"
    except Exception as e:
        return False, f"Invalid range specification: {str(e)}"

# Example usage and tests
if __name__ == "__main__":
    # Test cases
    test_cases = [
        ("5", 10, [4]),
        ("5-7", 10, [4, 5, 6]),
        ("1,3,5-7", 10, [0, 2, 4, 5, 6]),
        ("all", 5, [0, 1, 2, 3, 4]),
        ("16-18l", 20, None),  # Should be cleaned to "16-18"
    ]
    
    for range_str, max_slides, expected in test_cases:
        try:
            result = parse_slide_range(range_str, max_slides)
            if range_str == "16-18l":
                # Special case - should work after cleaning
                print(f"✅ '{range_str}' → {result} (cleaned input)")
            else:
                print(f"✅ '{range_str}' → {result}")
                assert result == expected, f"Expected {expected}, got {result}"
        except ValueError as e:
            if expected is None:
                print(f"❌ '{range_str}' → Error: {e}")
            else:
                print(f"❌ Unexpected error for '{range_str}': {e}")
