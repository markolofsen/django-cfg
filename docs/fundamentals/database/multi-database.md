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

### Configuration

```python
# config.py
from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    """Multi-database configuration."""
    # Main database
    url: str = "sqlite:///db/default.sqlite3"

    # Domain-specific databases
    url_blog: str = "sqlite:///db/blog.sqlite3"
    url_shop: str = "sqlite:///db/shop.sqlite3"
```

### YAML Configuration

```yaml
# config.yaml
database:
  url: "postgresql://localhost/main"
  url_blog: "postgresql://localhost/blog_db"
  url_shop: "postgresql://localhost/shop_db"
```

### Settings Integration

```python
# settings.py
import dj_database_url
from django_cfg import load_config

config = load_config()

DATABASES = {
    'default': dj_database_url.parse(config.database.url),
    'blog_db': dj_database_url.parse(config.database.url_blog),
    'shop_db': dj_database_url.parse(config.database.url_shop),
}

DATABASE_ROUTERS = ['django_cfg.routing.DatabaseRouter']

DATABASE_ROUTING_RULES = {
    'blog': 'blog_db',
    'shop': 'shop_db',
}
```

## Database Architecture

:::info[Multi-Database Benefits]
The multi-database setup provides:
- ✅ **Data isolation** - Logical separation of concerns
- ✅ **Scalability** - Independent scaling of different data stores
- ✅ **Performance** - Reduced contention on main database
- ✅ **Flexibility** - Different databases can use different engines
:::

### Architecture Diagram

```mermaid
graph TB
    subgraph "Django Application"
        BlogApp[Blog App]
        ShopApp[Shop App]
        AuthApp[Auth/Users]
    end

    subgraph "Database Router"
        Router[DatabaseRouter]
        Rules[ROUTING_RULES]
    end

    subgraph "Databases"
        BlogDB[(blog_db<br/>PostgreSQL)]
        ShopDB[(shop_db<br/>PostgreSQL)]
        MainDB[(default<br/>PostgreSQL)]
    end

    BlogApp -->|Query| Router
    ShopApp -->|Query| Router
    AuthApp -->|Query| Router

    Router -->|Check| Rules
    Rules -->|blog → blog_db| BlogDB
    Rules -->|shop → shop_db| ShopDB
    Rules -->|default → default| MainDB

    style BlogDB fill:#e1f5ff
    style ShopDB fill:#fff4e1
    style MainDB fill:#e8f5e9
    style Router fill:#fce4ec
```

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

## Production Example

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
DATABASES = {
    'default': dj_database_url.parse(config.database.url),
    'blog_db': dj_database_url.parse(config.database.url_blog),
    'shop_db': dj_database_url.parse(config.database.url_shop),
    'analytics': dj_database_url.parse(config.database.url_analytics),
}

DATABASE_ROUTING_RULES = {
    'blog': 'blog_db',
    'shop': 'shop_db',
    'analytics': 'analytics',
}
```

## Environment-Specific Configuration

### Development (SQLite)

```yaml
# config.dev.yaml
database:
  url: "sqlite:///db/default.sqlite3"
  url_blog: "sqlite:///db/blog.sqlite3"
  url_shop: "sqlite:///db/shop.sqlite3"
```

### Production (PostgreSQL)

```yaml
# config.prod.yaml
database:
  url: "postgresql://user:${DB_PASSWORD}@db.example.com/main"
  url_blog: "postgresql://user:${DB_PASSWORD}@db.example.com/blog"
  url_shop: "postgresql://user:${DB_PASSWORD}@db.example.com/shop"
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
