---
title: Dramatiq Testing
description: Testing guide for Dramatiq background tasks in Django-CFG.
sidebar_label: Testing
sidebar_position: 6
---

# Dramatiq Testing

Documentation coming soon.

## Quick Start

Django-CFG provides testing utilities for Dramatiq background tasks.

```python
from django_cfg import DjangoConfig

# Test configuration
class TestConfig(DjangoConfig):
    dramatiq_enabled: bool = True
```

## See Also

- [**Dramatiq Overview**](./overview) - Getting started with Dramatiq
- [**Configuration Guide**](./configuration) - Configure Dramatiq
- [**Examples**](./examples) - Task examples
