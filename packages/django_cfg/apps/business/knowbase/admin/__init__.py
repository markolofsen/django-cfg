"""
Knowledge Base Admin Configuration

Refactored admin interfaces using Django-CFG admin system.
"""

from .archive_admin import (
    ArchiveItemAdmin,
    ArchiveItemChunkAdmin,
    DocumentArchiveAdmin,
)
from .chat_admin import (
    ChatMessageAdmin,
    ChatSessionAdmin,
)
from .document_admin import (
    DocumentAdmin,
    DocumentCategoryAdmin,
    DocumentChunkAdmin,
)
from .external_data_admin import (
    ExternalDataAdmin,
    ExternalDataChunkAdmin,
)

__all__ = [
    'DocumentCategoryAdmin',
    'DocumentAdmin',
    'DocumentChunkAdmin',
    'DocumentArchiveAdmin',
    'ArchiveItemAdmin',
    'ArchiveItemChunkAdmin',
    'ExternalDataAdmin',
    'ExternalDataChunkAdmin',
    'ChatSessionAdmin',
    'ChatMessageAdmin',
]
