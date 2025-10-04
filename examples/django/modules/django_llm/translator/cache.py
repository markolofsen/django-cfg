"""
Translation Cache Manager - stores translations by language pairs like in unreal_llm
"""

import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from cachetools import TTLCache

logger = logging.getLogger(__name__)

class TranslationCacheManager:
    """Manages translation caching with TTL and file persistence (per language pair)"""
    
    def __init__(self, cache_dir: Optional[str] = None, ttl_hours: int = 24):
        """
        Initialize translation cache manager
        
        Args:
            cache_dir: Directory for file cache
            ttl_hours: Time-to-live for cache in hours
        """
        # Default cache directory inside django-cfg module structure
        if cache_dir is None:
            # Get the django_cfg module directory
            module_dir = Path(__file__).parent.parent.parent.parent  # django_cfg/modules/django_llm/translator -> django_cfg
            default_cache_dir = module_dir / ".cache" / "llm_translate"
            
            # Create cache directory if it doesn't exist
            default_cache_dir.mkdir(parents=True, exist_ok=True)
        else:
            default_cache_dir = Path(cache_dir)
            
        self.cache_dir = default_cache_dir
        self.ttl_seconds = ttl_hours * 3600
        
        # In-memory cache with TTL (like in unreal_llm)
        self._memory_cache = TTLCache(maxsize=1000, ttl=self.ttl_seconds)
        
        logger.info(f"Translation cache initialized: {self.cache_dir}")
    
    def _get_cache_file(self, source_lang: str, target_lang: str) -> Path:
        """Get cache file path for language pair (like in unreal_llm)"""
        return self.cache_dir / f"{source_lang}→{target_lang}.json"
    
    def _get_text_hash(self, text: str) -> str:
        """Generate hash for text"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _load_file_cache(self, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """Load translations from file cache"""
        cache_file = self._get_cache_file(source_lang, target_lang)
        
        if not cache_file.exists():
            return {}
            
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load cache file {cache_file}: {e}")
            return {}
    
    def _save_file_cache(self, source_lang: str, target_lang: str, cache_data: Dict[str, Any]):
        """Save translations to file cache"""
        cache_file = self._get_cache_file(source_lang, target_lang)
        
        try:
            # Ensure directory exists
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
        except IOError as e:
            logger.error(f"Failed to save cache file {cache_file}: {e}")
    
    def get(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Get translation from cache"""
        text_hash = self._get_text_hash(text)
        cache_key = f"{source_lang}→{target_lang}:{text_hash}"
        
        # Check memory cache first
        if cache_key in self._memory_cache:
            return self._memory_cache[cache_key]
        
        # Check file cache
        file_cache = self._load_file_cache(source_lang, target_lang)
        if text_hash in file_cache:
            translation = file_cache[text_hash]
            # Store in memory cache
            self._memory_cache[cache_key] = translation
            return translation
            
        return None
    
    def set(self, text: str, source_lang: str, target_lang: str, translation: str):
        """Store translation in cache"""
        text_hash = self._get_text_hash(text)
        cache_key = f"{source_lang}→{target_lang}:{text_hash}"
        
        # Store in memory cache
        self._memory_cache[cache_key] = translation
        
        # Store in file cache
        file_cache = self._load_file_cache(source_lang, target_lang)
        file_cache[text_hash] = translation
        self._save_file_cache(source_lang, target_lang, file_cache)
        
        logger.debug(f"Cached translation: {source_lang}→{target_lang} ({len(text)} chars)")
    
    def clear(self, source_lang: Optional[str] = None, target_lang: Optional[str] = None):
        """Clear cache (all or specific language pair)"""
        if source_lang and target_lang:
            # Clear specific language pair
            cache_file = self._get_cache_file(source_lang, target_lang)
            if cache_file.exists():
                cache_file.unlink()
            
            # Clear from memory cache
            prefix = f"{source_lang}→{target_lang}:"
            keys_to_remove = [k for k in self._memory_cache.keys() if k.startswith(prefix)]
            for key in keys_to_remove:
                del self._memory_cache[key]
                
            logger.info(f"Cleared cache for {source_lang}→{target_lang}")
        else:
            # Clear all caches
            self._memory_cache.clear()
            
            # Remove all cache files
            if self.cache_dir.exists():
                for cache_file in self.cache_dir.glob("*.json"):
                    cache_file.unlink()
                    
            logger.info("Cleared all translation caches")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            'memory_cache_size': len(self._memory_cache),
            'cache_dir': str(self.cache_dir),
            'language_pairs': []
        }
        
        # Count file caches
        if self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.json"):
                lang_pair = cache_file.stem
                file_cache = self._load_file_cache(*lang_pair.split('→'))
                stats['language_pairs'].append({
                    'pair': lang_pair,
                    'translations': len(file_cache),
                    'file_size': cache_file.stat().st_size
                })
        
        return stats
