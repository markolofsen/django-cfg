"""
LLM Cache Manager - caches LLM responses to avoid duplicate API calls
"""

import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, Optional, Any, List
from cachetools import TTLCache

logger = logging.getLogger(__name__)

class LLMCache:
    """Manages LLM response caching with TTL and file persistence"""
    
    def __init__(self, cache_dir: Optional[str] = None, ttl: int = 3600, max_size: int = 1000):
        """
        Initialize LLM cache manager
        
        Args:
            cache_dir: Directory for persistent cache storage
            ttl: Time to live in seconds (default: 1 hour)
            max_size: Maximum number of items in memory cache
        """
        # Default cache directory inside django-cfg module structure
        if cache_dir is None:
            # Get the django_cfg module directory
            module_dir = Path(__file__).parent.parent.parent  # django_cfg/modules/django_llm/llm -> django_cfg
            default_cache_dir = module_dir / ".cache" / "llm"
            
            # Create cache directory if it doesn't exist
            default_cache_dir.mkdir(parents=True, exist_ok=True)
        else:
            default_cache_dir = Path(cache_dir)
        
        self.cache_dir = default_cache_dir
        self.cache_file = self.cache_dir / "llm_responses.json"
        self.ttl = ttl
        self.max_size = max_size
        
        # TTL Memory Cache
        self.memory_cache = TTLCache(maxsize=max_size, ttl=ttl)
        
        # Load persistent cache
        self.persistent_cache = self._load_persistent_cache()
        
        logger.debug(f"LLM cache initialized: {self.cache_dir}")

    def _load_persistent_cache(self) -> Dict[str, Any]:
        """Load cache from file"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load persistent cache: {e}")
        return {}

    def _save_persistent_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.persistent_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save persistent cache: {e}")

    def generate_request_hash(self, messages: List[Dict], model: str, **kwargs) -> str:
        """Generate hash for request parameters"""
        # Create a consistent hash from request parameters
        request_data = {
            "messages": messages,
            "model": model,
            **kwargs
        }
        
        # Convert to JSON string for hashing
        request_str = json.dumps(request_data, sort_keys=True, ensure_ascii=False)
        
        # Generate SHA256 hash
        return hashlib.sha256(request_str.encode('utf-8')).hexdigest()

    def get_response(self, request_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached response by hash"""
        # Check memory cache first
        if request_hash in self.memory_cache:
            cache_entry = self.memory_cache[request_hash]
            logger.debug(f"Memory cache hit for hash: {request_hash[:8]}...")
            # Return only the response part, not the whole cache entry
            return cache_entry.get("response") if isinstance(cache_entry, dict) and "response" in cache_entry else cache_entry
        
        # Check persistent cache
        if request_hash in self.persistent_cache:
            cache_entry = self.persistent_cache[request_hash]
            # Add back to memory cache
            self.memory_cache[request_hash] = cache_entry
            logger.debug(f"Persistent cache hit for hash: {request_hash[:8]}...")
            # Return only the response part, not the whole cache entry
            return cache_entry.get("response") if isinstance(cache_entry, dict) and "response" in cache_entry else cache_entry
        
        return None

    def set_response(self, request_hash: str, response: Dict[str, Any], model: str):
        """Cache response"""
        try:
            # Add metadata
            cache_entry = {
                "response": response,
                "model": model,
                "cached_at": response.get("created", 0)
            }
            
            # Store in memory cache
            self.memory_cache[request_hash] = cache_entry
            
            # Store in persistent cache
            self.persistent_cache[request_hash] = cache_entry
            
            # Save to file
            self._save_persistent_cache()
            
            logger.debug(f"Cached response for hash: {request_hash[:8]}...")
            
        except Exception as e:
            logger.error(f"Failed to cache response: {e}")

    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "memory_cache_size": len(self.memory_cache),
            "memory_cache_maxsize": self.memory_cache.maxsize,
            "persistent_cache_size": len(self.persistent_cache),
            "cache_dir": str(self.cache_dir),
            "ttl_seconds": self.ttl
        }

    def clear_cache(self):
        """Clear all caches"""
        self.memory_cache.clear()
        self.persistent_cache.clear()
        
        # Remove cache file
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
        except Exception as e:
            logger.error(f"Failed to remove cache file: {e}")
        
        logger.info("LLM cache cleared")
