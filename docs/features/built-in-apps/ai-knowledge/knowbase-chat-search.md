---
title: Chat and Search
description: Django-CFG knowbase chat search feature guide. Production-ready chat and search with built-in validation, type safety, and seamless Django integration.
sidebar_label: Chat & Search
sidebar_position: 3
keywords:
  - django-cfg knowbase chat search
  - django knowbase chat search
  - knowbase chat search django-cfg
---
# AI Chat & Semantic Search - Conversational Knowledge Retrieval

## Overview

Knowbase provides enterprise-grade conversational AI with semantic search capabilities. Users can chat naturally with their knowledge base, and the system automatically retrieves relevant context from documents, external data, and code archives.

**Philosophy**: "Ask anything, get intelligent answers" - Natural language queries that understand context, intent, and relationships across all your content types.

**TAGS**: `ai-chat, semantic-search, rag, conversational-ai, context-retrieval, openai`

---

## Modules

### @knowbase/services/ChatService

**Purpose**:
Conversational AI service with automatic context retrieval from semantic search across all content types.

**Dependencies**:
- `SearchService` - semantic search across content
- `PromptBuilder` - context assembly and prompt engineering
- `LLMClient` - OpenAI API integration
- `ChatSession`, `ChatMessage` models

**Exports**:
- `ChatService` - main chat orchestration
- `create_session()` - start new conversations
- `process_query()` - handle user queries with context
- `get_conversation_history()` - retrieve chat history

**Used in**:
- Customer support interfaces
- Internal knowledge portals
- API documentation systems
- Code exploration tools

**Tags**: `chat, rag, context-retrieval, conversation-management`


---

### @knowbase/services/SearchService

**Purpose**:
Unified semantic search across documents, external data, and code archives using pgvector cosine similarity.

**Dependencies**:
- `pgvector` - vector similarity search
- `Document`, `ExternalData`, `ArchiveItem` models
- `EmbeddingService` - query embedding generation
- Content-specific similarity thresholds

**Exports**:
- `SearchService` - unified search interface
- `search_all_content()` - cross-content search
- `search_documents()` - document-specific search
- `search_external_data()` - external data search
- `search_archives()` - code archive search

**Used in**:
- Chat context retrieval
- Search interfaces
- Content discovery
- Related content suggestions

**Tags**: `semantic-search, pgvector, cosine-similarity, unified-search`


---



### Advanced Chat Configuration

```python
# Custom system prompt and settings
session = chat_service.create_session(
    title="Technical Support",
    system_prompt="""You are a technical support expert. 
    Always provide step-by-step solutions and ask clarifying questions 
    when the user's problem is unclear.""",
    max_messages=50,       # Conversation length limit
    auto_title=True        # Auto-generate titles from first query
)

# Query with specific content type filtering
response = chat_service.process_query(
    session_id=session.id,
    query="How do I configure the API authentication?",
    max_context_chunks=3,
    content_types=['document', 'external'],  # Exclude archives
    similarity_threshold=0.8,  # Higher precision
    include_metadata=True      # Include source metadata
)

# Access detailed response information
for chunk in response.context_chunks:
    print(f"Source: {chunk.source_title}")
    print(f"Relevance: {chunk.similarity_score:.3f}")
    print(f"Content: {chunk.content_preview}")
```

### Conversation Management

```python
# Get conversation history
history = chat_service.get_conversation_history(
    session_id=session.id,
    limit=20,              # Recent messages
    include_context=True   # Include context chunks
)

# Continue conversation with context
response = chat_service.process_query(
    session_id=session.id,
    query="Can you elaborate on the second point?",
    use_conversation_context=True,  # Use previous messages as context
    max_context_chunks=3
)

# Update session settings
chat_service.update_session(
    session_id=session.id,
    title="Updated Session Title",
    system_prompt="Updated system instructions"
)
```

## Search Service Usage

### Unified Content Search

```python
from django_cfg.apps.knowbase.services import SearchService

# Initialize search service
search_service = SearchService(user=request.user)

# Search across all content types
results = search_service.search_all_content(
    query="machine learning algorithms",
    limit=10,
    similarity_threshold=0.7,  # Auto-adjusted per content type
    include_metadata=True
)

# Process results
for result in results:
    print(f"Title: {result.title}")
    print(f"Type: {result.content_type}")
    print(f"Relevance: {result.similarity_score:.3f}")
    print(f"Preview: {result.content_preview}")
    print("---")
```

### Content-Specific Search

```python
# Search only documents
doc_results = search_service.search_documents(
    query="user authentication",
    limit=5,
    similarity_threshold=0.8,
    category_filter="api-docs"  # Optional category filtering
)

# Search external data (e.g., product catalog)
external_results = search_service.search_external_data(
    query="wireless headphones under $100",
    limit=10,
    similarity_threshold=0.6,
    metadata_filter={'category': 'electronics'}
)

# Search code archives
code_results = search_service.search_archives(
    query="authentication middleware",
    limit=8,
    similarity_threshold=0.7,
    file_type_filter=['.py', '.js']  # Specific file types
)
```

