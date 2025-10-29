# Code Block Methods Documentation

New methods added to `HtmlBuilder` for displaying code in Django Admin.

## Methods Added

### 1. `code()` - Inline Code

Display short code snippets inline.

**Signature:**
```python
def code(text: Any, css_class: str = "") -> SafeString
```

**Parameters:**
- `text`: Code text to display
- `css_class`: Additional CSS classes (optional)

**Usage:**
```python
from django_cfg.modules.django_admin.base import PydanticAdmin

class MyAdmin(PydanticAdmin):
    @computed_field("Command")
    def command_display(self, obj):
        return self.html.code(obj.full_command)
```

**Examples:**
```python
# File path
self.html.code("/path/to/file")

# Command
self.html.code("python manage.py migrate")

# Configuration value
self.html.code("DEBUG=True")
```

**Renders as:**
```html
<code class="font-mono text-xs bg-base-100 dark:bg-base-800 px-1.5 py-0.5 rounded">
    /path/to/file
</code>
```

---

### 2. `code_block()` - Multi-line Code Block

Display multi-line code with syntax highlighting hints, scrolling, and color variants.

**Signature:**
```python
def code_block(
    text: Any,
    language: Optional[str] = None,
    max_height: Optional[str] = None,
    variant: str = "default"
) -> SafeString
```

**Parameters:**
- `text`: Code content (multi-line supported)
- `language`: Programming language hint (`"json"`, `"python"`, `"bash"`, etc.) - for future syntax highlighting
- `max_height`: Maximum height with overflow scroll (e.g., `"400px"`, `"20rem"`)
- `variant`: Color variant - `"default"`, `"warning"`, `"danger"`, `"success"`, `"info"`

**Usage:**
```python
from django_cfg.modules.django_admin.base import PydanticAdmin
import json

class MyAdmin(PydanticAdmin):
    @computed_field("Configuration")
    def config_display(self, obj):
        if not obj.config:
            return self.html.empty()

        return self.html.code_block(
            json.dumps(obj.config, indent=2),
            language="json"
        )

    @computed_field("Standard Output")
    def stdout_display(self, obj):
        if not obj.stdout:
            return self.html.empty()

        return self.html.code_block(
            obj.stdout,
            max_height="400px"
        )

    @computed_field("Error Message")
    def error_display(self, obj):
        if not obj.error_message:
            return self.html.empty()

        return self.html.code_block(
            obj.error_message,
            max_height="200px",
            variant="danger"
        )
```

**Examples:**

#### JSON Display
```python
# Display JSON configuration
self.html.code_block(
    json.dumps({"key": "value", "nested": {"foo": "bar"}}, indent=2),
    language="json"
)
```

#### Log Output with Scrolling
```python
# Display command output with scroll
self.html.code_block(
    "Line 1\nLine 2\nLine 3\n...",
    max_height="400px"
)
```

#### Error Messages
```python
# Display error with danger styling
self.html.code_block(
    "Traceback (most recent call last):\n  File ...",
    variant="danger",
    max_height="300px"
)
```

#### Warnings
```python
# Display warnings with warning styling
self.html.code_block(
    "Warning: This is deprecated\nUse new_method() instead",
    variant="warning"
)
```

**Renders as:**
```html
<!-- Default variant -->
<pre class="font-mono text-xs whitespace-pre-wrap break-words border rounded-md p-3
            bg-base-50 dark:bg-base-900 border-base-200 dark:border-base-700"
     style="max-height: 400px; overflow-y: auto;">
    <code>{"key": "value"}</code>
</pre>

<!-- Danger variant -->
<pre class="font-mono text-xs whitespace-pre-wrap break-words border rounded-md p-3
            bg-danger-50 dark:bg-danger-900/20 border-danger-200 dark:border-danger-700"
     style="max-height: 200px; overflow-y: auto;">
    <code>Error: Something went wrong</code>
</pre>
```

---

## Color Variants

| Variant | Background | Border | Use Case |
|---------|-----------|--------|----------|
| `default` | Gray | Gray | Standard code, JSON, logs |
| `warning` | Yellow/Orange | Yellow/Orange | Warnings, stderr output |
| `danger` | Red | Red | Errors, exceptions, failures |
| `success` | Green | Green | Success messages, confirmations |
| `info` | Blue | Blue | Info messages, metadata |

---

## Use Cases

### 1. Command Execution Logs
```python
@computed_field("Output")
def output_display(self, obj):
    return self.html.code_block(
        obj.stdout,
        max_height="400px"
    )
```

### 2. JSON Configuration
```python
@computed_field("Settings")
def settings_display(self, obj):
    return self.html.code_block(
        json.dumps(obj.settings, indent=2),
        language="json"
    )
```

