---
title: Multi-Database Setup
description: Django-CFG multi database guide. Practical tutorial for multi-database setup with real-world examples, troubleshooting tips, and production patterns.
sidebar_label: Multi-Database
sidebar_position: 2
keywords:
  - django-cfg multi database
  - django-cfg guide multi database
  - how to multi database django
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Multi-Database Configuration

:::tip[Automatic Database Routing]
Django-CFG provides **automatic database routing** - no need to manually specify `using()` on every query. Configure once, and all queries route to the correct database automatically.
:::

Configure multiple databases with automatic routing in Django-CFG.

```mermaid
graph LR
    A[Django ORM<br/>Query] --> R[Database<br/>Router]

    R -->|Auth| DB1[(Default DB)]
    R -->|Blog| DB2[(Blog DB)]
    R -->|Shop| DB3[(Shop DB)]
```

## Basic Multi-Database Setup

<Tabs groupId="setup-pattern">
  <TabItem value="simple" label="Simple Setup (2-3 databases)" default>

### Simple Multi-Database Pattern

Perfect for small to medium projects with 2-3 databases.

```python
# config.py
from django_cfg import DjangoConfig
from django_cfg.models import DatabaseConfig

class MyConfig(DjangoConfig):
    databases = {
        "default": DatabaseConfig(
            engine="django.db.backends.postgresql",
            name="main_db",
            user="postgres",
            password="${DB_PASSWORD}",
            host="localhost",
        ),
        "blog_db": DatabaseConfig(
            engine="django.db.backends.postgresql",
            name="blog_db",
            user="postgres",
            password="${DB_PASSWORD}",
            host="localhost",
        ),
    }

    database_routers = ["django_cfg.routing.routers.AppDatabaseRouter"]

    # Routing rules
    database_routing_rules = {
        "blog": "blog_db",  # Blog app → blog_db
    }
```

:::info[Simple Pattern Benefits]
- ✅ **Easy to understand** - Clear database definitions
- ✅ **Type-safe** - Full IDE autocomplete
- ✅ **Automatic routing** - No manual `using()` calls
- ✅ **Environment variables** - Secure credential management
:::

</TabItem>
<TabItem value="advanced" label="Advanced Setup (4+ databases)">

### Advanced Multi-Database Pattern

For large applications with multiple domains and services.

```python
# config.py
from django_cfg import DjangoConfig
from django_cfg.models import DatabaseConfig

class MyConfig(DjangoConfig):
    databases = {
        # Core databases
        "default": DatabaseConfig(
            engine="django.db.backends.postgresql",
            name="main",
            user="${DB_USER}",
            password="${DB_PASSWORD}",
            host="${DB_HOST}",
            conn_max_age=600,  # Connection pooling
        ),

        # Domain databases
        "blog_db": DatabaseConfig(
            engine="django.db.backends.postgresql",
            name="blog",
            user="${DB_USER}",
            password="${DB_PASSWORD}",
            host="${DB_BLOG_HOST}",
            conn_max_age=600,
        ),

        "shop_db": DatabaseConfig(
            engine="django.db.backends.postgresql",
            name="shop",
            user="${DB_USER}",
            password="${DB_PASSWORD}",
            host="${DB_SHOP_HOST}",
            conn_max_age=600,
        ),

        # Analytics - read-only replica
        "analytics": DatabaseConfig(
            engine="django.db.backends.postgresql",
            name="analytics",
            user="${DB_READONLY_USER}",
            password="${DB_READONLY_PASSWORD}",
            host="${DB_ANALYTICS_HOST}",
            options={"connect_timeout": 10, "options": "-c default_transaction_read_only=on"},
        ),
    }

    database_routers = ["django_cfg.routing.routers.AppDatabaseRouter"]

    database_routing_rules = {
        "blog": "blog_db",
        "shop": "shop_db",
        "analytics": "analytics",
    }
```

:::tip[Advanced Pattern Benefits]
- ✅ **Scalability** - Separate databases per domain
- ✅ **Connection pooling** - Better performance
- ✅ **Read replicas** - Analytics on separate database
- ✅ **Per-database hosts** - Distributed architecture
:::

</TabItem>
<TabItem value="microservices" label="Microservices Pattern">

### Microservices Database Pattern

Each service has its own database with shared authentication.

```python
# config.py
from django_cfg import DjangoConfig
from django_cfg.models import DatabaseConfig

class MyConfig(DjangoConfig):
    databases = {
        # Shared auth database
        "default": DatabaseConfig(
            engine="django.db.backends.postgresql",
            name="auth_service",
            user="${DB_USER}",
            password="${DB_PASSWORD}",
            host="${DB_AUTH_HOST}",
        ),

        # Blog microservice
        "blog_service": DatabaseConfig(
            engine="django.db.backends.postgresql",
            name="blog_service",
            user="${DB_USER}",
            password="${DB_PASSWORD}",
            host="${DB_BLOG_HOST}",
        ),

        # Shop microservice
        "shop_service": DatabaseConfig(
            engine="django.db.backends.postgresql",
            name="shop_service",
            user="${DB_USER}",
            password="${DB_PASSWORD}",
            host="${DB_SHOP_HOST}",
        ),

        # Payment microservice
        "payment_service": DatabaseConfig(
            engine="django.db.backends.postgresql",
            name="payment_service",
            user="${DB_USER}",
            password="${DB_PASSWORD}",
            host="${DB_PAYMENT_HOST}",
        ),
    }

    database_routers = ["django_cfg.routing.routers.AppDatabaseRouter"]

    database_routing_rules = {
        "blog": "blog_service",
        "shop": "shop_service",
        "payments": "payment_service",
    }
```

