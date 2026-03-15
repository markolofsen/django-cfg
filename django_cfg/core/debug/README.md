# Django-CFG Debug Utilities

Debug utilities to help troubleshoot Django-CFG issues.

## Warnings Debug Helper

Shows full stack traceback for specific warnings to help identify their source.

### Quick Start

**Method 1: Via Config (Recommended)**

```python
# In your config.py
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    project_name: str = "My Project"
    debug_warnings: bool = True  # ← Enable warnings traceback
```

**Method 2: Via Environment Variable**

```bash
export DJANGO_CFG_DEBUG_WARNINGS=1
python manage.py runserver
```

This will show full traceback for:
- RuntimeWarnings about database access during app initialization
- APPS_NOT_READY warnings
- Other app initialization warnings

### Example Output

```
================================================================================
⚠️  WARNING TRACEBACK (to help find the source)
================================================================================
  File "/path/to/your/code/apps.py", line 42, in ready
    self.setup_database()
  File "/path/to/your/code/apps.py", line 55, in setup_database
    MyModel.objects.all()
    ^^^^^^^^^^^^^^^^^^^^

--------------------------------------------------------------------------------
⚠️  WARNING MESSAGE:
/usr/lib/python3.12/site-packages/django/db/backends/utils.py:98: RuntimeWarning:
Accessing the database during app initialization is discouraged. To fix this
warning, avoid executing queries in AppConfig.ready() or when your app modules
are imported.
================================================================================
```

### Manual Usage

```python
# In your manage.py or wsgi.py, BEFORE django.setup():
from django_cfg.core.debug import setup_warnings_debug

# Enable with default settings
setup_warnings_debug(enabled=True)

# Or customize:
setup_warnings_debug(
    enabled=True,
    categories=[RuntimeWarning, DeprecationWarning],
    patterns=['.*database.*', '.*deprecated.*']
)
```

### Common Issues Found

1. **Database access in AppConfig.ready()**
   ```python
   # ❌ Bad
   def ready(self):
       from .models import MyModel
       MyModel.objects.create(...)

   # ✅ Good - use post_migrate signal
   def ready(self):
       from django.db.models.signals import post_migrate
       post_migrate.connect(self.setup_data, sender=self)
   ```

2. **Model queries at module level**
   ```python
   # ❌ Bad - runs during import
   from .models import MyModel
   DEFAULT_SETTINGS = MyModel.objects.first()

   # ✅ Good - lazy evaluation
   def get_default_settings():
       from .models import MyModel
       return MyModel.objects.first()
   ```

3. **Database connection in __init__.py**
   ```python
   # ❌ Bad
   from django.db import connection
   cursor = connection.cursor()

   # ✅ Good - move to views/services
   ```

### Disabling

Simply unset or set to 0:

```bash
export DJANGO_CFG_DEBUG_WARNINGS=0
# or
unset DJANGO_CFG_DEBUG_WARNINGS
```
