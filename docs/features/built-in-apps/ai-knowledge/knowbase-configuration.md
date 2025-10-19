---
title: Knowledge Base Configuration
description: Django-CFG knowbase configuration feature guide. Production-ready knowledge base configuration with built-in validation, type safety, and seamless Django integr
sidebar_label: Configuration
sidebar_position: 2
keywords:
  - django-cfg knowbase configuration
  - django knowbase configuration
  - knowbase configuration django-cfg
---
# Knowledge Base Configuration


## Overview

Django CFG Knowbase is an enterprise-grade **RAG (Retrieval-Augmented Generation)** application that transforms your Django project into an intelligent knowledge management system. Built with modern AI technologies, it provides semantic search, document processing, and conversational AI capabilities out-of-the-box.

**Philosophy**: Zero-configuration AI integration that "just works" - enable one setting and get a complete knowledge management system with semantic search, document processing, and AI chat capabilities.

**TAGS**: `rag, ai, semantic-search, document-management, chat-ai, django-cfg, pgvector, openai`

---

## Modules

### @django_cfg.apps.knowbase

**Purpose**:
Complete AI-powered knowledge management system with document processing, semantic search, and conversational AI.

**Dependencies**:
- `PostgreSQL` with `pgvector` extension
- `Redis` for caching and task queues
- `Dramatiq` for background processing
- `OpenAI API` for embeddings and chat
- `Django 5.0+` with `django-cfg`

**Exports**:
- `Document` - File storage and processing
- `ChatSession` - Conversational AI sessions
- `ExternalData` - External system integration
- `ExternalDataMixin` - Auto-AI integration for models
- `SearchService` - Unified semantic search
- `ChatService` - AI chat with context retrieval

**Used in**:
- Document management systems
- Customer support platforms
- Internal knowledge bases
- API documentation systems
- Code repositories with AI search

**Tags**: `core, ai, rag, semantic-search, document-processing`

---

### @knowbase/mixins/ExternalDataMixin

**Purpose**:
"Out-of-the-box" AI integration for any Django model. Add one line to your model and get automatic vectorization, semantic search, and AI chat capabilities.

**Dependencies**:
- `django_cfg.apps.knowbase.models.ExternalData`
- Django signals system
- Background task processing

**Exports**:
- `ExternalDataMixin` - Model mixin for auto-AI integration

**Used in**:
- Product catalogs
- User profiles
- Content management
- Any Django model requiring AI search

**Tags**: `mixin, auto-integration, vectorization, signals`

---

## Usage Examples

### Auto-AI Integration for Models

```python
from django_cfg.apps.knowbase.mixins import ExternalDataMixin

class Product(ExternalDataMixin, models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class ExternalDataMeta:
        watch_fields = ['name', 'description']  # Fields to monitor
        similarity_threshold = 0.4              # Search sensitivity
        auto_sync = True                        # Auto-update on changes
    
    def get_external_content(self):
        return f"# {self.name}\n\nPrice: ${self.price}\n\n{self.description}"
```

### Document Upload and Processing

```python
from django_cfg.apps.knowbase.services import DocumentService

# Upload document
service = DocumentService(user=request.user)
document = service.upload_document(
    title="API Documentation",
    file=uploaded_file,
    is_public=False
)

# Document is automatically processed in background
# - Text extraction
# - Chunking
# - Embedding generation
# - Vector storage
```

### AI Chat with Context Retrieval

```python
from django_cfg.apps.knowbase.services import ChatService

# Create chat session
chat_service = ChatService(user=request.user)
session = chat_service.create_session(title="Product Questions")

# Query with automatic context retrieval
response = chat_service.process_query(
    session_id=session.id,
    query="What products do we have under $100?",
    max_context_chunks=5,
    max_tokens=500
)

print(response.content)  # AI response with product context
```

### Semantic Search Across All Content

```python
from django_cfg.apps.knowbase.services import SearchService

# Search across documents, external data, and archives
search_service = SearchService(user=request.user)
results = search_service.search_all_content(
    query="machine learning algorithms",
    limit=10,
    similarity_threshold=0.7
)

for result in results:
    print(f"{result.title}: {result.content_preview}")
```

---

## Data Models (Pydantic 2 & TypeScript)

### Pydantic 2 Models (Backend)

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class ExternalDataType(str, Enum):
    MODEL = "model"
    API = "api"
    CUSTOM = "custom"

class ExternalDataStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ExternalDataCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    content: str = Field(..., min_length=1)
    source_type: ExternalDataType = ExternalDataType.CUSTOM
    source_config: Optional[dict] = None
    similarity_threshold: float = Field(0.5, ge=0.0, le=1.0)
    is_public: bool = False
    tags: List[str] = Field(default_factory=list)

class ChatQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    max_tokens: int = Field(500, ge=1, le=4000)
    max_context_chunks: int = Field(5, ge=1, le=20)
    temperature: float = Field(0.7, ge=0.0, le=2.0)

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(10, ge=1, le=100)
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0)
    content_types: List[str] = Field(default_factory=lambda: ["document", "external", "archive"])
```

### TypeScript Interfaces (Frontend)

```typescript
// External Data Types
export enum ExternalDataType {
  MODEL = "model",
  API = "api",
  CUSTOM = "custom"
}

export enum ExternalDataStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed"
}

export interface ExternalDataCreate {
  title: string;
  description?: string;
  content: string;
  source_type: ExternalDataType;
  source_config?: Record<string, any>;
  similarity_threshold: number;
  is_public: boolean;
  tags: string[];
}

// Chat Interface Types
export interface ChatQueryRequest {
  query: string;
  max_tokens: number;
  max_context_chunks: number;
  temperature: number;
}

export interface ChatResponse {
  content: string;
  context_chunks: ContextChunk[];
  token_usage: TokenUsage;
  processing_time: number;
}

// Search Types
export interface SearchRequest {
  query: string;
  limit: number;
  similarity_threshold: number;
  content_types: string[];
}

export interface SearchResult {
  id: string;
  title: string;
  content_preview: string;
  similarity_score: number;
  content_type: string;
  metadata: Record<string, any>;
}
```

---

## 🔁 Flows

### Document Processing Flow

1. **Upload** → User uploads document via API or admin interface
2. **Validation** → File type, size, and content validation
3. **Background Task** → Dramatiq task queued for processing
4. **Text Extraction** → Extract text from PDF, DOCX, TXT, etc.
5. **Chunking** → Split text into semantic chunks with overlap
6. **Embedding Generation** → Generate vector embeddings via OpenAI
7. **Vector Storage** → Store embeddings in PostgreSQL with pgvector
8. **Index Update** → Update search indexes for fast retrieval

**Modules**:
- `DocumentService` - orchestrates the flow
- `ExtractionService` - handles file processing
- `ChunkingService` - text segmentation
- `EmbeddingService` - vector generation
- `VectorizationService` - database storage

---

### AI Chat with Context Retrieval Flow

1. **Query Received** → User sends chat message
2. **Query Embedding** → Generate embedding for user query
3. **Semantic Search** → Find relevant content chunks using cosine similarity
4. **Context Assembly** → Combine top matching chunks into context
5. **Prompt Building** → Create structured prompt with context and query
6. **LLM Request** → Send to OpenAI with context and conversation history
7. **Response Processing** → Parse and validate LLM response
8. **Storage** → Save query and response to chat session

**Modules**:
- `ChatService` - main orchestration
- `SearchService` - semantic search
- `PromptBuilder` - context assembly
- `LLMClient` - AI communication

---

### Auto-AI Integration Flow (ExternalDataMixin)

1. **Model Save** → Django model with mixin is saved
2. **Signal Trigger** → post_save signal detects changes
3. **Change Detection** → Compare watched fields for modifications
4. **Content Generation** → Call model's `get_external_content()` method
5. **ExternalData Creation** → Create or update ExternalData record
6. **Background Processing** → Queue vectorization task
7. **Embedding Update** → Generate new embeddings for updated content
8. **Search Index** → Update semantic search indexes

**Modules**:
- `ExternalDataMixin` - model integration
- `ExternalDataSignals` - change detection
- `ExternalDataService` - processing logic
- `ExternalDataTasks` - background jobs

---

## Philosophy & Design Principles

### Zero-Configuration AI

**Principle**: AI capabilities should be as easy to add as `enable_knowbase: bool = True`

- **No complex setup** - One configuration flag enables everything
- **Automatic discovery** - System finds and processes content automatically  
- **Intelligent defaults** - Sensible settings that work for 90% of use cases
- **Progressive enhancement** - Start simple, customize as needed

### Content-Agnostic Intelligence

**Principle**: The system should work with any type of content without manual configuration

- **Universal processing** - Documents, code, structured data, APIs
- **Automatic chunking** - Smart text segmentation based on content type
- **Adaptive thresholds** - Different similarity thresholds for different content types
- **Unified search** - Single interface to search across all content types

### Production-First Architecture

**Principle**: Built for real-world production environments from day one

- **Async processing** - Never block user requests with heavy operations
- **Cost optimization** - Token counting, response caching, batch processing
- **Error resilience** - Graceful degradation and automatic retries
- **Monitoring ready** - Built-in metrics, logging, and admin interfaces

### Developer Experience Focus

**Principle**: Make AI integration feel natural and Django-like

- **Familiar patterns** - Uses Django conventions (models, signals, admin)
- **Type safety** - 100% typed with Pydantic v2 throughout
- **Clear abstractions** - Service layer separates business logic
- **Comprehensive testing** - Full test coverage for confidence

---

## ⚠️ Anti-patterns to Avoid

### ❌ Manual Embedding Management

**Don't do this**:
```python
# Manual embedding generation - fragile and error-prone
embedding = openai.embeddings.create(input=text)
vector = embedding.data[0].embedding
ExternalDataChunk.objects.create(vector=vector, content=text)
```

**Do this instead**:
```python
# Use the service layer - handles batching, errors, retries
service = ExternalDataService(user=user)
service.create_external_data(title="My Data", content=text)
```

### ❌ Synchronous Processing

**Don't do this**:
```python
# Blocking request while processing large documents
def upload_document(request):
    document = Document.objects.create(file=request.FILES['file'])
    process_document_immediately(document)  # Blocks for minutes!
    return JsonResponse({'status': 'success'})
