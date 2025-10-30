---
title: Configuration Models
description: Type-safe Pydantic configuration models for Django-CFG
sidebar_label: Configuration Models
sidebar_position: 1
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Configuration Models

Django-CFG uses Pydantic v2 models for type-safe, validated configuration.

:::tip[Why Type-Safe Configuration?]
Type-safe configuration catches errors at **startup** instead of runtime, provides **IDE autocomplete**, and enables **static type checking** with mypy/pyright.
:::

## Quick Start

<Tabs groupId="config-style">
  <TabItem value="python" label="Python Config" default>

```python title="config.py"
from django_cfg import DjangoConfig
from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    url: str = "sqlite:///db/default.sqlite3"

class MyProjectConfig(DjangoConfig):
    # Core settings
    secret_key: str = "your-secret-key-here"
    debug: bool = True
    project_name: str = "My Project"

    # Database
    database: DatabaseConfig = DatabaseConfig()

    # Services (optional)
    # email: EmailConfig = EmailConfig()
    # telegram: TelegramConfig = TelegramConfig()
```

  </TabItem>
  <TabItem value="yaml" label="YAML Config">

```yaml title="config.yaml"
secret_key: "dev-secret-key"
debug: true
project_name: "My Project"

database:
  url: "sqlite:///db/default.sqlite3"

# Optional services
# email:
#   backend: "console"
# telegram:
#   bot_token: "your-token"
```

```python title="config.py"
from django_cfg import DjangoConfig, load_config

# Load from YAML
config = load_config()  # Reads config.yaml
```

  </TabItem>
</Tabs>

## Configuration Topics

### Core Configuration

- [**DjangoConfig**](./django-settings) - Base configuration class
- [**Security Settings**](./security) - Security, CORS, SSL configuration
- [**Environment**](./environment) - Environment detection and variables

### Infrastructure

- [**Database**](./database) - Database configuration
- [**Cache**](./cache) - Cache backends (Redis, LocMem, Dummy)
- [**Logging**](/deployment/logging) - Logging configuration

### Deployment

- [**Docker Configuration**](/guides/docker/configuration) - YAML + environment variables for Docker

### Services

- [**Email**](./email) - Email services (SendGrid, SMTP, Console)
- [**Telegram**](/features/modules/telegram/overview) - Telegram bot configuration
- [**Background Tasks**](/features/modules/tasks/overview) - ReArq task configuration

### Django Integrations

- [**Admin & UI**](/features/modules/unfold/overview) - Unfold admin interface
- [**API**](/features/integrations/overview) - DRF, Spectacular, JWT
- [**Payments**](/features/built-in-apps/payments/overview) - Payment providers (NowPayments, Stripe)

## Key Features

### Type Safety

:::info[Automatic Type Validation]
Pydantic validates all types automatically at instantiation time, preventing runtime errors.
:::

```python
# Pydantic validates types automatically
class MyConfig(DjangoConfig):
    debug: bool = True
    max_connections: int = 100
    timeout: float = 30.0

# ✅ This works
config = MyConfig(debug=True, max_connections=50)

# ❌ This fails with validation error
config = MyConfig(debug="yes", max_connections="fifty")
```

<details>
  <summary>See validation error output</summary>

```python
ValidationError: 2 validation errors for MyConfig
debug
  Input should be a valid boolean [type=bool_type]
max_connections
  Input should be a valid integer [type=int_type]
```

</details>

### Environment Variables

<Tabs>
  <TabItem value="auto" label="Automatic Loading" default>

```python
from pydantic_settings import BaseSettings

class DatabaseConfig(BaseSettings):
    url: str = "sqlite:///db/default.sqlite3"

    class Config:
        env_prefix = "DATABASE_"

# Automatically reads DATABASE_URL from environment
config = DatabaseConfig()
```

  </TabItem>
  <TabItem value="manual" label="Manual Loading">

```python
import os

class DatabaseConfig(BaseModel):
    url: str = os.getenv("DATABASE_URL", "sqlite:///db/default.sqlite3")
```

  </TabItem>
</Tabs>

