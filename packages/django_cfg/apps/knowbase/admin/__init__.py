"""
Knowledge Base Admin Configuration

Refactored admin interfaces using Django-CFG admin system.
"""

from .document_admin import *
from .chat_admin import *
from .archive_admin import *
from .external_data_admin import *

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