```

**Do this instead**:
```python
# Async processing with status tracking
def upload_document(request):
    document = Document.objects.create(file=request.FILES['file'])
    process_document_async.send(document.id)  # Background task
    return JsonResponse({'status': 'processing', 'id': document.id})
```

### ❌ Hardcoded Similarity Thresholds

**Don't do this**:
```python
# Fixed threshold doesn't work for all content types
results = search_service.search(query, similarity_threshold=0.7)
```

**Do this instead**:
```python
# Use content-type specific thresholds
results = search_service.search_all_content(query)  # Auto-selects thresholds
```

### ❌ Ignoring Token Costs

**Don't do this**:
```python
# Unlimited context can be expensive
response = chat_service.query(
    query=user_query,
    max_context_chunks=50,  # Could be thousands of tokens!
    max_tokens=4000
)
```

**Do this instead**:
```python
# Reasonable defaults with cost awareness
response = chat_service.query(
    query=user_query,
    max_context_chunks=5,   # Usually sufficient
    max_tokens=500          # Focused responses
)
```

---

## Version Tracking

- `ADDED_IN: v1.0` - Initial release with document processing and chat
- `ADDED_IN: v1.1` - External data system and auto-integration mixin
- `ADDED_IN: v1.2` - Archive system for code repositories
- `CHANGED_IN: v1.3` - Optimized batch embedding processing (7x performance improvement)
- `ADDED_IN: v1.4` - Per-object similarity thresholds
- `ADDED_IN: v1.5` - Django CFG integration and auto-configuration

---

## Quick Start Checklist

### Prerequisites

- [ ] **PostgreSQL** with `pgvector` extension installed
- [ ] **Redis** server running for caching and task queues  
- [ ] **OpenAI API Key** with sufficient credits
- [ ] **Django 5.0+** with `django-cfg` installed

### Setup Steps

1. **Enable in Configuration**
   ```python
   class MyConfig(DjangoConfig):
       enable_knowbase: bool = True
       openai_api_key: str = env.openai_api_key  # From YAML config
   ```

2. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

3. **Start Background Workers**
   ```bash
   python manage.py rundramatiq
   ```

4. **Access Admin Interface**
   - Navigate to `/admin/` 
   - Look for "Knowledge Base" section
   - Upload your first document

5. **Test AI Chat**
   - Go to `/cfg/knowbase/chat/`
   - Ask questions about your uploaded content
   - Experience semantic search in action

### Verification

- [ ] Documents upload and process successfully
- [ ] Chat responses include relevant context
- [ ] Search finds semantically similar content
- [ ] Background tasks complete without errors
- [ ] Admin interface shows processing statistics

---

## Website Integration

### Marketing Content
- **[Homepage Features](/getting-started/intro)** - AI capabilities showcase
- **[Features Overview](/getting-started/intro)** - Complete knowbase features
- **[Real-World Examples](/guides/production-config)** - Production implementations
- **[Getting Started](/getting-started/intro)** - Quick setup guide

### SEO Keywords
- **Primary**: "Django AI integration", "Django RAG system", "Django semantic search"
- **Long-tail**: "How to add AI to Django", "Django vector database", "Django knowledge management"
- **Technical**: "Django pgvector setup", "Django OpenAI integration", "Django embeddings"

---

**NEXT**: See implementation examples in `/guides/` directory and detailed API documentation at `/cfg/knowbase/api/docs/`

**DEPENDS_ON**: [Django 5.0+, PostgreSQL, pgvector, Redis, OpenAI API, django-cfg]  
**USED_BY**: [Document management, Customer support, API documentation, Code search, Website marketing]  
**TAGS**: `rag, ai, semantic-search, django-cfg, production-ready, website-content`
