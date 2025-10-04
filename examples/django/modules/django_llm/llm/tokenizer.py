"""
Token counting utilities using tiktoken.

Provides token counting functionality for various LLM models.
"""

import logging
from typing import Dict, List
import tiktoken

logger = logging.getLogger(__name__)


class Tokenizer:
    """Token counting utility using tiktoken."""
    
    def __init__(self):
        """Initialize tokenizer with encoder cache."""
        self.encoders = {}
    
    def _get_encoder(self, model: str):
        """Get tiktoken encoder for model."""
        if model not in self.encoders:
            try:
                # Map model names to encoding names
                encoding_name = self._get_encoding_name(model)
                self.encoders[model] = tiktoken.get_encoding(encoding_name)
            except Exception as e:
                logger.warning(f"Failed to get encoder for {model}, using cl100k_base: {e}")
                self.encoders[model] = tiktoken.get_encoding("cl100k_base")
        
        return self.encoders[model]
    
    def _get_encoding_name(self, model: str) -> str:
        """Get encoding name for model."""
        # GPT-4 and GPT-3.5 models use cl100k_base
        if any(name in model.lower() for name in ["gpt-4", "gpt-3.5", "gpt-4o"]):
            return "cl100k_base"
        # GPT-2 models use gpt2
        elif "gpt-2" in model.lower():
            return "gpt2"
        # Default to cl100k_base for most modern models
        else:
            return "cl100k_base"
    
    def count_tokens(self, text: str, model: str) -> int:
        """
        Count tokens in text using tiktoken.
        
        Args:
            text: Text to count tokens for
            model: Model name for encoding
            
        Returns:
            Number of tokens
        """
        encoder = self._get_encoder(model)
        return len(encoder.encode(text))
    
    def count_messages_tokens(self, messages: List[Dict[str, str]], model: str) -> int:
        """
        Count total tokens in messages.
        
        Args:
            messages: List of chat messages
            model: Model name for encoding
            
        Returns:
            Total number of tokens
        """
        total_tokens = 0
        
        for message in messages:
            # Format message as it would be sent to API
            role = message.get('role', 'user')
            content = message.get('content', '')
            formatted_message = f"{role}\n{content}"
            total_tokens += self.count_tokens(formatted_message, model)
        
        # Add overhead for message formatting
        total_tokens += len(messages) * 4  # Rough estimate for message overhead
        
        return total_tokens