### Advanced Search Features

```python
# Hybrid search with keyword and semantic
results = search_service.hybrid_search(
    query="Django REST API authentication",
    semantic_weight=0.7,   # 70% semantic, 30% keyword
    limit=15
)

# Similar content discovery
similar_results = search_service.find_similar_content(
    content_id="doc_123",
    content_type="document",
    limit=5,
    exclude_self=True
)

# Search with date filtering
recent_results = search_service.search_all_content(
    query="new features",
    date_filter={
        'field': 'created_at',
        'after': '2024-01-01',
        'before': '2024-12-31'
    }
)
```

%%END%%
````

---

## Data Models (Pydantic 2 & TypeScript)

### Pydantic 2 Models (Backend)

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ChatQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    max_tokens: int = Field(500, ge=1, le=4000)
    max_context_chunks: int = Field(5, ge=1, le=20)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    content_types: List[str] = Field(default_factory=lambda: ["document", "external", "archive"])
    similarity_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    use_conversation_context: bool = True
    include_metadata: bool = False

class ContextChunk(BaseModel):
    content: str
    source_title: str
    source_type: str
    similarity_score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    content_preview: str = Field(..., max_length=200)

class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float

class ChatResponse(BaseModel):
    content: str
    context_chunks: List[ContextChunk]
    token_usage: TokenUsage
    processing_time: float
    session_id: str
    message_id: str

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(10, ge=1, le=100)
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0)
    content_types: List[str] = Field(default_factory=lambda: ["document", "external", "archive"])
    include_metadata: bool = False
    metadata_filter: Optional[Dict[str, Any]] = None

class SearchResult(BaseModel):
    id: str
    title: str
    content_type: str
    content_preview: str = Field(..., max_length=300)
    similarity_score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
```

### TypeScript Interfaces (Frontend)

```typescript
export interface ChatQueryRequest {
  query: string;
  max_tokens: number;
  max_context_chunks: number;
  temperature: number;
  content_types: string[];
  similarity_threshold?: number;
  use_conversation_context: boolean;
  include_metadata: boolean;
}

export interface ContextChunk {
  content: string;
  source_title: string;
  source_type: string;
  similarity_score: number;
  metadata: Record<string, any>;
  content_preview: string;
}

export interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  estimated_cost: number;
}

export interface ChatResponse {
  content: string;
  context_chunks: ContextChunk[];
  token_usage: TokenUsage;
  processing_time: number;
  session_id: string;
  message_id: string;
}

export interface SearchRequest {
  query: string;
  limit: number;
  similarity_threshold: number;
  content_types: string[];
  include_metadata: boolean;
  metadata_filter?: Record<string, any>;
}

