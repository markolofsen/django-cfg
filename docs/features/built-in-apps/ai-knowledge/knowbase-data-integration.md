---
title: Data Integration
description: Django-CFG knowbase data integration feature guide. Production-ready data integration with built-in validation, type safety, and seamless Django integration.
sidebar_label: Data Integration
sidebar_position: 4
keywords:
  - django-cfg knowbase data integration
  - django knowbase data integration
  - knowbase data integration django-cfg
---
# External Data Integration - Auto-AI for Django Models

## Overview

Transform any Django model into an AI-searchable knowledge source with a single mixin. The `ExternalDataMixin` provides automatic vectorization, semantic search, and AI chat integration with zero additional configuration.

**Philosophy**: "One line of code, infinite AI possibilities" - Add the mixin to your model and get automatic AI integration that updates in real-time as your data changes.

**TAGS**: `mixin, auto-integration, vectorization, real-time, django-models, ai-search`

---

## Modules

### @knowbase/mixins/ExternalDataMixin

**Purpose**:
Automatic AI integration for Django models with real-time vectorization and semantic search capabilities.

**Dependencies**:
- `django_cfg.apps.knowbase.models.ExternalData`
- Django signals (`post_save`, `post_delete`)
- ReArq background tasks
- OpenAI embeddings API

**Exports**:
- `ExternalDataMixin` - Main mixin class
- `ExternalDataMeta` - Configuration class
- Auto-generated fields and methods

**Used in**:
- E-commerce product catalogs
- User profiles and content
- Documentation systems
- Any Django model requiring AI search

**Tags**: `mixin, signals, auto-sync, vectorization`


---



### Advanced Configuration

```python
class Article(ExternalDataMixin, models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag')
    published_at = models.DateTimeField(auto_now_add=True)
    
    class ExternalDataMeta:
        watch_fields = ['title', 'content', 'tags']
        similarity_threshold = 0.6
        auto_sync = True
        is_public = True  # Searchable by all users
        
        # Optional: Custom source type
        source_type = ExternalDataType.CUSTOM
    
    def get_external_content(self):
        # Include related data in content
        tag_names = ", ".join(self.tags.values_list('name', flat=True))
        
        return f"""# {self.title}

**Author**: {self.author.get_full_name()}
**Published**: {self.published_at.strftime('%Y-%m-%d')}
**Tags**: {tag_names}

## Content
{self.content}
"""
    
    def get_external_metadata(self):
        # Custom metadata for search filtering
        return {
            'author_id': self.author.id,
            'author_name': self.author.get_full_name(),
            'tag_count': self.tags.count(),
            'word_count': len(self.content.split()),
            'published_year': self.published_at.year
        }
```

### Manual Control Methods

```python
class Document(ExternalDataMixin, models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    class ExternalDataMeta:
        watch_fields = ['title', 'content']
        auto_sync = False  # Manual control
    
    def get_external_content(self):
        return f"# {self.title}\n\n{self.content}"
    
    def publish(self):
        """Custom method that triggers AI sync"""
        self.is_published = True
        self.save()
        
        # Manually trigger AI sync
        self.sync_to_external_data()
    
    def archive(self):
        """Remove from AI search"""
        self.is_archived = True
        self.save()
        
        # Remove from AI system
        self.remove_from_external_data()
```

%%END%%
````

---

## Data Models (Pydantic 2 & TypeScript)

### Pydantic 2 Models (Backend)

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class ExternalDataType(str, Enum):
    MODEL = "model"
    API = "api" 
    CUSTOM = "custom"

class ExternalDataMetaConfig(BaseModel):
    """Configuration for ExternalDataMixin"""
    watch_fields: List[str] = Field(..., min_items=1)
    similarity_threshold: float = Field(0.5, ge=0.0, le=1.0)
    auto_sync: bool = True
    is_public: bool = False
    source_type: ExternalDataType = ExternalDataType.MODEL

class ExternalDataSyncRequest(BaseModel):
    """Request to sync model data to external data system"""
    model_name: str = Field(..., min_length=1)
    model_id: str = Field(..., min_length=1)
    force_update: bool = False
    
