---
title: Knowledge Base Commands
description: Django-CFG CLI knowbase commands. Command-line interface for knowledge base commands with examples, options, and production workflows.
sidebar_label: Knowledge Base
sidebar_position: 4
keywords:
  - django-cfg knowbase
  - django-cfg command knowbase
  - cli knowbase
---

# Knowledge Base Commands

Commands for managing the AI knowledge base, vector search, and pgvector integration.

## Setup Commands

### `setup_knowbase`

Setup Knowledge Base with pgvector extension and migrations.

```bash
python manage.py setup_knowbase [OPTIONS]
```

**Options:**
- `--skip-extensions` - Skip creating PostgreSQL extensions

---

## Complete Setup

### First-Time Setup

```bash
python manage.py setup_knowbase
```

**What it does:**
1. ✅ Creates `pgvector` extension for vector similarity search
2. ✅ Creates `pg_trgm` extension for text search
3. ✅ Runs required database migrations
4. ✅ Sets up vector indexes

**Output:**
```
🚀 Setting up Knowledge Base...
📦 Creating PostgreSQL extensions...
  ✓ pgvector extension created
  ✓ pg_trgm extension created
✅ Knowledge Base setup completed!
```

### Skip Extensions (Already Created)

```bash
python manage.py setup_knowbase --skip-extensions
```

**Use when:**
- Extensions already created manually
- Running as non-superuser
- Extensions exist from previous setup

---

## Statistics Commands

### `knowbase_stats`

Display knowledge base statistics and metrics.

```bash
python manage.py knowbase_stats [OPTIONS]
```

**Options:**
- `--format [json|yaml|table]` - Output format (default: table)
- `--detailed` - Show detailed statistics

---

## Viewing Statistics

### Basic Statistics

```bash
python manage.py knowbase_stats
```

**Output:**
```
📚 Knowledge Base Statistics
==================================================
Documents:              1,234
Embeddings:            1,234
Average Embedding Size: 1536
Storage Used:          45.2 MB
Last Updated:          2025-10-01 14:30:00
```

### Detailed Statistics

```bash
python manage.py knowbase_stats --detailed
```

**Additional output:**
```
Document Types:
  Text:      856 (69.4%)
  PDF:       234 (19.0%)
  Markdown:  144 (11.6%)

Index Performance:
  Average Query Time:    12ms
  Cache Hit Rate:        87.3%
  Total Queries (24h):   4,567

Storage Breakdown:
  Documents:    12.3 MB
  Embeddings:   32.9 MB
  Indexes:      0.8 MB
```

### JSON Export

```bash
python manage.py knowbase_stats --format json
```

**Output:**
```json
{
  "documents": 1234,
  "embeddings": 1234,
  "average_embedding_size": 1536,
  "storage_used_mb": 45.2,
  "last_updated": "2025-10-01T14:30:00Z",
  "document_types": {
    "text": 856,
    "pdf": 234,
    "markdown": 144
  }
}
```

### YAML Export

```bash
python manage.py knowbase_stats --format yaml
```

**Output:**
```yaml
documents: 1234
embeddings: 1234
average_embedding_size: 1536
storage_used_mb: 45.2
last_updated: "2025-10-01T14:30:00Z"
document_types:
  text: 856
  pdf: 234
  markdown: 144
```

---

## PostgreSQL Extensions

### pgvector Extension

**Purpose:** Enables vector similarity search

**Features:**
- Store embeddings as vector data types
- Similarity search (cosine, L2, inner product)
- Indexing for fast retrieval
- Works with OpenAI, Cohere, Hugging Face embeddings

**Example query:**
```sql
SELECT * FROM knowbase_document
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 10;
```

### pg_trgm Extension

**Purpose:** Enables fuzzy text search

**Features:**
- Trigram-based text search
- Fuzzy matching
- Fast text similarity queries
- Works with LIKE, ILIKE, similarity()

**Example query:**
```sql
SELECT * FROM knowbase_document
WHERE content % 'search query'
ORDER BY similarity(content, 'search query') DESC;
```

---

## Common Tasks

### Initial Setup Workflow

