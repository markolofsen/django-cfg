---
title: Multi-Database Setup
description: Configure multiple databases with Django-CFG
sidebar_label: Multi-Database
sidebar_position: 3
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Multi-Database Setup

:::tip[Automatic Database Routing]
Django-CFG provides **automatic database routing** based on app labels - configure once, route everywhere automatically.
:::

Configure multiple databases with automatic routing in Django-CFG.

## Quick Start

:::warning[Do You Really Need This?]
**Most SaaS applications use a single database.** Multi-database is an advanced feature needed only for:
- Read replicas (performance scaling)
- Analytics/reporting warehouse
- Legacy system integration
- Multi-tenant isolation (complex)

**Default recommendation:** Use one database with multiple Django apps.
:::

### Single Database Setup (Recommended)

```python
# api/environment/loader.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseConfig(BaseSettings):
    """Single database configuration."""
    url: str = Field(default="sqlite:///db/default.sqlite3")

    model_config = SettingsConfigDict(
        env_prefix="DATABASE__",
        env_nested_delimiter="__",
    )
```

```bash
# .env
DATABASE__URL="postgresql://localhost/mydb"
```

```python
# api/config.py
from django_cfg import DjangoConfig, DatabaseConfig
from .environment import env

class MyDjangoConfig(DjangoConfig):
    databases = {
        "default": DatabaseConfig.from_url(url=env.database.url),
    }

config = MyDjangoConfig()
```

**Your Django apps** (e.g., crypto, profiles, trading) all use the default database automatically.

---

### Multi-Database Setup (Advanced)

For **read replicas**, **analytics warehouses**, or **legacy system integration**:

```python
# api/environment/loader.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseConfig(BaseSettings):
    """Multi-database configuration."""
    # Primary database
    url: str = Field(default="sqlite:///db/default.sqlite3")

    # Read replica (optional)
    url_replica: str | None = Field(default=None)

    # Analytics warehouse (optional)
    url_analytics: str | None = Field(default=None)

    model_config = SettingsConfigDict(
        env_prefix="DATABASE__",
        env_nested_delimiter="__",
    )
```

```bash
# .env or system ENV
DATABASE__URL="postgresql://user:pass@db-primary.example.com/mydb"
DATABASE__URL_REPLICA="postgresql://readonly:pass@db-replica.example.com/mydb"
DATABASE__URL_ANALYTICS="postgresql://analytics:pass@warehouse.example.com/analytics"
```

```python
# api/config.py
from django_cfg import DjangoConfig, DatabaseConfig
from .environment import env

class MyDjangoConfig(DjangoConfig):
    databases = {
        "default": DatabaseConfig.from_url(url=env.database.url),
    }

    # Add replica if configured
    if env.database.url_replica:
        databases["replica"] = DatabaseConfig.from_url(url=env.database.url_replica)

    # Add analytics if configured
    if env.database.url_analytics:
        databases["analytics"] = DatabaseConfig.from_url(url=env.database.url_analytics)

    # Optional: Configure routing rules
    # database_routers = ["myapp.routers.ReadReplicaRouter"]

config = MyDjangoConfig()
```

**Common use cases:**
- **Read replica** - Route 80% of read queries to replica for performance
- **Analytics warehouse** - Separate database for heavy reporting queries
- **Legacy integration** - Connect to existing external database

---

## Database Architecture

:::info[Multi-Database Benefits]
The multi-database setup provides:
- ✅ **Data isolation** - Logical separation of concerns
- ✅ **Scalability** - Independent scaling of different data stores
- ✅ **Performance** - Reduced contention on main database
- ✅ **Flexibility** - Different databases can use different engines
:::

### Architecture Diagram - Read Replica Pattern

```mermaid
graph TB
    subgraph "Django Application"
        App[SaaS App]
        Analytics[Analytics/Reports]
    end

    subgraph "Database Router"
        Router[ReadReplicaRouter]
    end

    subgraph "Databases"
        Primary[(Primary DB<br/>Read+Write)]
        Replica[(Replica DB<br/>Read Only)]
        Warehouse[(Analytics<br/>Read Only)]
    end

    App -->|Writes| Primary
    App -->|80% Reads| Replica
    App -->|20% Reads| Primary
    Analytics -->|Heavy Queries| Warehouse

    Primary -.->|Replication| Replica
    Primary -.->|ETL Pipeline| Warehouse

    style Primary fill:#e8f5e9
    style Replica fill:#e1f5ff
    style Warehouse fill:#fff4e1
    style Router fill:#fce4ec
```

