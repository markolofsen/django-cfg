"""
Response builder for LLM client.

Builds Pydantic response objects from API responses.
"""

import logging
from datetime import datetime
from typing import Optional

from openai.types.chat import ChatCompletion

from ..costs import calculate_chat_cost
from ..models import ChatChoice, ChatCompletionResponse, TokenUsage

logger = logging.getLogger(__name__)


class ResponseBuilder:
    """Builds Pydantic response objects from API responses."""

    def __init__(self, models_cache=None, json_extractor=None):
        """
        Initialize response builder.

        Args:
            models_cache: Optional models cache for cost calculation
            json_extractor: Optional JSON extractor for parsing JSON responses
        """
        self.models_cache = models_cache
        self.json_extractor = json_extractor

    def build_chat_response(
        self,
        api_response: ChatCompletion,
        model: str,
        provider: str,
        response_format: Optional[str] = None,
        processing_time: float = 0.0
    ) -> ChatCompletionResponse:
        """
        Build ChatCompletionResponse from API response.

        Args:
            api_response: Raw API response from OpenAI
            model: Model used for generation
            provider: Provider used
            response_format: Response format (e.g., "json")
            processing_time: Time taken to process request

        Returns:
            ChatCompletionResponse Pydantic model
        """
        # Calculate cost
        usage_dict = self._extract_usage(api_response)
        cost_usd = calculate_chat_cost(usage_dict, model, self.models_cache)

        # Extract content
        content = self._extract_content(api_response)

        # Try to extract JSON if requested
        extracted_json = None
        if response_format == "json" and content and self.json_extractor:
            try:
                extracted_json = self.json_extractor.extract_json_from_response(content)
            except Exception as e:
                logger.warning(f"Failed to extract JSON from response: {e}")

        # Build response object
        return ChatCompletionResponse(
            id=api_response.id,
            model=api_response.model,
            created=datetime.fromtimestamp(api_response.created).isoformat(),
            choices=self._build_choices(api_response),
            usage=self._build_token_usage(api_response.usage),
            finish_reason=self._extract_finish_reason(api_response),
            content=content,
            tokens_used=usage_dict['total_tokens'],
            cost_usd=cost_usd,
            processing_time=processing_time,
            extracted_json=extracted_json
        )

    def _extract_usage(self, api_response: ChatCompletion) -> dict:
        """Extract usage dictionary from API response."""
        if api_response.usage:
            return api_response.usage.model_dump()
        return {
            'total_tokens': 0,
            'prompt_tokens': 0,
            'completion_tokens': 0
        }

    def _extract_content(self, api_response: ChatCompletion) -> str:
        """Extract content from API response."""
        if api_response.choices and len(api_response.choices) > 0:
            return api_response.choices[0].message.content or ""
        return ""

    def _extract_finish_reason(self, api_response: ChatCompletion) -> Optional[str]:
        """Extract finish reason from API response."""
        if api_response.choices and len(api_response.choices) > 0:
            return api_response.choices[0].finish_reason
        return None

    def _build_choices(self, api_response: ChatCompletion) -> list:
        """Build list of ChatChoice objects from API response."""
        if not api_response.choices:
            return []

        return [
            ChatChoice(
                index=choice.index,
                message=choice.message.model_dump() if hasattr(choice.message, 'model_dump') else choice.message,
                finish_reason=choice.finish_reason
            ) for choice in api_response.choices
        ]

    def _build_token_usage(self, usage) -> TokenUsage:
        """Build TokenUsage object from API response usage."""
        if usage:
            return TokenUsage(
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens
            )
        return TokenUsage(
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0
        )
