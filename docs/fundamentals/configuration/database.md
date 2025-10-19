---
title: Database Models
description: DatabaseConfig and DatabaseRoutingRule configuration models
sidebar_label: Database Models
sidebar_position: 4
---

# Database Models

Django-CFG provides Pydantic models for type-safe database configuration.

## DatabaseConfig

Type-safe database connection configuration with validation.

### Complete Model

```python
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Optional, Any

class DatabaseConfig(BaseModel):
    """Database connection configuration"""

    engine: str = Field(
        ...,
        description="Django database engine"
    )
    name: str = Field(
        ...,
        description="Database name or connection string"
    )
    user: Optional[str] = Field(
        default=None,
        description="Database user"
    )
    password: Optional[str] = Field(
        default=None,
        description="Database password",
        repr=False  # Don't show in repr for security
    )
    host: str = Field(
        default="localhost",
        description="Database host"
    )
    port: int = Field(
        default=5432,
        description="Database port",
        ge=1,
        le=65535
    )
    options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional database options"
    )

    # Connection settings
    connect_timeout: int = Field(
        default=10,
        description="Connection timeout in seconds",
        ge=1
    )
    sslmode: str = Field(
        default="prefer",
        description="SSL mode for connection"
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate database name or parse connection string"""
        if v.startswith(('postgresql://', 'mysql://', 'sqlite:///')):
            # Parse connection string and extract components
            return cls._parse_connection_string(v)
        return v

    @staticmethod
    def _parse_connection_string(connection_string: str) -> str:
        """Parse database connection string"""
        # Implementation for parsing connection strings
        # Returns the database name component
        pass

    def to_django_config(self) -> Dict[str, Any]:
        """Convert to Django database configuration format"""
        config = {
            'ENGINE': self.engine,
            'NAME': self.name,
            'OPTIONS': {
                'connect_timeout': self.connect_timeout,
                'sslmode': self.sslmode,
                **self.options
            }
        }

        if self.user:
            config['USER'] = self.user

        if self.password:
            config['PASSWORD'] = self.password

        if self.host:
            config['HOST'] = self.host

        if self.port:
            config['PORT'] = self.port

        return config
```

## Usage Examples

### SQLite Configuration

```python
from django_cfg import DjangoConfig
from django_cfg.models import DatabaseConfig

class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = True

    databases: dict = {
        'default': DatabaseConfig(
            engine='django.db.backends.sqlite3',
            name='db/default.sqlite3'
        )
    }
```

**Generated Django settings:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db/default.sqlite3',
        'OPTIONS': {
            'connect_timeout': 10,
            'sslmode': 'prefer',
        }
    }
}
```

### PostgreSQL Configuration

```python
class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = False

    databases: dict = {
        'default': DatabaseConfig(
            engine='django.db.backends.postgresql',
            name='production_db',
            user='dbuser',
            password='secure_password',
            host='db.example.com',
            port=5432,
            sslmode='require',
            connect_timeout=30
        )
    }
```

**Generated Django settings:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'production_db',
        'USER': 'dbuser',
        'PASSWORD': 'secure_password',
        'HOST': 'db.example.com',
        'PORT': 5432,
        'OPTIONS': {
            'connect_timeout': 30,
            'sslmode': 'require',
        }
    }
}
```

### MySQL Configuration

```python
class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = False

    databases: dict = {
        'default': DatabaseConfig(
            engine='django.db.backends.mysql',
            name='myapp_db',
            user='root',
            password='mysql_password',
            host='localhost',
            port=3306,
            options={
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
            }
        )
    }
```

### Multi-Database Configuration

```python
class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = False

    databases: dict = {
        'default': DatabaseConfig(
            engine='django.db.backends.postgresql',
            name='users_db',
            user='dbuser',
            password='password',
            host='localhost'
        ),
        'blog_db': DatabaseConfig(
            engine='django.db.backends.postgresql',
            name='blog_db',
            user='dbuser',
            password='password',
            host='localhost'
        ),
        'shop_db': DatabaseConfig(
            engine='django.db.backends.postgresql',
            name='shop_db',
            user='dbuser',
            password='password',
            host='localhost'
        )
    }
```

## DatabaseRoutingRule

Type-safe database routing configuration for multi-database setups.

### Complete Model

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class DatabaseRoutingRule(BaseModel):
    """Database routing rule for multi-database setups"""

    apps: List[str] = Field(
        ...,
        description="List of Django apps for this rule"
    )
    database: str = Field(
        ...,
        description="Target database alias"
    )
    operations: List[Literal["read", "write", "migrate"]] = Field(
        default_factory=lambda: ["read", "write", "migrate"],
        description="Allowed operations for this rule"
    )
    migrate_to: Optional[str] = Field(
        default=None,
        description="Override database for migrations"
    )
    description: str = Field(
        default="",
        description="Human-readable description of this rule"
    )

    def matches_app(self, app_label: str) -> bool:
        """Check if this rule matches the given app"""
        return app_label in self.apps

    def allows_operation(self, operation: str) -> bool:
        """Check if this rule allows the given operation"""
        return operation in self.operations

    def get_migration_database(self) -> str:
        """Get the database to use for migrations"""
        return self.migrate_to or self.database
```

## Routing Rules Usage

### Basic Routing

```python
from django_cfg import DjangoConfig
from django_cfg.models import DatabaseConfig, DatabaseRoutingRule

