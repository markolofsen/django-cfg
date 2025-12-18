# 🚀 Django 5.2 Async/Sync Operations Complete Guide

## 🎯 Overview

Complete reference for Django 5.2 asynchronous and synchronous operations, including ORM, Channels WebSocket support, and context-aware programming patterns. Optimized for modern async/await workflows and production deployments.

**TAGS**: `django, async, orm, channels, websockets, context-aware, performance`

---

## 📦 Modules

### django.db.models %%PRIORITY:HIGH%%

**Purpose**: 
Async-enabled ORM operations with `a`-prefixed methods for non-blocking database interactions.

**Dependencies**:
- Django 5.2+
- ASGI server (Uvicorn, Daphne)
- Async-compatible database backend

**Key Features**:
- `a`-prefixed async methods (`aget`, `acreate`, `aupdate`, etc.)
- `async for` iteration over QuerySets
- Context-aware operations
- Full async/await support

**Used in**:
- Async views and services
- Background task processors
- Real-time data handlers

%%AI_HINT: Always use a-prefixed methods in async contexts%%

---

### django.channels %%PRIORITY:HIGH%%

**Purpose**:
WebSocket and long-lived connection handling with ASGI protocol support.

**Dependencies**:
- `channels`
- `daphne` (ASGI server)
- Channel layer backend (Redis/InMemory)

**Exports**:
- `AsyncWebsocketConsumer`
- `AuthMiddlewareStack`
- `ProtocolTypeRouter`

**Used in**:
- Real-time notifications
- Live data streaming
- Chat applications

**Tags**: `websockets, asgi, real-time, channels`

---

### Context Detection Utilities

**Purpose**:
Detect and handle async/sync execution contexts for hybrid operations.

**Key Functions**:
- `is_async_context()` - Runtime context detection
- `sync_to_async()` - Convert sync to async
- `async_to_sync()` - Convert async to sync

**Tags**: `context, hybrid, compatibility`

---

## 🧾 APIs (ReadMe.LLM Format)

````markdown
%%README.LLM id=async-orm%%

## 🧭 Library Description

Django 5.2 async ORM operations provide non-blocking database access using `a`-prefixed methods and `async for` iteration.

## ✅ Rules

- Use `a`-prefixed methods in async contexts only
- Never mix sync/async ORM calls without proper context handling
- Always run in ASGI server for async support
- Use `async for` for QuerySet iteration

## 🧪 Functions

### Model.objects.aget(id: int) -> Model

**Asynchronously retrieve single object by ID.**

```python
book = await Book.objects.aget(id=1)
```

### Model.objects.acreate(**kwargs) -> Model

**Asynchronously create new object.**

```python
book = await Book.objects.acreate(
    title="Async Python",
    author="Developer"
)
```

### Model.objects.aall() -> AsyncQuerySet

**Get all objects asynchronously.**

```python
books = await Book.objects.aall()
```

### QuerySet async iteration

**Iterate over QuerySet without blocking.**

```python
async for book in Book.objects.filter(author="Django"):
    print(book.title)
```

%%END%%
````

````markdown
%%README.LLM id=channels-websockets%%

## 🧭 Library Description

Django Channels enables WebSocket support and real-time communication through ASGI protocol.

## ✅ Rules

- Use `AsyncWebsocketConsumer` for WebSocket handling
- Configure ASGI application properly
- Handle connection lifecycle (connect/disconnect/receive)
- Use channel layers for group communication

## 🧪 Consumer Methods

### async def connect(self)

**Handle WebSocket connection establishment.**

```python
async def connect(self):
    self.room_name = "chat_room"
    await self.channel_layer.group_add(
        self.room_name,
        self.channel_name
    )
    await self.accept()
```

### async def disconnect(self, close_code)

**Handle WebSocket disconnection.**

```python
async def disconnect(self, close_code):
    await self.channel_layer.group_discard(
        self.room_name,
        self.channel_name
    )
```

### async def receive(self, text_data)

**Handle incoming WebSocket messages.**

```python
async def receive(self, text_data):
    data = json.loads(text_data)
    await self.channel_layer.group_send(
        self.room_name,
        {
            'type': 'chat.message',
            'message': data['message']
        }
    )
```

%%END%%
````

---

## 🏗️ Data Models (Pydantic 2 & TypeScript)

### Pydantic 2 Models (Backend)

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class AsyncOperationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class AsyncTaskConfig(BaseModel):
    """Configuration for async task execution."""
    
    task_id: str = Field(..., description="Unique task identifier")
    timeout: int = Field(default=30, ge=1, le=300)
    retry_count: int = Field(default=3, ge=0, le=10)
    concurrent_limit: int = Field(default=5, ge=1, le=50)
    status: AsyncOperationStatus = AsyncOperationStatus.PENDING
    
    class Config:
        use_enum_values = True
        validate_assignment = True

