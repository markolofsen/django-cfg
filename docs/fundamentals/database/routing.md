---
title: Database Routing
description: Automatic database routing with Django-CFG
sidebar_label: Routing
sidebar_position: 4
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Database Routing

Django-CFG provides automatic database routing based on app labels with zero manual `.using()` calls.

:::info[Automatic Routing]
The `DatabaseRouter` automatically routes **100% of queries** to the correct database based on app labels—no manual `.using()` calls needed!
:::

## How It Works

The `DatabaseRouter` automatically routes database operations based on `DATABASE_ROUTING_RULES`:

```python
# settings.py
DATABASE_ROUTERS = ['django_cfg.routing.DatabaseRouter']

DATABASE_ROUTING_RULES = {
    'blog': 'blog_db',
    'shop': 'shop_db',
    # Apps not listed → default database
}
```

## Router Implementation

The `DatabaseRouter` provides four key methods:

<Tabs groupId="router-methods">
  <TabItem value="read" label="Read Operations" default>

```python
def db_for_read(self, model, **hints):
    """Route read operations to appropriate database."""
    rules = getattr(settings, 'DATABASE_ROUTING_RULES', {})
    app_label = model._meta.app_label

    return rules.get(app_label, 'default')
```

**Use Case**: Routes `SELECT` queries to the correct database based on model's app_label.

  </TabItem>
  <TabItem value="write" label="Write Operations">

```python
def db_for_write(self, model, **hints):
    """Route write operations to appropriate database."""
    rules = getattr(settings, 'DATABASE_ROUTING_RULES', {})
    app_label = model._meta.app_label

    return rules.get(app_label, 'default')
```

**Use Case**: Routes `INSERT`, `UPDATE`, `DELETE` operations to the correct database.

  </TabItem>
  <TabItem value="relations" label="Relationships">

```python
def allow_relation(self, obj1, obj2, **hints):
    """
    Allow relations between objects.

    - Both routed to SAME db → allow
    - One or both NOT routed → allow (enables cross-db FK)
    - Both routed to DIFFERENT dbs → deny
    """
    rules = getattr(settings, 'DATABASE_ROUTING_RULES', {})
    db1 = rules.get(obj1._meta.app_label)
    db2 = rules.get(obj2._meta.app_label)

    # If both are routed, they must be in the same database
    if db1 and db2:
        return db1 == db2

    # If one or both are not routed, allow the relation
    # This enables cross-database ForeignKeys to shared models (e.g., User)
    return True
```

**Use Case**: Controls whether ForeignKey relationships are allowed between models in different databases.

  </TabItem>
  <TabItem value="migrations" label="Migrations">

```python
def allow_migrate(self, db, app_label, **hints):
    """Control which apps can migrate on which databases."""
    rules = getattr(settings, 'DATABASE_ROUTING_RULES', {})
    target_db = rules.get(app_label)

    if target_db:
        # App IS routed → allow only on target db
        return db == target_db

    # Check if this db is used by other apps
    if db in rules.values():
        # This db is used by other apps → don't migrate default apps here
        return False

    # Default apps → migrate on default database
    return db == 'default'
```

**Use Case**: Controls which migrations run on which databases. Prevents accidental migrations to wrong database.

  </TabItem>
</Tabs>

## Configuration

### Setup

:::warning[Advanced Feature]
Most applications don't need database routing. Use this **only** if you have:
- Multiple physical databases for different modules
- Read replicas for performance
- Separate analytics/reporting database
:::

```python
# api/config.py - ONLY use if you need multiple databases!
from django_cfg import DjangoConfig, DatabaseConfig
from .environment import env

class MyDjangoConfig(DjangoConfig):
    # Single database (default for most SaaS apps)
    databases = {
        "default": DatabaseConfig.from_url(url=env.database.url),
    }

# Generate Django settings
config = MyDjangoConfig()
```

