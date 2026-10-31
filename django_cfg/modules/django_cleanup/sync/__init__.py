"""
Storage delete sync: owned-file registry, guard, outbox worker, CDN purge.

Importing this package never touches models; `worker`, `metrics` and `tasks`
import them inside functions so the package is safe to import before the app
registry is ready.
"""

from .owned import OwnedFiles, clear_registry, owned_entries, register_owned_files

__all__ = ["OwnedFiles", "register_owned_files", "owned_entries", "clear_registry"]
