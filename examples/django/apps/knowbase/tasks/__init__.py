"""
Knowledge Base Background Tasks

Dramatiq tasks for document processing and maintenance.
"""

from .document_processing import *
from .maintenance import *
from .archive_tasks import *
from .external_data_tasks import *


__all__ = [
    # Document processing
    'process_document_async',
    'reprocess_document_chunks',
    'generate_embeddings_batch',
    
    # Archive processing
    'process_archive_task',
    'vectorize_archive_items_task',
    'cleanup_failed_archives_task',
    'generate_archive_statistics_task',
    'archive_health_check_task',
    'test_archive_task',
    
    # External data processing
    'process_external_data_async',
    'bulk_process_external_data_async',
    'cleanup_failed_external_data_async',
    
    # Maintenance
    'cleanup_old_embeddings',
    'optimize_vector_indexes',
    'health_check_knowledge_base',
    
    # Test tasks
    'test_simple_task',
]
