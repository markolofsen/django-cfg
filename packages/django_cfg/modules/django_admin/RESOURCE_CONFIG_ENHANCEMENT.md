# ResourceConfig & BackgroundTaskConfig Enhancement

## Summary

Enhanced django-admin module with declarative import/export configuration and background task support.

## New Features

### 1. ResourceConfig

Declarative configuration for django-import-export Resource classes.

**Location:** `django_cfg/modules/django_admin/config/resource_config.py`

**Features:**
- Field selection and exclusion
- Import ID fields configuration
- Import/export behavior control
- Hook support (before/after import, per-row hooks)
- Export field ordering
- Batch processing options

**Example:**
```python
from django_cfg.modules.django_admin import ResourceConfig

resource_config = ResourceConfig(
    fields=['host', 'port', 'username', 'password'],
    exclude=['metadata', 'config'],
    import_id_fields=['host', 'port'],
    skip_unchanged=True,
    after_import_row='apps.myapp.tasks.test_after_import',
    batch_size=100,
)
```

### 2. BackgroundTaskConfig

Configuration for background task processing.

**Location:** `django_cfg/modules/django_admin/config/background_task_config.py`

**Features:**
- Task runner selection (rearq, celery, django_q, sync)
- Batch size configuration
- Timeout settings
- Retry policy
- Priority levels

**Example:**
```python
from django_cfg.modules.django_admin import BackgroundTaskConfig

background_config = BackgroundTaskConfig(
    enabled=True,
    task_runner='rearq',
    batch_size=50,
    timeout=300,
    retry_on_failure=True,
    max_retries=3,
)
```

### 3. Enhanced AdminConfig

**Updated:** `django_cfg/modules/django_admin/config/admin_config.py`

**New Fields:**
```python
class AdminConfig(BaseModel):
    # ... existing fields ...

    # Import/Export enhancement
    resource_config: Optional[ResourceConfig] = None

    # Background task processing
    background_task_config: Optional[BackgroundTaskConfig] = None
```

### 4. Enhanced PydanticAdmin

**Updated:** `django_cfg/modules/django_admin/base/pydantic_admin.py`

**Key Changes:**
- `_generate_resource_class()` now uses ResourceConfig if provided
- Auto-generates Resource with hooks support
- Dynamically attaches hook methods to Resource class

**Hook Support:**
- `before_import` - Called before import starts
- `after_import` - Called after import completes
- `before_import_row` - Called before each row import
- `after_import_row` - Called after each row import (★ most useful)

## Usage Example

### Complete Proxy Admin with Import/Export

```python
from django_cfg.modules.django_admin import (
    ActionConfig,
    AdminConfig,
    BackgroundTaskConfig,
    ResourceConfig,
)

proxy_config = AdminConfig(
    model=Proxy,

    # Enable import/export with ResourceConfig
    import_export_enabled=True,
    resource_config=ResourceConfig(
        fields=[
            'host', 'port', 'proxy_type', 'proxy_mode',
            'username', 'password',
            'provider', 'country',
        ],
        exclude=['metadata', 'config', 'last_error'],
        import_id_fields=['host', 'port', 'provider'],
        skip_unchanged=True,
        # Auto-test after import
        after_import_row='apps.proxies.tasks.after_import_row_test_proxy',
    ),

    # Background task configuration
    background_task_config=BackgroundTaskConfig(
        enabled=True,
        task_runner='rearq',
        batch_size=50,
        timeout=300,
    ),

    # Admin actions
    actions=[
        ActionConfig(
            name='test_selected_proxies',
            description='Test selected proxies',
            variant='warning',
            icon='speed',
            handler='apps.proxies.admin.actions.test_selected_proxies',
        ),
    ],

    list_display=['host', 'port', 'status', 'success_rate'],
)

@admin.register(Proxy)
class ProxyAdmin(PydanticAdmin):
    config = proxy_config
```

### Hook Implementation

```python
# apps/proxies/tasks.py

def after_import_row_test_proxy(row, row_result, **kwargs):
    """Hook called after each proxy import."""

    # Skip if dry run
    if kwargs.get('dry_run'):
        return

    # Only test new proxies
    if row_result.import_type == 'new':
        proxy = row_result.instance

        # Queue async test
        from api.workers import get_worker
        worker = get_worker()
        worker.enqueue_task(
            'apps.proxies.tasks.test_proxy_async',
            proxy_id=str(proxy.id)
        )
```

## Benefits