class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = False

    databases: dict = {
        'default': DatabaseConfig(
            engine='django.db.backends.postgresql',
            name='users_db',
            user='dbuser',
            password='password',
            host='localhost'
        ),
        'blog_db': DatabaseConfig(
            engine='django.db.backends.postgresql',
            name='blog_db',
            user='dbuser',
            password='password',
            host='localhost'
        )
    }

    database_routing: list = [
        DatabaseRoutingRule(
            apps=['blog'],
            database='blog_db',
            description='Route blog app to blog_db'
        )
    ]
```

### Advanced Routing

```python
class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = False

    databases: dict = {
        'default': DatabaseConfig(
            engine='django.db.backends.postgresql',
            name='users_db',
            user='dbuser',
            password='password',
            host='localhost'
        ),
        'blog_db': DatabaseConfig(
            engine='django.db.backends.postgresql',
            name='blog_db',
            user='dbuser',
            password='password',
            host='localhost'
        ),
        'shop_db': DatabaseConfig(
            engine='django.db.backends.postgresql',
            name='shop_db',
            user='dbuser',
            password='password',
            host='localhost'
        ),
        'analytics_db': DatabaseConfig(
            engine='django.db.backends.postgresql',
            name='analytics_db',
            user='readonly',
            password='password',
            host='analytics-server'
        )
    }

    database_routing: list = [
        # Blog app
        DatabaseRoutingRule(
            apps=['blog'],
            database='blog_db',
            description='Blog content in blog_db'
        ),

        # Shop app
        DatabaseRoutingRule(
            apps=['shop', 'payments'],
            database='shop_db',
            description='E-commerce in shop_db'
        ),

        # Analytics (read-only)
        DatabaseRoutingRule(
            apps=['analytics'],
            database='analytics_db',
            operations=['read'],  # Read-only
            description='Analytics in analytics_db (read-only)'
        ),

        # Separate migrations database
        DatabaseRoutingRule(
            apps=['legacy'],
            database='default',
            migrate_to='legacy_migrations_db',
            description='Legacy app uses separate migrations DB'
        )
    ]
```

## Environment-Specific Configuration

### Using Properties

```python
class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"

    @property
    def databases(self) -> dict:
        if self._environment == "production":
            return {
                'default': DatabaseConfig(
                    engine='django.db.backends.postgresql',
                    name='production_db',
                    user='prod_user',
                    password=os.getenv('DB_PASSWORD'),
                    host='prod-db.example.com',
                    sslmode='require'
                )
            }
        else:
            return {
                'default': DatabaseConfig(
                    engine='django.db.backends.sqlite3',
                    name='db/dev.sqlite3'
                )
            }
```

### Using YAML

```yaml
# config.production.yaml
databases:
  default:
    engine: "django.db.backends.postgresql"
    name: "production_db"
    user: "prod_user"
    password: "${DB_PASSWORD}"
    host: "prod-db.example.com"
    sslmode: "require"

# config.development.yaml
databases:
  default:
    engine: "django.db.backends.sqlite3"
    name: "db/dev.sqlite3"
```

## Connection String Parsing

DatabaseConfig can parse connection URLs:

```python
class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"

    databases: dict = {
        'default': DatabaseConfig(
            engine='django.db.backends.postgresql',
            name='postgresql://user:pass@localhost/dbname'
        )
    }
```

**Supported formats:**

- PostgreSQL: `postgresql://user:pass@host:port/dbname`
- MySQL: `mysql://user:pass@host:port/dbname`
- SQLite: `sqlite:///path/to/db.sqlite3`

## Security Best Practices

### 1. Use Environment Variables

```python
import os

class MyConfig(DjangoConfig):
    databases: dict = {
        'default': DatabaseConfig(
            engine='django.db.backends.postgresql',
            name=os.getenv('DB_NAME', 'default_db'),
            user=os.getenv('DB_USER', 'dbuser'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST', 'localhost')
        )
    }
```

### 2. Enable SSL in Production

```python
class MyConfig(DjangoConfig):
    databases: dict = {
        'default': DatabaseConfig(
            engine='django.db.backends.postgresql',
            name='production_db',
            user='prod_user',
            password=os.getenv('DB_PASSWORD'),
            host='prod-db.example.com',
            sslmode='require',  # Enforce SSL
            options={
                'sslrootcert': '/path/to/ca-cert.pem'
            }
        )
    }
```

### 3. Set Connection Timeouts

```python
class MyConfig(DjangoConfig):
    databases: dict = {
        'default': DatabaseConfig(
            engine='django.db.backends.postgresql',
            name='production_db',
            user='prod_user',
            password=os.getenv('DB_PASSWORD'),
            host='prod-db.example.com',
            connect_timeout=30,  # 30 second timeout
        )
    }
```

## Validation

DatabaseConfig validates:

- **Port range** (1-65535)
- **Timeout** (≥1 second)
- **Connection string format**
- **Required fields** (engine, name)

**Example validation error:**

```python
# ❌ Invalid port
DatabaseConfig(
    engine='django.db.backends.postgresql',
    name='mydb',
    port=99999  # Validation error: port must be ≤ 65535
)
```

## See Also

- [**Database Overview**](../database) - Database configuration guide
- [**Multi-Database**](../database/multi-database) - Multi-database setup
- [**Routing**](../database/routing) - Database routing system
- [**DjangoConfig**](./django-settings) - Base configuration class