export interface SearchResult {
  id: string;
  title: string;
  content_type: string;
  content_preview: string;
  similarity_score: number;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

// Chat session management
export interface ChatSession {
  id: string;
  title: string;
  system_prompt: string;
  message_count: number;
  total_tokens: number;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  context_chunks?: ContextChunk[];
  token_usage?: TokenUsage;
  created_at: string;
}
```

---

## 🔁 Flows

### AI Chat with Context Retrieval Flow

1. **User Query** → User sends message to chat session
2. **Query Embedding** → Generate vector embedding for user query
3. **Semantic Search** → Search across all content types using cosine similarity
4. **Context Ranking** → Rank results by relevance and content type
5. **Context Assembly** → Combine top chunks into structured context
6. **Prompt Building** → Create LLM prompt with context and conversation history
7. **LLM Request** → Send to OpenAI with optimized prompt
8. **Response Processing** → Parse and validate AI response
9. **Storage** → Save message and context to database
10. **Token Tracking** → Update usage statistics and costs

**Modules**:
- `ChatService.process_query()` - orchestrates entire flow
- `SearchService.search_all_content()` - context retrieval
- `PromptBuilder.build_chat_prompt()` - prompt engineering
- `LLMClient.chat_completion()` - AI communication

---

### Semantic Search Flow

1. **Query Input** → User enters search query
2. **Query Processing** → Clean and normalize query text
3. **Embedding Generation** → Create query vector embedding
4. **Multi-Content Search** → Search documents, external data, archives in parallel
5. **Similarity Calculation** → Calculate cosine similarity scores
6. **Threshold Filtering** → Apply content-type specific thresholds
7. **Result Ranking** → Combine and rank results across content types
8. **Metadata Enrichment** → Add source information and previews
9. **Response Assembly** → Format results for presentation

**Modules**:
- `SearchService.search_all_content()` - main orchestration
- `EmbeddingService.generate_query_embedding()` - vector generation
- Content-specific search methods for each type
- Result ranking and formatting utilities

---

### Conversation Context Flow

1. **Context Request** → System needs conversation context for query
2. **History Retrieval** → Get recent messages from chat session
3. **Context Extraction** → Extract key information from previous messages
4. **Relevance Scoring** → Score historical context relevance to current query
5. **Context Integration** → Combine historical and semantic context
6. **Prompt Enhancement** → Include conversation context in LLM prompt

**Modules**:
- `ChatService.get_conversation_context()` - context extraction
- `PromptBuilder.integrate_conversation_context()` - context integration

---

## Advanced Features

### Smart Context Selection

```python
# Automatic context optimization based on query type
response = chat_service.process_query(
    session_id=session.id,
    query="How do I implement OAuth2 authentication?",
    smart_context=True,  # Automatically optimize context selection
    # System will:
    # - Prioritize technical documentation
    # - Include code examples
    # - Adjust similarity thresholds
    # - Select optimal chunk count
)
```

### Multi-turn Conversation Awareness

```python
# System maintains conversation context automatically
session = chat_service.create_session(title="API Integration Help")

# First query
response1 = chat_service.process_query(
    session_id=session.id,
    query="How do I authenticate with your API?"
)

# Follow-up query - system understands "it" refers to API authentication
response2 = chat_service.process_query(
    session_id=session.id,
    query="What if it fails with a 401 error?"
    # System automatically includes previous context
)
```

### Content Type Prioritization

```python
# Prioritize specific content types based on query analysis
response = chat_service.process_query(
    session_id=session.id,
    query="Show me the login function implementation",
    content_type_weights={
        'archive': 0.8,    # Prioritize code archives
        'document': 0.6,   # Include documentation
        'external': 0.3    # Lower priority for external data
    }
)
```

### Real-time Search Suggestions

```python
# Get search suggestions as user types
suggestions = search_service.get_search_suggestions(
    partial_query="machine learn",
    limit=5,
    min_query_length=3
)

# Returns: ["machine learning", "machine learning algorithms", 
#          "machine learning models", "machine learning tutorial", 
#          "machine learning best practices"]
```

---

## ⚠️ Anti-patterns to Avoid

### ❌ Excessive Context Retrieval

**Don't do this**:
```python
# Too much context overwhelms the LLM and increases costs
response = chat_service.process_query(
    session_id=session.id,
    query="What is authentication?",
    max_context_chunks=20,  # Overkill for simple question
    max_tokens=4000         # Expensive and unnecessary
)
```

**Do this instead**:
```python
# Appropriate context for the query complexity
response = chat_service.process_query(
    session_id=session.id,
    query="What is authentication?",
    max_context_chunks=3,   # Sufficient for basic questions
    max_tokens=300          # Concise and cost-effective
)
```

### ❌ Ignoring Similarity Thresholds

**Don't do this**:
```python
# Using same threshold for all content types
results = search_service.search_all_content(
    query="user login",
    similarity_threshold=0.9  # Too strict for all content types
)
```

**Do this instead**:
```python
# Let the system use optimized thresholds per content type
results = search_service.search_all_content(
    query="user login"
    # System automatically uses:
    # - 0.7 for documents (general content)
    # - 0.6 for archives (code similarity)
    # - 0.5 for external data (structured data)
)
```

### ❌ Not Managing Conversation Length

**Don't do this**:
```python
# Unlimited conversation history
session = chat_service.create_session(
    title="Long Conversation",
    max_messages=None  # Can grow indefinitely
)
```

**Do this instead**:
```python
# Reasonable conversation limits
session = chat_service.create_session(
    title="Focused Conversation",
    max_messages=50,  # Prevent context overflow
    auto_summarize=True  # Summarize old messages
)
```

---

## Version Tracking

- `ADDED_IN: v1.0` - Basic chat and search functionality
- `ADDED_IN: v1.1` - Multi-content type search integration
- `ADDED_IN: v1.2` - Conversation context awareness
- `ADDED_IN: v1.3` - Smart context selection and content type weighting
- `CHANGED_IN: v1.4` - Optimized similarity thresholds per content type
- `ADDED_IN: v1.5` - Real-time search suggestions and hybrid search

---

## Performance Optimization

### Search Performance

- **Vector Indexes**: Automatic pgvector HNSW indexes for fast similarity search
- **Batch Processing**: Parallel search across content types
- **Caching**: Query embedding caching for repeated searches
- **Threshold Optimization**: Content-type specific similarity thresholds

### Chat Performance

- **Context Caching**: Cache assembled context for similar queries
- **Prompt Optimization**: Efficient prompt templates to minimize tokens
- **Response Streaming**: Stream responses for better user experience
- **Background Processing**: Async context preparation

### Cost Optimization

- **Token Counting**: Accurate token usage tracking and limits
- **Response Caching**: Cache responses for identical queries
- **Context Pruning**: Remove redundant context chunks
- **Batch Embeddings**: Process multiple queries efficiently

---

**DEPENDS_ON**: [SearchService, LLMClient, pgvector, OpenAI API, ChatSession models]  
**USED_BY**: [Customer support, Knowledge portals, API documentation, Code exploration]  
**TAGS**: `ai-chat, semantic-search, rag, conversational-ai, context-retrieval`