### Before (Manual Resource Class)
```python
from import_export import resources

class ProxyResource(resources.ModelResource):
    class Meta:
        model = Proxy
        fields = ('host', 'port', 'username', 'password')
        import_id_fields = ['host', 'port']
        skip_unchanged = True

    def after_import_row(self, row, row_result, **kwargs):
        # Custom logic here
        pass

proxy_config = AdminConfig(
    model=Proxy,
    import_export_enabled=True,
    resource_class=ProxyResource,  # Manual class
)
```

### After (Declarative ResourceConfig)
```python
proxy_config = AdminConfig(
    model=Proxy,
    import_export_enabled=True,
    resource_config=ResourceConfig(
        fields=['host', 'port', 'username', 'password'],
        import_id_fields=['host', 'port'],
        skip_unchanged=True,
        after_import_row='apps.proxies.tasks.after_import_row_test_proxy',
    ),
)
```

**Advantages:**
- ✅ No separate Resource class needed
- ✅ All configuration in one place
- ✅ Type-safe with Pydantic validation
- ✅ Reusable across multiple admins
- ✅ Hook as string path (lazy import)
- ✅ Auto-generated Resource with full control

## Dependencies Added

**pyproject.toml updates:**
```toml
dependencies = [
    # ... existing ...
    "pytz>=2025.1",
    "httpx>=0.28.1,<1.0",
]
```

- `pytz` - Timezone support for datetime operations
- `httpx` - Modern HTTP client for proxy testing

## Files Changed

### django-cfg Core
1. `config/resource_config.py` - NEW
2. `config/background_task_config.py` - NEW
3. `config/admin_config.py` - MODIFIED (added new configs)
4. `config/__init__.py` - MODIFIED (exports)
5. `base/pydantic_admin.py` - MODIFIED (Resource generation)
6. `__init__.py` - MODIFIED (exports)
7. `pyproject.toml` - MODIFIED (dependencies)

### stockapis Implementation
1. `apps/proxies/admin/proxy_admin.py` - Uses ResourceConfig
2. `apps/proxies/admin/actions.py` - NEW (admin actions)
3. `apps/proxies/services/proxy_tester.py` - NEW (testing logic)
4. `apps/proxies/tasks.py` - NEW (background tasks)
5. `apps/proxies/@docs/IMPORT_EXPORT_SETUP.md` - NEW (docs)

## Backward Compatibility

✅ **100% Backward Compatible**

Old code still works:
```python
# Old way - still works
proxy_config = AdminConfig(
    model=Proxy,
    import_export_enabled=True,
    resource_class=MyCustomResource,  # Manual class
)

# New way - alternative
proxy_config = AdminConfig(
    model=Proxy,
    import_export_enabled=True,
    resource_config=ResourceConfig(...),  # Declarative
)
```

Priority:
1. If `resource_class` provided → use it (legacy)
2. If `resource_config` provided → auto-generate Resource
3. If neither → auto-generate basic Resource

## Testing

```bash
# Test django-cfg imports
cd django-cfg-dev
poetry run python -c "from django_cfg.modules.django_admin import ResourceConfig, BackgroundTaskConfig; print('✅ OK')"

# Test stockapis admin
cd stockapis
poetry run python manage.py check --tag admin

# Test in browser
poetry run python manage.py runserver
# Visit: http://localhost:8000/admin/proxies/proxy/
```

## Future Enhancements

- [ ] `ResourceConfig.field_widgets` - Custom widgets for fields
- [ ] `ResourceConfig.validators` - Custom validation rules
- [ ] `ResourceConfig.transformers` - Data transformation before import
- [ ] Progress tracking for large imports
- [ ] Import history and rollback
- [ ] Scheduled imports via cron
- [ ] API endpoint for programmatic imports

## Migration Guide

### For Existing Projects

1. Update django-cfg to latest version
2. Optional: Replace manual Resource classes with ResourceConfig
3. Optional: Add BackgroundTaskConfig for async operations
4. Optional: Add after_import_row hooks for post-import processing

### Example Migration

**Before:**
```python
# resources.py
class ProxyResource(resources.ModelResource):
    class Meta:
        model = Proxy
        fields = ('host', 'port')

# admin.py
config = AdminConfig(
    model=Proxy,
    import_export_enabled=True,
    resource_class=ProxyResource,
)
```

**After:**
```python
# admin.py only - no resources.py needed
config = AdminConfig(
    model=Proxy,
    import_export_enabled=True,
    resource_config=ResourceConfig(
        fields=['host', 'port'],
    ),
)
```

## Version

- **django-cfg**: 1.4.106+
- **Python**: 3.12+
- **Django**: 5.2+
