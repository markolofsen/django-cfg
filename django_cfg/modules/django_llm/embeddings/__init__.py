"""
Embedding generation strategies for LLM client.

Provides real and mock embedding implementations.
"""

from .mock_embedder import MockEmbedder
from .openai_embedder import OpenAIEmbedder
from .openrouter_embedder import OpenRouterEmbedder

__all__ = [
    'OpenAIEmbedder',
    'OpenRouterEmbedder',
    'MockEmbedder',
]
