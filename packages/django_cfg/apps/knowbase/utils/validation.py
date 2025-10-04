"""
Validation utilities for the knowbase app.
"""

import math
from typing import Union, Optional


def is_valid_float(value: Union[float, int, None]) -> bool:
    """
    Check if a value is a valid float for JSON serialization.
    
    Args:
        value: The value to check
        
    Returns:
        True if the value is a valid float, False otherwise
    """
    if value is None:
        return False
    
    try:
        float_value = float(value)
        return not (math.isnan(float_value) or math.isinf(float_value))
    except (ValueError, TypeError):
        return False


def safe_float(value: Union[float, int, None], default: float = 0.0) -> float:
    """
    Convert a value to a safe float, replacing invalid values with default.
    
    Args:
        value: The value to convert
        default: Default value to use for invalid inputs
        
    Returns:
        A valid float value
    """
    if value is None:
        return default
    
    try:
        float_value = float(value)
        if math.isnan(float_value) or math.isinf(float_value):
            return default
        return float_value
    except (ValueError, TypeError):
        return default


def validate_similarity_score(similarity: Union[float, int, None]) -> Optional[float]:
    """
    Validate and normalize a similarity score.
    
    Args:
        similarity: The similarity score to validate
        
    Returns:
        Valid similarity score or None if invalid
    """
    if not is_valid_float(similarity):
        return None
    
    score = float(similarity)
    
    # Clamp to valid range [0.0, 1.0] for similarity scores
    if score < 0.0:
        return 0.0
    elif score > 1.0:
        return 1.0
    
    return score


def clean_search_results(results: list) -> list:
    """
    Clean search results by removing entries with invalid similarity scores.
    
    Args:
        results: List of search result dictionaries
        
    Returns:
        Cleaned list with valid similarity scores
    """
    cleaned_results = []
    
    for result in results:
        if 'similarity' not in result:
            continue
            
        similarity = validate_similarity_score(result['similarity'])
        if similarity is not None:
            # Create a copy and update similarity
            cleaned_result = result.copy()
            cleaned_result['similarity'] = similarity
            cleaned_results.append(cleaned_result)
    
    return cleaned_results
