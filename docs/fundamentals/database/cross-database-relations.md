---
title: Cross-Database Relations
description: ForeignKeys across different databases with db_constraint=False
sidebar_label: Cross-Database Relations
sidebar_position: 6
---

# Cross-Database Relations

When using multi-database setup, ForeignKeys to models in different databases require special handling.

## The Problem

Consider this scenario:

- **User** model lives in `default` database
- **Post** model lives in `blog_db` database
- Post needs a ForeignKey to User

### Without db_constraint=False

```python
# ❌ This WILL FAIL during migrations
class Post(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
```

**Error:**
```
django.db.utils.ProgrammingError: relation "auth_user" does not exist
```

**Why?** Django tries to create a database-level foreign key constraint in `blog_db`, but the `User` table only exists in `default` database.

## The Solution: db_constraint=False

```python
# ✅ CORRECT - Works with multi-database
from django.contrib.auth import get_user_model

User = get_user_model()

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

## How It Works

### What db_constraint=False Does

- ✅ Prevents database-level foreign key constraint
- ✅ Django ORM still validates relationships
- ✅ `post.author` still returns User object
- ✅ `user.blog_posts.all()` still works
- ❌ No referential integrity at database level
- ❌ No cascade deletes at database level

### Django Handles It

Django manages the relationship at the **application level** instead of database level:

```python
# This works - Django fetches from both databases
post = Post.objects.get(id=1)  # From blog_db
author = post.author  # Django fetches from default database

# Reverse relation also works
user = User.objects.get(id=1)  # From default
posts = user.blog_posts.all()  # Django fetches from blog_db
```

## Complete Examples

### Blog App

```python
# apps/blog/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()  # Lives in 'default' database

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()

    # Cross-database ForeignKey to User
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_posts',
        db_constraint=False  # REQUIRED
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'blog_post'


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        # No db_constraint=False needed - same database
    )

    # Cross-database ForeignKey to User
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_comments',
        db_constraint=False  # REQUIRED
    )

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

### Shop App

```python
# apps/shop/models.py
from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

class Order(models.Model):
    order_number = models.CharField(max_length=50, unique=True)

    # Cross-database ForeignKey to User
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        db_constraint=False  # REQUIRED
    )

    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shop_order'


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # Same database - no db_constraint=False needed
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
    )
```

## Usage Examples

### Creating Objects

```python
from django.contrib.auth import get_user_model
from apps.blog.models import Post
from apps.shop.models import Order

User = get_user_model()

# Create user in default database
user = User.objects.create_user(
    username='john',
    email='john@example.com',
    password='secure_password'
)

# Create post in blog_db with cross-database FK
post = Post.objects.create(
    title='Hello World',
    content='Multi-database setup works!',
    author=user  # Cross-database FK works!
)

# Create order in shop_db with cross-database FK
order = Order.objects.create(
    order_number='ORD-001',
    customer=user,  # Cross-database FK works!
    total=Decimal('99.99')
)
```

### Accessing Relationships

```python
# Forward relationship (Post → User)
post = Post.objects.get(id=1)
print(post.author.username)  # Django fetches from default database

# Reverse relationship (User → Posts)
user = User.objects.get(id=1)
posts = user.blog_posts.all()  # Django fetches from blog_db

# Reverse relationship (User → Orders)
orders = user.orders.all()  # Django fetches from shop_db
```

## Trade-offs

### What You Gain

✅ **Multi-database architecture**
- Separate databases for different domains
- Independent scaling
- Data isolation

✅ **Django ORM works normally**
- `post.author` returns User object
- `user.blog_posts.all()` returns QuerySet
- Django validates relationships

### What You Lose

❌ **No database-level integrity**
- Database doesn't enforce foreign keys
- Can have orphaned records
- No automatic referential integrity

❌ **No database-level cascades**
- `ON DELETE CASCADE` doesn't work at DB level
- Django handles deletes at application level
- Requires extra queries

## Handling Data Integrity

### 1. Django Signals for Cascade Deletes

```python
# apps/blog/signals.py
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(pre_delete, sender=User)
def delete_user_content(sender, instance, **kwargs):
    """Delete user's content when user is deleted."""
    # Delete blog posts
    instance.blog_posts.all().delete()

    # Delete comments
    instance.blog_comments.all().delete()

    # Delete orders
    instance.orders.all().delete()
```

```python
# apps/blog/apps.py
class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.blog'

    def ready(self):
        import apps.blog.signals  # Register signals
```

