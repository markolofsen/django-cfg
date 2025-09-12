"""
Django LLM Service for django_cfg.

Auto-configuring LLM service that integrates with DjangoConfig.
"""

import logging
from typing import Optional, Dict, Any, Union, List
from datetime import datetime
from pathlib import Path

from django_cfg.modules import BaseModule
from .llm.client import LLMClient
from .llm.cache import LLMCache

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Base exception for LLM-related errors."""
    pass


class LLMConfigError(LLMError):
    """Raised when configuration is missing or invalid."""
    pass


class LLMRequestError(LLMError):
    """Raised when LLM request fails."""
    pass


class DjangoLLM(BaseModule):
    """
    LLM Service for django_cfg, configured via DjangoConfig.

    Provides LLM functionality with automatic configuration
    from the main DjangoConfig instance.
    """

    def __init__(self):
        self._client = None
        self._is_configured = None

    @property
    def config(self):
        """Get the DjangoConfig instance."""
        return self.get_config()

    @property
    def is_configured(self) -> bool:
        """Check if LLM service is properly configured."""
        if self._is_configured is None:
            try:
                # Check if LLM config exists and has required fields
                if hasattr(self.config, 'llm') and self.config.llm:
                    llm_config = self.config.llm
                    self._is_configured = (
                        hasattr(llm_config, 'api_key') and 
                        llm_config.api_key and 
                        len(llm_config.api_key.strip()) > 0
                    )
                else:
                    self._is_configured = False
            except Exception:
                self._is_configured = False

        return self._is_configured

    @property
    def client(self) -> LLMClient:
        """Get LLM client instance."""
        if self._client is None:
            # Get configuration
            cache_dir = None
            provider = "openrouter"
            api_key = None
            cache_ttl = 3600
            max_cache_size = 1000
            models_cache_ttl = 86400
            
            try:
                if hasattr(self.config, 'llm') and self.config.llm:
                    llm_config = self.config.llm
                    # Use new API key methods
                    api_key = llm_config.get_api_key()
                    provider = getattr(llm_config, 'provider', 'openrouter')
                    cache_ttl = getattr(llm_config, 'cache_ttl', 3600)
                    max_cache_size = getattr(llm_config, 'max_cache_size', 1000)
                    
                    # Custom cache directory if specified
                    if hasattr(llm_config, 'cache_dir'):
                        cache_dir = Path(llm_config.cache_dir)
                    elif hasattr(self.config, 'llm_cache_dir'):
                        cache_dir = Path(self.config.llm_cache_dir)
                
                # Check for models config
                if hasattr(self.config, 'llm_models') and self.config.llm_models:
                    models_config = self.config.llm_models
                    models_cache_ttl = getattr(models_config, 'models_cache_ttl', 86400)
            except Exception:
                pass
            
            self._client = LLMClient(
                provider=provider,
                api_key=api_key,
                cache_dir=cache_dir,
                cache_ttl=cache_ttl,
                max_cache_size=max_cache_size,
                models_cache_ttl=models_cache_ttl,
                config=self.config
            )
        return self._client

    @property
    def cache(self) -> LLMCache:
        """Get LLM cache instance from client."""
        return self.client.cache

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[str] = None,
        fail_silently: bool = False,
    ) -> Dict[str, Any]:
        """
        Send chat completion request.

        Args:
            messages: List of chat messages
            model: Model to use (auto-detected if not provided)
            temperature: Temperature for generation
            max_tokens: Maximum tokens
            response_format: Response format (e.g., "json")
            fail_silently: Don't raise exceptions on failure

        Returns:
            Chat completion response

        Raises:
            LLMRequestError: If request fails and fail_silently is False
        """
        try:
            if not self.is_configured:
                error_msg = "LLM service is not configured"
                logger.error(error_msg)
                if not fail_silently:
                    raise LLMConfigError(error_msg)
                return {}

            # Get default model if not specified
            if model is None:
                model = self._get_default_model()

            # Get default temperature if not specified
            if temperature is None:
                temperature = self._get_default_temperature()

            result = self.client.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format
            )

            logger.debug(f"Chat completion successful with model: {model}")
            return result

        except Exception as e:
            error_msg = f"Failed to complete chat request: {e}"
            logger.error(error_msg)
            if not fail_silently:
                raise LLMRequestError(error_msg) from e
            return {}

    def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        fail_silently: bool = False,
    ) -> str:
        """
        Generate text from prompt.

        Args:
            prompt: Input prompt
            model: Model to use
            temperature: Temperature for generation
            max_tokens: Maximum tokens
            fail_silently: Don't raise exceptions on failure

        Returns:
            Generated text
        """
        try:
            messages = [{"role": "user", "content": prompt}]
            
            result = self.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                fail_silently=fail_silently
            )
            
            return result.get('content', '') if result else ''

        except Exception as e:
            error_msg = f"Failed to generate text: {e}"
            logger.error(error_msg)
            if not fail_silently:
                raise LLMRequestError(error_msg) from e
            return ''

    def generate_json(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        fail_silently: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate JSON from prompt.

        Args:
            prompt: Input prompt
            model: Model to use
            temperature: Temperature for generation
            max_tokens: Maximum tokens
            fail_silently: Don't raise exceptions on failure

        Returns:
            Generated JSON object
        """
        try:
            messages = [{"role": "user", "content": prompt}]
            
            result = self.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format="json",
                fail_silently=fail_silently
            )
            
            return result.get('extracted_json', {}) if result else {}

        except Exception as e:
            error_msg = f"Failed to generate JSON: {e}"
            logger.error(error_msg)
            if not fail_silently:
                raise LLMRequestError(error_msg) from e
            return {}

    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        Count tokens in text.

        Args:
            text: Text to count tokens for
            model: Model to use for counting

        Returns:
            Number of tokens
        """
        try:
            if model is None:
                model = self._get_default_model()
            
            return self.client.count_tokens(text, model)

        except Exception as e:
            logger.error(f"Failed to count tokens: {e}")
            return 0

    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: Optional[str] = None
    ) -> float:
        """
        Estimate cost for tokens.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model to use for cost calculation

        Returns:
            Estimated cost in USD
        """
        try:
            if model is None:
                model = self._get_default_model()
            
            return self.client.estimate_cost(model, input_tokens, output_tokens)

        except Exception as e:
            logger.error(f"Failed to estimate cost: {e}")
            return 0.0

    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get available models.

        Returns:
            List of available models with information
        """
        try:
            return self.client.get_available_models()
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []

    def refresh_models(self, fail_silently: bool = False) -> bool:
        """
        Force refresh available models.

        Args:
            fail_silently: Don't raise exceptions on failure

        Returns:
            True if refresh was successful, False otherwise
        """
        try:
            success = self.client.refresh_models()
            if success:
                logger.info("Models refreshed successfully")
            else:
                logger.warning("Failed to refresh models")
            return success

        except Exception as e:
            error_msg = f"Failed to refresh models: {e}"
            logger.error(error_msg)
            if not fail_silently:
                raise LLMError(error_msg) from e
            return False

    def get_config_info(self) -> Dict[str, Any]:
        """Get LLM service configuration information."""
        try:
            cache_info = self.cache.get_cache_info()
            client_info = self.client.get_client_info()
            
            return {
                "configured": self.is_configured,
                "provider": getattr(self.config.llm, 'provider', 'openrouter') if hasattr(self.config, 'llm') else 'openrouter',
                "cache_directory": str(self.cache.cache_dir),
                "cache_info": cache_info,
                "client_info": client_info,
                "available_models_count": len(self.get_available_models()),
            }
        except Exception as e:
            logger.error(f"Failed to get config info: {e}")
            return {
                "configured": False,
                "error": str(e)
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        try:
            return self.client.get_stats()
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}

    def clear_cache(self) -> bool:
        """Clear the cache."""
        try:
            self.cache.clear_cache()
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False

    def _get_default_model(self) -> str:
        """Get default model from config."""
        try:
            if hasattr(self.config, 'llm') and self.config.llm:
                return getattr(self.config.llm, 'default_model', 'openai/gpt-4o-mini')
            return 'openai/gpt-4o-mini'
        except Exception:
            return 'openai/gpt-4o-mini'

    def _get_default_temperature(self) -> float:
        """Get default temperature from config."""
        try:
            if hasattr(self.config, 'llm') and self.config.llm:
                return getattr(self.config.llm, 'default_temperature', 0.7)
            return 0.7
        except Exception:
            return 0.7

    @classmethod
    def send_llm_alert(cls, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Send LLM alert via configured notification services."""
        try:
            # Try to send via Telegram if available
            from django_cfg.modules.django_telegram import DjangoTelegram
            telegram = DjangoTelegram()
            
            text = f"🤖 <b>LLM Alert</b>\n\n{message}"
            if context:
                text += "\n\n<b>Context:</b>\n"
                for key, value in context.items():
                    text += f"• {key}: {value}\n"
            
            telegram.send_message(text, parse_mode="HTML", fail_silently=True)
            
        except Exception as e:
            logger.error(f"Failed to send LLM alert: {e}")