class ExternalDataSyncResponse(BaseModel):
    """Response from sync operation"""
    success: bool
    external_data_id: Optional[str] = None
    message: str
    processing_time: float
    chunks_created: int = 0
```

### TypeScript Interfaces (Frontend)

```typescript
export enum ExternalDataType {
  MODEL = "model",
  API = "api",
  CUSTOM = "custom"
}

export interface ExternalDataMetaConfig {
  watch_fields: string[];
  similarity_threshold: number;
  auto_sync: boolean;
  is_public: boolean;
  source_type: ExternalDataType;
}

export interface ExternalDataSyncRequest {
  model_name: string;
  model_id: string;
  force_update: boolean;
}

export interface ExternalDataSyncResponse {
  success: boolean;
  external_data_id?: string;
  message: string;
  processing_time: number;
  chunks_created: number;
}

// Model integration status
export interface ModelIntegrationStatus {
  model_name: string;
  total_instances: number;
  synced_instances: number;
  pending_sync: number;
  last_sync: string;
  sync_enabled: boolean;
}
```

---

## 🔁 Flows

### Automatic Sync Flow (Real-time)

1. **Model Save** → Django model with mixin is saved/updated
2. **Signal Detection** → `post_save` signal detects changes in watched fields
3. **Change Validation** → Compare current values with previous state
4. **Content Generation** → Call model's `get_external_content()` method
5. **Background Task** → Queue `sync_external_data_async` task
6. **Content Processing** → Generate embeddings and create chunks
7. **Vector Storage** → Store in ExternalData with updated embeddings
8. **Search Index** → Update semantic search indexes

**Modules**:
- `ExternalDataMixin` - signal registration
- `external_data_signals.py` - change detection
- `external_data_tasks.py` - background processing
- `ExternalDataService` - content processing

---

### Manual Sync Flow (On-demand)

1. **Manual Trigger** → Developer calls `instance.sync_to_external_data()`
2. **Content Generation** → Generate fresh content from model
3. **Immediate Processing** → Process synchronously or queue task
4. **Status Update** → Update `external_source_id` field
5. **Confirmation** → Return success/failure status

**Modules**:
- `ExternalDataMixin.sync_to_external_data()` method
- `ExternalDataService.create_or_update()` method

---

### Bulk Sync Flow (Management Commands)

1. **Command Execution** → Run `python manage.py sync_external_models`
2. **Model Discovery** → Find all models using ExternalDataMixin
3. **Batch Processing** → Process models in configurable batches
4. **Progress Tracking** → Show sync progress and statistics
5. **Error Handling** → Log failures and continue processing
6. **Summary Report** → Display final sync statistics

**Modules**:
- Management command `sync_external_models`
- `ExternalDataService.bulk_sync()` method

---

## Advanced Patterns

### Conditional Sync

```python
class BlogPost(ExternalDataMixin, models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ])
    
    class ExternalDataMeta:
        watch_fields = ['title', 'content', 'status']
        auto_sync = True
    
    def should_sync_to_external_data(self):
        """Override to control when sync happens"""
        return self.status == 'published'
    
    def get_external_content(self):
        if self.status != 'published':
            return None  # Don't sync non-published posts
        return f"# {self.title}\n\n{self.content}"
```

### Multi-language Content

```python
class MultiLanguageArticle(ExternalDataMixin, models.Model):
    title_en = models.CharField(max_length=200)
    title_es = models.CharField(max_length=200)
    content_en = models.TextField()
    content_es = models.TextField()
    
    class ExternalDataMeta:
        watch_fields = ['title_en', 'title_es', 'content_en', 'content_es']
        auto_sync = True
    
    def get_external_content(self):
        """Generate multi-language content"""
        return f"""# {self.title_en}
        
## English
{self.content_en}

## Español  
# {self.title_es}
{self.content_es}
"""
    
    def get_external_metadata(self):
        return {
            'languages': ['en', 'es'],
            'primary_language': 'en'
        }
