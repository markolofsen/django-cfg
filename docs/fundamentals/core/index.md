---
title: Core Concepts
description: Core concepts and architecture of Django-CFG
sidebar_label: Overview
sidebar_position: 1
---

# Core Concepts

Django-CFG provides type-safe configuration management for Django projects using Pydantic models.

## Key Features

- **Type Safety** - Pydantic validation for all settings
- **Environment Detection** - Auto-detect dev/staging/production
- **Smart Defaults** - Context-aware configuration
- **Clean Architecture** - Separation of concerns

## Core Components

### [Architecture](./architecture)
System design and component interaction

### [Type Safety](./type-safety)
Benefits of Pydantic validation and type-safe configuration

## Quick Example

```python
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = False
    project_name: str = "My App"
```

## Related Sections

- [Configuration](/fundamentals/configuration/) - Configuration models and settings
- [Database](/fundamentals/database/) - Database configuration
- [System](/fundamentals/system/) - System integration