**Pattern: Read Replica**
- All writes → Primary
- Most reads → Replica (reduces primary load)
- Analytics → Separate warehouse

### Example Architecture

<Tabs>
  <TabItem value="basic" label="Basic Setup" default>

**3-Database Architecture:**

1. **default** - Main database for users, sessions, authentication
2. **blog_db** - Dedicated database for blog content
3. **shop_db** - Separate database for e-commerce data

:::note[When to Use]
Use multi-database when you need:
- Logical separation between domains
- Different backup strategies
- Independent scaling per domain
- Team-based database access control
:::

  </TabItem>
  <TabItem value="advanced" label="Advanced Setup">

**5-Database Architecture:**

1. **default** - Core application data
2. **blog_db** - Content management
3. **shop_db** - E-commerce transactions
4. **analytics** - Data warehouse (read-only)
5. **cache_db** - Cache persistence

:::tip[Enterprise Pattern]
Large applications often use:
- **Read replicas** for heavy read operations
- **Write master** for all write operations
- **Analytics warehouse** for reporting
- **Separate cache DB** for session storage
:::

  </TabItem>
</Tabs>

## Automatic Routing

Django-CFG automatically routes database operations based on `DATABASE_ROUTING_RULES`:

```python
# settings.py
DATABASE_ROUTING_RULES = {
    'blog': 'blog_db',    # All blog app models → blog_db
    'shop': 'shop_db',    # All shop app models → shop_db
    # Apps not listed → default database
}
```

### Usage Example

```python
# Blog operations automatically use blog_db
from apps.blog.models import Post

post = Post.objects.create(
    title="My First Post",
    content="Hello Django-CFG!"
)
# Automatically routed to blog_db

# Shop operations automatically use shop_db
from apps.shop.models import Product

product = Product.objects.create(
    name="Django-CFG Book",
    price=29.99
)
# Automatically routed to shop_db

# User operations automatically use default
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.create_user(
    email="user@example.com",
    password="secure_password"
)
# Automatically routed to default database
```

## Production Examples

### Example 1: Single Database (Most Common)

```bash
# Production environment variables (Docker/K8s)
DATABASE__URL="postgresql://user:${DB_PASSWORD}@db.example.com:5432/mydb?sslmode=require&connect_timeout=10"
```

```python
# api/config.py
from django_cfg import DjangoConfig, DatabaseConfig
from .environment import env

class MyDjangoConfig(DjangoConfig):
    databases = {
        "default": DatabaseConfig.from_url(url=env.database.url),
    }
```

All your apps (crypto, profiles, trading, etc.) use this single database.

---

### Example 2: Primary + Read Replica (Performance Scaling)

```bash
# Production environment variables
DATABASE__URL="postgresql://app:${DB_PASSWORD}@db-primary.example.com:5432/mydb?sslmode=require"
DATABASE__URL_REPLICA="postgresql://readonly:${DB_READONLY_PASSWORD}@db-replica.example.com:5432/mydb?sslmode=require"
```

```python
# api/environment/loader.py
class DatabaseConfig(BaseSettings):
    url: str = Field(default="sqlite:///db/default.sqlite3")
    url_replica: str | None = Field(default=None)

    model_config = SettingsConfigDict(
        env_prefix="DATABASE__",
        env_nested_delimiter="__",
    )
```

```python
# api/config.py
class MyDjangoConfig(DjangoConfig):
    databases = {
        "default": DatabaseConfig.from_url(url=env.database.url),
    }

    if env.database.url_replica:
        databases["replica"] = DatabaseConfig.from_url(url=env.database.url_replica)
        database_routers = ["myapp.routers.ReadReplicaRouter"]
```

```python
# myapp/routers.py - Custom read replica router
class ReadReplicaRouter:
    """Route reads to replica, writes to primary."""

    def db_for_read(self, model, **hints):
        """80% of reads go to replica."""
        import random
        return 'replica' if random.random() < 0.8 else 'default'

    def db_for_write(self, model, **hints):
        """All writes to primary."""
        return 'default'
```

