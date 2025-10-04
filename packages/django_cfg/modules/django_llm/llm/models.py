"""
Pydantic models for LLM client responses.
"""

import math
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime


class TokenUsage(BaseModel):
    """Token usage information."""
    prompt_tokens: int = Field(default=0, description="Number of tokens in the prompt")
    completion_tokens: int = Field(default=0, description="Number of tokens in the completion")
    total_tokens: int = Field(default=0, description="Total number of tokens used")


class ChatChoice(BaseModel):
    """Chat completion choice."""
    index: int = Field(description="Choice index")
    message: Dict[str, Any] = Field(description="Message content")
    finish_reason: Optional[str] = Field(default=None, description="Reason for finishing")


class ChatCompletionResponse(BaseModel):
    """Chat completion response from LLM."""
    id: str = Field(description="Response ID")
    model: str = Field(description="Model used")
    created: str = Field(description="Creation timestamp")
    choices: List[ChatChoice] = Field(default_factory=list, description="Response choices")
    usage: Optional[TokenUsage] = Field(default=None, description="Token usage")
    finish_reason: Optional[str] = Field(default=None, description="Finish reason")
    content: str = Field(description="Response content")
    tokens_used: int = Field(default=0, description="Total tokens used")
    cost_usd: float = Field(default=0.0, description="Cost in USD")
    processing_time: float = Field(default=0.0, description="Processing time in seconds")
    extracted_json: Optional[Dict[str, Any]] = Field(default=None, description="Extracted JSON if any")
    
    @validator('cost_usd')
    def validate_cost_usd(cls, v):
        """Validate cost_usd to prevent NaN values."""
        if v is None or math.isnan(v) or math.isinf(v):
            return 0.0
        return v
    
    @validator('processing_time')
    def validate_processing_time(cls, v):
        """Validate processing_time to prevent NaN values."""
        if v is None or math.isnan(v) or math.isinf(v):
            return 0.0
        return v


class EmbeddingResponse(BaseModel):
    """Embedding generation response from LLM."""
    embedding: List[float] = Field(description="Generated embedding vector")
    tokens: int = Field(description="Number of tokens processed")
    cost: float = Field(description="Cost in USD")
    model: str = Field(description="Model used for embedding")
    text_length: int = Field(description="Length of input text")
    dimension: int = Field(description="Embedding vector dimension")
    response_time: float = Field(description="Response time in seconds")
    warning: Optional[str] = Field(default=None, description="Warning message if any")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            # Custom encoders if needed
        }


class LLMStats(BaseModel):
    """LLM client statistics."""
    successful_requests: int = Field(default=0, description="Number of successful requests")
    failed_requests: int = Field(default=0, description="Number of failed requests")
    total_tokens_used: int = Field(default=0, description="Total tokens used")
    total_cost_usd: float = Field(default=0.0, description="Total cost in USD")
    model_usage: Dict[str, int] = Field(default_factory=dict, description="Usage per model")
    provider_usage: Dict[str, int] = Field(default_factory=dict, description="Usage per provider")
    cache_hits: int = Field(default=0, description="Number of cache hits")
    cache_misses: int = Field(default=0, description="Number of cache misses")


class ModelInfo(BaseModel):
    """Model information."""
    id: str = Field(description="Model ID")
    name: str = Field(description="Model name")
    provider: str = Field(description="Provider name")
    max_tokens: int = Field(description="Maximum tokens")
    input_cost_per_token: float = Field(description="Input cost per token")
    output_cost_per_token: float = Field(description="Output cost per token")
    supports_functions: bool = Field(default=False, description="Supports function calling")
    supports_vision: bool = Field(default=False, description="Supports vision")
    context_window: int = Field(description="Context window size")


class CostEstimate(BaseModel):
    """Cost estimation result."""
    estimated_cost: float = Field(description="Estimated cost in USD")
    input_tokens: int = Field(description="Estimated input tokens")
    output_tokens: int = Field(description="Estimated output tokens")
    total_tokens: int = Field(description="Total estimated tokens")
    model: str = Field(description="Model used for estimation")


class ValidationResult(BaseModel):
    """Validation result for requests."""
    is_valid: bool = Field(description="Whether the request is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    estimated_tokens: Optional[int] = Field(default=None, description="Estimated token count")
    estimated_cost: Optional[float] = Field(default=None, description="Estimated cost")


class CacheInfo(BaseModel):
    """Cache information."""
    hit: bool = Field(description="Whether it was a cache hit")
    key: str = Field(description="Cache key")
    ttl: Optional[int] = Field(default=None, description="Time to live in seconds")
    size: Optional[int] = Field(default=None, description="Cache entry size")


class LLMError(BaseModel):
    """LLM error information."""
    error_type: str = Field(description="Type of error")
    message: str = Field(description="Error message")
    code: Optional[str] = Field(default=None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    retry_after: Optional[int] = Field(default=None, description="Retry after seconds")
