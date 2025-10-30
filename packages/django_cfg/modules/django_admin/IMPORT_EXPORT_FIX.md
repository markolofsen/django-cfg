# Import/Export Button Fix

## Problem

Import/Export buttons in `PydanticAdmin` were displaying incorrectly because:

1. `PydanticAdmin` was using the original `ImportExportModelAdmin` from django-import-export
2. Original django-import-export templates don't integrate properly with Unfold UI
3. Buttons were styled as tabs instead of toolbar buttons

## Solution

Updated `PydanticAdmin` base class to use django_cfg's custom `ImportExportMixin`:

### Before
```python
class UnfoldImportExportModelAdmin(ImportExportModelAdmin, UnfoldModelAdmin):
    pass
```

### After
```python
class UnfoldImportExportModelAdmin(UnfoldModelAdmin, ImportExportMixin):
    pass
```

## Changes Made

1. **MRO (Method Resolution Order)**:
   - `UnfoldModelAdmin` comes first (for template priority)
   - `ImportExportMixin` comes second (adds import/export functionality)

2. **Custom Templates** (`django_cfg.modules.django_import_export`):
   - Custom `change_list_*.html` templates that extend Unfold's base
   - Properly styled import/export buttons as round icons
   - Import button: green with upload icon
   - Export button: blue with download icon

3. **Integration**:
   - Uses Unfold's forms (`ImportForm`, `ExportForm`)
   - Buttons appear in `object-tools-items` block (next to "Add" button)
   - Full dark mode support

## Result

Now `PydanticAdmin` admins with `import_export_enabled=True` will have:
- ✅ Properly styled import/export buttons
- ✅ Consistent Unfold UI
- ✅ Round icon buttons matching the design system
- ✅ Correct positioning in the toolbar

## Usage

No changes required in user code - this fix is automatic:

```python
from django_cfg.modules.django_admin import AdminConfig
from django_cfg.modules.django_admin.base import PydanticAdmin

config = AdminConfig(
    model=MyModel,
    import_export_enabled=True,
    resource_class=MyModelResource,
    list_display=["name", "status"],
)

@admin.register(MyModel)
class MyModelAdmin(PydanticAdmin):
    config = config
```

The import/export buttons will now display correctly!
