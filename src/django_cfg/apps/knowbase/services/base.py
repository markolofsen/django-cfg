"""
Base service classes and protocols.
"""

from typing import Protocol, Optional, List, Dict, Any
from django.contrib.auth import get_user_model
from django_cfg.modules.django_llm.llm.client import LLMClient
from django.conf import settings
from abc import ABC
from ..config.settings import get_openai_api_key, get_openrouter_api_key, get_cache_settings

User = get_user_model()


class LLMServiceProtocol(Protocol):
    """Protocol for LLM service dependency injection."""
    
    def generate_embedding(self, text: str) -> List[float]: ...
    def chat_completion(self, messages: List[Dict[str, str]]) -> Dict[str, Any]: ...
    def count_tokens(self, text: str, model: str = None) -> int: ...
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str = None) -> float: ...


class CacheServiceProtocol(Protocol):
    """Protocol for cache service."""
    
    def get(self, key: str) -> Optional[str]: ...
    def set(self, key: str, value: str, ttl: int = 3600) -> None: ...
    def delete(self, key: str) -> None: ...


class BaseService(ABC):
    """Base service with common functionality."""
    
    def __init__(self, user: User):
        self.user = user
        # Initialize LLM client with configuration
        cache_settings = get_cache_settings()
        self.llm_client = LLMClient(
            cache_dir=cache_settings.cache_dir,
            cache_ttl=cache_settings.cache_ttl,
            max_cache_size=cache_settings.max_cache_size
        )
    
    def _ensure_user_access(self, obj) -> None:
        """Ensure user has access to object."""
        if hasattr(obj, 'user') and obj.user != self.user:
            raise PermissionError(f"User {self.user.id} cannot access this resource")
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate SHA-256 hash for content."""
        import hashlib
        return hashlib.sha256(content.encode()).hexdigest()
