"""
Django SaaS Knowledge Assistant

Enterprise-grade RAG (Retrieval-Augmented Generation) application built on Django 5.2
with pgvector semantic search, Dramatiq background processing, and comprehensive
API endpoints for document management and AI-powered chat.

Key Features:
- Document ingestion with automatic chunking and embedding generation
- Semantic search using pgvector cosine similarity
- RAG-powered chat with context retrieval
- Multi-tenant user isolation
- Background processing with Dramatiq
- Cost tracking for LLM usage monitoring
- Comprehensive admin interface with Unfold styling
- Type-safe APIs with Pydantic v2 validation
- Full test coverage

Architecture:
- Models: Document, DocumentChunk, ChatSession, ChatMessage
- Services: DocumentService, ChatService, SearchService
- Tasks: Async document processing, maintenance, optimization
- APIs: REST endpoints with DRF and OpenAPI documentation
- Admin: Unfold-optimized interfaces with statistics
"""

default_app_config = 'django_cfg.apps.knowbase.apps.KnowbaseConfig'
