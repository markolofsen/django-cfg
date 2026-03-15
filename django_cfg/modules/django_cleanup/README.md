# Django Cleanup Module

Automatic file cleanup for Django `FileField` and `ImageField` when model instances are deleted or file fields are updated.

## Features

- **Auto-delete on instance deletion** - Files are automatically removed when model instances are deleted
- **Auto-delete on file replacement** - Old files are deleted when a field is updated with a new file
- **Transaction-safe** - File deletion happens after transaction commit (no orphaned deletions on rollback)
- **Soft-delete aware** - Respects soft-delete patterns (won't delete files for soft-deleted records)
- **Configurable exclusions** - Exclude specific models or fields from cleanup
- **Storage-agnostic** - Works with any Django storage backend (local, S3, GCS, etc.)

## Usage

### Automatic Mode (Default)

The module is enabled by default in Django-CFG. No configuration needed - it just works.

```python
# Your model - files will be cleaned up automatically
class Document(models.Model):
    file = models.FileField(upload_to='documents/')
    image = models.ImageField(upload_to='images/')
```

### Configuration via DjangoConfig

```python
from django_cfg import DjangoConfig
from django_cfg.models import StorageConfig

class MyConfig(DjangoConfig):
    project_name = "My Project"

    # Configure storage cleanup
    storage = StorageConfig(
        auto_cleanup=True,           # Enable automatic cleanup (default: True)
        delete_on_replace=True,      # Delete old file when replaced (default: True)
        log_deletions=True,          # Log file deletions (default: False)
        check_shared_files=False,    # Check if file is shared (default: False)
        respect_soft_delete=True,    # Don't delete for soft-deleted records (default: True)
        exclude_models=[
            "backups.DatabaseBackup",  # Keep backup files
        ],
        exclude_fields=[
            "documents.Contract.original_scan",  # Keep original scans
        ],
    )
```

### Disable Cleanup

```python
from django_cfg import DjangoConfig
from django_cfg.models import StorageConfig

class MyConfig(DjangoConfig):
    storage = StorageConfig(enabled=False)
```

### Manual Mode (Mixin)

For fine-grained control, use the mixin:

```python
from django.db import models
from django_cfg.modules.django_cleanup import FileCleanupMixin

class MyModel(FileCleanupMixin, models.Model):
    document = models.FileField(upload_to='documents/')
    backup = models.FileField(upload_to='backups/')

    # Exclude specific fields from cleanup
    file_cleanup_exclude_fields = ['backup']
```

### Manual Cleanup Functions

```python
from django_cfg.modules.django_cleanup import (
    delete_file,
    cleanup_instance_files,
    get_file_fields,
)

# Delete a specific file field
delete_file(instance.avatar)

# Clean up all files for an instance
from django_cfg.modules.django_cleanup import get_config
cleanup_instance_files(instance, get_config())

# Get all file fields from a model
fields = get_file_fields(MyModel)  # Returns [(field_name, field), ...]
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | `True` | Enable the cleanup module |
| `auto_cleanup` | bool | `True` | Auto-register signals for all models with file fields |
| `delete_on_replace` | bool | `True` | Delete old file when field is updated with new file |
| `log_deletions` | bool | `False` | Log file deletions at INFO level |
| `check_shared_files` | bool | `False` | Check if file is used by other records before deleting (adds DB query) |
| `respect_soft_delete` | bool | `True` | Don't delete files for soft-deleted records |
| `exclude_models` | Set[str] | `{}` | Models to exclude (e.g., `"app.Model"`) |
| `exclude_fields` | Set[str] | `{}` | Fields to exclude (e.g., `"app.Model.field"`) |
| `soft_delete_fields` | Set[str] | `{"deleted_at", "is_deleted", "deleted"}` | Field names that indicate soft-delete |

## How It Works

### Signal-Based Cleanup

The module uses Django signals to track file changes:

1. **`pre_save`** - Caches original file values before save
2. **`post_save`** - Compares with cached values, deletes replaced files
3. **`post_delete`** - Deletes all files associated with deleted instance

### Transaction Safety

File deletions are wrapped in `transaction.on_commit()`:

```python
# Files are only deleted after the transaction commits
with transaction.atomic():
    instance.delete()  # File deletion is scheduled
# Transaction commits -> files are deleted
```

If the transaction rolls back, files remain intact.

### Soft Delete Support

The module detects soft-delete patterns by checking for common field names:
- `deleted_at` (timestamp)
- `is_deleted` (boolean)
- `deleted` (boolean)

When a record has these fields set, file cleanup is skipped.

## Edge Cases

### Bulk Delete

Works with `QuerySet.delete()` - signals fire for each instance:

```python
# All files will be cleaned up
MyModel.objects.filter(status='expired').delete()
```

### Cascade Delete

When parent is deleted, related models' files are also cleaned up (via cascade signals).

### Shared Files

If multiple records reference the same file, enable `check_shared_files`:

```python
storage = StorageConfig(check_shared_files=True)
```

This adds a DB query per file field to check for other references.

## Comparison with django-cleanup

| Feature | django_cfg.django_cleanup | django-cleanup |
|---------|---------------------------|----------------|
| Auto-discovery | ✅ | ✅ |
| Delete on replace | ✅ | ✅ |
| Transaction-safe | ✅ | ✅ |
| Soft-delete aware | ✅ | ❌ |
| DjangoConfig integration | ✅ | ❌ |
| Exclude models/fields | ✅ | ❌ |
| Shared file check | ✅ | ❌ |
| Logging | ✅ | ❌ |

## API Reference

### Functions

```python
# Delete a file field
delete_file(file_field: FieldFile, save: bool = False) -> bool

# Delete file by name using storage
delete_file_by_name(storage, file_name: str, log: bool = False) -> bool

# Clean up all files for an instance
cleanup_instance_files(instance, config, fields: list = None) -> int

# Get all FileField/ImageField from a model
get_file_fields(model: Type[Model]) -> List[Tuple[str, FileField]]

# Check if file is used by other records
is_file_shared(model, field_name: str, file_name: str, exclude_pk: int = None) -> bool

# Check if model is excluded from cleanup
is_model_excluded(model: Type[Model], config) -> bool

# Check if model has soft-delete pattern
has_soft_delete(model: Type[Model], config) -> bool

# Check if instance is soft-deleted
is_soft_deleted(instance: Model, config) -> bool
```

### Signal Management

```python
# Connect cleanup signals to a model
connect_signals_for_model(model: Type[Model])

# Disconnect cleanup signals from a model
disconnect_signals_for_model(model: Type[Model])
```

### Configuration

```python
# Get current configuration
from django_cfg.modules.django_cleanup import get_config
config = get_config()

# Clear configuration cache (for testing)
from django_cfg.modules.django_cleanup import clear_config_cache
clear_config_cache()
```

## Troubleshooting

### Files not being deleted

1. Check if model is excluded: `is_model_excluded(MyModel, get_config())`
2. Check if using soft-delete: `is_soft_deleted(instance, get_config())`
3. Enable logging: `StorageConfig(log_deletions=True)`

### Files deleted unexpectedly

1. Add model to exclusions: `exclude_models=["myapp.MyModel"]`
2. Add field to exclusions: `exclude_fields=["myapp.MyModel.keep_this"]`

### Transaction issues

Files are deleted after `transaction.on_commit()`. If you need immediate deletion:

```python
from django_cfg.modules.django_cleanup import delete_file
delete_file(instance.file_field)  # Immediate deletion
```
