---
title: URL-Based Configuration
description: URL-based database configuration with dj-database-url
sidebar_label: URL Configuration
sidebar_position: 2
---

# URL-Based Database Configuration

Django-CFG uses URL-based database configuration for simplicity and security.

## Why URL-Based Configuration?

**Benefits:**
- ✅ Single string for all connection parameters
- ✅ Easy to override with environment variables
- ✅ Standard format across different databases
- ✅ No hardcoded credentials in code
- ✅ Compatible with 12-factor app methodology

## URL Format

```
{engine}://{user}:{password}@{host}:{port}/{database}?{options}
```

## Database Engines

### SQLite

```python
# File-based database
url: str = "sqlite:///db/mydb.sqlite3"

# Absolute path
url: str = "sqlite:////absolute/path/to/db.sqlite3"

# In-memory database
url: str = "sqlite:///:memory:"
```

### PostgreSQL

```python
# Full URL with all parameters
url: str = "postgresql://user:password@localhost:5432/dbname"

# Default port (5432)
url: str = "postgresql://user:password@localhost/dbname"

# Short form (postgres instead of postgresql)
url: str = "postgres://user:password@localhost/dbname"

# With SSL
url: str = "postgresql://user:pass@localhost/db?sslmode=require"

# With connection timeout
url: str = "postgresql://user:pass@localhost/db?connect_timeout=10"

# Multiple options
url: str = "postgresql://user:pass@localhost/db?sslmode=require&connect_timeout=10"
```

### MySQL

```python
# MySQL connection
url: str = "mysql://user:password@localhost:3306/dbname"

# With charset
url: str = "mysql://user:pass@localhost/db?charset=utf8mb4"
```

### Oracle

```python
# Oracle connection
url: str = "oracle://user:password@localhost:1521/dbname"
```

## Configuration Examples

### Development (SQLite)

```python
# config.py
from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    url: str = "sqlite:///db/dev.sqlite3"
```

```yaml
# config.dev.yaml
database:
  url: "sqlite:///db/dev.sqlite3"
```

### Production (PostgreSQL)

```python
# config.py
from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    url: str = "postgresql://user:password@db.example.com:5432/production"
```

```yaml
# config.prod.yaml
database:
  url: "postgresql://user:${DB_PASSWORD}@db.example.com:5432/production"
```

### Environment Variable Override

```bash
# .env
DATABASE_URL="postgresql://user:password@localhost:5432/mydb"
```

```python
# config.py - automatically reads DATABASE_URL
from pydantic import BaseModel
from pydantic_settings import BaseSettings

class DatabaseConfig(BaseSettings):
    url: str = "sqlite:///db/default.sqlite3"  # Fallback

    class Config:
        env_prefix = "DATABASE_"
```

## Settings Integration

Django-CFG automatically converts URLs to Django's `DATABASES` format:

```python
# settings.py
import dj_database_url
from django_cfg import load_config

config = load_config()

DATABASES = {
    'default': dj_database_url.parse(config.database.url),
}
```

## Advanced Options

### Connection Pooling

```python
# PostgreSQL with connection pooling
url: str = "postgresql://user:pass@localhost/db?pool_size=20&max_overflow=10"
```

### SSL Configuration

```python
# Require SSL
url: str = "postgresql://user:pass@localhost/db?sslmode=require"

# Verify SSL certificate
url: str = "postgresql://user:pass@localhost/db?sslmode=verify-full&sslrootcert=/path/to/cert"
```

### Timeouts

```python
# Connection timeout
url: str = "postgresql://user:pass@localhost/db?connect_timeout=10"

# Statement timeout
url: str = "postgresql://user:pass@localhost/db?options=-c statement_timeout=30000"
```

### Character Encoding

```python
# UTF-8 for MySQL
url: str = "mysql://user:pass@localhost/db?charset=utf8mb4"

# Client encoding for PostgreSQL
url: str = "postgresql://user:pass@localhost/db?client_encoding=UTF8"
```

## Security Best Practices

### 1. Never Hardcode Credentials

❌ **Bad:**
```python
url: str = "postgresql://admin:MyPassword123@localhost/db"
```

✅ **Good:**
```yaml
# config.prod.yaml
database:
  url: "postgresql://admin:${DB_PASSWORD}@localhost/db"
```

```bash
# Environment variable
export DB_PASSWORD="MyPassword123"
```

### 2. Use Environment Variables in Production

```python
# config.py
import os
from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    url: str = os.getenv("DATABASE_URL", "sqlite:///db/default.sqlite3")
```

### 3. Different Credentials Per Environment

```yaml
# config.dev.yaml
database:
  url: "postgresql://dev_user:dev_pass@localhost/dev_db"
```

```yaml
# config.prod.yaml
database:
  url: "postgresql://prod_user:${DB_PASSWORD}@db.example.com/prod_db"
```

## Troubleshooting

### Special Characters in Password

If password contains special characters, URL-encode them:

```python
# Password: p@ssw0rd!
# URL-encoded: p%40ssw0rd%21
url: str = "postgresql://user:p%40ssw0rd%21@localhost/db"
```

Or use Python's urllib:

```python
from urllib.parse import quote_plus

password = "p@ssw0rd!"
encoded_password = quote_plus(password)
url = f"postgresql://user:{encoded_password}@localhost/db"
```

### Connection Issues

```bash
# Test connection
python manage.py check --database default

# Verify URL parsing
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DATABASES['default'])
```

## See Also

- [**Multi-Database**](./multi-database) - Configure multiple databases
- [**Environment Variables**](../configuration/environment) - Environment configuration
- [**Configuration Models**](../configuration) - DatabaseConfig API
