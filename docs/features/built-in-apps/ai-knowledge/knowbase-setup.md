---
title: Knowledge Base Setup
description: Django-CFG knowbase setup feature guide. Production-ready knowledge base setup with built-in validation, type safety, and seamless Django integration.
sidebar_label: Setup
sidebar_position: 1
keywords:
  - django-cfg knowbase setup
  - django knowbase setup
  - knowbase setup django-cfg
---
# Knowledge Base Setup


## Overview

Django CFG Knowbase follows the "zero-configuration" philosophy - enable one setting and get a complete AI-powered knowledge management system. This guide covers configuration options, setup requirements, and deployment considerations.

**Philosophy**: "Configuration over convention, but smart defaults everywhere" - Minimal required configuration with extensive customization options for advanced use cases.

**TAGS**: `configuration, setup, deployment, django-cfg, zero-config, production-ready`

---

## Modules

### @django_cfg.core.config/KnowbaseConfig

**Purpose**:
Configuration management for Knowbase module with type-safe settings and intelligent defaults.

**Dependencies**:
- `django_cfg.core.config.DjangoConfig` - base configuration
- `pydantic` - type validation and settings management
- Environment variable resolution
- Constance dynamic settings integration

**Exports**:
- `enable_knowbase` - main feature flag
- `openai_api_key` - AI service authentication
- Similarity threshold settings
- Processing configuration options
- Cache and performance settings

**Used in**:
- Django settings generation
- Service initialization
- Background task configuration
- Admin interface setup

**Tags**: `configuration, type-safety, environment-variables, dynamic-settings`


---



### Environment Variables

```bash
# .env file
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional: Custom database for knowledge data
KNOWLEDGE_DATABASE_URL=postgresql://user:pass@localhost/knowledge_db

# Optional: Redis for caching and tasks
REDIS_URL=redis://localhost:6379/0

# Optional: Custom similarity thresholds
KNOWBASE_DOCUMENT_THRESHOLD=0.7
KNOWBASE_ARCHIVE_THRESHOLD=0.6
KNOWBASE_EXTERNAL_THRESHOLD=0.5
```

### Advanced Configuration

```python
class ProductionConfig(DjangoConfig):
    # Core Settings
    enable_knowbase: bool = True
    openai_api_key: str = env.openai_api_key  # From YAML config
    
    # AI Model Configuration
    openai_model: str = "gpt-4"  # Default: gpt-3.5-turbo
    embedding_model: str = "text-embedding-ada-002"  # Default
    
    # Similarity Thresholds (0.0-1.0)
    knowbase_document_threshold: float = 0.75    # Documents
    knowbase_archive_threshold: float = 0.65     # Code archives
    knowbase_external_threshold: float = 0.55    # External data
    
    # Processing Configuration
    knowbase_chunk_size: int = 1000              # Text chunk size
    knowbase_overlap_size: int = 200             # Chunk overlap
    knowbase_batch_size: int = 50                # Embedding batch size
    
    # Performance Settings
    knowbase_max_context_chunks: int = 10        # Max context per query
    knowbase_max_tokens_per_query: int = 1000    # Response length limit
    knowbase_cache_ttl: int = 3600               # Cache timeout (seconds)
    
    # Security Settings
    knowbase_require_auth: bool = True           # Require authentication
    knowbase_allow_public_search: bool = False   # Public search access
    knowbase_rate_limit_per_minute: int = 60     # API rate limiting
    
    # Database Configuration
    knowbase_use_separate_db: bool = True        # Dedicated knowledge DB
    knowbase_db_name: str = "knowledge"          # Database name
    
    # Background Processing
    knowbase_worker_concurrency: int = 4         # Dramatiq workers
    knowbase_task_timeout: int = 300             # Task timeout (seconds)
    knowbase_retry_attempts: int = 3             # Failed task retries
```

### Development Configuration

```python
class DevelopmentConfig(DjangoConfig):
    enable_knowbase: bool = True
    openai_api_key: str = env.openai_api_key  # From YAML config
    
    # Development-friendly settings
    knowbase_debug_mode: bool = True             # Verbose logging
    knowbase_cache_ttl: int = 60                 # Short cache for testing
    knowbase_require_auth: bool = False          # Easy testing
    knowbase_allow_public_search: bool = True    # Open access
    
    # Faster processing for development
    knowbase_chunk_size: int = 500               # Smaller chunks
    knowbase_batch_size: int = 10                # Smaller batches
    knowbase_worker_concurrency: int = 1         # Single worker
```

## Infrastructure Setup

### PostgreSQL with pgvector

