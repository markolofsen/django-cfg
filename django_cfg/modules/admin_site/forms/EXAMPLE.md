# Login Autofill Example

`AdminSiteConfig` can prefill the admin login form in development. The fields are `dev_autofill_email`, `dev_autofill_password` and `dev_autofill_force`.

## Basic usage (development only)

```python
from django_cfg import DjangoConfig
from django_cfg import AdminSiteConfig

class MyConfig(DjangoConfig):
    admin_site = AdminSiteConfig(
        site_title="My Admin",

        # Autofill is active only in DEBUG / development
        dev_autofill_email="admin@example.com",
        dev_autofill_password="admin123",
    )
```

## Force in production (demo or staging)

```python
class MyConfig(DjangoConfig):
    admin_site = AdminSiteConfig(
        site_title="My Admin",
        dev_autofill_email="demo@example.com",
        dev_autofill_password="demo123",
        dev_autofill_force=True,  # works regardless of DEBUG
    )
```

## How it works

1. If `dev_autofill_email` or `dev_autofill_password` is set, `DevAuthForm` is enabled as the login form.
2. Autofill is applied when any of these is true:
   - `DEBUG=True`
   - django-cfg detects a development environment
   - `dev_autofill_force=True`
3. The form prefills the username and password fields on the login page.

## Use cases

- Development: automatic via `DEBUG=True` or a development environment.
- Demo or staging: set `dev_autofill_force=True`.
- Production: leave the autofill fields unset.
