"""
Retry utilities for Cloudflare operations.

Simple retry logic extracted from the complex old system.
"""

import time
import random
import logging
from typing import Callable, Any, List
from functools import wraps

logger = logging.getLogger(__name__)


class CloudflareRetryError(Exception):
    """Exception raised when all retry attempts fail."""
    pass


def retry_on_failure(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_factor: float = 2.0,
    retry_on_status: List[int] = None,
    jitter: bool = True
):
    """
    Decorator for retrying Cloudflare operations with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Factor to multiply delay by after each retry
        retry_on_status: HTTP status codes to retry on (deprecated, kept for compatibility)
        jitter: Whether to add random jitter to delays
    """
    if retry_on_status is None:
        retry_on_status = [429, 502, 503, 504]
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    last_exception = e
                    
                    # Don't retry on the last attempt
                    if attempt == max_retries:
                        break
                    
                    # Check if we should retry based on the error
                    should_retry = True  # Default to retry
                    
                    # Check for HTTP status codes in the error message
                    error_str = str(e).lower()
                    
                    # Check if any custom retry status codes are in the error
                    has_custom_status = False
                    for status in retry_on_status:
                        if str(status) in error_str:
                            has_custom_status = True
                            break
                    
                    # If we have custom status codes and found one, always retry
                    if has_custom_status:
                        should_retry = True
                    else:
                        # Don't retry on certain non-retryable errors (only if no custom status found)
                        if any(keyword in error_str for keyword in [
                            'authentication', 'unauthorized', 'forbidden', 'not found',
                            'invalid', 'malformed'
                        ]):
                            should_retry = False
                    
                    if not should_retry:
                        # Don't retry on non-retryable errors
                        break
                    
                    # Calculate delay with exponential backoff and optional jitter
                    delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                    if jitter:
                        jitter_amount = random.uniform(0.1, 0.3) * delay
                        total_delay = delay + jitter_amount
                    else:
                        total_delay = delay
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {e}. "
                        f"Retrying in {total_delay:.2f}s..."
                    )
                    
                    time.sleep(total_delay)
            
            # All retries failed
            raise CloudflareRetryError(
                f"All {max_retries + 1} attempts failed for {func.__name__}. "
                f"Last error: {last_exception}"
            ) from last_exception
        
        return wrapper
    return decorator
