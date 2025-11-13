# Django Admin Widgets

Custom widgets for django_admin module.

## Available Widgets

### JSONEditorWidget

Rich JSON editor with syntax highlighting, validation, and copy button.

**Features:**
- 🎨 Syntax highlighting
- ✅ JSON validation
- 📋 Copy to clipboard button
- 🌙 Automatic dark/light theme (Unfold integration)
- 🔄 Multiple modes: code, tree, view

**Auto-applied to all JSONField models** - no configuration needed!

**Usage:**
```python
# Automatic - no config needed
class Bot(models.Model):
    settings = models.JSONField(default=dict)  # Auto-gets JSONEditorWidget!

# Custom configuration
from django_cfg.modules.django_admin import AdminConfig, JSONWidgetConfig

config = AdminConfig(
    model=Bot,
    widgets=[
        JSONWidgetConfig(
            field="settings",
            mode="code",  # or "tree", "view"
            height="400px",
            show_copy_button=True,
        ),
    ],
)
```

See: [@docs/JSON_WIDGET.md](../@docs/JSON_WIDGET.md)

### EncryptedFieldWidget

Widget for django-crypto-fields with copy button.

**Features:**
- 🔒 Secure input (password type)
- 📋 Copy button for encrypted values
- 🎯 Placeholder hints

---

## Widget Architecture

### Display vs Form Widgets

**Important:** Django Admin has two separate concepts:

1. **display_fields** - For list_display (table view)
   - Uses FieldConfig subclasses (BadgeField, DateTimeField, etc.)
   - Controls HOW data is displayed in tables
   
2. **widgets** - For form fields (edit view)
   - Uses WidgetConfig subclasses (JSONWidgetConfig, TextWidgetConfig, etc.)
   - Controls form input widgets

```python
AdminConfig(
    model=Bot,
    
    # For TABLE display (list view)
    display_fields=[
        BadgeField(name="status", ...),
        DateTimeField(name="created_at", ...),
    ],
    
    # For FORM widgets (edit view)
    widgets=[
        JSONWidgetConfig(field="settings", ...),
    ],
)
```

## Creating Custom Widgets

### 1. Create Widget Class

```python
from django.forms import Widget

class MyCustomWidget(Widget):
    template_name = "django_admin/widgets/my_widget.html"
    
    class Media:
        css = {'all': ('django_admin/css/my_widget.css',)}
        js = ('django_admin/js/my_widget.js',)
    
    def __init__(self, attrs=None, **kwargs):
        self.custom_param = kwargs.pop('custom_param', 'default')
        super().__init__(attrs)
```

### 2. Create WidgetConfig

```python
from django_cfg.modules.django_admin.config import WidgetConfig
from pydantic import Field

class MyWidgetConfig(WidgetConfig):
    """Configuration for MyCustomWidget."""
    
    custom_param: str = Field("default", description="Custom parameter")
    
    def to_widget_kwargs(self) -> dict:
        return {
            'custom_param': self.custom_param,
        }
```

### 3. Use in AdminConfig

```python
config = AdminConfig(
    model=MyModel,
    widgets=[
        MyWidgetConfig(
            field="my_field",
            custom_param="value",
        ),
    ],
)
```

## Widget Registry

All widgets are registered in `WidgetRegistry` for centralized management:

```python
from django_cfg.modules.django_admin.widgets import WidgetRegistry

# Register widget
WidgetRegistry.register('my_widget', MyCustomWidget)

# Get widget
widget_class = WidgetRegistry.get('my_widget')
```
