# Django Import/Export Integration

Simple integration with `django-import-export` package through django-cfg registry system.

## Features

- 🔗 **Registry Integration**: Access django-import-export components through django-cfg imports
- 🎨 **Stock styling**: the import/export templates and forms as django-import-export ships them
- 📦 **Zero Overhead**: Direct re-exports without unnecessary wrappers
- 🚀 **Full Compatibility**: 100% compatible with original django-import-export

## Quick Start

```python
from django_cfg import ImportExportModelAdmin, BaseResource

class VehicleResource(BaseResource):
    class Meta:
        model = Vehicle
        fields = ('id', 'brand', 'model', 'year', 'price')

@admin.register(Vehicle)
class VehicleAdmin(ImportExportModelAdmin):
    resource_class = VehicleResource
    list_display = ('brand', 'model', 'year', 'price')
```

## Available Components

All components are direct re-exports from `django-import-export`:

### Admin Classes
- `ImportExportMixin` - Mixin for adding import/export to existing admin
- `ImportExportModelAdmin` - Complete admin class with import/export

### Forms  
- `ImportForm` - Standard import form
- `ExportForm` - Standard export form
- `SelectableFieldsExportForm` - Form for selecting fields to export

### Resources
- `BaseResource` - Base resource class (alias for `ModelResource`)

## Why This Approach?

Instead of creating unnecessary wrappers, this module simply:

1. **Re-exports** original django-import-export components
2. **Integrates** them into django-cfg registry for consistent imports
3. **Uses** the stock import/export templates on the stock Django admin
4. **Maintains** 100% compatibility with original package

## Usage

```python
# Instead of:
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

# Use:
from django_cfg import ImportExportModelAdmin, BaseResource
```

## Configuration

No additional configuration needed. Just install `django-import-export`:

```bash
pip install django-import-export
```

The module works with:
- the stock Django admin (no theme)
- Django-cfg configuration system
- All original django-import-export features

No template overrides: the Import and Export links are the stock
`object-tools` items from `import_export/templates/admin/import_export/`.

## Full Documentation

For complete documentation, see the official [django-import-export docs](https://django-import-export.readthedocs.io/).

The stock django-import-export templates are used; no override ships here.