```

### Related Data Integration

```python
class Product(ExternalDataMixin, models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    reviews = models.ManyToManyField('Review', blank=True)
    
    class ExternalDataMeta:
        watch_fields = ['name', 'description', 'category']
        auto_sync = True
    
    def get_external_content(self):
        # Include related data in content
        recent_reviews = self.reviews.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).order_by('-rating')[:5]
        
        review_text = "\n".join([
            f"- {review.comment} (Rating: {review.rating}/5)"
            for review in recent_reviews
        ])
        
        return f"""# {self.name}

**Category**: {self.category.name}

## Description
{self.description}

## Recent Reviews
{review_text}
"""
```

---

## ⚠️ Anti-patterns to Avoid

### ❌ Heavy Content Generation

**Don't do this**:
```python
def get_external_content(self):
    # Expensive operations in content generation
    related_data = self.expensive_related_query()  # Slow!
    processed_content = self.complex_processing()   # CPU intensive!
    return f"Heavy content: {related_data} {processed_content}"
```

**Do this instead**:
```python
def get_external_content(self):
    # Keep content generation fast and simple
    return f"# {self.title}\n\n{self.description}"

# Use background tasks for heavy processing
def process_heavy_content(self):
    # Queue background task for expensive operations
    process_related_data_async.send(self.id)
```

### ❌ Watching Too Many Fields

**Don't do this**:
```python
class ExternalDataMeta:
    # Watching every field causes unnecessary updates
    watch_fields = ['field1', 'field2', 'field3', 'field4', 'field5', 
                   'field6', 'field7', 'field8', 'field9', 'field10']
```

**Do this instead**:
```python
class ExternalDataMeta:
    # Only watch fields that affect search relevance
    watch_fields = ['title', 'description']  # Core content only
```

### ❌ Ignoring Performance

**Don't do this**:
```python
def get_external_content(self):
    # N+1 queries in content generation
    reviews = []
    for review in self.reviews.all():  # N+1 problem!
        reviews.append(f"{review.user.name}: {review.comment}")
    return "\n".join(reviews)
```

**Do this instead**:
```python
def get_external_content(self):
    # Optimized queries with select_related/prefetch_related
    reviews = self.reviews.select_related('user').values_list(
        'user__name', 'comment', flat=False
    )
    review_text = "\n".join([f"{name}: {comment}" for name, comment in reviews])
    return f"# {self.title}\n\n{review_text}"
```

---

## Version Tracking

- `ADDED_IN: v1.1` - Initial ExternalDataMixin implementation
- `ADDED_IN: v1.2` - Conditional sync with `should_sync_to_external_data()`
- `ADDED_IN: v1.3` - Manual control methods (`sync_to_external_data()`, `remove_from_external_data()`)
- `ADDED_IN: v1.4` - Per-object similarity thresholds
- `CHANGED_IN: v1.5` - Improved signal handling and performance optimization

---

## Quick Integration Checklist

### Basic Setup

- [ ] Add `ExternalDataMixin` to your model
- [ ] Define `ExternalDataMeta` class with `watch_fields`
- [ ] Implement `get_external_content()` method
- [ ] Test with a simple model instance

### Advanced Configuration

- [ ] Set appropriate `similarity_threshold` for your content type
- [ ] Configure `is_public` based on your security requirements
- [ ] Implement custom `get_external_title()` and `get_external_description()`
- [ ] Add relevant metadata with `get_external_metadata()`

### Production Readiness

- [ ] Ensure background workers are running
- [ ] Monitor sync performance and adjust batch sizes
- [ ] Set up error monitoring for failed syncs
- [ ] Test with realistic data volumes

### Verification

- [ ] Model changes trigger automatic sync
- [ ] Content appears in semantic search results
- [ ] AI chat includes model data in responses
- [ ] Admin interface shows sync status

---

**DEPENDS_ON**: [django_cfg.apps.knowbase, Django signals, ReArq, OpenAI API]
**USED_BY**: [Product catalogs, User profiles, Content management, Documentation systems]  
**TAGS**: `mixin, auto-integration, real-time-sync, django-models, ai-search`