```bash
# Install pgvector extension
sudo apt-get install postgresql-14-pgvector

# Enable extension in your database
psql -d your_database -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Verify installation
psql -d your_database -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### Redis Configuration

```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test connection
redis-cli ping  # Should return PONG
```

### Background Workers

```bash
# Start ReArq workers for background processing
rearq

# Production: Use supervisor or systemd
# /etc/supervisor/conf.d/knowbase-workers.conf
[program:knowbase-workers]
command=/path/to/venv/bin/rearq
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
numprocs=4
```

## Database Migrations

```bash
# Apply Knowbase migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# Optional: Load sample data
python manage.py loaddata knowbase_sample_data.json
```

%%END%%
````

---

## Data Models (Pydantic 2 & TypeScript)

### Pydantic 2 Models (Backend)

```python
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import Optional, Dict, Any, List
from enum import Enum

class KnowbaseConfig(BaseModel):
    """Complete Knowbase configuration model"""
    
    # Core Settings
    enable_knowbase: bool = True
    openai_api_key: str = Field(..., min_length=1)
    
    # AI Model Configuration
    openai_model: str = Field("gpt-3.5-turbo", pattern=r"^gpt-")
    embedding_model: str = "text-embedding-ada-002"
    
    # Similarity Thresholds
    knowbase_document_threshold: float = Field(0.7, ge=0.0, le=1.0)
    knowbase_archive_threshold: float = Field(0.6, ge=0.0, le=1.0)
    knowbase_external_threshold: float = Field(0.5, ge=0.0, le=1.0)
    
    # Processing Configuration
    knowbase_chunk_size: int = Field(1000, ge=100, le=4000)
    knowbase_overlap_size: int = Field(200, ge=0, le=1000)
    knowbase_batch_size: int = Field(50, ge=1, le=200)
    
    # Performance Settings
    knowbase_max_context_chunks: int = Field(10, ge=1, le=50)
    knowbase_max_tokens_per_query: int = Field(1000, ge=100, le=4000)
    knowbase_cache_ttl: int = Field(3600, ge=60, le=86400)
    
    # Security Settings
    knowbase_require_auth: bool = True
    knowbase_allow_public_search: bool = False
    knowbase_rate_limit_per_minute: int = Field(60, ge=1, le=1000)
    
    # Database Configuration
    knowbase_use_separate_db: bool = False
    knowbase_db_name: str = "knowledge"
    
    # Background Processing
    knowbase_worker_concurrency: int = Field(4, ge=1, le=20)
    knowbase_task_timeout: int = Field(300, ge=30, le=3600)
    knowbase_retry_attempts: int = Field(3, ge=1, le=10)
    
    @field_validator('knowbase_overlap_size')
    @classmethod
    def overlap_must_be_less_than_chunk_size(cls, v, info: ValidationInfo):
        if 'knowbase_chunk_size' in info.data and v >= info.data['knowbase_chunk_size']:
            raise ValueError('overlap_size must be less than chunk_size')
        return v

class DatabaseConfig(BaseModel):
    """Database configuration for Knowbase"""
    host: str = "localhost"
    port: int = Field(5432, ge=1, le=65535)
    name: str = "knowledge"
    user: str
    password: str
    options: Dict[str, Any] = Field(default_factory=dict)
    
    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

class RedisConfig(BaseModel):
    """Redis configuration for caching and tasks"""
    host: str = "localhost"
    port: int = Field(6379, ge=1, le=65535)
    db: int = Field(0, ge=0, le=15)
    password: Optional[str] = None
    
    @property
    def url(self) -> str:
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"
```

### TypeScript Interfaces (Frontend)

```typescript
export interface KnowbaseConfig {
  // Core Settings
  enable_knowbase: boolean;
  openai_api_key: string;
  
  // AI Model Configuration
  openai_model: string;
  embedding_model: string;
  
  // Similarity Thresholds
  knowbase_document_threshold: number;
  knowbase_archive_threshold: number;
  knowbase_external_threshold: number;
  
  // Processing Configuration
  knowbase_chunk_size: number;
  knowbase_overlap_size: number;
  knowbase_batch_size: number;
  
  // Performance Settings
  knowbase_max_context_chunks: number;
  knowbase_max_tokens_per_query: number;
  knowbase_cache_ttl: number;
  
  // Security Settings
  knowbase_require_auth: boolean;
  knowbase_allow_public_search: boolean;
  knowbase_rate_limit_per_minute: number;
  
  // Database Configuration
  knowbase_use_separate_db: boolean;
  knowbase_db_name: string;
  
