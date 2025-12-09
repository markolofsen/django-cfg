# Extensions Directory

This folder contains **Django-CFG extensions** - ready-to-use Django apps from [hub.djangocfg.com](https://hub.djangocfg.com/).

## What's Here

Pre-installed extensions (there are **tons more** at [hub.djangocfg.com](https://hub.djangocfg.com/)):

- **agents** - AI workflow automation
- **backup** - Database backups
- **currency** - Multi-currency support
- **knowbase** - Knowledge base
- **leads** - CRM system
- **maintenance** - Maintenance mode
- **newsletter** - Email campaigns
- **payments** - Payment processing
- **support** - Support tickets

## How to Use

Extensions are **auto-enabled** if they have `__cfg__.py` file with `settings` variable.

### 1. Configure extension

```python
# extensions/apps/leads/__cfg__.py
from django_cfg.extensions.configs.apps.leads import BaseLeadsSettings

class LeadsSettings(BaseLeadsSettings):
    # Override defaults here
    telegram_enabled: bool = True

settings = LeadsSettings()  # ← This enables the extension
```

To **disable** - comment out or remove `settings = ...`

### 2. Run migrations

```bash
python manage.py migrate_all
```

### 3. Customize freely

All code in `extensions/apps/` can be modified for your needs - models, views, admin, etc.

## Install More

There are **tons of extensions** available at [hub.djangocfg.com](https://hub.djangocfg.com/)!

```bash
django-cfg install <extension-name>
```

## Create Your Own

Extensions are just **regular Django apps** - nothing special! You can create and publish your own:

👉 **[hub.djangocfg.com/create](https://hub.djangocfg.com/create/)**

Your custom extension works exactly like any Django app. The only difference - it can be shared and installed by others.

---

**Extensions = Ready apps you can install and customize** 🚀
