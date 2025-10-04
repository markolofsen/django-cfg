"""
Knowledge Base App Configuration
"""

from django.apps import AppConfig
from django.db.models.signals import post_migrate


class KnowbaseConfig(AppConfig):
    """Knowledge Base application configuration."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_cfg.apps.knowbase'
    label = 'django_cfg_knowbase'
    verbose_name = 'Django CFG Knowledge Base'
    
    def ready(self):
        """Initialize app when Django starts."""
        # Import signals to register them
        from . import signals
        
        # Connect post-migrate signal for database setup
        post_migrate.connect(self.create_pgvector_extension, sender=self)
        
        # Initialize task system and auto-start worker if configured
        try:
            from django_cfg.modules.django_tasks import initialize_task_system
            initialize_task_system()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to initialize task system: {e}")
    
    def create_pgvector_extension(self, sender, **kwargs):
        """Create pgvector extension and indexes if they don't exist."""
        from django.db import connection
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            with connection.cursor() as cursor:
                # Create extensions
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")  # For text search
                logger.info("✅ pgvector extensions created/verified")
                
                # Create vector index for cosine similarity if table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'django_cfg_knowbase_document_chunks'
                    );
                """)
                table_exists = cursor.fetchone()[0]
                
                if table_exists:
                    # Check if index already exists
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM pg_indexes 
                            WHERE indexname = 'embedding_cosine_idx'
                        );
                    """)
                    index_exists = cursor.fetchone()[0]
                    
                    if not index_exists:
                        cursor.execute("""
                            CREATE INDEX CONCURRENTLY IF NOT EXISTS embedding_cosine_idx 
                            ON django_cfg_knowbase_document_chunks 
                            USING ivfflat (embedding vector_cosine_ops) 
                            WITH (lists = 100);
                        """)
                        logger.info("✅ Created embedding_cosine_idx index")
                    else:
                        logger.debug("✅ embedding_cosine_idx index already exists")
                else:
                    logger.debug("⏳ django_cfg_knowbase_document_chunks table not yet created, skipping index creation")
                    
        except Exception as e:
            # Log warning but don't fail - extension/index might already exist
            logger.warning(f"Could not create pgvector extension/indexes: {e}")