class WebSocketMessage(BaseModel):
    """WebSocket message structure."""
    
    type: str = Field(..., description="Message type")
    data: dict = Field(default_factory=dict)
    timestamp: Optional[str] = None
    room: Optional[str] = None
    
    class Config:
        json_encoders = {
            'datetime': lambda v: v.isoformat()
        }
```

### TypeScript Interfaces (Frontend)

```typescript
export type AsyncOperationStatus = 
    | "pending" 
    | "in_progress" 
    | "completed" 
    | "failed";

export interface AsyncTaskConfig {
    taskId: string;
    timeout?: number; // 1-300 seconds
    retryCount?: number; // 0-10 retries
    concurrentLimit?: number; // 1-50 concurrent
    status: AsyncOperationStatus;
}

export interface WebSocketMessage {
    type: string;
    data?: Record<string, any>;
    timestamp?: string;
    room?: string;
}

export interface AsyncOrmResult<T> {
    data: T[];
    count: number;
    hasNext: boolean;
    executionTime: number;
}
```

---

## 🔁 Flows

### Async ORM Operation Flow %%PRIORITY:HIGH%%

1. **Context Check**: Verify running in async context
2. **Connection**: Establish async database connection
3. **Query Execution**: Use `a`-prefixed methods
4. **Result Processing**: Handle async results with `await`
5. **Connection Cleanup**: Automatic cleanup via context managers

**Modules**:
- `django.db.models`
- `django.db.connection`
- `asyncio`

```python
# Complete async ORM flow
async def process_books_async():
    # Step 1: Context verification (implicit)
    try:
        # Step 2-4: Query execution and processing
        async for book in Book.objects.filter(
            published_date__year=2024
        ).order_by('title'):
            await process_book(book)
            
        # Bulk operations
        books = await Book.objects.aall()
        
    except Exception as e:
        logger.error(f"Async ORM error: {e}")
    # Step 5: Cleanup handled automatically
```

---

### WebSocket Real-time Communication Flow

1. **Connection**: Client establishes WebSocket connection
2. **Authentication**: Verify user permissions and join groups
3. **Message Handling**: Process incoming/outgoing messages
4. **Broadcasting**: Send messages to channel groups
5. **Disconnection**: Clean up resources and leave groups

**Modules**:
- `channels.generic.websocket`
- `channels.layers`
- `channels.auth`

```python
# Complete WebSocket flow
class RealTimeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Step 1: Connection establishment
        self.user = self.scope["user"]
        self.room_name = f"user_{self.user.id}"
        
        # Step 2: Authentication and group join
        if self.user.is_authenticated:
            await self.channel_layer.group_add(
                self.room_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()
    
    async def receive(self, text_data):
        # Step 3: Message handling
        data = json.loads(text_data)
        
        # Step 4: Broadcasting
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'notification.send',
                'message': data['message']
            }
        )
    
    async def disconnect(self, close_code):
        # Step 5: Cleanup
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )
```

---

### Context-Aware Operation Flow

1. **Context Detection**: Check if running in async or sync context
2. **Method Selection**: Choose appropriate sync/async method
3. **Execution**: Run operation with proper context handling
4. **Error Handling**: Context-specific error management
5. **Result Return**: Consistent result format

```python
import asyncio
from asgiref.sync import sync_to_async, async_to_sync

def is_async_context() -> bool:
    """Detect current execution context."""
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False

async def context_aware_database_operation(model_class, **kwargs):
    """Perform database operation based on context."""
    if is_async_context():
        # Async context - use async methods
        return await model_class.objects.acreate(**kwargs)
    else:
        # Sync context - use sync methods
        return model_class.objects.create(**kwargs)

# Usage in hybrid environments
def hybrid_service_function():
    if is_async_context():
        # Already in async context
        result = await context_aware_database_operation(Book, title="Test")
    else:
        # Sync context - convert to async
        async_func = sync_to_async(context_aware_database_operation)
        result = async_func(Book, title="Test")
    
    return result
```

---

## 🚨 Common Issues & Solutions %%PRIORITY:HIGH%%

### Issue: Event Loop Closed

**Problem**: `RuntimeError: Event loop is closed`

**Root Cause**: Attempting to use closed event loops in threads

**Solution**: Create new event loops in threads

```python
def run_async_in_thread(async_func, *args, **kwargs):
    """Run async function in new thread with fresh event loop."""
    def thread_target():
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run async operations
            return loop.run_until_complete(async_func(*args, **kwargs))
            
        except Exception as e:
            logger.error(f"Thread async error: {e}")
            raise
        finally:
            # Clean up event loop
            if loop and not loop.is_closed():
                loop.close()
    
    return thread_target
```

---

### Issue: Django ORM Async Context Error %%BREAKING_CHANGE%%

**Problem**: `You cannot call this from an async context - use a thread or sync_to_async`

**Root Cause**: Mixing sync ORM operations in async contexts

**Solution**: Context-aware database operations

```python
from asgiref.sync import sync_to_async

