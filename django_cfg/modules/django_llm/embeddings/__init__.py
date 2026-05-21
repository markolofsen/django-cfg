"""
Embedding generation strategies for LLM client.

Provides real and mock embedding implementations.
"""

from .mock_embedder import MockEmbedder
from .openai_embedder import OpenAIEmbedder

__all__ = [
    'OpenAIEmbedder',
    'MockEmbedder',
]
