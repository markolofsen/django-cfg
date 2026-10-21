"""
Development media storage: local writes, remote URLs for files not on disk.

Selected outside production when `StorageConfig.backend` is declared with a
`custom_domain`. A dev database restored from a production dump then still
shows its media, while nothing in dev can write to or delete from the bucket.
"""

from typing import Any, Optional
from urllib.parse import urljoin

from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible
from django.utils.encoding import filepath_to_uri


@deconstructible(path="django_cfg.core.backends.storage.LocalStorageWithRemoteURLs")
class LocalStorageWithRemoteURLs(FileSystemStorage):
    """
    FileSystemStorage whose `url()` points at the remote for missing files.

    Only `url()` falls back. `open()`, `exists()`, `size()`, `delete()` and
    every write stay on local disk, so the bucket is never fetched or touched.
    """

    def __init__(self, remote_base_url: Optional[str] = None, **kwargs: Any):
        super().__init__(**kwargs)
        # Public prefix the production backend serves the same names under.
        self.remote_base_url = remote_base_url

    def url(self, name: Optional[str]) -> str:
        if name and self.remote_base_url and not self.exists(name):
            url = filepath_to_uri(name).lstrip("/")
            return urljoin(self.remote_base_url, url)
        return super().url(name)


__all__ = ["LocalStorageWithRemoteURLs"]