:::warning[Microservices Considerations]
**Benefits:**
- ✅ Service isolation - Each service has independent database
- ✅ Independent scaling - Scale databases separately
- ✅ Technology diversity - Different DB engines per service

**Challenges:**
- ⚠️ **Cross-service queries** - Must use `db_constraint=False` for FKs
- ⚠️ **Distributed transactions** - No ACID across services
- ⚠️ **Data consistency** - Eventual consistency patterns needed
- ⚠️ **Testing complexity** - Multiple databases to seed
:::

</TabItem>
</Tabs>

## YAML Configuration

```yaml
# config.yaml
database:
  url: "postgresql://user:${DB_PASSWORD}@localhost:5432/main_db"
  url_blog: "postgresql://user:${DB_PASSWORD}@localhost:5432/blog_db"
  url_shop: "postgresql://user:${DB_PASSWORD}@localhost:5432/shop_db"
```

### URL Format Examples

**SQLite (Development):**
```yaml
database:
  url: "sqlite:///db/default.sqlite3"
  url_blog: "sqlite:///db/blog.sqlite3"
```

**PostgreSQL (Production):**
```yaml
database:
  url: "postgresql://user:pass@db-main.example.com:5432/main"
  url_blog: "postgresql://user:pass@db-blog.example.com:5432/blog"
```

**With SSL:**
```yaml
database:
  url: "postgresql://user:pass@localhost/main?sslmode=require"
```

## Database Routing

Django-CFG automatically routes database operations based on `DATABASE_ROUTING_RULES`:

```python
# settings.py
DATABASE_ROUTING_RULES = {
    'blog': 'blog_db',    # All blog app models → blog_db
    'shop': 'shop_db',    # All shop app models → shop_db
    # Apps not listed → default database
}
```

### Automatic Routing

```python
# models.py - apps/blog/models.py
class Post(models.Model):
    title = models.CharField(max_length=200)
    # No need to specify database!

# Usage - automatically routed to blog_db
Post.objects.create(title="Hello")
Post.objects.all()  # Queries blog_db automatically
```

## Cross-Database ForeignKeys

:::danger[CRITICAL: db_constraint=False Required]
When creating ForeignKeys to models in different databases (e.g., User in default, Post in blog_db), **you MUST use `db_constraint=False`**. This is required because database constraints cannot span multiple databases.
:::

```mermaid
graph TB
    subgraph "Default Database"
        U[User Model<br/>id=1, username='john']
    end

    subgraph "Blog Database"
        P[Post Model<br/>id=1, title='Hello'<br/>author_id=1]
    end

    subgraph "Django ORM Layer"
        FK[ForeignKey Relationship<br/>db_constraint=False]
    end

    U -.->|"Application-level<br/>relationship"| FK
    FK -.->|"No DB constraint"| P
```

### Implementation

```python
# apps/blog/models.py
from django.contrib.auth import get_user_model

User = get_user_model()  # Lives in 'default' database

class Post(models.Model):
    title = models.CharField(max_length=200)

    # Cross-database ForeignKey
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_posts',
        db_constraint=False  # ⚠️ REQUIRED for cross-database FK
    )

    class Meta:
        db_table = 'blog_post'
```

### Why `db_constraint=False`?

<Tabs>
  <TabItem value="explanation" label="Explanation" default>

**Technical reasons:**
- User model is in `default` database
- Post model is in `blog_db` database
- **Database-level foreign key constraints cannot span databases**
- Django ORM handles the relationship at application level
- Without it: `relation "auth_user" does not exist` error during migrations

**How it works:**
1. Django stores only the foreign key value (`author_id=1`)
2. No database constraint created
3. Relationship resolved at application level when accessed
4. `post.author` triggers ORM query to default database

</TabItem>
<TabItem value="tradeoffs" label="Trade-offs">

**Benefits:**
- ✅ **Cross-database relationships work** - Link models across databases
- ✅ **Django ORM validates relationships** - `post.author`, `user.blog_posts` work
- ✅ **Automatic routing** - ORM queries correct database for each model
- ✅ **Select/prefetch works** - Can optimize queries with `select_related()`

**Limitations:**
- ❌ **No database-level referential integrity** - Database won't enforce constraint
- ❌ **No automatic cascade deletes at DB level** - Django handles in Python
- ❌ **Orphaned records possible** - If you delete directly in database
- ❌ **Performance overhead** - Relationship validation happens in Python

</TabItem>
<TabItem value="best-practices" label="Best Practices">

