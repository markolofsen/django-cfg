"""
Embedding generation strategies for LLM client.

Provides real and mock embedding implementations.
"""

from .openai_embedder import OpenAIEmbedder
from .mock_embedder import MockEmbedder

__all__ = [
    'OpenAIEmbedder',
    'MockEmbedder',
]