class ContextAwareService:
    """Service that handles both sync and async contexts."""
    
    def __init__(self):
        self.sync_methods = {
            'create': self._sync_create,
            'get': self._sync_get,
            'update': self._sync_update,
        }
        self.async_methods = {
            'create': self._async_create,
            'get': self._async_get,
            'update': self._async_update,
        }
    
    async def create_object(self, model_class, **kwargs):
        """Context-aware object creation."""
        if is_async_context():
            return await self.async_methods['create'](model_class, **kwargs)
        else:
            # Convert sync method to async
            sync_create = sync_to_async(self.sync_methods['create'])
            return await sync_create(model_class, **kwargs)
    
    async def _async_create(self, model_class, **kwargs):
        """Async object creation."""
        return await model_class.objects.acreate(**kwargs)
    
    def _sync_create(self, model_class, **kwargs):
        """Sync object creation."""
        return model_class.objects.create(**kwargs)
```

---

### Issue: HTTPTransport Async Context

**Problem**: `'HTTPTransport' object has no attribute '__aenter__'`

**Root Cause**: Incorrect httpx client usage in async context

**Solution**: Proper async client initialization

```python
import httpx
import asyncio

class AsyncHTTPService:
    """Proper async HTTP client usage."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self._client = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            verify=False  # For IP-based requests
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
    
    async def make_request(self, url: str, **kwargs) -> httpx.Response:
        """Make async HTTP request."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        return await self._client.get(url, **kwargs)

# Usage
async def test_ip_performance():
    async with AsyncHTTPService(timeout=10) as http_service:
        response = await http_service.make_request("https://api.example.com")
        return response.json()
```

---

## 🧪 Testing Patterns

### Async Test Configuration

```python
import pytest
from django.test import AsyncClient
from asgiref.sync import sync_to_async

@pytest.mark.django_db(transaction=True)
async def test_async_orm_operations():
    """Test async ORM operations."""
    # Create test data
    book = await Book.objects.acreate(
        title="Test Book",
        author="Test Author",
        published_date="2024-01-01"
    )
    
    # Test async retrieval
    retrieved_book = await Book.objects.aget(id=book.id)
    assert retrieved_book.title == "Test Book"
    
    # Test async filtering
    books = []
    async for b in Book.objects.filter(author="Test Author"):
        books.append(b)
    
    assert len(books) == 1
    assert books[0].id == book.id

@pytest.mark.django_db(transaction=True)
def test_sync_orm_operations():
    """Test sync ORM operations for comparison."""
    # Create test data
    book = Book.objects.create(
        title="Sync Test Book",
        author="Sync Author",
        published_date="2024-01-01"
    )
    
    # Test sync retrieval
    retrieved_book = Book.objects.get(id=book.id)
    assert retrieved_book.title == "Sync Test Book"
```

---

## 🔧 Configuration

### ASGI Application Setup

```python
# asgi.py
import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

# HTTP application
http_application = get_asgi_application()

# WebSocket routes
websocket_urlpatterns = [
    path("ws/notifications/", NotificationConsumer.as_asgi()),
    path("ws/chat/<str:room_name>/", ChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": http_application,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
    ),
})
```

### Settings Configuration

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',  # Add channels
    # Your apps
]

# ASGI Application
ASGI_APPLICATION = "project.asgi.application"

# Channel Layers (Redis recommended for production)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

# Database configuration for async support
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # Async-compatible
        'NAME': 'your_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'MAX_CONNS': 20,  # Connection pooling
        }
    }
}
```

---

## 🧠 Notes

### Performance Considerations %%PRIORITY:HIGH%%

- **Async ORM**: 2-3x faster for I/O bound operations
- **Connection Pooling**: Essential for production async deployments
- **Memory Usage**: Async operations use more memory per request
- **CPU Bound**: Use sync operations for CPU-intensive tasks

### Best Practices

1. **Context Awareness**: Always check execution context
2. **Error Handling**: Comprehensive async exception handling
3. **Resource Cleanup**: Use async context managers
4. **Testing**: Test both sync and async code paths
5. **Monitoring**: Track async operation performance

### Anti-patterns to Avoid %%DEPRECATED%%

- Mixing sync/async ORM calls without context handling
- Using sync HTTP clients in async contexts
- Blocking async operations with sync calls
- Not handling connection cleanup properly
- Ignoring context detection in hybrid services

### Version Tracking

- `ADDED_IN: Django 5.0` - Basic async ORM support
- `ENHANCED_IN: Django 5.1` - Improved async QuerySet methods
- `STABLE_IN: Django 5.2` - Production-ready async operations
- `%%BREAKING_CHANGE%% WILL_CHANGE_IN: Django 6.0` - Async-first ORM design

---

## 📚 References

- [Django 5.2 Async Documentation](https://docs.djangoproject.com/en/5.2/topics/async/)
- [Channels Documentation](https://channels.readthedocs.io/)
- [ASGI Specification](https://asgi.readthedocs.io/)
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
