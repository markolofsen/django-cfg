"""
Image caching service with TTL support.

Provides caching for fetched images and vision responses.
"""

import hashlib
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class ImageCache:
    """
    Cache for images and vision responses with TTL.

    Features:
    - File-based caching
    - Configurable TTL
    - Automatic cleanup of expired entries
    - Size limits
    """

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        ttl_hours: int = 168,  # 7 days
        max_size_mb: int = 1024,  # 1GB
        enabled: bool = True,
    ):
        """
        Initialize image cache.

        Args:
            cache_dir: Directory for cache files
            ttl_hours: Time-to-live in hours
            max_size_mb: Maximum cache size in megabytes
            enabled: Whether caching is enabled
        """
        self.enabled = enabled
        self.ttl_seconds = ttl_hours * 3600
        self.max_size_bytes = max_size_mb * 1024 * 1024

        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / ".cache" / "django_llm" / "images"

        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._metadata_file = self.cache_dir / "metadata.json"
            self._load_metadata()

    def _load_metadata(self):
        """Load cache metadata from file."""
        self._metadata: Dict[str, Dict[str, Any]] = {}
        if self._metadata_file.exists():
            try:
                with open(self._metadata_file, "r") as f:
                    self._metadata = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load cache metadata: {e}")
                self._metadata = {}

    def _save_metadata(self):
        """Save cache metadata to file."""
        try:
            with open(self._metadata_file, "w") as f:
                json.dump(self._metadata, f)
        except IOError as e:
            logger.warning(f"Failed to save cache metadata: {e}")

    @staticmethod
    def _hash_key(key: str) -> str:
        """Generate hash for cache key."""
        return hashlib.sha256(key.encode()).hexdigest()[:32]

    def _is_expired(self, key_hash: str) -> bool:
        """Check if cache entry is expired."""
        if key_hash not in self._metadata:
            return True
        created = self._metadata[key_hash].get("created", 0)
        return (time.time() - created) > self.ttl_seconds

    def get_image(self, url: str) -> Optional[Tuple[bytes, str]]:
        """
        Get cached image.

        Args:
            url: Image URL (cache key)

        Returns:
            Tuple of (image_bytes, content_type) or None if not cached
        """
        if not self.enabled:
            return None

        key_hash = self._hash_key(url)
        if self._is_expired(key_hash):
            return None

        cache_file = self.cache_dir / f"{key_hash}.bin"
        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "rb") as f:
                data = f.read()
            content_type = self._metadata[key_hash].get("content_type", "image/jpeg")
            logger.debug(f"Cache hit for {url[:50]}...")
            return data, content_type
        except IOError as e:
            logger.warning(f"Failed to read cached image: {e}")
            return None

    def set_image(
        self,
        url: str,
        data: bytes,
        content_type: str,
    ) -> bool:
        """
        Cache image data.

        Args:
            url: Image URL (cache key)
            data: Image bytes
            content_type: MIME type

        Returns:
            True if cached successfully
        """
        if not self.enabled:
            return False

        key_hash = self._hash_key(url)
        cache_file = self.cache_dir / f"{key_hash}.bin"

        try:
            with open(cache_file, "wb") as f:
                f.write(data)

            self._metadata[key_hash] = {
                "url": url[:200],
                "content_type": content_type,
                "size": len(data),
                "created": time.time(),
            }
            self._save_metadata()
            logger.debug(f"Cached image: {url[:50]}...")
            return True
        except IOError as e:
            logger.warning(f"Failed to cache image: {e}")
            return False

    def get_response(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached vision response.

        Args:
            key: Cache key (e.g., hash of image + prompt)

        Returns:
            Cached response dict or None
        """
        if not self.enabled:
            return None

        key_hash = self._hash_key(key)
        if self._is_expired(key_hash):
            return None

        cache_file = self.cache_dir / f"{key_hash}.json"
        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to read cached response: {e}")
            return None

    def set_response(self, key: str, response: Dict[str, Any]) -> bool:
        """
        Cache vision response.

        Args:
            key: Cache key
            response: Response dict to cache

        Returns:
            True if cached successfully
        """
        if not self.enabled:
            return False

        key_hash = self._hash_key(key)
        cache_file = self.cache_dir / f"{key_hash}.json"

        try:
            with open(cache_file, "w") as f:
                json.dump(response, f)

            self._metadata[key_hash] = {
                "type": "response",
                "created": time.time(),
            }
            self._save_metadata()
            return True
        except IOError as e:
            logger.warning(f"Failed to cache response: {e}")
            return False

    def make_cache_key(self, *args: Any) -> str:
        """
        Generate cache key from arguments.

        Args:
            *args: Values to include in key

        Returns:
            Cache key string
        """
        parts = [str(arg) for arg in args]
        return "|".join(parts)

    def clear(self) -> int:
        """
        Clear all cached data.

        Returns:
            Number of entries cleared
        """
        if not self.enabled:
            return 0

        count = 0
        for file in self.cache_dir.glob("*"):
            if file.is_file() and file.name != "metadata.json":
                try:
                    file.unlink()
                    count += 1
                except IOError:
                    pass

        self._metadata = {}
        self._save_metadata()
        logger.info(f"Cleared {count} cache entries")
        return count

    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.

        Returns:
            Number of entries removed
        """
        if not self.enabled:
            return 0

        count = 0
        expired_keys = []

        for key_hash, meta in self._metadata.items():
            if self._is_expired(key_hash):
                expired_keys.append(key_hash)
                # Remove files
                for ext in [".bin", ".json"]:
                    cache_file = self.cache_dir / f"{key_hash}{ext}"
                    if cache_file.exists():
                        try:
                            cache_file.unlink()
                            count += 1
                        except IOError:
                            pass

        # Update metadata
        for key_hash in expired_keys:
            del self._metadata[key_hash]
        self._save_metadata()

        logger.info(f"Cleaned up {count} expired cache entries")
        return count

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with cache stats
        """
        if not self.enabled:
            return {"enabled": False}

        total_size = 0
        image_count = 0
        response_count = 0

        for key_hash, meta in self._metadata.items():
            if meta.get("type") == "response":
                response_count += 1
            else:
                image_count += 1
                total_size += meta.get("size", 0)

        return {
            "enabled": True,
            "cache_dir": str(self.cache_dir),
            "ttl_hours": self.ttl_seconds / 3600,
            "image_count": image_count,
            "response_count": response_count,
            "total_size_mb": total_size / (1024 * 1024),
            "max_size_mb": self.max_size_bytes / (1024 * 1024),
        }


# Global cache instance (lazy initialization)
_global_cache: Optional[ImageCache] = None


def get_image_cache(
    cache_dir: Optional[Path] = None,
    ttl_hours: int = 168,
) -> ImageCache:
    """
    Get global image cache instance.

    Args:
        cache_dir: Optional custom cache directory
        ttl_hours: TTL in hours

    Returns:
        ImageCache instance
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = ImageCache(cache_dir=cache_dir, ttl_hours=ttl_hours)
    return _global_cache


__all__ = [
    "ImageCache",
    "get_image_cache",
]
