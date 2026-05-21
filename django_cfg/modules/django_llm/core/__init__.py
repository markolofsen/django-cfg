"""
Core foundation — host-agnostic Pydantic types and error taxonomy.
"""

from .errors import (
    AllProvidersFailedError,
    LLMAuthError,
    LLMBadRequestError,
    LLMBudgetError,
    LLMConfigError,
    LLMContentFilterError,
    LLMCreditsError,
    LLMError,
    LLMRateLimitError,
    LLMServerError,
    LLMTimeoutError,
    LLMTransportError,
    LLMTruncationError,
    LLMValidationError,
    classify_exception,
)
from .types import (
    CacheInfo,
    ChatChoice,
    ChatCompletionResponse,
    CostEstimate,
    EmbeddingResponse,
    LLMStats,
    ModelInfo,
    TokenUsage,
    ValidationResult,
)

__all__ = [
    # types
    'CacheInfo',
    'ChatChoice',
    'ChatCompletionResponse',
    'CostEstimate',
    'EmbeddingResponse',
    'LLMStats',
    'ModelInfo',
    'TokenUsage',
    'ValidationResult',
    # error taxonomy
    'LLMError',
    'LLMConfigError',
    'LLMAuthError',
    'LLMBadRequestError',
    'LLMCreditsError',
    'LLMContentFilterError',
    'LLMValidationError',
    'LLMTruncationError',
    'LLMBudgetError',
    'LLMTransportError',
    'LLMTimeoutError',
    'LLMServerError',
    'LLMRateLimitError',
    'AllProvidersFailedError',
    'classify_exception',
]