**✅ Do:**
```python
# Use db_constraint=False for cross-database FKs
author = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    db_constraint=False,  # ✅ Required
)

# Use Django ORM for all deletes
user.delete()  # ✅ Cascades to related posts in blog_db
```

**❌ Don't:**
```python
# Don't omit db_constraint=False
author = models.ForeignKey(User)  # ❌ Will fail during migration

# Don't delete directly in database
# DELETE FROM auth_user WHERE id=1;  # ❌ Orphans posts in blog_db

# Don't use database-level cascades
# They won't work across databases
```

**Validation strategy:**
```python
# Add application-level validation
class Post(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_constraint=False,
    )

    def clean(self):
        # Validate author exists
        if not User.objects.filter(id=self.author_id).exists():
            raise ValidationError("Author does not exist")
```

</TabItem>
</Tabs>

## Migration Commands

Django-CFG provides two commands for multi-database migrations:

### migrate_all (Recommended for Production)

Automatically migrates all databases:

```bash
# Migrate all databases
python manage.py migrate_all

# Skip automatic makemigrations
python manage.py migrate_all --skip-makemigrations
```

**Features:**
- Auto-detects all databases
- Creates migrations first
- Migrates each database based on routing rules
- Handles constance app automatically

### migrator (Recommended for Development)

Interactive migration tool with auto mode:

```bash
# Auto mode - migrates all databases without prompts
python manage.py migrator --auto

# Interactive mode - shows menu
python manage.py migrator

# Migrate specific database
python manage.py migrator --database blog_db

# Migrate specific app
python manage.py migrator --app blog
```

**See:** [Core Commands](/cli/commands/core-commands#migrator) for detailed migrator documentation.

## Complete Production Example

```yaml
# config.prod.yaml
database:
  # Main database
  url: "postgresql://user:${DB_PASSWORD}@db-main.example.com:5432/main?sslmode=require&connect_timeout=10"

  # Domain databases
  url_blog: "postgresql://user:${DB_PASSWORD}@db-blog.example.com:5432/blog?sslmode=require"
  url_shop: "postgresql://user:${DB_PASSWORD}@db-shop.example.com:5432/shop?sslmode=require"

  # Analytics - read-only
  url_analytics: "postgresql://readonly:${DB_READONLY_PASSWORD}@warehouse.example.com:5432/analytics?sslmode=require"
```

```python
# settings.py
import dj_database_url
from django_cfg import load_config

config = load_config()

DATABASES = {
    'default': dj_database_url.parse(config.database.url),
    'blog_db': dj_database_url.parse(config.database.url_blog),
    'shop_db': dj_database_url.parse(config.database.url_shop),
    'analytics': dj_database_url.parse(config.database.url_analytics),
}

DATABASE_ROUTERS = ['django_cfg.routing.DatabaseRouter']

DATABASE_ROUTING_RULES = {
    'blog': 'blog_db',
    'shop': 'shop_db',
    'analytics': 'analytics',
}
```

## Testing Multi-Database Setup

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

## See Also

### Database Configuration

**Core Database Setup:**
- [**Database Configuration**](/fundamentals/database) - Complete database configuration guide
- [**Database Routing**](/fundamentals/system/routing) - Advanced routing strategies and patterns
- [**Configuration Models**](/fundamentals/configuration) - Database config API reference

**Infrastructure:**
- [**Cache Configuration**](/fundamentals/configuration/cache) - Redis for multi-database caching
- [**Environment Detection**](/fundamentals/configuration/environment) - Database per environment
- [**Docker Deployment**](/guides/docker/production) - Multi-database in Docker

### Configuration & Setup

**Getting Started:**
- [**Installation**](/getting-started/installation) - Install Django-CFG
- [**Configuration Guide**](/getting-started/configuration) - YAML configuration setup
- [**First Project**](/getting-started/first-project) - Quick start with database

**Production:**
- [**Production Config**](./production-config) - Production database setup
- [**Environment Variables**](/fundamentals/configuration/environment) - Secure database credentials
- [**Type-Safe Configuration**](/fundamentals/core/type-safety) - Database config validation

### Examples & Guides

**Practical Examples:**
- [**Sample Project**](./sample-project/overview) - Multi-database example project
- [**Sample Project Multi-DB**](./sample-project/multi-database) - Detailed multi-database setup
- [**Examples Guide**](./examples) - Real-world database patterns

**Related Guides:**
- [**Migration Guide**](./migration-guide) - Migrate existing multi-database projects
- [**Troubleshooting**](./troubleshooting) - Common database issues

### Tools & Operations

**CLI & Management:**
- [**CLI Tools**](/cli/introduction) - Database management commands
- [**Core Commands**](/cli/commands/core-commands) - Migration and database commands

**Background Processing:**
- [**Dramatiq Integration**](/features/integrations/dramatiq/overview) - Task routing per database
- [**Background Tasks**](/features/built-in-apps/operations/tasks) - Database-aware tasks

**Note:** All examples use YAML-based configuration via `env` loader. See [Configuration Guide](/getting-started/configuration) for setup.