:::warning[Environment Variables in Production]
Always use environment variables for **secrets** (API keys, passwords) in production. Never commit them to version control.
:::

### YAML Configuration

<Tabs>
  <TabItem value="basic" label="Basic YAML" default>

```yaml title="config.yaml"
secret_key: "dev-secret-key"
debug: true
project_name: "My Project"

database:
  url: "postgresql://localhost/mydb"

email:
  backend: "console"
```

  </TabItem>
  <TabItem value="env-vars" label="With Environment Variables">

```yaml title="config.yaml"
# Use ${VAR_NAME} for environment variable substitution
secret_key: "${SECRET_KEY}"
debug: false
project_name: "My Project"

database:
  url: "${DATABASE_URL}"

email:
  host: "${EMAIL_HOST}"
  password: "${EMAIL_PASSWORD}"
```

  </TabItem>
</Tabs>

```python title="config.py"
# Load from YAML
from django_cfg import load_config

config = load_config()  # Reads config.yaml
```

:::tip[YAML Best Practice]
Keep sensitive values in environment variables and reference them in YAML with `${VAR_NAME}` syntax.
:::

### Validation

```python
from pydantic import Field, field_validator

class MyConfig(DjangoConfig):
    secret_key: str = Field(..., min_length=50)
    max_connections: int = Field(default=100, ge=1, le=1000)

    @field_validator('secret_key')
    def validate_secret_key(cls, v):
        if v == "changeme":
            raise ValueError("Please change the default secret key")
        return v
```

:::note[Pydantic Validators]
Use `field_validator` for custom validation logic. Validators run automatically during configuration instantiation.
:::

## Configuration Patterns

### Development vs Production

<Tabs>
  <TabItem value="property" label="Using Properties" default>

```python title="config.py"
from django_cfg import DjangoConfig, Environment

class MyConfig(DjangoConfig):
    @property
    def debug(self) -> bool:
        return Environment.current() == Environment.DEVELOPMENT

    @property
    def database_url(self) -> str:
        if Environment.is_production():
            return "postgresql://prod-db/main"
        return "sqlite:///db/dev.sqlite3"
```

  </TabItem>
  <TabItem value="separate" label="Separate Configs">

```python title="config.py"
class BaseConfig(DjangoConfig):
    project_name: str = "My Project"

class DevConfig(BaseConfig):
    debug: bool = True
    database_url: str = "sqlite:///dev.db"

class ProdConfig(BaseConfig):
    debug: bool = False
    database_url: str = "postgresql://prod-db/main"

# Select based on environment
import os
config = ProdConfig() if os.getenv("ENV") == "production" else DevConfig()
```

  </TabItem>
</Tabs>

### Nested Configuration

```python
class DatabaseConfig(BaseModel):
    url: str
    pool_size: int = 5

class CacheConfig(BaseModel):
    backend: str = "redis"
    location: str = "redis://localhost:6379/1"

class MyConfig(DjangoConfig):
    database: DatabaseConfig
    cache: CacheConfig
```

:::tip[Organize Complex Configs]
Use nested Pydantic models to organize complex configurations into logical groups.
:::

### Optional Features

```python
class MyConfig(DjangoConfig):
    # Optional email configuration
    email: Optional[EmailConfig] = None

    # Enable optional features
    enable_telegram: bool = False
    enable_payments: bool = False
```

<details>
  <summary>Example: Conditional Feature Enabling</summary>

```python
class MyConfig(DjangoConfig):
    # Enable features based on environment
    enable_telegram: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_TELEGRAM", "false") == "true"
    )
    enable_payments: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_PAYMENTS", "false") == "true"
    )
```

</details>

## See Also

### Configuration Deep Dive
- [**Type-Safe Configuration**](../core/type-safety) - Why type safety matters
- [**Environment**](./environment) - Environment detection and YAML config
- [**Database**](../database) - Database configuration details

### Docker Deployment
- [**Docker Configuration**](/guides/docker/configuration) - Layered config strategy for Docker
- [**Docker Overview**](/guides/docker/overview) - Complete Docker deployment guide
