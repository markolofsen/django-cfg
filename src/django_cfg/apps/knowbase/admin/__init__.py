"""
Knowledge Base Admin Configuration

Unfold-optimized admin interfaces for knowledge management.
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