### 3. Error Details
```python
@computed_field("Error")
def error_display(self, obj):
    if not obj.error_message:
        return self.html.empty()

    return self.html.code_block(
        obj.error_message,
        max_height="300px",
        variant="danger"
    )
```

### 4. API Request/Response
```python
@computed_field("Request Body")
def request_body_display(self, obj):
    return self.html.code_block(
        obj.request_body,
        language="json",
        max_height="300px"
    )
```

### 5. SQL Queries
```python
@computed_field("Query")
def query_display(self, obj):
    return self.html.code_block(
        obj.sql_query,
        language="sql",
        max_height="200px"
    )
```

---

## Styling Details

### Tailwind Classes Used

**Base Classes:**
- `font-mono` - Monospace font
- `text-xs` - Small text size
- `whitespace-pre-wrap` - Preserve whitespace, wrap long lines
- `break-words` - Break long words
- `border` - Border
- `rounded-md` - Rounded corners
- `p-3` - Padding

**Variant-specific:**
- Light mode: `bg-{variant}-50 border-{variant}-200`
- Dark mode: `dark:bg-{variant}-900/20 dark:border-{variant}-700`

**Scrolling:**
- Applied via inline `style` attribute
- `max-height` and `overflow-y: auto`

---

## Implementation Notes

1. **Escaping**: All text is automatically escaped using Django's `escape()` to prevent XSS
2. **SafeString**: Returns Django's `SafeString` for safe HTML rendering
3. **Dark Mode**: Full dark mode support with Tailwind's dark: prefix
4. **Responsive**: Works on mobile with `break-words` and `whitespace-pre-wrap`
5. **Future-proof**: `language` parameter allows for syntax highlighting integration later

---

## Complete Example: Command Execution Admin

```python
from django.contrib import admin
from django_cfg.modules.django_admin import (
    AdminConfig, BadgeField, DateTimeField, Icons, computed_field
)
from django_cfg.modules.django_admin.base import PydanticAdmin
import json

commandexecution_config = AdminConfig(
    model=CommandExecution,
    list_display=["id", "command", "status", "created_at"],
    readonly_fields=[
        "command_display",
        "args_display",
        "stdout_display",
        "stderr_display",
        "error_display",
    ],
)

@admin.register(CommandExecution)
class CommandExecutionAdmin(PydanticAdmin):
    config = commandexecution_config

    @computed_field("Command")
    def command_display(self, obj):
        """Inline code for command."""
        return self.html.code(obj.full_command)

    @computed_field("Arguments")
    def args_display(self, obj):
        """JSON code block for args."""
        if not obj.args:
            return self.html.empty()

        return self.html.code_block(
            json.dumps(obj.args, indent=2),
            language="json"
        )

    @computed_field("Standard Output")
    def stdout_display(self, obj):
        """Scrollable output."""
        if not obj.stdout:
            return self.html.empty()

        return self.html.code_block(
            obj.stdout,
            max_height="400px"
        )

    @computed_field("Standard Error")
    def stderr_display(self, obj):
        """Warning-styled error output."""
        if not obj.stderr:
            return self.html.empty()

        return self.html.code_block(
            obj.stderr,
            max_height="400px",
            variant="warning"
        )

    @computed_field("Error Message")
    def error_display(self, obj):
        """Danger-styled error message."""
        if not obj.error_message:
            return self.html.empty()

        return self.html.code_block(
            obj.error_message,
            max_height="200px",
            variant="danger"
        )
```

---

## Testing

```python
# Test inline code
assert 'font-mono' in str(html.code("test"))

# Test code block
assert '<pre' in str(html.code_block("test"))
assert 'overflow-y: auto' in str(html.code_block("test", max_height="400px"))

# Test variants
assert 'bg-danger' in str(html.code_block("error", variant="danger"))
assert 'bg-warning' in str(html.code_block("warn", variant="warning"))
```

---

## Migration from Old Format

**Before (manual HTML):**
```python
def output_display(self, obj):
    return format_html(
        '<pre style="max-height: 400px; overflow-y: auto; '
        'background: #f8f9fa; padding: 10px; border-radius: 4px;">{}</pre>',
        obj.stdout
    )
```

**After (with code_block):**
```python
def output_display(self, obj):
    return self.html.code_block(
        obj.stdout,
        max_height="400px"
    )
```

Benefits:
- ✅ Cleaner, more readable code
- ✅ Consistent styling across project
- ✅ Dark mode support
- ✅ Proper escaping
- ✅ Tailwind CSS classes
- ✅ Variant support for different contexts
