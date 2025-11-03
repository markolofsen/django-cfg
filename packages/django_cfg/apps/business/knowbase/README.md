# Django CFG Knowledge Base

Enterprise-grade RAG (Retrieval-Augmented Generation) application built on Django with pgvector semantic search, Dramatiq background processing, and comprehensive API endpoints for document management and AI-powered chat.

## Features

- 📄 **Document Management**: Upload, process, and manage documents with automatic chunking
- 🔍 **Semantic Search**: pgvector-powered cosine similarity search
- 🤖 **AI Chat**: RAG-powered conversational interface with context retrieval
- 👥 **Multi-tenant**: Complete user isolation and access control
- ⚡ **Background Processing**: Async document processing with Dramatiq
- 💰 **Cost Tracking**: Monitor LLM usage and costs
- 🎨 **Admin Interface**: Beautiful Unfold-styled admin with statistics
- 🔒 **Type Safety**: Pydantic v2 validation throughout
- ✅ **Full Testing**: Comprehensive test coverage

## Quick Start

### 1. Enable in Configuration

```python
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    enable_knowbase: bool = True
    
    # Required for AI features
    openai_api_key: str = "${OPENAI_API_KEY}"
    
    # Optional: Configure similarity thresholds
    knowbase_document_threshold: float = 0.7
    knowbase_archive_threshold: float = 0.6
```

### 2. Add to INSTALLED_APPS

```python
INSTALLED_APPS = [
    # ... other apps
    'django_cfg.apps.knowbase',
]
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Start Using

The Knowledge Base will be available at `/cfg/knowbase/` with:

- **Admin Interface**: Document and chat management
- **API Endpoints**: RESTful API for integration
- **Chat Interface**: AI-powered conversational search

## Architecture

### Models
- **Document**: File storage and metadata
- **DocumentChunk**: Text chunks with embeddings
- **ChatSession**: Conversation management
- **ChatMessage**: Individual messages with context

### Services
- **DocumentService**: Document processing and management
- **ChatService**: AI chat with RAG capabilities
- **SearchService**: Semantic search across all content types

### Background Tasks
- Document processing and vectorization
- Embedding generation and optimization
- Maintenance and cleanup tasks

## Configuration Options

```python
class MyConfig(DjangoConfig):
    # Enable/disable the app
    enable_knowbase: bool = True
    
    # AI Configuration
    openai_api_key: str = "${OPENAI_API_KEY}"
    
    # Search Thresholds
    knowbase_document_threshold: float = 0.7  # Document similarity
    knowbase_archive_threshold: float = 0.6   # Code similarity
    
    # Processing Settings
    knowbase_chunk_size: int = 1000           # Text chunk size
    knowbase_overlap_size: int = 200          # Chunk overlap
    knowbase_batch_size: int = 50             # Embedding batch size
```

## API Usage

### Document Upload

```python
import requests

response = requests.post('/cfg/knowbase/api/documents/', {
    'title': 'My Document',
    'file': open('document.pdf', 'rb')
})
```

### Chat Query

```python
response = requests.post('/cfg/knowbase/api/chat/sessions/{session_id}/query/', {
    'query': 'What is machine learning?',
    'max_tokens': 500
})
```

### Search Documents

```python
response = requests.get('/cfg/knowbase/api/search/', {
    'query': 'artificial intelligence',
    'limit': 10
})
```

## Integration with External Apps

The Knowledge Base supports integration with external Django apps through the `ExternalDataMixin`:

```python
from django_cfg.apps.knowbase.mixins import ExternalDataMixin

class MyModel(ExternalDataMixin, models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    # That's it! Auto AI integration enabled
```

## Requirements

- **PostgreSQL** with pgvector extension
- **Redis** for Dramatiq task queue
- **OpenAI API Key** for embeddings and chat
- **Python 3.11+** and **Django 5.0+**

## License

Part of Django CFG - MIT License