For advanced multi-database setup (rare), see [Multi-Database Guide](./multi-database).

### Environment Configuration

```bash
# .env or system environment variables
DATABASE__URL="postgresql://localhost/mydb"
```

```python
# api/environment/loader.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseConfig(BaseSettings):
    url: str = Field(default="sqlite:///db/default.sqlite3")

    model_config = SettingsConfigDict(
        env_prefix="DATABASE__",
        env_nested_delimiter="__",
    )
```

:::tip[Single Database for SaaS]
Most SaaS applications use a **single database** with multiple apps/modules. Database routing is typically only needed for:
- Read replicas (performance)
- Analytics warehouses (separate reporting DB)
- Legacy system integration
:::

---

## Advanced: Read Replica Setup

For **performance scaling** with read replicas:

### Configuration

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

```bash
# Production ENV
DATABASE__URL="postgresql://app:pass@db-primary.example.com/mydb"
DATABASE__URL_REPLICA="postgresql://readonly:pass@db-replica.example.com/mydb"
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

### Custom Router

```python
# myapp/routers.py
import random

class ReadReplicaRouter:
    """Route 80% of reads to replica, all writes to primary."""

    def db_for_read(self, model, **hints):
        """Most reads go to replica."""
        return 'replica' if random.random() < 0.8 else 'default'

    def db_for_write(self, model, **hints):
        """All writes to primary."""
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations between same database."""
        return True

    def allow_migrate(self, db, app_label, **hints):
        """Only migrate on primary."""
        return db == 'default'
```

### Usage Examples

```python
from apps.profiles.models import User

# Writes always go to primary
user = User.objects.create(email="user@example.com")
# → Routed to 'default' (primary)

# Reads mostly go to replica (80%)
users = User.objects.all()
# → Routed to 'replica' (80%) or 'default' (20%)

# Force specific database when needed
fresh_user = User.objects.using('default').get(id=user.id)
# → Always reads from primary (latest data)

heavy_report = User.objects.using('analytics').aggregate(
    total=Count('*'),
    revenue=Sum('purchases__amount')
)
# → Use analytics warehouse for heavy queries
```

### Manual Database Selection

```python
# Force read from primary (when you need latest data)
latest_user = User.objects.using('default').get(id=123)

# Force read from replica (when eventual consistency is ok)
cached_users = User.objects.using('replica').filter(is_active=True)

# Use analytics database for reports
from django.db import connections

with connections['analytics'].cursor() as cursor:
    cursor.execute("SELECT * FROM user_stats WHERE created_at > NOW() - INTERVAL '30 days'")
    results = cursor.fetchall()
```

## Routing Flow - Read Replica Pattern

<Tabs groupId="routing-flow">
  <TabItem value="read" label="Read Operation" default>

```mermaid
sequenceDiagram
    participant U as User Code
    participant D as Django ORM
    participant R as ReadReplicaRouter
    participant Replica as Replica DB
    participant Primary as Primary DB

    U->>D: User.objects.all()
    D->>R: db_for_read(User)
    R->>R: random() < 0.8?
    alt 80% of time
        R-->>D: Return 'replica'
        D->>Replica: SELECT * FROM users
        Replica-->>D: Query results
    else 20% of time
        R-->>D: Return 'default'
        D->>Primary: SELECT * FROM users
        Primary-->>D: Query results
    end
    D-->>U: QuerySet[User]

    Note over U,Primary: 80% reads → replica, 20% → primary
```

**Flow Steps:**
1. User calls: `User.objects.all()`
2. Django calls: `router.db_for_read(User)`
3. Router randomizes: 80% replica, 20% primary
4. Django executes query on selected database

  </TabItem>
  <TabItem value="write" label="Write Operation">

```mermaid
sequenceDiagram
    participant U as User Code
    participant D as Django ORM
    participant R as ReadReplicaRouter
    participant Primary as Primary DB
    participant Replica as Replica DB

    U->>D: User.objects.create(...)
    D->>R: db_for_write(User)
    R-->>D: Return 'default' (always)
    D->>Primary: INSERT INTO users VALUES (...)
    Primary-->>D: Insert successful (id=123)
    Primary-.>>Replica: Async replication
    D-->>U: User object (id=123)

    Note over U,Replica: All writes → primary, then replicated
```

**Flow Steps:**
1. User calls: `User.objects.create(...)`
2. Django calls: `router.db_for_write(User)`
3. Router always returns: `'default'` (primary)
4. Django executes INSERT on primary
5. Data replicates to replica asynchronously

  </TabItem>
  <TabItem value="migrate" label="Migration">

```mermaid
sequenceDiagram
    participant U as Command Line
    participant M as Migration Command
    participant R as ReadReplicaRouter
    participant Primary as Primary DB

    U->>M: python manage.py migrate
    M->>R: allow_migrate(db='default', app_label='users')
    R->>R: Check if db == 'default'
    R-->>M: Return True
    M->>Primary: Run migrations
    Primary-->>M: Migrations applied
    M-->>U: ✅ Migrations complete

    Note over U,Primary: Only primary gets migrations
```

**Flow Steps:**
1. User runs: `python manage.py migrate`
2. Django calls: `router.allow_migrate(db='default', app_label='users')`
3. Router checks: `db == 'default'` → `True`
4. Django migrates: only on primary
5. Replica syncs schema via replication

  </TabItem>
</Tabs>

## Debugging Routing

### Check Which Database Will Be Used

```python
from django.db import router
from apps.blog.models import Post

# For reading
db = router.db_for_read(Post)
print(f"Post reads from: {db}")  # blog_db

# For writing
db = router.db_for_write(Post)
print(f"Post writes to: {db}")  # blog_db

# Check if migration is allowed
allowed = router.allow_migrate('blog_db', 'blog')
print(f"Migrate blog on blog_db: {allowed}")  # True
```

### View Active Router

```python
from django.conf import settings

print("Active routers:", settings.DATABASE_ROUTERS)
print("Routing rules:", settings.DATABASE_ROUTING_RULES)
```

### Test Routing

```python
# Test automatic routing
post = Post.objects.create(title="Test")
print(post._state.db)  # blog_db

user = User.objects.create_user(email="test@example.com")
print(user._state.db)  # default
```

## Advanced Patterns

<details>
  <summary>📚 Read Replicas - Scale Read Operations</summary>

### Read Replicas Setup

```python
# settings.py
DATABASE_ROUTING_RULES = {
    'blog': 'blog_db',
    'blog_replica': 'blog_replica_db',
}
```

### Custom Router for Load Distribution

```python
class ReplicaRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'blog':
            # 80% of reads go to replica
            import random
            return 'blog_replica_db' if random.random() < 0.8 else 'blog_db'
        return None  # Fall through to next router

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'blog':
            return 'blog_db'  # All writes to primary
        return None
```

### Enable Multi-Router Chain

```python
# settings.py
DATABASE_ROUTERS = [
    'myapp.routers.ReplicaRouter',  # Custom read replica logic
    'django_cfg.routing.DatabaseRouter',  # Fallback routing
]
```

:::tip[Performance Gain]
Read replicas can handle **80% of database load**, reducing primary database pressure and improving response times.
:::

</details>

<details>
  <summary>🔀 Sharding by User - Horizontal Scaling</summary>

### User-Based Sharding

```python
def get_user_shard(user_id):
    """Determine database shard for user."""
    shard_count = 4
    shard_id = user_id % shard_count
    return f"shard_{shard_id}"

# Use in queries
shard = get_user_shard(user.id)
user_posts = Post.objects.using(shard).filter(author=user)
```

### Advanced Sharding Router

```python
class ShardingRouter:
    def db_for_read(self, model, **hints):
        if 'user_id' in hints:
            return get_user_shard(hints['user_id'])
        return None

    def db_for_write(self, model, **hints):
        if 'user_id' in hints:
            return get_user_shard(hints['user_id'])
        return None
```

:::warning[Complexity Trade-off]
Sharding adds complexity. Consider read replicas first—only shard when you exceed **100M+ records** or **10K+ writes/sec**.
:::

</details>

## Best Practices

### 1. Use Automatic Routing

```python
# ✅ Good: Automatic routing
post = Post.objects.create(title="My Post")

# ❌ Bad: Manual routing (unless necessary)
post = Post.objects.using('blog_db').create(title="My Post")
```

### 2. Avoid Cross-Database JOINs

```python
# ✅ Good: Query from the correct side
orders = Order.objects.filter(user_id=user.id)

# ❌ Bad: Cross-database relationship traversal
orders = user.order_set.all()  # May not work across databases
```

### 3. Document Routing Rules

```python
# settings.py
DATABASE_ROUTING_RULES = {
    # Blog app → blog_db (PostgreSQL on db-blog.example.com)
    'blog': 'blog_db',

    # Shop app → shop_db (PostgreSQL on db-shop.example.com)
    'shop': 'shop_db',

    # Analytics app → analytics (PostgreSQL read-only warehouse)
    'analytics': 'analytics',
}
```

## Troubleshooting

:::danger[Common Issue: Routing Not Working]
**Symptom**: Queries still go to default database

**Solution**:
```python
# 1. Check if router is configured
from django.conf import settings
print(settings.DATABASE_ROUTERS)
# Should show: ['django_cfg.routing.DatabaseRouter']

# 2. Check routing rules exist
print(settings.DATABASE_ROUTING_RULES)
# Should show: {'blog': 'blog_db', ...}

# 3. Verify app_label matches
from apps.blog.models import Post
print(Post._meta.app_label)  # Should be 'blog', not 'apps.blog'
```
:::

:::warning[Wrong Database Being Used]
**Symptom**: Model saves to unexpected database

**Debug Steps**:
```python
# 1. Check which database is actually being used
from django.db import connections
print(connections['blog_db'].queries)  # Show recent queries

# 2. Inspect model after save
post = Post.objects.create(title="Test")
print(post._state.db)  # Should show 'blog_db'

# 3. Test router directly
from django.db import router
db = router.db_for_write(Post)
print(f"Router selected: {db}")  # Should be 'blog_db'
```
:::

:::tip[Migration Issues - Quick Fix]
**Symptom**: Migrations applied to wrong database

**Solution**:
```bash
# 1. Check migration status for all databases
python manage.py showmigrations

# 2. Migrate specific database
python manage.py migrate --database=blog_db

# 3. Use migrate_all for all databases (Django-CFG helper)
python manage.py migrate_all

# 4. Rollback if needed
python manage.py migrate blog 0003 --database=blog_db
```
:::

<details>
  <summary>🔍 Advanced Debugging Techniques</summary>

### Enable Query Logging

```python
# settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',  # Shows all SQL queries with database alias
        },
    },
}
```

### Test Routing Programmatically

```python
# test_routing.py
from django.test import TestCase
from django.db import router
from apps.blog.models import Post

class RoutingTestCase(TestCase):
    def test_read_routing(self):
        db = router.db_for_read(Post)
        self.assertEqual(db, 'blog_db')

    def test_write_routing(self):
        db = router.db_for_write(Post)
        self.assertEqual(db, 'blog_db')

    def test_actual_database_used(self):
        post = Post.objects.create(title="Test")
        self.assertEqual(post._state.db, 'blog_db')
```

</details>

## See Also

- [**Multi-Database**](./multi-database) - Multi-database setup
- [**Migrations**](./migrations) - Migration commands
- [**Cross-Database Relations**](./cross-database-relations) - ForeignKeys across databases
- [**Sample Project**](/guides/sample-project/multi-database) - Complete example
