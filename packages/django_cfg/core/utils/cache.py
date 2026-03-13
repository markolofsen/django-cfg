"""
Universal caching utilities for django-cfg.

Provides three building blocks used across the project:

- ``CacheKey``  — deterministic SHA-256 key builder from arbitrary data.
- ``FileCache`` — TTL-aware file-based cache (bytes or JSON) with optional
                  Git-style shard directories and metadata tracking.
- ``LazyFileResource`` — download-once remote resource (fonts, icons, …)
                         stored in a local directory.

Quick start::

    from django_cfg.core.utils.cache import CacheKey, FileCache, LazyFileResource

    # --- key builder ---
    key = CacheKey.from_dict({"title": "Hello", "locale": "en"})  # sha256[:40]
    key = CacheKey.from_args("model-v2", messages)                 # any JSON-able args

    # --- file cache ---
    cache = FileCache(cache_dir=Path("/tmp/my_cache"), ttl=3600)
    cache.set(key, b"<png bytes>", suffix=".png")
    data = cache.get(key, suffix=".png")   # None on miss or expiry

    # absolute path + relative URL for sharded media layout (OG images etc.)
    path, url = cache.sharded_paths(key, "ogimage", suffix=".png")

    # --- lazy remote resource ---
    font = LazyFileResource(
        url="https://example.com/NotoSansKR.ttf",
        dest=Path.home() / ".cache" / "django_cfg" / "fonts" / "NotoSansKR.ttf",
    )
    local_path = font.resolve()  # downloads on first call, cached afterwards
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
import urllib.request
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CacheKey
# ---------------------------------------------------------------------------

class CacheKey(str):
    """A SHA-256 hex-digest string with factory helpers.

    Inherits ``str`` so it can be used anywhere a plain string is expected.
    """

    LENGTH = 40  # hex chars (160 bits) — same as git short SHA

    # -- factories ----------------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict, *, exclude: set[str] | None = None) -> "CacheKey":
        """Build a key from a dict, optionally excluding certain keys.

        Keys are sorted before hashing, so insertion order doesn't matter.
        """
        stable = {k: v for k, v in data.items() if k not in (exclude or set())}
        raw = json.dumps(stable, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return cls._hash(raw)

    @classmethod
    def from_args(cls, *args: Any) -> "CacheKey":
        """Build a key from positional arguments (any JSON-serialisable values)."""
        raw = json.dumps(args, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return cls._hash(raw)

    @classmethod
    def from_string(cls, text: str) -> "CacheKey":
        """Build a key from a plain string (e.g. a URL)."""
        return cls._hash(text)

    @classmethod
    def from_bytes(cls, data: bytes) -> "CacheKey":
        """Build a key from raw bytes (e.g. file content)."""
        digest = hashlib.sha256(data).hexdigest()[: cls.LENGTH]
        return cls(digest)

    # -- shard helpers ------------------------------------------------------

    @property
    def shard_a(self) -> str:
        """First 2 hex chars — top-level shard dir (like git objects)."""
        return self[:2]

    @property
    def shard_b(self) -> str:
        """Next 2 hex chars — second-level shard dir."""
        return self[2:4]

    # -- internals ----------------------------------------------------------

    @classmethod
    def _hash(cls, text: str) -> "CacheKey":
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[: cls.LENGTH]
        return cls(digest)


# ---------------------------------------------------------------------------
# FileCache
# ---------------------------------------------------------------------------

class FileCache:
    """TTL-aware file cache stored in a local directory.

    Layout::

        <cache_dir>/
            metadata.json        ← per-key metadata (created_at, ttl, …)
            <key><suffix>        ← flat layout (default)
            <key[:2]>/<key[2:4]>/<key><suffix>  ← sharded layout (optional)

    Args:
        cache_dir: Root directory for this cache.
        ttl:       Time-to-live in seconds; ``0`` means no expiry.
        sharded:   When ``True`` uses Git-style 2+2 shard dirs inside
                   *cache_dir* — useful for large caches to avoid huge
                   directory listings.
        enabled:   When ``False`` all operations are no-ops.
    """

    _METADATA_FILE = "metadata.json"

    def __init__(
        self,
        cache_dir: Path,
        *,
        ttl: int = 0,
        sharded: bool = False,
        enabled: bool = True,
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.ttl = ttl
        self.sharded = sharded
        self.enabled = enabled
        self._meta: dict[str, dict[str, Any]] = {}

        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._meta = self._load_meta()

    # -- public API ---------------------------------------------------------

    def get(self, key: str, *, suffix: str = "") -> bytes | None:
        """Return cached bytes or ``None`` on miss / expiry."""
        if not self.enabled:
            return None
        if self._is_expired(key):
            return None
        path = self._file_path(key, suffix)
        if not path.exists():
            return None
        try:
            return path.read_bytes()
        except OSError as exc:
            logger.warning("FileCache.get failed: %s", exc)
            return None

    def get_json(self, key: str) -> Any | None:
        """Return deserialized JSON or ``None`` on miss / expiry."""
        raw = self.get(key, suffix=".json")
        if raw is None:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            logger.warning("FileCache.get_json decode failed: %s", exc)
            return None

    def set(self, key: str, data: bytes, *, suffix: str = "", meta: dict | None = None) -> bool:
        """Write bytes to the cache.

        Returns ``True`` on success, ``False`` on error.
        """
        if not self.enabled:
            return False
        path = self._file_path(key, suffix)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            entry: dict[str, Any] = {"created_at": time.time(), "size": len(data)}
            if meta:
                entry.update(meta)
            self._meta[key] = entry
            self._save_meta()
            return True
        except OSError as exc:
            logger.warning("FileCache.set failed: %s", exc)
            return False

    def set_json(self, key: str, value: Any, *, meta: dict | None = None) -> bool:
        """Serialize *value* as JSON and write to the cache."""
        raw = json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8")
        return self.set(key, raw, suffix=".json", meta=meta)

    def exists(self, key: str, *, suffix: str = "") -> bool:
        """Return ``True`` if a non-expired entry exists for *key*."""
        if not self.enabled:
            return False
        if self._is_expired(key):
            return False
        return self._file_path(key, suffix).exists()

    def delete(self, key: str, *, suffixes: list[str] | None = None) -> int:
        """Delete all files for *key*.  Returns number of files removed."""
        if not self.enabled:
            return 0
        count = 0
        for suffix in (suffixes or ["", ".json", ".bin"]):
            path = self._file_path(key, suffix)
            if path.exists():
                try:
                    path.unlink()
                    count += 1
                except OSError:
                    pass
        self._meta.pop(key, None)
        self._save_meta()
        return count

    def clear(self) -> int:
        """Delete every cached file.  Returns number of files removed."""
        if not self.enabled:
            return 0
        count = 0
        for path in self.cache_dir.glob("**/*"):
            if path.is_file() and path.name != self._METADATA_FILE:
                try:
                    path.unlink()
                    count += 1
                except OSError:
                    pass
        self._meta.clear()
        self._save_meta()
        return count

    def cleanup_expired(self) -> int:
        """Remove expired entries.  Returns number of files removed."""
        if not self.enabled or self.ttl == 0:
            return 0
        expired = [k for k in list(self._meta) if self._is_expired(k)]
        count = 0
        for key in expired:
            count += self.delete(key, suffixes=["", ".json", ".bin", ".png"])
        return count

    def stats(self) -> dict[str, Any]:
        """Return basic cache statistics."""
        if not self.enabled:
            return {"enabled": False}
        total_bytes = sum(m.get("size", 0) for m in self._meta.values())
        return {
            "enabled": True,
            "cache_dir": str(self.cache_dir),
            "entries": len(self._meta),
            "total_mb": round(total_bytes / 1_048_576, 2),
            "ttl_seconds": self.ttl,
            "sharded": self.sharded,
        }

    @staticmethod
    def sharded_paths(
        key: str,
        namespace: str,
        *,
        suffix: str = ".png",
    ) -> tuple[Path, str]:
        """Return (absolute_path, relative_url) for a sharded media layout.

        Convenience method for the OG-image pattern where files live at::

            MEDIA_ROOT/<namespace>/<key[:2]>/<key[2:4]>/<key><suffix>

        and are served as::

            /media/<namespace>/<key[:2]>/<key[2:4]>/<key><suffix>

        Requires Django to be configured (reads ``settings.MEDIA_ROOT`` /
        ``settings.MEDIA_URL`` lazily at call time).
        """
        from django_cfg.core.utils.paths import get_media_path, get_media_url

        shard_a, shard_b = key[:2], key[2:4]
        filename = f"{key}{suffix}"
        abs_path = get_media_path(namespace, shard_a, shard_b, filename)
        rel_url = get_media_url(namespace, shard_a, shard_b, filename)
        return abs_path, rel_url

    # -- internals ----------------------------------------------------------

    def _file_path(self, key: str, suffix: str) -> Path:
        filename = f"{key}{suffix}"
        if self.sharded:
            return self.cache_dir / key[:2] / key[2:4] / filename
        return self.cache_dir / filename

    def _is_expired(self, key: str) -> bool:
        if self.ttl == 0:
            return False
        entry = self._meta.get(key)
        if entry is None:
            return True
        return (time.time() - entry.get("created_at", 0)) > self.ttl

    def _meta_path(self) -> Path:
        return self.cache_dir / self._METADATA_FILE

    def _load_meta(self) -> dict[str, dict[str, Any]]:
        path = self._meta_path()
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text("utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("FileCache: failed to load metadata: %s", exc)
            return {}

    def _save_meta(self) -> None:
        try:
            self._meta_path().write_text(
                json.dumps(self._meta, ensure_ascii=False, indent=2), "utf-8"
            )
        except OSError as exc:
            logger.warning("FileCache: failed to save metadata: %s", exc)


# ---------------------------------------------------------------------------
# LazyFileResource
# ---------------------------------------------------------------------------

class LazyFileResource:
    """Download-once remote resource stored at a local path.

    On first call to :meth:`resolve` the file is downloaded from *url* and
    saved to *dest*.  All subsequent calls return *dest* immediately.

    Supports background pre-fetching via :meth:`prefetch` — starts a daemon
    thread so Django startup is never blocked.

    Args:
        url:      Remote URL to download from.
        dest:     Local ``Path`` where the file will be stored.
        fallback: Optional local path to return if *dest* is missing
                  and the download fails.
        timeout:  HTTP request timeout in seconds (default: 30).
    """

    def __init__(
        self,
        url: str,
        dest: Path,
        *,
        fallback: Path | None = None,
        timeout: int = 30,
    ) -> None:
        self.url = url
        self.dest = Path(dest)
        self.fallback = Path(fallback) if fallback else None
        self.timeout = timeout
        self._lock = __import__("threading").Lock()

    def resolve(self) -> Path:
        """Return the local path, downloading synchronously if necessary.

        Returns fallback if download fails and fallback exists.
        Raises ``RuntimeError`` only if both download and fallback are unavailable.
        """
        if self.dest.exists():
            return self.dest

        with self._lock:
            # re-check after acquiring lock (another thread may have downloaded)
            if self.dest.exists():
                return self.dest
            return self._download()

    def prefetch(self) -> None:
        """Start a background daemon thread to download the resource.

        Safe to call at Django startup — never blocks the main thread.
        The file will be ready by the time it is first needed.
        """
        if self.dest.exists():
            return
        import threading
        t = threading.Thread(target=self._download_safe, daemon=True, name=f"prefetch:{self.dest.name}")
        t.start()

    def is_cached(self) -> bool:
        """Return ``True`` if the local file already exists."""
        return self.dest.exists()

    def evict(self) -> bool:
        """Delete the local file so it will be re-downloaded on next :meth:`resolve`."""
        if self.dest.exists():
            self.dest.unlink()
            return True
        return False

    # -- internals ----------------------------------------------------------

    def _download(self) -> Path:
        logger.info("LazyFileResource: downloading %s → %s", self.url, self.dest)
        try:
            self.dest.parent.mkdir(parents=True, exist_ok=True)
            # Use certifi SSL context if available (needed on macOS stock Python)
            try:
                import ssl
                import certifi
                ctx = ssl.create_default_context(cafile=certifi.where())
                opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
                with opener.open(self.url, timeout=self.timeout) as resp:  # noqa: S310
                    self.dest.write_bytes(resp.read())
            except ImportError:
                urllib.request.urlretrieve(self.url, self.dest)  # noqa: S310
            logger.debug("LazyFileResource: saved %s (%d bytes)", self.dest, self.dest.stat().st_size)
            return self.dest
        except Exception as exc:  # noqa: BLE001
            logger.warning("LazyFileResource: download failed for %s: %s", self.url, exc)
            # clean up partial file
            if self.dest.exists():
                try:
                    self.dest.unlink()
                except OSError:
                    pass
            if self.fallback and self.fallback.exists():
                logger.warning("LazyFileResource: using fallback %s", self.fallback)
                return self.fallback
            raise RuntimeError(
                f"Could not obtain resource {self.url!r} — "
                f"download failed and no fallback is available."
            ) from exc

    def _download_safe(self) -> None:
        """Like _download but swallows all exceptions (for background threads)."""
        try:
            self._download()
        except Exception as exc:  # noqa: BLE001
            logger.warning("LazyFileResource: background prefetch failed for %s: %s", self.url, exc)


__all__ = ["CacheKey", "FileCache", "LazyFileResource"]