  // Background Processing
  knowbase_worker_concurrency: number;
  knowbase_task_timeout: number;
  knowbase_retry_attempts: number;
}

export interface DatabaseConfig {
  host: string;
  port: number;
  name: string;
  user: string;
  password: string;
  options: Record<string, any>;
}

export interface RedisConfig {
  host: string;
  port: number;
  db: number;
  password?: string;
}

// Configuration validation
export interface ConfigValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
  recommendations: string[];
}
```

---

## 🔁 Flows

### Configuration Loading Flow

1. **Environment Loading** → Load environment variables and .env files
2. **Config Validation** → Validate configuration with Pydantic models
3. **Default Application** → Apply intelligent defaults for missing values
4. **Service Registration** → Register Knowbase services with Django
5. **Database Setup** → Configure database routing and connections
6. **Cache Configuration** → Set up Redis caching and sessions
7. **Background Tasks** → Initialize ReArq task queues
8. **URL Registration** → Register API endpoints and admin interfaces

**Modules**:
- `django_cfg.core.config` - configuration loading
- `django_cfg.apps.knowbase.apps` - service registration
- Django settings generation

---

### Production Deployment Flow

1. **Environment Preparation** → Set up production environment variables
2. **Infrastructure Setup** → Configure PostgreSQL, Redis, and workers
3. **Security Configuration** → Set authentication and rate limiting
4. **Performance Tuning** → Optimize thresholds and batch sizes
5. **Monitoring Setup** → Configure logging and error tracking
6. **Health Checks** → Implement service health monitoring
7. **Scaling Configuration** → Set up horizontal scaling options

**Modules**:
- Production configuration classes
- Infrastructure setup scripts
- Monitoring and logging configuration

---

## Configuration Best Practices

### Environment-Specific Settings

```python
# Base configuration
class BaseKnowbaseConfig(DjangoConfig):
    enable_knowbase: bool = True
    openai_api_key: str = env.openai_api_key  # From YAML config

# Development
class DevelopmentConfig(BaseKnowbaseConfig):
    knowbase_debug_mode: bool = True
    knowbase_require_auth: bool = False
    knowbase_cache_ttl: int = 60

# Staging
class StagingConfig(BaseKnowbaseConfig):
    knowbase_debug_mode: bool = True
    knowbase_require_auth: bool = True
    knowbase_rate_limit_per_minute: int = 100

# Production
class ProductionConfig(BaseKnowbaseConfig):
    knowbase_debug_mode: bool = False
    knowbase_require_auth: bool = True
    knowbase_rate_limit_per_minute: int = 60
    knowbase_use_separate_db: bool = True
```

### Security Hardening

```python
class SecureKnowbaseConfig(DjangoConfig):
    enable_knowbase: bool = True
    openai_api_key: str = env.openai_api_key  # From YAML config
    
    # Security settings
    knowbase_require_auth: bool = True
    knowbase_allow_public_search: bool = False
    knowbase_rate_limit_per_minute: int = 30
    
    # API key rotation
    knowbase_api_key_rotation_days: int = 90
    
    # Content filtering
    knowbase_enable_content_filter: bool = True
    knowbase_blocked_file_types: List[str] = ['.exe', '.bat', '.sh']
    
    # Audit logging
    knowbase_enable_audit_log: bool = True
    knowbase_log_all_queries: bool = True
```

### Performance Optimization

```python
class HighPerformanceConfig(DjangoConfig):
    enable_knowbase: bool = True
    openai_api_key: str = env.openai_api_key  # From YAML config
    
    # Optimized processing
    knowbase_batch_size: int = 100
    knowbase_worker_concurrency: int = 8
    knowbase_chunk_size: int = 1500
    
    # Aggressive caching
    knowbase_cache_ttl: int = 7200
    knowbase_enable_query_cache: bool = True
    knowbase_enable_embedding_cache: bool = True
    
    # Database optimization
    knowbase_use_separate_db: bool = True
    knowbase_db_pool_size: int = 20
    knowbase_db_max_overflow: int = 30
```

---

## ⚠️ Anti-patterns to Avoid

### ❌ Hardcoded API Keys

**Don't do this**:
```python
class BadConfig(DjangoConfig):
    openai_api_key: str = "sk-hardcoded-key-in-source-code"  # Security risk!
```

**Do this instead**:
```python
class GoodConfig(DjangoConfig):
    openai_api_key: str = env.openai_api_key  # From YAML config  # Environment variable
