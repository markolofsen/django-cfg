"""
Maintenance and cleanup tasks.
"""

import dramatiq
import logging
from typing import Dict, Any
from django.db import connection
from django.utils import timezone
from datetime import timedelta
from django_cfg.modules.django_llm.llm.client import LLMClient
from django.core.cache import cache
from django.conf import settings

from ..models import Document, DocumentChunk, ProcessingStatus

logger = logging.getLogger(__name__)


@dramatiq.actor(
    queue_name="knowbase",
    max_retries=1,
    priority=2
)
def cleanup_old_embeddings(days_old: int = 90) -> Dict[str, Any]:
    """
    Clean up old, unused embeddings and optimize storage.
    
    Args:
        days_old: Age threshold for cleanup
        
    Returns:
        Cleanup statistics
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=days_old)
        
        # Find orphaned chunks (documents deleted but chunks remain)
        orphaned_chunks = DocumentChunk.objects.filter(
            document__isnull=True
        )
        orphaned_count = orphaned_chunks.count()
        orphaned_chunks.delete()
        
        # Find very old, unused chunks
        old_chunks = DocumentChunk.objects.filter(
            created_at__lt=cutoff_date,
            document__processing_status=ProcessingStatus.FAILED
        )
        old_count = old_chunks.count()
        old_chunks.delete()
        
        # Vacuum and analyze tables
        with connection.cursor() as cursor:
            cursor.execute("VACUUM ANALYZE django_cfg_knowbase_document_chunks;")
            cursor.execute("VACUUM ANALYZE django_cfg_knowbase_documents;")
        
        result = {
            "orphaned_chunks_deleted": orphaned_count,
            "old_chunks_deleted": old_count,
            "total_deleted": orphaned_count + old_count,
            "cutoff_date": cutoff_date.isoformat(),
            "timestamp": timezone.now().isoformat()
        }
        
        logger.info(f"Cleanup completed: {result}")
        return result
        
    except Exception as exc:
        logger.error(f"Cleanup failed: {exc}")
        raise


@dramatiq.actor(
    queue_name="knowbase",
    max_retries=1,
    priority=1
)
def optimize_vector_indexes() -> Dict[str, Any]:
    """
    Optimize pgvector indexes for better performance.
    
    Returns:
        Optimization results
    """
    try:
        with connection.cursor() as cursor:
            # Reindex vector indexes (match model definition)
            cursor.execute("REINDEX INDEX CONCURRENTLY embedding_cosine_idx;")
            
            # Update table statistics
            cursor.execute("ANALYZE django_cfg_knowbase_document_chunks;")
            
            # Get index usage statistics
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes 
                WHERE tablename = 'django_cfg_knowbase_document_chunks';
            """)
            
            index_stats = cursor.fetchall()
        
        logger.info("Vector indexes optimized successfully")
        
        return {
            "status": "optimized",
            "index_stats": index_stats,
            "timestamp": timezone.now().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Index optimization failed: {exc}")
        raise


@dramatiq.actor(
    queue_name="knowbase",
    max_retries=1,
    priority=1
)
def health_check_knowledge_base() -> Dict[str, Any]:
    """
    Perform health check on knowledge base components.
    
    Returns:
        Health check results
    """
    try:
        health_status = {
            "timestamp": timezone.now().isoformat(),
            "database": "unknown",
            "embeddings": "unknown",
            "llm_service": "unknown",
            "redis_cache": "unknown",
            "statistics": {}
        }
        
        # Check database connectivity
        try:
            total_docs = Document.objects.count()
            total_chunks = DocumentChunk.objects.count()
            
            health_status["database"] = "healthy"
            health_status["statistics"]["total_documents"] = total_docs
            health_status["statistics"]["total_chunks"] = total_chunks
        except Exception:
            health_status["database"] = "unhealthy"
        
        # Check LLM service
        try:
            llm_service = LLMClient(
                apikey_openrouter=settings.api_keys.openrouter,
                apikey_openai=settings.api_keys.openai
            )
            if hasattr(llm_service, 'is_configured') and llm_service.is_configured:
                health_status["llm_service"] = "healthy"
            elif settings.api_keys.openrouter:
                health_status["llm_service"] = "healthy"
            else:
                health_status["llm_service"] = "not_configured"
        except Exception:
            health_status["llm_service"] = "unhealthy"
        
        # Check Redis cache
        try:
            cache.set("health_check", "ok", 10)
            if cache.get("health_check") == "ok":
                health_status["redis_cache"] = "healthy"
            else:
                health_status["redis_cache"] = "unhealthy"
        except Exception:
            health_status["redis_cache"] = "unhealthy"
        
        # Overall health
        health_status["overall"] = (
            "healthy" if all(
                status == "healthy" for status in [
                    health_status["database"],
                    health_status["llm_service"],
                    health_status["redis_cache"]
                ]
            ) else "degraded"
        )
        
        logger.info(f"Health check completed: {health_status['overall']}")
        return health_status
        
    except Exception as exc:
        logger.error(f"Health check failed: {exc}")
        raise
