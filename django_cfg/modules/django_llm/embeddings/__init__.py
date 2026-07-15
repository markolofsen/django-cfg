"""
Embedding generation strategies for LLM client.

Provides real and mock embedding implementations.
"""

from .mock_embedder import MOCK_WARNING, MockEmbedder, is_mock_embedding
from .openai_embedder import OpenAIEmbedder
from .openrouter_embedder import OpenRouterEmbedder

__all__ = [
    'OpenAIEmbedder',
    'OpenRouterEmbedder',
    'MockEmbedder',
    'MOCK_WARNING',
    'is_mock_embedding',
]
