---
title: Multi-Database Setup
description: Comprehensive guide to multi-database architecture and automatic routing in Django-CFG
sidebar_label: Multi-Database Setup
sidebar_position: 4
---

# Multi-Database Setup

The Django-CFG sample project demonstrates sophisticated multi-database architecture with automatic routing. This guide covers database configuration, routing strategies, and migration management.

## Database Architecture

The sample project uses three separate databases:

1. **default** - Main database for users, sessions, authentication
2. **blog_db** - Dedicated database for blog content
3. **shop_db** - Separate database for e-commerce data

This architecture provides:
- **Data isolation** - Logical separation of concerns
- **Scalability** - Independent scaling of different data stores
- **Performance** - Reduced contention on main database
- **Flexibility** - Different databases can use different engines

## Database Configuration

### Basic Setup

Configure databases in `api/config.py`:

```python
from django_cfg import DjangoConfig, DatabaseConfig
from typing import Dict

class SampleProjectConfig(DjangoConfig):
    databases: Dict[str, DatabaseConfig] = {
        "default": DatabaseConfig(
            engine="django.db.backends.sqlite3",
            name="db/db.sqlite3",
            # Main database for users, sessions, admin
        ),
        "blog_db": DatabaseConfig(
            engine="django.db.backends.sqlite3",
            name="db/blog.sqlite3",
            # Routed database for blog app
            apps=["apps.blog"],
            operations=["read", "write"],
            migrate_to="default",  # Migrations go to main DB
        ),
        "shop_db": DatabaseConfig(
            engine="django.db.backends.sqlite3",
            name="db/shop.sqlite3",
            # Routed database for shop app
            apps=["apps.shop"],
            operations=["read", "write", "migrate"],
        )
    }
```

### Database Configuration Options

#### engine
Database backend to use:
- `django.db.backends.sqlite3` - SQLite (development)
- `django.db.backends.postgresql` - PostgreSQL (recommended for production)
- `django.db.backends.mysql` - MySQL
- `django.db.backends.oracle` - Oracle

#### name
Database name or file path:
```python
# SQLite: File path
name="db/blog.sqlite3"

# PostgreSQL/MySQL: Database name
name="blog_production"
```

#### apps
List of Django apps that use this database:
```python
apps=["apps.blog", "apps.comments"]
```

Operations on these models automatically route to this database.

#### operations
Allowed operations on this database:
```python
operations=["read", "write", "migrate"]
```

Options:
- `"read"` - Allow SELECT queries
- `"write"` - Allow INSERT, UPDATE, DELETE
- `"migrate"` - Allow schema migrations

#### migrate_to
Where to store migration records:
```python
migrate_to="default"
```

Useful for keeping all migration history in one place.

## Database Routing

### Automatic Routing

Django-CFG provides automatic database routing based on your configuration. No manual `.using()` calls needed!