### 2. Periodic Cleanup Job

```python
# apps/blog/management/commands/cleanup_orphaned.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.blog.models import Post, Comment

User = get_user_model()

class Command(BaseCommand):
    help = 'Remove orphaned blog records'

    def handle(self, *args, **options):
        # Get all user IDs
        valid_user_ids = set(User.objects.values_list('id', flat=True))

        # Find orphaned posts
        orphaned_posts = Post.objects.exclude(author_id__in=valid_user_ids)
        count = orphaned_posts.count()
        orphaned_posts.delete()

        self.stdout.write(
            self.style.SUCCESS(f'Deleted {count} orphaned posts')
        )

        # Find orphaned comments
        orphaned_comments = Comment.objects.exclude(author_id__in=valid_user_ids)
        count = orphaned_comments.count()
        orphaned_comments.delete()

        self.stdout.write(
            self.style.SUCCESS(f'Deleted {count} orphaned comments')
        )
```

### 3. Application-Level Validation

```python
# apps/blog/views.py
from django.core.exceptions import ValidationError

def create_post(request):
    user_id = request.POST.get('author_id')

    # Validate user exists before creating post
    if not User.objects.filter(id=user_id).exists():
        raise ValidationError("User does not exist")

    post = Post.objects.create(
        title=request.POST.get('title'),
        content=request.POST.get('content'),
        author_id=user_id
    )

    return post
```

### 4. Database Constraints (When Possible)

For same-database relationships, use normal ForeignKeys:

```python
# ✅ Same database - use normal FK with constraints
class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,  # Database enforces this
        # No db_constraint=False - both in blog_db
    )
```

## Performance Considerations

### N+1 Query Problem Across Databases

```python
# ❌ Bad: N+1 queries across databases
posts = Post.objects.all()
for post in posts:
    print(post.author.username)  # Separate query to default db for each post
```

```python
# ✅ Better: Manual prefetch
posts = Post.objects.all()
user_ids = [p.author_id for p in posts]
users = {u.id: u for u in User.objects.filter(id__in=user_ids)}

for post in posts:
    post._author_cache = users[post.author_id]
    print(post._author_cache.username)
```

### select_related Doesn't Work

```python
# ❌ select_related doesn't work across databases
posts = Post.objects.select_related('author').all()
# Author will still be fetched separately
```

### Cache Cross-Database Lookups

```python
from django.core.cache import cache

def get_post_with_author(post_id):
    cache_key = f'post_author_{post_id}'
    author = cache.get(cache_key)

    if not author:
        post = Post.objects.get(id=post_id)
        author = post.author
        cache.set(cache_key, author, timeout=3600)

    return author
```

## When db_constraint=False Is Required

### Required

✅ ForeignKey from routed app to `default` database:
```python
# Post in blog_db → User in default
author = models.ForeignKey(User, ..., db_constraint=False)
```

### NOT Required

❌ ForeignKey within same database:
```python
# Comment in blog_db → Post in blog_db
post = models.ForeignKey(Post, on_delete=models.CASCADE)
# Normal FK - both in blog_db
```

❌ ForeignKey in default database:
```python
# UserProfile in default → User in default
user = models.ForeignKey(User, on_delete=models.CASCADE)
# Normal FK - both in default
```

## Migration Example

```python
# apps/blog/migrations/0001_initial.py
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('author', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='blog_posts',
                    to='auth.user',
                    db_constraint=False,  # Note: db_constraint=False
                )),
            ],
        ),
    ]
```

## Troubleshooting

### Error: relation "auth_user" does not exist

**Problem:** Missing `db_constraint=False`

**Solution:**
```python
author = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    db_constraint=False  # Add this
)
```

### Orphaned Records

**Check for orphaned records:**
```python
# Find posts with missing authors
from apps.blog.models import Post
from django.contrib.auth import get_user_model

User = get_user_model()
valid_user_ids = User.objects.values_list('id', flat=True)
orphaned = Post.objects.exclude(author_id__in=valid_user_ids)
print(f"Orphaned posts: {orphaned.count()}")
```

## See Also

- [**Multi-Database**](./multi-database) - Multi-database setup
- [**Routing**](./routing) - Database routing system
- [**Migrations**](./migrations) - Migration commands
- [**Multi-Database Guide**](/guides/multi-database) - Complete guide
- [**Sample Project**](/guides/sample-project/multi-database) - Working example
