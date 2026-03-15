# Login Autofill Example

## Basic Usage (Development only)

```python
from django_cfg.models import UnfoldConfig

class MyConfig(BaseConfig):
    unfold: UnfoldConfig = Field(
        default_factory=lambda: UnfoldConfig(
            site_title="My Admin",

            # Auto-enabled only in DEBUG mode
            dev_autofill_email="admin@example.com",
            dev_autofill_password="admin123",
        )
    )
```

## Force in Production (Demo/Staging)

```python
unfold: UnfoldConfig = Field(
    default_factory=lambda: UnfoldConfig(
        site_title="My Admin",

        # Force autofill even in production
        dev_autofill_email="demo@example.com",
        dev_autofill_password="demo123",
        dev_autofill_force=True,  # Works regardless of DEBUG
    )
)
```

## How it works

1. If `dev_autofill_email` or `dev_autofill_password` is set → `DevAuthForm` is auto-enabled
2. Autofill is enabled when ANY of these conditions are true:
   - `DEBUG=True` (Django DEBUG mode)
   - `environment.is_development=True` (django-cfg environment detection)
   - `dev_autofill_force=True` (force in production)
3. Prefills username/password fields on login page

## Use Cases

- ✅ Development: Auto-enabled via `DEBUG=True` or `environment="development"`
- ✅ Demo/Staging: Use `dev_autofill_force=True`
- ✅ Production: Don't set autofill fields
