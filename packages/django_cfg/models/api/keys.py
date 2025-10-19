"""
API Keys configuration models for django-cfg.

Simple model for OpenAI and OpenRouter API keys.
Following CRITICAL_REQUIREMENTS.md:
- No raw Dict/Any usage - everything through Pydantic models
- Proper type annotations for all fields
- No mutable default arguments
"""

from typing import Optional

from pydantic import BaseModel, Field, SecretStr, field_validator


class ApiKeys(BaseModel):
    """
    API keys configuration for LLM services.
    
    Simple model for storing OpenAI and OpenRouter API keys.
    
    Example:
        ```python
        api_keys = ApiKeys(
            openai="${OPENAI_API_KEY}",
            openrouter="${OPENROUTER_API_KEY}"
        )
        ```
    """

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
        "validate_default": True,
    }

    # === LLM Provider Keys ===
    openai: Optional[SecretStr] = Field(
        default=None,
        description="OpenAI API key for GPT models and embeddings"
    )

    openrouter: Optional[SecretStr] = Field(
        default=None,
        description="OpenRouter API key for access to multiple LLM providers"
    )

    @field_validator("openai")
    @classmethod
    def validate_openai_key(cls, v: Optional[SecretStr]) -> Optional[SecretStr]:
        """Validate OpenAI API key format."""
        if v is None:
            return v

        key_str = v.get_secret_value()

        # Treat empty string as None
        if not key_str or key_str.strip() == "":
            return None

        if not key_str.startswith(("sk-", "sk-proj-")):
            raise ValueError("OpenAI API key must start with 'sk-' or 'sk-proj-'")

        if len(key_str) < 20:
            raise ValueError("OpenAI API key appears to be too short")

        return v

    @field_validator("openrouter")
    @classmethod
    def validate_openrouter_key(cls, v: Optional[SecretStr]) -> Optional[SecretStr]:
        """Validate OpenRouter API key format."""
        if v is None:
            return v

        key_str = v.get_secret_value()

        # Treat empty string as None
        if not key_str or key_str.strip() == "":
            return None

        if not key_str.startswith(("sk-or-", "sk-proj-")):
            raise ValueError("OpenRouter API key must start with 'sk-or-' or 'sk-proj-'")

        if len(key_str) < 20:
            raise ValueError("OpenRouter API key appears to be too short")

        return v

    def get_openai_key(self) -> Optional[str]:
        """Get OpenAI API key as string."""
        return self.openai.get_secret_value() if self.openai else None

    def get_openrouter_key(self) -> Optional[str]:
        """Get OpenRouter API key as string."""
        return self.openrouter.get_secret_value() if self.openrouter else None

    def has_openai(self) -> bool:
        """Check if OpenAI key is configured."""
        return self.openai is not None

    def has_openrouter(self) -> bool:
        """Check if OpenRouter key is configured."""
        return self.openrouter is not None

    def get_preferred_provider(self) -> Optional[str]:
        """
        Get preferred provider based on availability.
        
        Priority: OpenRouter (default) > OpenAI
        
        Returns:
            "openrouter" or "openai" or None
        """
        if self.has_openrouter():
            return "openrouter"
        elif self.has_openai():
            return "openai"
        return None


# Export the main class
__all__ = [
    "ApiKeys",
]