```

### ❌ Ignoring Resource Limits

**Don't do this**:
```python
class ResourceHungryConfig(DjangoConfig):
    knowbase_batch_size: int = 1000          # Too large
    knowbase_worker_concurrency: int = 50    # Too many workers
    knowbase_max_context_chunks: int = 100   # Expensive queries
```

**Do this instead**:
```python
class OptimizedConfig(DjangoConfig):
    knowbase_batch_size: int = 50            # Reasonable batch size
    knowbase_worker_concurrency: int = 4     # Match CPU cores
    knowbase_max_context_chunks: int = 10    # Cost-effective
```

### ❌ Same Settings for All Environments

**Don't do this**:
```python
# Using production settings in development
class OneConfigForAll(DjangoConfig):
    knowbase_require_auth: bool = True        # Slows development
    knowbase_cache_ttl: int = 3600           # Hard to test changes
    knowbase_debug_mode: bool = False        # No debugging info
```

**Do this instead**:
```python
# Environment-specific configurations
class DevelopmentConfig(DjangoConfig):
    knowbase_require_auth: bool = False      # Easy testing
    knowbase_cache_ttl: int = 60            # Quick cache refresh
    knowbase_debug_mode: bool = True        # Verbose logging
```

---

## Version Tracking

- `ADDED_IN: v1.0` - Basic configuration with enable_knowbase flag
- `ADDED_IN: v1.1` - Similarity threshold configuration
- `ADDED_IN: v1.2` - Performance and security settings
- `ADDED_IN: v1.3` - Environment-specific configuration classes
- `CHANGED_IN: v1.4` - Improved validation and type safety
- `ADDED_IN: v1.5` - Production deployment configuration

---

## Configuration Checklist

### Development Setup

- [ ] Set `enable_knowbase: bool = True`
- [ ] Configure `OPENAI_API_KEY` environment variable
- [ ] Install PostgreSQL with pgvector extension
- [ ] Set up Redis server
- [ ] Run `python manage.py migrate`
- [ ] Start background workers with `rearq`

### Production Deployment

- [ ] Use environment-specific configuration class
- [ ] Set up dedicated knowledge database
- [ ] Configure Redis clustering for high availability
- [ ] Set up multiple background workers
- [ ] Enable authentication and rate limiting
- [ ] Configure monitoring and logging
- [ ] Set up health checks and alerts
- [ ] Implement backup and recovery procedures

### Security Hardening

- [ ] Enable authentication (`knowbase_require_auth: bool = True`)
- [ ] Disable public search in production
- [ ] Set appropriate rate limits
- [ ] Use strong database passwords
- [ ] Enable audit logging
- [ ] Regular API key rotation
- [ ] Content filtering for uploads

### Performance Optimization

- [ ] Tune similarity thresholds for your content
- [ ] Optimize chunk sizes based on content type
- [ ] Configure appropriate batch sizes
- [ ] Set up caching with reasonable TTL
- [ ] Monitor token usage and costs
- [ ] Scale workers based on load
- [ ] Use database connection pooling

---

**DEPENDS_ON**: [django-cfg, PostgreSQL, pgvector, Redis, OpenAI API]  
**USED_BY**: [All Knowbase components, Django settings, Background workers]  
**TAGS**: `configuration, setup, deployment, type-safety, environment-variables`

---


## Quick Navigation

This directory contains comprehensive user documentation for the Django CFG Knowbase module, following the `@DOCS_MODULE.md` methodology for LLM-optimized documentation.

---

## Documentation Structure

### 🏠 [configuration](./knowbase-configuration)
**Main overview and philosophy**
- Complete module overview and philosophy
- Zero-configuration AI integration approach
- Quick start checklist and verification steps
- Core modules and their relationships
- Production-ready architecture insights

**Key Topics**: Overview, Philosophy, Quick Start, Architecture, Anti-patterns

---

### [data-integration](./knowbase-data-integration)
**Auto-AI integration for Django models**
- ExternalDataMixin usage and configuration
- Real-time vectorization and sync patterns
- Advanced integration patterns and examples
- Performance optimization for model integration

**Key Topics**: ExternalDataMixin, Auto-sync, Model Integration, Real-time Updates

---

### [chat-search](./knowbase-chat-search)
**Conversational AI and semantic search**
- ChatService and SearchService usage
- Context retrieval and conversation management
- Multi-content type semantic search
- Performance optimization and cost management

**Key Topics**: AI Chat, Semantic Search, Context Retrieval, RAG Pipeline

---

### Configuration Setup
**Zero-config setup and deployment**
- Configuration options and environment setup
- Production deployment best practices
- Security hardening and performance tuning
- Infrastructure requirements and scaling

**Key Topics**: Configuration, Setup, Deployment, Security, Performance

---

## Getting Started Path

### For New Users
1. **Start here**: [configuration](./knowbase-configuration) - Understand the philosophy and architecture
2. **Setup**: Basic Configuration - Get your system running
3. **Integration**: [data-integration](./knowbase-data-integration) - Add AI to your models
4. **Usage**: [chat-search](./knowbase-chat-search) - Use AI chat and search features

### For Experienced Users
- **Quick Reference**: Each file contains API examples and configuration options
- **Advanced Patterns**: Look for "Advanced Features" sections in each guide
- **Production**: Focus on "Production" and "Performance" sections
- **Troubleshooting**: Check "Anti-patterns to Avoid" sections

---

## Documentation Features

### LLM-Optimized Format
- **Token-efficient**: Concise but comprehensive content
- **Structured**: Consistent headings and organization
- **Searchable**: Tagged with relevant keywords
- **Executable**: All code examples are working and tested

### Type-Safe Examples
- **Pydantic 2**: Backend models with full validation
- **TypeScript**: Frontend interfaces and types
- **Django**: Production-ready Django patterns
- **API**: Complete API usage examples

### Production-Ready
- **Security**: Authentication, rate limiting, content filtering
- **Performance**: Caching, batching, optimization techniques
- **Monitoring**: Logging, metrics, health checks
- **Scaling**: Horizontal scaling and load balancing

---

## Content Statistics

| Guide | Lines | Topics | Code Examples | API Methods |
|-------|-------|--------|---------------|-------------|
| configuration | ~400 | 8 | 15+ | 10+ |
| data-integration | ~500 | 10 | 20+ | 15+ |
| chat-search | ~600 | 12 | 25+ | 20+ |
| Basic Configuration | ~550 | 11 | 18+ | 12+ |
| **Total** | **~2050** | **41** | **78+** | **57+** |

---

## 🏷️ Tags and Keywords

**Core Tags**: `django-cfg`, `knowbase`, `ai`, `rag`, `semantic-search`, `chat-ai`, `documentation`

**Technical Tags**: `pydantic2`, `typescript`, `postgresql`, `pgvector`, `redis`, `dramatiq`, `openai`

**Feature Tags**: `zero-config`, `auto-integration`, `real-time-sync`, `production-ready`, `type-safe`

**Use Case Tags**: `document-management`, `customer-support`, `knowledge-base`, `code-search`, `api-docs`

---

## Version Information

- **Documentation Version**: v1.0
- **Knowbase Module Version**: v1.5+
- **Django CFG Version**: v1.1.82+
- **Last Updated**: September 2024

---

## Contributing

This documentation follows the `@DOCS_MODULE.md` methodology:

### Guidelines
- **Maximum 1000 lines per file** (enforced)
- **Token-efficient content** - every line adds value
- **Working code examples** - all examples must be executable
- **Type safety** - 100% typed examples (Pydantic 2 / TypeScript)
- **No duplication** - DRY principle for documentation

### Structure Requirements
- **Overview** section with philosophy and tags
- **Modules** section with dependencies and exports
- **APIs** section with function documentation
- **Data Models** with Pydantic 2 and TypeScript
- **Flows** section with process descriptions
- **Anti-patterns** section with what to avoid
- **Version Tracking** with change history

---

## Quick Reference

### Essential Commands
```bash
# Enable Knowbase
enable_knowbase: bool = True

# Start system
python manage.py migrate
rearq

# Test integration
python manage.py shell
>>> from django_cfg.apps.knowbase.services import ChatService
>>> chat = ChatService(user=user)
>>> session = chat.create_session(title="Test")
>>> response = chat.process_query(session.id, "Hello AI!")
```

### Key URLs
- **Admin**: `/admin/` (Knowledge Base section)
- **API**: `/cfg/knowbase/api/`
- **Chat**: `/cfg/knowbase/chat/`
- **Docs**: `/cfg/knowbase/api/docs/`

### Support Resources
- **Technical Documentation**: `/src/django_cfg/features/built-in-apps/knowbase/@docs/`
- **Examples**: `/src/django_cfg/features/built-in-apps/knowbase/guides/`
- **Tests**: `/src/django_cfg/features/built-in-apps/knowbase/tests/`

---

**DEPENDS_ON**: [Django CFG, PostgreSQL, pgvector, Redis, OpenAI API]  
**USED_BY**: [Django developers, AI integrators, Knowledge management systems]  
**TAGS**: `documentation, user-guide, django-cfg, knowbase, ai-integration`
