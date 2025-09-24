"""
Django Agent - Wrapper around Pydantic AI Agent with Django integration.
"""

import time
import logging
from typing import TypeVar, Generic, Type, Any, Optional, Dict, Callable
from dataclasses import dataclass

from pydantic_ai import Agent
from pydantic_ai.models import Model

from .exceptions import ExecutionError, ConfigurationError
from .models import ExecutionResult

# Type variables for generic typing
DepsT = TypeVar('DepsT')
OutputT = TypeVar('OutputT')

logger = logging.getLogger(__name__)


class DjangoAgent(Generic[DepsT, OutputT]):
    """
    Django-integrated agent wrapper around Pydantic AI Agent.
    
    Provides Django-specific functionality like:
    - Integration with django_llm module
    - Caching support
    - Metrics collection
    - Error handling
    - Type safety
    """
    
    def __init__(
        self,
        name: str,
        deps_type: Type[DepsT],
        output_type: Type[OutputT],
        instructions: str,
        model: Optional[str] = None,
        llm_client: Optional[Any] = None,
        timeout: int = 300,
        max_retries: int = 3,
        enable_caching: bool = True
    ):
        """
        Initialize Django Agent.
        
        Args:
            name: Unique agent identifier
            deps_type: Type for dependency injection (must be dataclass)
            output_type: Pydantic model for output validation
            instructions: System prompt for the agent
            model: Override model (uses client default if None)
            llm_client: Optional LLM client (uses default if None)
            timeout: Execution timeout in seconds
            max_retries: Maximum retry attempts
            enable_caching: Whether to enable result caching
        """
        self.name = name
        self.deps_type = deps_type
        self.output_type = output_type
        self.instructions = instructions
        self.timeout = timeout
        self.max_retries = max_retries
        self.enable_caching = enable_caching
        
        # Get LLM client
        self.llm_client = llm_client or self._get_default_llm_client()
        
        # Determine model to use
        model_name = model or self._get_default_model()
        
        # Create Pydantic AI agent
        self.agent = Agent[DepsT, OutputT](
            model=model_name,
            deps_type=deps_type,
            output_type=output_type,
            instructions=instructions,
            retries=max_retries
        )
        
        # Initialize metrics
        self._execution_count = 0
        self._total_execution_time = 0.0
        self._error_count = 0
        self._cache_hits = 0
        
        logger.info(f"Initialized DjangoAgent '{name}' with model '{model_name}'")
    
    async def run(self, prompt: str, deps: DepsT, **kwargs) -> ExecutionResult:
        """
        Run agent with Django-specific enhancements.
        
        Args:
            prompt: User prompt/instruction
            deps: Dependencies instance
            **kwargs: Additional Pydantic AI parameters
            
        Returns:
            ExecutionResult with output, usage, and metadata
        """
        start_time = time.time()
        self._execution_count += 1
        
        # Check cache if enabled
        if self.enable_caching:
            cached_result = await self._check_cache(prompt, deps)
            if cached_result:
                self._cache_hits += 1
                logger.debug(f"Cache hit for agent '{self.name}'")
                return ExecutionResult(
                    agent_name=self.name,
                    output=cached_result,
                    execution_time=0.0,
                    cached=True
                )
        
        try:
            # Execute agent
            logger.debug(f"Executing agent '{self.name}' with prompt: {prompt[:100]}...")
            
            result = await self.agent.run(prompt, deps=deps, **kwargs)
            
            execution_time = time.time() - start_time
            self._total_execution_time += execution_time
            
            # Extract metrics
            tokens_used = 0
            cost = 0.0
            if hasattr(result, 'usage') and result.usage:
                tokens_used = getattr(result.usage, 'total_tokens', 0)
                # Calculate cost based on model and tokens (implement based on your pricing)
                cost = self._calculate_cost(tokens_used)
            
            execution_result = ExecutionResult(
                agent_name=self.name,
                output=result.output,
                execution_time=execution_time,
                tokens_used=tokens_used,
                cost=cost
            )
            
            # Cache result if enabled
            if self.enable_caching:
                await self._cache_result(prompt, deps, result.output)
            
            logger.info(
                f"Agent '{self.name}' executed successfully in {execution_time:.2f}s "
                f"(tokens: {tokens_used}, cost: ${cost:.4f})"
            )
            
            return execution_result
            
        except Exception as e:
            self._error_count += 1
            execution_time = time.time() - start_time
            
            logger.error(f"Agent '{self.name}' execution failed: {e}")
            
            raise ExecutionError(
                f"Agent '{self.name}' execution failed: {str(e)}",
                agent_name=self.name,
                original_error=e
            )
    
    def tool(self, func: Callable) -> Callable:
        """
        Register tool with agent.
        
        Args:
            func: Function to register as agent tool
            
        Returns:
            Decorated function
        """
        return self.agent.tool(func)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent execution metrics."""
        return {
            'name': self.name,
            'execution_count': self._execution_count,
            'total_execution_time': self._total_execution_time,
            'average_execution_time': (
                self._total_execution_time / self._execution_count 
                if self._execution_count > 0 else 0
            ),
            'error_count': self._error_count,
            'success_rate': (
                (self._execution_count - self._error_count) / self._execution_count
                if self._execution_count > 0 else 0
            ),
            'cache_hits': self._cache_hits,
            'cache_hit_rate': (
                self._cache_hits / self._execution_count
                if self._execution_count > 0 else 0
            )
        }
    
    def reset_metrics(self):
        """Reset agent metrics."""
        self._execution_count = 0
        self._total_execution_time = 0.0
        self._error_count = 0
        self._cache_hits = 0
    
    def _get_default_llm_client(self):
        """Get default LLM client from django_llm module."""
        try:
            from django_cfg.modules.django_llm import DjangoLLM
            llm_service = DjangoLLM()
            if llm_service.is_configured:
                return llm_service.client
        except ImportError:
            logger.warning("django_llm module not available, using default client")
        
        return None
    
    def _get_default_model(self) -> str:
        """Get default model name."""
        if self.llm_client and hasattr(self.llm_client, 'primary_provider'):
            if self.llm_client.primary_provider == 'openrouter':
                return 'openai:gpt-4o-mini'
            elif self.llm_client.primary_provider == 'openai':
                return 'openai:gpt-4o-mini'
        
        return 'openai:gpt-4o-mini'  # Default fallback
    
    async def _check_cache(self, prompt: str, deps: DepsT) -> Optional[Any]:
        """Check cache for existing result."""
        if not self.llm_client or not hasattr(self.llm_client, 'cache'):
            return None
        
        try:
            cache_key = self._generate_cache_key(prompt, deps)
            return self.llm_client.cache.get(cache_key)
        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
            return None
    
    async def _cache_result(self, prompt: str, deps: DepsT, result: Any):
        """Cache execution result."""
        if not self.llm_client or not hasattr(self.llm_client, 'cache'):
            return
        
        try:
            cache_key = self._generate_cache_key(prompt, deps)
            self.llm_client.cache.set(cache_key, result)
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")
    
    def _generate_cache_key(self, prompt: str, deps: DepsT) -> str:
        """Generate cache key for prompt and dependencies."""
        # Create a simple hash-based key
        import hashlib
        
        # Include agent name, prompt, and relevant deps data
        key_data = f"{self.name}:{prompt}"
        
        # Add user info if available
        if hasattr(deps, 'user') and deps.user:
            key_data += f":user_{deps.user.id}"
        
        # Add other relevant dependency data
        if hasattr(deps, 'to_dict'):
            deps_str = str(sorted(deps.to_dict().items()))
            key_data += f":deps_{deps_str}"
        
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _calculate_cost(self, tokens_used: int) -> float:
        """Calculate cost based on tokens used."""
        # Implement based on your pricing model
        # This is a simple example
        cost_per_1k_tokens = 0.002  # Example: $0.002 per 1K tokens
        return (tokens_used / 1000) * cost_per_1k_tokens
    
    def __repr__(self) -> str:
        return f"DjangoAgent(name='{self.name}', deps_type={self.deps_type.__name__}, output_type={self.output_type.__name__})"