**Performance gain:** 80% read load shifted to replica → reduces primary DB pressure.

---

### Example 3: Primary + Analytics Warehouse

```bash
# Production environment variables
DATABASE__URL="postgresql://app:${DB_PASSWORD}@db.example.com:5432/mydb"
DATABASE__URL_ANALYTICS="postgresql://analytics:${ANALYTICS_PASSWORD}@warehouse.example.com:5432/analytics"
```

```python
# api/environment/loader.py
class DatabaseConfig(BaseSettings):
    url: str = Field(default="sqlite:///db/default.sqlite3")
    url_analytics: str | None = Field(default=None)

    model_config = SettingsConfigDict(
        env_prefix="DATABASE__",
        env_nested_delimiter="__",
    )
```

```python
# api/config.py
class MyDjangoConfig(DjangoConfig):
    databases = {
        "default": DatabaseConfig.from_url(url=env.database.url),
    }

    if env.database.url_analytics:
        databases["analytics"] = DatabaseConfig.from_url(url=env.database.url_analytics)
```

```python
# apps/reports/views.py - Use analytics database explicitly
from django.db import connections

def generate_report(request):
    """Heavy analytics query on separate warehouse."""
    with connections['analytics'].cursor() as cursor:
        cursor.execute("""
            SELECT date_trunc('month', created_at) as month,
                   COUNT(*) as total_users,
                   SUM(revenue) as total_revenue
            FROM analytics.user_metrics
            GROUP BY month
            ORDER BY month DESC
        """)
        results = cursor.fetchall()

    return render(request, 'report.html', {'data': results})
```

**Use case:** Separate heavy reporting queries from transactional database.

## Environment-Specific Configuration

### Development (SQLite)

```bash
# .env (development) - optional, uses defaults if not set
DATABASE__URL="sqlite:///db/dev.sqlite3"
```

Or use defaults in code:

```python
# api/environment/loader.py
class DatabaseConfig(BaseSettings):
    url: str = Field(default="sqlite:///db/default.sqlite3")

    model_config = SettingsConfigDict(
        env_prefix="DATABASE__",
        env_nested_delimiter="__",
    )
```

### Production (PostgreSQL)

```bash
# System ENV or Docker environment
DATABASE__URL="postgresql://user:${DB_PASSWORD}@db.example.com/mydb?sslmode=require"
```

## Testing Setup

```bash
# Create migrations
python manage.py makemigrations

# Migrate all databases
python manage.py migrate_all

# Or use migrator in auto mode
python manage.py migrator --auto

# Test routing in shell
python manage.py shell
```

```python
# Shell - test automatic routing
from apps.blog.models import Post
from django.contrib.auth import get_user_model

User = get_user_model()

# Create user in default database
user = User.objects.create_user(username='john', email='john@example.com')

# Create post in blog_db with cross-database FK
post = Post.objects.create(
    title='Hello World',
    content='Multi-database setup works!',
    author=user  # Cross-database FK
)

# Test relationships
print(post.author.username)  # 'john'
print(user.blog_posts.all())  # QuerySet with post
```

## Best Practices

### 1. Consistent Naming

Use consistent naming convention for database URLs:

```python
url: str        # Main database (always 'default')
url_blog: str   # Blog database → 'blog_db' in DATABASES
url_shop: str   # Shop database → 'shop_db' in DATABASES
```

### 2. Environment Variables

```bash
# .env
DATABASE_URL="postgresql://user:pass@localhost/main"
DATABASE_URL_BLOG="postgresql://user:pass@localhost/blog"
DATABASE_URL_SHOP="postgresql://user:pass@localhost/shop"
```

### 3. Different Engines Per Environment

```yaml
# Development - fast SQLite
database:
  url: "sqlite:///db/default.sqlite3"
  url_blog: "sqlite:///db/blog.sqlite3"
```

```yaml
# Production - robust PostgreSQL
database:
  url: "postgresql://user:pass@db.example.com/main"
  url_blog: "postgresql://user:pass@db.example.com/blog"
```

## See Also

- [**Routing**](./routing) - Database routing details
- [**Migrations**](./migrations) - migrate_all and migrator commands
- [**Cross-Database Relations**](./cross-database-relations) - ForeignKeys across databases
- [**Multi-Database Guide**](/guides/multi-database) - Complete guide