```python
# Blog operations automatically use blog_db
from apps.blog.models import Post, Comment

post = Post.objects.create(
    title="My First Post",
    content="Hello Django-CFG!"
)
# Automatically routed to blog_db

# Shop operations automatically use shop_db
from apps.shop.models import Product, Order

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

### Router Implementation

Django-CFG's database router handles routing automatically:

```python
# Simplified router logic (handled internally)
class DatabaseRouter:
    def db_for_read(self, model, **hints):
        """Route read operations to appropriate database."""
        app_label = model._meta.app_label

        # Check each database configuration
        for db_alias, db_config in config.databases.items():
            if app_label in db_config.apps:
                if "read" in db_config.operations:
                    return db_alias

        return "default"

    def db_for_write(self, model, **hints):
        """Route write operations to appropriate database."""
        app_label = model._meta.app_label

        for db_alias, db_config in config.databases.items():
            if app_label in db_config.apps:
                if "write" in db_config.operations:
                    return db_alias

        return "default"

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Determine if migration should run on this database."""
        for db_alias, db_config in config.databases.items():
            if app_label in db_config.apps:
                # Check if migrations should run on this DB
                target_db = db_config.migrate_to or db_alias
                return db == target_db

        # Default apps go to default database
        return db == "default"
```

### Cross-Database ForeignKeys ⚠️ IMPORTANT

**Problem**: ForeignKeys to models in different databases fail during migration.

**Solution**: Use `db_constraint=False` for cross-database relationships:

```python
# apps/blog/models.py
from django.contrib.auth import get_user_model

User = get_user_model()  # In 'default' database

class Post(models.Model):
    title = models.CharField(max_length=200)

    # Cross-database ForeignKey to User
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_posts',
        db_constraint=False  # ⚠️ REQUIRED for cross-database FK
    )

    class Meta:
        db_table = 'blog_post'
```

```python
# apps/shop/models.py
class Order(models.Model):
    order_number = models.CharField(max_length=50, unique=True)

    # Cross-database ForeignKey to User
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        db_constraint=False  # ⚠️ REQUIRED for cross-database FK
    )
```

**What `db_constraint=False` does:**
- ✅ Prevents database-level foreign key constraint
- ✅ Django ORM still validates relationships
- ✅ `post.author` and `user.blog_posts` still work
- ❌ Database doesn't enforce referential integrity
- ❌ No cascade deletes at database level

**Without `db_constraint=False`:**
```
❌ Error: relation "auth_user" does not exist
Migration fails because blog_db can't create FK to user table in default database
```

### Cross-Database Queries

Be cautious with cross-database queries:

```python
# ✅ Good: Query within same database
blog_posts = Post.objects.filter(author=request.user)

# ✅ Works: Cross-database relationship with db_constraint=False
post.author.username  # Accesses User from default database
user.blog_posts.all()  # Accesses Posts from blog_db

# ⚠️ Caution: Performance impact
# Each cross-database FK access triggers separate query
for post in Post.objects.all():
    print(post.author.username)  # N+1 query problem across databases

# ✅ Better: Query from the correct database side
from apps.shop.models import Order
user_orders = Order.objects.filter(user_id=request.user.id)
```

### Manual Database Selection

When needed, you can still manually specify a database:

```python
# Use specific database explicitly
post = Post.objects.using('blog_db').get(id=1)

# Write to specific database
product = Product.objects.using('shop_db').create(name="Special Product")

# Query across all databases
all_databases = ['default', 'blog_db', 'shop_db']
for db in all_databases:
    count = Post.objects.using(db).count()
    print(f"Posts in {db}: {count}")
```

## Migration Strategy

### Running Migrations

Django-CFG provides `migrate_all` command for easy multi-database migrations:

```bash
# ✅ Recommended: Migrate all databases automatically
python manage.py migrate_all

# Skip automatic makemigrations
python manage.py migrate_all --skip-makemigrations

# Alternative: CLI migrator
poetry run cli migrator --auto

# Migrate specific database
poetry run cli migrator --database blog_db
poetry run cli migrator --database shop_db

# Standard Django migrations (all databases)
python manage.py migrate
```

**migrate_all command:**
- Automatically migrates all configured databases
- Respects DATABASE_ROUTING_RULES
- Shows success/failure for each database
- Runs makemigrations first (unless --skip-makemigrations)

**Example output:**
```
🚀 Migrating all databases...

🔄 Migrating database: default
  📦 Migrating all apps...
  ✅ Migrations completed for default

🔄 Migrating database: blog_db
  📦 Migrating app: blog
  ✅ Migrations completed for blog_db

🔄 Migrating database: shop_db
  📦 Migrating app: shop
  ✅ Migrations completed for shop_db
```

### Migration Storage

Control where migration records are stored:

#### Option 1: Store All Migrations in Default Database

```python
"blog_db": DatabaseConfig(
    engine="django.db.backends.sqlite3",
    name="db/blog.sqlite3",
    apps=["apps.blog"],
    operations=["read", "write"],
    migrate_to="default",  # Migrations stored in default DB
)
```

**Pros**:
- All migration history in one place
- Easier to track migration state
- Simpler deployment

**Cons**:
- Requires default database access
- Can't migrate databases independently

#### Option 2: Store Migrations in Each Database

```python
"shop_db": DatabaseConfig(
    engine="django.db.backends.sqlite3",
    name="db/shop.sqlite3",
    apps=["apps.shop"],
    operations=["read", "write", "migrate"],  # Includes "migrate"
)
```

**Pros**:
- Complete database independence
- Can migrate databases separately
- Better for distributed systems

**Cons**:
- Migration tracking split across databases
- More complex to manage

### Creating Migrations

Create migrations for specific apps:

```bash
# Create migration for blog app
python manage.py makemigrations blog

# Create migration for shop app
python manage.py makemigrations shop

# Create migrations for all apps
python manage.py makemigrations
```

### Initial Migration Setup

When setting up a new environment:

```bash
# 1. Create databases (if needed)
python manage.py migrate --database default
python manage.py migrate --database blog_db
python manage.py migrate --database shop_db

# 2. Or migrate all at once
python manage.py migrate

# 3. Using django-cfg CLI
poetry run cli migrator --auto
```

## Production Database Configuration

### PostgreSQL Setup

For production, use PostgreSQL:

```python
# api/config.py
from django_cfg import DatabaseConfig

databases: Dict[str, DatabaseConfig] = {
    "default": DatabaseConfig(
        engine="django.db.backends.postgresql",
        name=env.database.name,
        user=env.database.user,
        password=env.database.password,
        host=env.database.host,
        port=env.database.port,
        options={
            "connect_timeout": 10,
            "options": "-c statement_timeout=30000"
        }
    ),
    "blog_db": DatabaseConfig(
        engine="django.db.backends.postgresql",
        name=env.database.blog_name,
        user=env.database.blog_user,
        password=env.database.blog_password,
        host=env.database.blog_host,
        port=env.database.port,
        apps=["apps.blog"],
        operations=["read", "write", "migrate"],
    ),
}
```

### Environment Configuration

```yaml
# api/environment/config.prod.yaml
database:
  # Default database
  name: "djangocfg_main"
  user: "djangocfg"
  password: "<from-yaml-config>"
  host: "db.example.com"
  port: 5432

  # Blog database
  blog_name: "djangocfg_blog"
  blog_user: "djangocfg_blog"
  blog_password: "<from-yaml-config>"
  blog_host: "blog-db.example.com"

  # Shop database
  shop_name: "djangocfg_shop"
  shop_user: "djangocfg_shop"
  shop_password: "<from-yaml-config>"
  shop_host: "shop-db.example.com"
```

See [Configuration](./configuration) for environment configuration details.

## Database Usage Examples

### Blog Application

```python
# apps/blog/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # No need to specify database - routing is automatic!
        ordering = ['-created_at']

# Usage - automatically routes to blog_db
post = Post.objects.create(
    title="Django-CFG Tutorial",
    content="Learn about multi-database setup...",
    author=current_user
)

# Queries automatically routed
recent_posts = Post.objects.filter(
    created_at__gte=timezone.now() - timedelta(days=7)
)
```

### Shop Application

```python
# apps/shop/models.py
from django.db import models
from decimal import Decimal

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)

    class Meta:
        # Automatically routes to shop_db
        ordering = ['name']

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Automatically routes to shop_db
        ordering = ['-created_at']

# Usage - automatically routes to shop_db
product = Product.objects.create(
    name="Django-CFG Book",
    price=Decimal("29.99"),
    stock=100
)

order = Order.objects.create(
    user=current_user,
    total=product.price
)
```

## Advanced Routing Patterns

### Read Replicas

Configure read replicas for scalability:

```python
databases: Dict[str, DatabaseConfig] = {
    "default": DatabaseConfig(
        engine="django.db.backends.postgresql",
        name="main_db",
        host="primary.db.example.com",
        operations=["read", "write", "migrate"],
    ),
    "default_replica": DatabaseConfig(
        engine="django.db.backends.postgresql",
        name="main_db",
        host="replica.db.example.com",
        operations=["read"],  # Read-only
        apps=["apps.blog", "apps.shop"],  # Apps that can read from replica
    ),
}
```

### Sharding by User

Implement user-based sharding:

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

## Monitoring and Health Checks

Check database connectivity:

```python
# Check all databases
from django.db import connections

for alias in connections:
    try:
        cursor = connections[alias].cursor()
        print(f"✓ {alias} - Connected")
    except Exception as e:
        print(f"✗ {alias} - Error: {e}")
```

Health check endpoint:

```python
from django_cfg.modules.django_health import SimpleHealthView

health = DjangoHealthService()

@health.register_check("blog_database")
def check_blog_database():
    """Check blog database connectivity."""
    try:
        from apps.blog.models import Post
        Post.objects.using('blog_db').count()
        return {"status": "healthy", "details": "Blog database accessible"}
    except Exception as e:
        return {"status": "unhealthy", "details": str(e)}

@health.register_check("shop_database")
def check_shop_database():
    """Check shop database connectivity."""
    try:
        from apps.shop.models import Product
        Product.objects.using('shop_db').count()
        return {"status": "healthy", "details": "Shop database accessible"}
    except Exception as e:
        return {"status": "unhealthy", "details": str(e)}
```

## Best Practices

### 1. Use Automatic Routing

Let Django-CFG handle routing:

```python
# ✅ Good: Automatic routing
post = Post.objects.create(title="My Post")

# ❌ Bad: Manual routing (unless necessary)
post = Post.objects.using('blog_db').create(title="My Post")
```

### 2. Avoid Cross-Database JOINs

Design your schema to minimize cross-database queries:

```python
# ✅ Good: Query from the correct side
orders = Order.objects.filter(user_id=user.id)

# ❌ Bad: Cross-database relationship traversal
orders = user.order_set.all()  # May not work across databases
```

### 3. Test Migration Strategy

Test migrations in a staging environment:

```bash
# Test migrations before production
poetry run cli migrator --auto --dry-run

# Run migrations
poetry run cli migrator --auto
```

### 4. Document Database Relationships

Clearly document which models use which databases:

```python
class Post(models.Model):
    """Blog post model.

    Database: blog_db
    Relationships: Author (User in default database)
    """
    pass
```

## Troubleshooting

### Migration Issues

If migrations fail:

```bash
# Check migration status
python manage.py showmigrations

# Fake migration if needed
python manage.py migrate --fake blog_db

# Reset migrations (development only)
python manage.py migrate blog zero
python manage.py migrate blog
```

### Routing Issues

Debug routing problems:

```python
# Check which database will be used
from django.db import router

# For reading
db = router.db_for_read(Post)
print(f"Post reads from: {db}")

# For writing
db = router.db_for_write(Post)
print(f"Post writes to: {db}")
```

## Related Topics

- [Configuration](./configuration) - Database configuration setup
- [Project Structure](./project-structure) - Database file organization
- [Deployment](./deployment) - Production database setup

Multi-database architecture provides flexibility and scalability for growing Django applications!
