"""
Django Agent - Proper Pydantic AI integration for Django.

This module provides a Django-friendly wrapper around Pydantic AI agents
with optimal model selection for Python development tasks.
"""

import time
from collections.abc import Sequence
from typing import Any, Callable, Dict, Generic, Optional, Type, TypeVar

from pydantic_ai import Agent
from pydantic_ai.models import KnownModelName
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.openrouter import OpenRouterProvider

from django_cfg.modules.base import BaseCfgModule
from django_cfg.modules.django_logging import get_logger

from .exceptions import ExecutionError

# Type variables for generic typing
DepsT = TypeVar('DepsT')
OutputT = TypeVar('OutputT')

logger = get_logger("agents.core")


class DjangoAgent(Generic[DepsT, OutputT]):
    """
    Django-integrated agent using Pydantic AI.
    
    Features:
    - Optimal model selection (Kimi Dev 72B for Python coding via OpenRouter)
    - Automatic fallback to OpenAI models
    - Metrics collection
    - Error handling
    - Tool management
    """

    def __init__(
        self,
        name: str,
        deps_type: Type[DepsT],
        output_type: Type[OutputT],
        instructions: str,
        model: Optional[KnownModelName | str] = None,
        tools: Optional[Sequence] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        """Initialize Django Agent with Pydantic AI."""
        self.name = name
        self.deps_type = deps_type
        self.output_type = output_type
        self.instructions = instructions

        # Select optimal model for Python development
        if model:
            selected_model = model
            model_kwargs = {}
        else:
            selected_model, model_kwargs = self._get_optimal_model()

        # Merge model_kwargs with user kwargs (user kwargs take priority)
        final_kwargs = {**model_kwargs, **kwargs}

        # Initialize Pydantic AI Agent directly
        self.agent = Agent(
            model=selected_model,
            deps_type=deps_type,
            output_type=output_type,
            instructions=instructions,
            system_prompt=system_prompt or "",
            tools=tools or [],
            **final_kwargs
        )

        # Metrics
        self._execution_count = 0
        self._total_execution_time = 0.0
        self._error_count = 0

        logger.info(f"Initialized DjangoAgent '{name}' with model '{selected_model}'")

    def _get_optimal_model(self) -> tuple[str, dict]:
        """
        Get optimal model for Python development tasks.
        
        Returns:
            tuple: (model_instance, model_kwargs) where model_instance is an initialized Pydantic AI model
        
        Priority:
        1. OpenRouter + GPT-4o-mini (supports tools, better rate limits) - DEFAULT
        2. OpenAI GPT-4o-mini (fallback if OpenRouter unavailable)
        3. Test model (for testing)
        
        Note: We use GPT-4o-mini through OpenRouter instead of specialized models like Kimi Dev 72B
        because our agents require tool support, which many specialized models don't provide.
        """
        try:
            # Initialize django-cfg configuration
            cfg = BaseCfgModule()
            django_config = cfg.get_config()

            if django_config and hasattr(django_config, 'api_keys') and django_config.api_keys:
                api_keys = django_config.api_keys

                # Priority 1: OpenRouter + GPT-4o-mini (supports tools) - DEFAULT
                if api_keys.has_openrouter():
                    openrouter_key = api_keys.get_openrouter_key()
                    logger.info("🚀 Using OpenAI GPT-4o-mini via OpenRouter - reliable tool support (DEFAULT)")
                    logger.debug(f"🔑 OpenRouter API key: {openrouter_key[:10]}...{openrouter_key[-4:] if openrouter_key else 'None'}")

                    provider = OpenRouterProvider(api_key=openrouter_key)
                    # Use GPT-4o-mini through OpenRouter (supports tools)
                    model = OpenAIChatModel('openai/gpt-4o-mini', provider=provider)
                    return model, {}

                # Priority 2: OpenAI GPT-4o-mini (fallback if OpenRouter unavailable)
                if api_keys.has_openai():
                    openai_key = api_keys.get_openai_key()
                    logger.info("⚠️  Using OpenAI GPT-4o-mini - reliable tool support (FALLBACK - OpenRouter unavailable)")
                    logger.debug(f"🔑 OpenAI API key: {openai_key[:10]}...{openai_key[-4:] if openai_key else 'None'}")

                    provider = OpenAIProvider(api_key=openai_key)
                    model = OpenAIChatModel('gpt-4o-mini', provider=provider)
                    return model, {}

            # Test model for development
            logger.warning("⚠️  No API keys found in django-cfg config, using test model")
            return 'test', {}

        except Exception as e:
            logger.error(f"❌ Failed to load django-cfg config: {e}")
            logger.warning("⚠️  Using test model due to config error")
            return 'test', {}

    async def run(self, prompt: str, deps: DepsT, **kwargs) -> OutputT:
        """Run the agent with given prompt and dependencies."""
        start_time = time.time()

        try:
            self._execution_count += 1

            # Run Pydantic AI agent
            result = await self.agent.run(prompt, deps=deps, **kwargs)

            execution_time = time.time() - start_time
            self._total_execution_time += execution_time

            logger.debug(f"✅ Agent '{self.name}' executed in {execution_time:.2f}s")

            # Return the result data (Pydantic AI returns RunResult with .data attribute)
            return result.data if hasattr(result, 'data') else result

        except Exception as e:
            self._error_count += 1
            execution_time = time.time() - start_time
            self._total_execution_time += execution_time

            logger.error(f"❌ Agent '{self.name}' failed after {execution_time:.2f}s: {e}")
            raise ExecutionError(f"Agent execution failed: {e}") from e

    def run_sync(self, prompt: str, deps: DepsT, **kwargs) -> OutputT:
        """Run the agent synchronously."""
        start_time = time.time()

        try:
            self._execution_count += 1

            # Run Pydantic AI agent synchronously
            result = self.agent.run_sync(prompt, deps=deps, **kwargs)

            execution_time = time.time() - start_time
            self._total_execution_time += execution_time

            logger.debug(f"✅ Agent '{self.name}' executed sync in {execution_time:.2f}s")

            # Return the result data (Pydantic AI returns RunResult with .data attribute)
            return result.data if hasattr(result, 'data') else result

        except Exception as e:
            self._error_count += 1
            execution_time = time.time() - start_time
            self._total_execution_time += execution_time

            logger.error(f"❌ Agent '{self.name}' failed sync after {execution_time:.2f}s: {e}")
            raise ExecutionError(f"Agent execution failed: {e}") from e

    def tool(self, func: Callable = None, *, name: str = None):
        """Decorator to add tools to the agent."""
        return self.agent.tool(func, name=name)

    def get_metrics(self) -> Dict[str, Any]:
        """Get agent execution metrics."""
        avg_time = self._total_execution_time / max(self._execution_count, 1)
        success_rate = (self._execution_count - self._error_count) / max(self._execution_count, 1)

        return {
            "name": self.name,
            "model": str(self.agent.model),
            "execution_count": self._execution_count,
            "total_execution_time": self._total_execution_time,
            "average_execution_time": avg_time,
            "error_count": self._error_count,
            "success_rate": success_rate
        }

    def reset_metrics(self):
        """Reset agent metrics."""
        self._execution_count = 0
        self._total_execution_time = 0.0
        self._error_count = 0

    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"DjangoAgent(name='{self.name}', model='{self.agent.model}', deps_type={self.deps_type.__name__}, output_type={self.output_type.__name__})"


# Export the main class
__all__ = ['DjangoAgent']
