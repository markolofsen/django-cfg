---
title: Migrations
description: Multi-database migration commands
sidebar_label: Migrations
sidebar_position: 5
---

# Multi-Database Migrations

Django-CFG provides two powerful commands for managing multi-database migrations.

## migrate_all (Production)

Automatically migrates all databases based on routing configuration.

### Usage

```bash
# Migrate all databases
python manage.py migrate_all

# Skip automatic makemigrations
python manage.py migrate_all --skip-makemigrations
```

### Features

- ✅ Auto-detects all databases from settings
- ✅ Creates migrations first (unless --skip-makemigrations)
- ✅ Migrates each database based on routing rules
- ✅ Handles constance app automatically
- ✅ Shows success/failure for each database

### Example Output

```bash
$ python manage.py migrate_all

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

✅ All migrations completed successfully
```

### When to Use

**Production deployments:**
```bash
# CI/CD pipeline
python manage.py migrate_all
```

**Docker entrypoint:**
```dockerfile
CMD python manage.py migrate_all && gunicorn
```

## migrator (Development)

Interactive migration tool with auto mode and targeted migrations.

### Usage

```bash
# Auto mode - migrates all databases without prompts
python manage.py migrator --auto

# Interactive mode - shows menu
python manage.py migrator

# Migrate specific database
python manage.py migrator --database blog_db

# Migrate specific app
python manage.py migrator --app blog

# Migrate specific app on specific database
python manage.py migrator --database blog_db --app blog
```

### Interactive Mode

When run without `--auto`, shows an interactive menu:

```
🗄️  Django Database Migrator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Current Configuration:
   Databases: default, blog_db, shop_db
   Apps: accounts, blog, shop, profiles

What would you like to do?
> Migrate all databases (recommended)
  Migrate specific database
  Show database status
  View configuration info
  Exit
```

### Auto Mode

Runs automatic migration without prompts:

```bash
$ python manage.py migrator --auto

🚀 Running automatic migration...

📦 Creating migrations for all apps...
✅ Migrations created successfully

🔄 Migrating database: default
  📦 Migrating all apps...
  ✅ Migrations completed for default

🔄 Migrating database: blog_db
  📦 Migrating app: blog
  ✅ Migrations completed for blog_db

🔄 Migrating database: shop_db
  📦 Migrating app: shop
  ✅ Migrations completed for shop_db

✅ Constance migrated successfully
```

### Migration Flow

1. **Creates migrations** - Runs `makemigrations` for all apps
2. **Migrates default database** - Migrates main database first
3. **Migrates routed databases** - Migrates blog_db, shop_db based on routing rules
4. **Migrates constance** - Always migrates constance app (required by django-cfg)

### When to Use

**Development:**
```bash
# Quick migration during development
python manage.py migrator --auto
```

**Testing specific database:**
```bash
# Test blog database migrations only
python manage.py migrator --database blog_db
```

**Troubleshooting:**
```bash
# Interactive mode to explore database status
python manage.py migrator
# Select "Show database status" from menu
```

## Comparison

| Feature | `migrate_all` | `migrator --auto` |
|---------|---------------|-------------------|
| Interactive menu | ❌ No | ✅ Yes (without --auto) |
| Auto makemigrations | ✅ Yes (unless --skip-makemigrations) | ✅ Yes |
| Respects routing rules | ✅ Yes | ✅ Yes |
| Specific database | ❌ Migrates all | ✅ --database flag |
| Specific app | ❌ Migrates all apps | ✅ --app flag |
| Constance handling | ✅ Automatic | ✅ Automatic |
| Best for | Production, CI/CD | Development, targeted migrations |

## Standard Django Migrations

You can still use standard Django migration commands:

```bash
# Create migrations
python manage.py makemigrations
python manage.py makemigrations blog

# Migrate specific database
python manage.py migrate --database=blog_db
python manage.py migrate blog --database=blog_db

# Migrate all databases (respects routing)
python manage.py migrate

# Show migration status
python manage.py showmigrations
python manage.py showmigrations --database=blog_db

# Fake migration
python manage.py migrate --fake blog_db

# Rollback migration
python manage.py migrate blog 0001
```

## Migration Strategies

### Initial Setup

```bash
# 1. Create migrations
python manage.py makemigrations

# 2. Migrate all databases
python manage.py migrate_all

# 3. Verify
python manage.py showmigrations
```

### Adding New Model

```bash
# 1. Add model to apps/blog/models.py
# 2. Create migration
python manage.py makemigrations blog

# 3. Migrate blog database only
python manage.py migrator --database blog_db
```

### Production Deployment

```bash
# Pre-deployment check
python manage.py migrate_all --dry-run

# Deploy migrations
python manage.py migrate_all

# Verify
python manage.py showmigrations
```

## Routing and Migrations

### How Routing Affects Migrations

```python
# settings.py
DATABASE_ROUTING_RULES = {
    'blog': 'blog_db',
    'shop': 'shop_db',
}
```

**Migration behavior:**
- Blog app migrations → run on `blog_db` only
- Shop app migrations → run on `shop_db` only
- Other apps → run on `default` database

### Migration Storage

Migrations are tracked in the `django_migrations` table in each database:

```bash
# Check migrations on specific database
python manage.py dbshell --database=blog_db
```

```sql
SELECT * FROM django_migrations WHERE app = 'blog';
```

## Troubleshooting

### Migration Already Applied

```bash
# Fake the migration
python manage.py migrate --fake blog 0001 --database=blog_db
```

### Migration Conflicts

```bash
# Check for conflicts
python manage.py makemigrations --check

# Merge migrations
python manage.py makemigrations --merge
```

### Reset Migrations (Development Only)

```bash
# Delete migration files (keep __init__.py)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Drop and recreate databases
python manage.py migrate_all --fake-initial
```

### Cross-Database Migration Errors

If you get `relation does not exist` errors:

```python
# models.py - Add db_constraint=False for cross-database ForeignKeys
author = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    db_constraint=False  # REQUIRED for cross-database FK
)
```

See: [Cross-Database Relations](./cross-database-relations)

## Best Practices

### 1. Always Create Migrations First

```bash
# ✅ Good
python manage.py makemigrations
python manage.py migrate_all

# ❌ Bad
python manage.py migrate_all  # May fail if migrations don't exist
```

### 2. Test Migrations Locally

```bash
# Test before production
python manage.py migrate_all --dry-run
```

### 3. Use migrate_all in CI/CD

```yaml
# .github/workflows/deploy.yml
- name: Run migrations
  run: python manage.py migrate_all
```

### 4. Keep Migration History Clean

```bash
# Squash migrations periodically
python manage.py squashmigrations blog 0001 0010
```

## See Also

- [**Core Commands**](/cli/commands/core-commands#migrate_all) - migrate_all documentation
- [**Core Commands**](/cli/commands/core-commands#migrator) - migrator documentation
- [**Routing**](./routing) - Database routing details
- [**Multi-Database**](./multi-database) - Multi-database setup
