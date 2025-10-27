---
title: Database Configuration
description: Database configuration guide for Django-CFG with URL-based setup and multi-database support.
sidebar_label: Database
sidebar_position: 1
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Database Configuration

:::tip[URL-Based Configuration]
Django-CFG uses **URL-based configuration** for databases, providing a simple, consistent interface across all database backends (PostgreSQL, MySQL, SQLite, etc.).
:::

## Quick Start

<Tabs>
  <TabItem value="env" label="Environment Variables" default>

```bash title=".env"
DATABASE__URL="postgresql://user:password@localhost:5432/mydb"
```

```python title="api/environment/loader.py"
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseConfig(BaseSettings):
    url: str = Field(default="sqlite:///db/default.sqlite3")

    model_config = SettingsConfigDict(
        env_prefix="DATABASE__",
        env_nested_delimiter="__",
    )

env = EnvironmentConfig()  # Auto-loads from ENV and .env
```

```python title="api/config.py"
from django_cfg import DjangoConfig, DatabaseConfig
from .environment import env

class MyConfig(DjangoConfig):
    databases = {
        "default": DatabaseConfig.from_url(url=env.database.url)
    }

config = MyConfig()
```

:::warning[Production Secrets]
Always use environment variables for database credentials in production. Never commit passwords to version control.
:::

  </TabItem>
  <TabItem value="python" label="Direct Config">

```python title="api/config.py"
from django_cfg import DjangoConfig, DatabaseConfig

class MyConfig(DjangoConfig):
    databases: dict[str, DatabaseConfig] = {
        "default": DatabaseConfig.from_url(
            url="postgresql://user:password@localhost:5432/mydb"
        )
    }

config = MyConfig()
```

:::danger[Not Recommended]
Hardcoded credentials are a security risk. Use environment variables instead.
:::

  </TabItem>
</Tabs>

:::info[Automatic Conversion]
Django-CFG automatically converts `database.url` to Django's `DATABASES` setting using `dj-database-url`. No manual dictionary configuration needed.
:::

## Database URL Formats

:::note[URL Pattern]
All database URLs follow the pattern: `backend://user:password@host:port/database?options`
:::

<Tabs>
  <TabItem value="postgresql" label="PostgreSQL" default>

```python title="PostgreSQL URL Examples"
# Basic connection
url = "postgresql://user:password@localhost:5432/dbname"

# Default port (5432 can be omitted)
url = "postgresql://user:password@localhost/dbname"

# Short form (postgres:// also works)
url = "postgres://user:password@localhost/dbname"

# With SSL (production)
url = "postgresql://user:password@localhost/dbname?sslmode=require"

# Connection timeout
url = "postgresql://user:password@localhost/dbname?connect_timeout=10"

# Multiple options
url = "postgresql://user:password@localhost/dbname?sslmode=require&connect_timeout=10"
```

:::tip[PostgreSQL in Production]
PostgreSQL is the **recommended database** for production Django applications due to:
- Advanced features (JSON fields, full-text search, arrays)
- Excellent Django ORM support
- Strong data integrity and ACID compliance
- Active development and community support
:::

  </TabItem>
  <TabItem value="mysql" label="MySQL/MariaDB">

```python title="MySQL URL Examples"
# Basic MySQL connection
url = "mysql://user:password@localhost:3306/dbname"

# MariaDB (same format)
url = "mysql://user:password@localhost:3306/dbname"

# With charset
url = "mysql://user:password@localhost/dbname?charset=utf8mb4"

# Connection options
url = "mysql://user:password@localhost/dbname?init_command=SET sql_mode='STRICT_TRANS_TABLES'"

# SSL connection
url = "mysql://user:password@localhost/dbname?ssl_ca=/path/to/ca.pem"
```

:::warning[MySQL Charset]
Always use `charset=utf8mb4` for full Unicode support (including emojis). The default `utf8` is limited to 3-byte UTF-8 characters.
:::

  </TabItem>
  <TabItem value="sqlite" label="SQLite">

```python title="SQLite URL Examples"
# File-based database (development)
url = "sqlite:///db/mydb.sqlite3"

# Relative path
url = "sqlite:///./mydb.sqlite3"

# Absolute path
url = "sqlite:////absolute/path/to/mydb.sqlite3"

# In-memory database (testing)
url = "sqlite:///:memory:"
```

:::note[SQLite Use Cases]
SQLite is ideal for:
- **Development:** Quick setup, no server needed
- **Testing:** In-memory databases for fast tests
- **Small deployments:** Single-server applications with light load

**NOT recommended for production** with multiple workers or high concurrency.
:::

  </TabItem>
  <TabItem value="other" label="Other Databases">

```python title="Other Database Backends"
# Oracle
url = "oracle://user:password@localhost:1521/dbname"

# Microsoft SQL Server
url = "mssql://user:password@localhost:1433/dbname"

# CockroachDB (PostgreSQL-compatible)
url = "cockroachdb://user:password@localhost:26257/dbname?sslmode=require"

# Amazon Redshift (PostgreSQL-compatible)
url = "redshift://user:password@cluster.region.redshift.amazonaws.com:5439/dbname"
```

:::info[Custom Backends]
For databases not listed here, ensure the appropriate Django database backend is installed and use the correct URL scheme.
:::

  </TabItem>
</Tabs>

<details>
  <summary>Advanced URL Options</summary>

### Connection Pooling
```python
# PgBouncer connection pooling
url = "postgresql://user:password@pgbouncer:6432/dbname?sslmode=require"

# Django connection pool settings (via DatabaseConfig)
databases: dict[str, DatabaseConfig] = {
    "default": DatabaseConfig.from_url(
        url=env.database.url,
        options={
            "MAX_CONNS": 20,
            "MIN_CONNS": 5,
        }
    )
}
```

### SSL/TLS Configuration
```python
# PostgreSQL SSL modes
url = "postgresql://user:pass@host/db?sslmode=disable"   # No SSL
url = "postgresql://user:pass@host/db?sslmode=allow"     # Try SSL, fallback to plain
url = "postgresql://user:pass@host/db?sslmode=prefer"    # Prefer SSL
url = "postgresql://user:pass@host/db?sslmode=require"   # Require SSL (production)
url = "postgresql://user:pass@host/db?sslmode=verify-ca" # Verify CA certificate
url = "postgresql://user:pass@host/db?sslmode=verify-full" # Full verification
```

### Timeout Configuration
```python
# Connection timeout (seconds)
url = "postgresql://user:pass@host/db?connect_timeout=10"

# Statement timeout (milliseconds)
url = "postgresql://user:pass@host/db?options=-c statement_timeout=30000"
```

</details>

## Topics

- [**URL Configuration**](./url-configuration) - URL-based database setup
- [**Multi-Database**](./multi-database) - Multiple database configuration
- [**Routing**](./routing) - Database routing system
- [**Migrations**](./migrations) - Migration commands
- [**Cross-Database Relations**](./cross-database-relations) - ForeignKeys across databases

## See Also

- [**Multi-Database Guide**](/guides/multi-database) - Complete multi-database setup
- [**Configuration Guide**](../configuration) - DjangoConfig models
- [**Environment Variables**](../configuration/environment) - Configure via YAML/env