```bash
# 1. Setup Knowledge Base
python manage.py setup_knowbase

# 2. Verify setup
python manage.py knowbase_stats

# 3. Check database extensions
psql -d your_database -c "\dx"
```

### Manual Extension Creation

If `setup_knowbase` fails due to permissions:

```bash
# Connect as PostgreSQL superuser
psql -U postgres -d your_database

# Create extensions manually
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

# Verify extensions
\dx
```

Then run setup without extensions:

```bash
python manage.py setup_knowbase --skip-extensions
```

### Monitor Knowledge Base Growth

```bash
# Create script to track growth
#!/bin/bash
while true; do
  echo "$(date)"
  python manage.py knowbase_stats --format json | jq '.documents'
  sleep 3600  # Every hour
done
```

### Export Statistics for Monitoring

```bash
# Export to monitoring system
python manage.py knowbase_stats --format json > /var/log/knowbase_stats.json

# Schedule with cron
0 * * * * cd /path/to/project && python manage.py knowbase_stats --format json > /var/log/knowbase_stats_$(date +\%Y\%m\%d_\%H).json
```

---

## Configuration

### Database Requirements

**Minimum PostgreSQL Version:** 11+
**Recommended Version:** 14+

### pgvector Configuration

Add to `postgresql.conf`:

```conf
# Increase shared_buffers for better vector performance
shared_buffers = 256MB

# Optimize for vector operations
max_parallel_workers_per_gather = 4
```

### Django Configuration

```python
# config.py
from django_cfg import DjangoConfig, DatabaseConfig

class MyConfig(DjangoConfig):
    # Enable Knowledge Base
    enable_knowbase: bool = True

    # Configure database
    databases: dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(
            engine="postgresql",
            name="mydb",
            host="localhost",
            port=5432,
        )
    }
```

---

## Troubleshooting

### Extension Creation Failed

**Error:**
```
❌ Failed to create extensions: permission denied
```

**Solution:**
```bash
# Option 1: Run as superuser
psql -U postgres -d your_database -c "CREATE EXTENSION vector;"
psql -U postgres -d your_database -c "CREATE EXTENSION pg_trgm;"

# Option 2: Grant permissions
GRANT CREATE ON DATABASE your_database TO your_user;
```

### Missing pgvector Extension

**Error:**
```
could not open extension control file: No such file or directory
```

**Solution:**
```bash
# Install pgvector
# Ubuntu/Debian
sudo apt-get install postgresql-14-pgvector

# macOS (Homebrew)
brew install pgvector

# From source
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

### Performance Issues

**Slow queries?**

```sql
-- Create indexes for better performance
CREATE INDEX ON knowbase_document USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX ON knowbase_document USING gin (content gin_trgm_ops);
```

---

## Best Practices

### 1. Setup Early in Development

```bash
# Run setup immediately after project creation
django-cfg create-project "My Project" && \
cd my_project && \
python manage.py migrate_all && \
python manage.py setup_knowbase
```

### 2. Monitor Storage Usage

```bash
# Check storage regularly
python manage.py knowbase_stats --detailed

# Set up alerts for storage limits
```

### 3. Regular Statistics Export

```bash
# Daily statistics export
0 0 * * * python manage.py knowbase_stats --format json > /backups/kb_stats_$(date +\%Y\%m\%d).json
```

### 4. Backup Extensions Configuration

```bash
# Backup PostgreSQL extensions
pg_dump --schema-only --create your_database > extensions_backup.sql
```

### 5. Test Vector Search Performance

```python
# In Django shell
from django_cfg.apps.knowbase.models import Document
import time

start = time.time()
results = Document.objects.vector_search("test query", limit=10)
duration = time.time() - start

print(f"Query took {duration*1000:.2f}ms")
```

---

## Related Documentation

- **[Quick Reference](./quick-reference)** - Fast command lookup
- **[AI Agents Commands](./ai-agents)** - Agent management
- **[Knowledge Base Guide](/features/built-in-apps/ai-knowledge/knowbase-setup)** - Complete KB documentation

---

**Knowledge Base powers semantic search!** 📚
