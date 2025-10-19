---
title: Django Integration
description: Django integration guide for Django-CFG.
sidebar_label: Django Integration
sidebar_position: 10
---

# Django Integration

Documentation coming soon.

## Quick Start

Django-CFG seamlessly integrates with Django's settings system.

```python
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    project_name: str = "My Project"
    root_urlconf: str = "myproject.urls"
```

## See Also

- [**Configuration Guide**](../configuration) - DjangoConfig models
- [**Getting Started**](/getting-started/first-project) - First project
