"""
LLM Cache Manager — caches LLM responses to avoid duplicate API calls.

The persistent layer is a SQLite store (WAL mode, per-entry TTL, LRU
eviction). An in-memory ``TTLCache`` sits in front of it as an L1 read
cache so repeated hits within a process skip the DB entirely.
"""

import hashlib
import json
import logging
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, Optional

from cachetools import TTLCache

logger = logging.getLogger(__name__)

# SQLite busy_timeout in milliseconds — wait rather than fail when another
# process holds a write lock.
_BUSY_TIMEOUT_MS = 5000


class LLMCache:
    """Manages LLM response caching with TTL, LRU eviction and SQLite persistence."""

    def __init__(self, cache_dir: Optional[str] = None, ttl: int = 3600, max_size: int = 1000):
        """
        Initialize LLM cache manager.

        Args:
            cache_dir: Directory for persistent cache storage
            ttl: Time to live in seconds (default: 1 hour)
            max_size: Maximum number of items in the persistent store and L1 cache
        """
        if cache_dir is None:
            # Default cache directory inside the django_llm module structure.
            module_dir = Path(__file__).parent.parent
            default_cache_dir = module_dir / ".cache" / "llm"
            default_cache_dir.mkdir(parents=True, exist_ok=True)
        else:
            default_cache_dir = Path(cache_dir)
            default_cache_dir.mkdir(parents=True, exist_ok=True)

        self.cache_dir = default_cache_dir
        self.cache_file = self.cache_dir / "llm_responses.sqlite3"
        self.ttl = ttl
        self.max_size = max_size

        # L1 in-memory read cache.
        self.memory_cache: TTLCache = TTLCache(maxsize=max_size, ttl=ttl)

        # Opening the DB is the one failure that propagates — the caller
        # (RequestCacheManager) wraps construction and degrades fail-open.
        self._conn = sqlite3.connect(str(self.cache_file), check_same_thread=False)
        self._init_db()

        logger.debug(f"LLM cache initialized: {self.cache_file}")

    def _init_db(self) -> None:
        """Create the schema and apply pragmas for multi-process safety."""
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(f"PRAGMA busy_timeout={_BUSY_TIMEOUT_MS}")
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS llm_responses (
                request_hash TEXT PRIMARY KEY,
                payload      TEXT NOT NULL,
                model        TEXT,
                created_at   REAL NOT NULL,
                expires_at   REAL NOT NULL,
                last_hit_at  REAL NOT NULL
            )
            """
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_llm_responses_last_hit "
            "ON llm_responses (last_hit_at)"
        )
        self._conn.commit()

    def generate_request_hash(self, messages: list, model: str, **kwargs) -> str:
        """Generate a SHA-256 hash for request parameters (sorted-JSON)."""
        request_data = {
            "messages": messages,
            "model": model,
            **kwargs,
        }
        request_str = json.dumps(request_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(request_str.encode("utf-8")).hexdigest()

    def get_response(self, request_hash: str) -> Optional[Dict[str, Any]]:
        """Get a cached response by hash, or None on a miss / expiry."""
        # L1 read cache — already TTL-bounded.
        if request_hash in self.memory_cache:
            logger.debug(f"Memory cache hit for hash: {request_hash[:8]}...")
            return self.memory_cache[request_hash]

        row = self._conn.execute(
            "SELECT payload, expires_at FROM llm_responses WHERE request_hash = ?",
            (request_hash,),
        ).fetchone()
        if row is None:
            return None

        payload_str, expires_at = row
        now = time.time()

        # Expired -> opportunistic delete + miss.
        if expires_at <= now:
            self._delete(request_hash)
            return None

        try:
            response = json.loads(payload_str)
        except (json.JSONDecodeError, TypeError) as exc:
            # Corrupt row -> self-heal and treat as a miss.
            logger.warning(f"Corrupt cache row for {request_hash[:8]}...: {exc}")
            self._delete(request_hash)
            return None

        # Bump LRU recency.
        self._conn.execute(
            "UPDATE llm_responses SET last_hit_at = ? WHERE request_hash = ?",
            (now, request_hash),
        )
        self._conn.commit()

        self.memory_cache[request_hash] = response
        logger.debug(f"Persistent cache hit for hash: {request_hash[:8]}...")
        return response

    def set_response(self, request_hash: str, response: Dict[str, Any], model: str) -> None:
        """Cache a response (upsert) and prune to max_size."""
        try:
            payload_str = json.dumps(response, ensure_ascii=False)
        except (TypeError, ValueError) as exc:
            logger.error(f"Failed to serialize response for cache: {exc}")
            return

        now = time.time()
        expires_at = now + self.ttl

        self._conn.execute(
            """
            INSERT INTO llm_responses
                (request_hash, payload, model, created_at, expires_at, last_hit_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(request_hash) DO UPDATE SET
                payload     = excluded.payload,
                model       = excluded.model,
                created_at  = excluded.created_at,
                expires_at  = excluded.expires_at,
                last_hit_at = excluded.last_hit_at
            """,
            (request_hash, payload_str, model, now, expires_at, now),
        )
        self._conn.commit()

        self.memory_cache[request_hash] = response
        self._prune()
        logger.debug(f"Cached response for hash: {request_hash[:8]}...")

    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache statistics."""
        row = self._conn.execute("SELECT COUNT(*) FROM llm_responses").fetchone()
        persistent_size = row[0] if row else 0
        return {
            "memory_cache_size": len(self.memory_cache),
            "memory_cache_maxsize": self.memory_cache.maxsize,
            "persistent_cache_size": persistent_size,
            "cache_dir": str(self.cache_dir),
            "cache_file": str(self.cache_file),
            "ttl_seconds": self.ttl,
            "max_size": self.max_size,
        }

    def clear_cache(self) -> None:
        """Clear all caches."""
        self.memory_cache.clear()
        self._conn.execute("DELETE FROM llm_responses")
        self._conn.commit()
        logger.info("LLM cache cleared")

    def _delete(self, request_hash: str) -> None:
        """Remove a single row from the persistent store."""
        self._conn.execute(
            "DELETE FROM llm_responses WHERE request_hash = ?", (request_hash,)
        )
        self._conn.commit()
        self.memory_cache.pop(request_hash, None)

    def _prune(self) -> None:
        """Drop expired rows, then LRU-evict down to max_size."""
        now = time.time()
        self._conn.execute("DELETE FROM llm_responses WHERE expires_at <= ?", (now,))

        row = self._conn.execute("SELECT COUNT(*) FROM llm_responses").fetchone()
        count = row[0] if row else 0
        if count > self.max_size:
            overflow = count - self.max_size
            # Evict the least-recently-hit rows.
            self._conn.execute(
                """
                DELETE FROM llm_responses
                WHERE request_hash IN (
                    SELECT request_hash FROM llm_responses
                    ORDER BY last_hit_at ASC
                    LIMIT ?
                )
                """,
                (overflow,),
            )
        self._conn.commit()
