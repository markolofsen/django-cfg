---
title: API Reference
description: Complete API reference for Django Admin module - all classes, methods, and utilities.
sidebar_label: API Reference
sidebar_position: 7
keywords:
  - django admin api
  - AdminConfig api
  - field types api
---

# API Reference

Complete reference for all Django Admin classes, methods, and utilities.

## Core Classes

### AdminConfig

Pydantic model for admin configuration.

```python
from django_cfg.modules.django_admin import AdminConfig

class AdminConfig(BaseModel):
    # Required
    model: Type[Model]

    # Display
    list_display: List[str] = []
    list_display_links: List[str] | None = None
    list_per_page: int = 50
    list_max_show_all: int = 200

    # Display fields (auto-generate display methods)
    display_fields: List[FieldConfig] = []

    # Filters and search
    list_filter: List[str | Type] = []
    search_fields: List[str] = []
    date_hierarchy: str | None = None

    # Ordering
    ordering: List[str] = []

    # Readonly
    readonly_fields: List[str] = []

    # Form options
    autocomplete_fields: List[str] = []
    raw_id_fields: List[str] = []
    prepopulated_fields: Dict[str, Tuple[str, ...]] = {}

    # Performance
    select_related: List[str] = []
    prefetch_related: List[str] = []
    annotations: Dict[str, Any] = {}

    # Fieldsets
    fieldsets: List[FieldsetConfig] = []

    # Actions
    actions: List[ActionConfig] = []

    # Inlines
    inlines: List[Type] = []

    # Import/Export
    import_export_enabled: bool = False
    resource_class: Type | None = None

    # Other
    save_on_top: bool = False
    save_as: bool = False
    preserve_filters: bool = True
```

### PydanticAdmin

Base admin class that processes AdminConfig.

```python
from django_cfg.modules.django_admin.base import PydanticAdmin

@admin.register(MyModel)
class MyModelAdmin(PydanticAdmin):
    config = my_config

    # Access to HTML builder
    self.html.badge(...)
    self.html.span(...)
    # ... etc
```

**Properties:**
- `config: AdminConfig` - Configuration instance
- `html: HtmlBuilder` - HTML builder utility

## Field Types

### FieldConfig (Base)

Base class for all field configurations.

```python
class FieldConfig(BaseModel):
    name: str                    # Field name (required)
    title: str | None = None     # Display title
    ui_widget: str | None = None # Widget name
    empty_value: str = "—"       # Value when None
    ordering: str | None = None  # Sort field
    header: bool = False         # Sticky header column
```

### BadgeField

Badge with conditional colors.

```python
class BadgeField(FieldConfig):
    ui_widget: Literal["badge"] = "badge"
    variant: Literal["primary", "secondary", "success", "danger", "warning", "info"] = "primary"
    icon: str | None = None
    label_map: Dict[str, str] | None = None  # value → variant mapping
```

### BooleanField

Boolean indicator with icons.

```python
class BooleanField(FieldConfig):
    ui_widget: Literal["boolean"] = "boolean"
```

### CurrencyField

Formatted currency.

```python
class CurrencyField(FieldConfig):
    ui_widget: Literal["currency"] = "currency"
    currency: str = "USD"  # Currency code
    precision: int = 2     # Decimal places
```

### DateTimeField

Formatted datetime.

```python
class DateTimeField(FieldConfig):
    ui_widget: Literal["datetime"] = "datetime"
    format: str = "%Y-%m-%d %H:%M"  # strftime format
    show_relative: bool = False      # Show "2 hours ago"
```

### TextField

Text with optional truncation.

```python
class TextField(FieldConfig):
    ui_widget: Literal["text"] = "text"
    max_length: int | None = None  # Truncate after N chars
    show_tooltip: bool = False     # Tooltip on hover
```

### UserField

User with avatar support.

```python
class UserField(FieldConfig):
    ui_widget: Literal["user_avatar"] = "user_avatar"
    # Inherits header=True for sticky column
```

### ShortUUIDField

Shortened UUID display with tooltip.

```python
class ShortUUIDField(FieldConfig):
    ui_widget: Literal["short_uuid"] = "short_uuid"
    length: int = 8                    # Number of characters to display
    copy_on_click: bool = True         # Enable click-to-copy
    show_full_on_hover: bool = True    # Show full UUID in tooltip
```

## Configuration Classes

### FieldsetConfig

Fieldset configuration.

```python
class FieldsetConfig(BaseModel):
    title: str                    # Fieldset title
    fields: List[str]             # Field names
    collapsed: bool = False       # Start collapsed
    description: str | None = None  # Optional description

    def to_django_fieldset(self) -> Tuple:
        """Convert to Django fieldset format."""
```

### ActionConfig

Action configuration.

```python
class ActionConfig(BaseModel):
    name: str                     # Action name
    description: str              # Display description
    handler: Callable             # Action function
    variant: str = "primary"      # Button variant
    permissions: List[str] = []   # Required permissions

    def get_handler_function(self) -> Callable:
        """Get handler with attributes set."""
```

## Decorators

### @computed_field

Decorator for custom display methods.

```python
from django_cfg.modules.django_admin import computed_field

@computed_field(
    short_description: str,         # Column header
    ordering: str | None = None,    # Sort field
    boolean: bool = False,          # Boolean display
    empty_value: str = "—"          # When None
)
def method_name(self, obj): ...
```

### @annotated_field

Decorator for annotated values.

```python
from django_cfg.modules.django_admin import annotated_field

@annotated_field(
    short_description: str,         # Column header
    annotation_name: str,           # Annotation key
    ordering: str | None = None,    # Sort field (defaults to annotation_name)
    empty_value: str = "—"          # When None
)
def method_name(self, obj): ...
```

## HTML Utilities

HTML utilities provide rich formatting for readonly fields and custom display methods in Django Admin.

### Using in Admin Classes

**The primary way to use HTML utilities is through `self.html.*` in admin methods:**

```python
from django_cfg.modules.django_admin.base import PydanticAdmin

class MyAdmin(PydanticAdmin):
    def my_readonly_field(self, obj):
        """Custom display using self.html utilities."""
        return self.html.inline([
            self.html.badge(obj.status, variant="success"),
            self.html.span(f"Items: {obj.count}", "font-semibold"),
        ])

    def another_display(self, obj):
        """Format numbers and UUIDs."""
        return self.html.inline([
            self.html.number(obj.price, precision=2, prefix="$"),
            self.html.uuid_short(obj.id, length=6),
        ])
```

All methods available on `self.html`:
- **Basic**: `icon()`, `span()`, `text()`, `div()`, `link()`, `empty()`
- **Code**: `code()`, `code_block()`
- **Badges**: `badge()`
- **Composition**: `inline()`, `icon_text()`, `colored_text()`, `header()`
- **Formatting**: `number()`, `uuid_short()`
- **Key-Value**: `key_value()`, `breakdown()`, `divider()`, `key_value_list()`
- **Progress**: `segment()`, `progress_bar()`
- **Markdown**: `markdown()`, `markdown_docs()`

### Module Structure (Advanced)

For advanced use cases outside admin classes, you can import modules directly:

```python
from django_cfg.modules.django_admin.utils import (
    BaseElements,           # Basic HTML: icon, span, text, div, link, empty
    CodeElements,          # Code blocks: code, code_block
    BadgeElements,         # Badges: badge
    CompositionElements,   # Composition: inline, icon_text, colored_text, header
    FormattingElements,    # Formatting: number, uuid_short
    KeyValueElements,      # Key-value: key_value, breakdown, divider
    ProgressElements,      # Progress: segment, progress_bar
    MarkdownIntegration,   # Markdown: markdown, markdown_docs
)
```

### BaseElements

Basic HTML building blocks.

#### icon()

```python
BaseElements.icon(
    icon_name: str,
    size: str = "xs",          # xs, sm, base, lg, xl
    css_class: str = ""
) -> SafeString
```

#### span()

```python
BaseElements.span(
    text: Any,
    css_class: str = ""
) -> SafeString
```

#### text()

Styled text with semantic variants.

```python
BaseElements.text(
    content: Any,
    variant: str | None = None,    # success, warning, danger, info, primary
    size: str | None = None,       # xs, sm, base, lg, xl, 2xl
    weight: str | None = None,     # normal, medium, semibold, bold
    muted: bool = False
) -> SafeString
```

#### div()

```python
BaseElements.div(
    content: Any,
    css_class: str = ""
) -> SafeString
```

#### link()

```python
BaseElements.link(
    url: str,
    text: str,
    css_class: str = "",
    target: str = ""           # _blank, _self, etc.
) -> SafeString
```

#### empty()

```python
BaseElements.empty(
    text: str = "—"
) -> SafeString
```

### CodeElements

Code display utilities.

#### code()

Inline code block.

```python
CodeElements.code(
    text: Any,
    css_class: str = ""
) -> SafeString
```

#### code_block()

Multi-line code block with syntax highlighting support.

```python
CodeElements.code_block(
    text: Any,
    language: str | None = None,    # json, python, bash, etc.
    max_height: str | None = None,  # "400px", "20rem"
    variant: str = "default"        # default, warning, danger, success, info
) -> SafeString
```

### BadgeElements

Badge rendering.

#### badge()

```python
BadgeElements.badge(
    text: Any,
    variant: str = "primary",  # primary, success, warning, danger, info, secondary
    icon: str | None = None    # Material icon name
) -> SafeString
```

### CompositionElements

Element composition utilities.

#### inline()

Join items with separator, preserving SafeString HTML.

```python
CompositionElements.inline(
    *items,
    separator: str = " | ",
    size: str = "small",       # small, medium, large
    css_class: str = ""
) -> SafeString
```

**Usage:**
```python
# Join multiple elements with separator
def stats_display(self, obj):
    return CompositionElements.inline(
        CompositionElements.icon_text(Icons.EDIT, obj.posts_count),
        CompositionElements.icon_text(Icons.CHAT, obj.comments_count),
        separator=" | "
    )
```

#### icon_text()

Icon with text and optional color.

```python
CompositionElements.icon_text(
    icon_or_text: str | Any,
    text: Any = None,
    icon_size: str = "xs",
    separator: str = " ",
    color: str = None  # success, warning, danger, info, secondary, primary
) -> SafeString
```

**Examples:**

```python
# Icon with text
self.html.icon_text(Icons.EDIT, 5)

# Icon with text and color
self.html.icon_text(Icons.CHECK_CIRCLE, "Yes", color="success")
self.html.icon_text(Icons.CANCEL, "No", color="secondary")

# Just text (no icon)
self.html.icon_text("Active")
```

#### colored_text()

Colored text without icon.

```python
CompositionElements.colored_text(
    text: Any,
    color: str = None  # success, warning, danger, info, secondary, primary
) -> SafeString
```

**Examples:**

```python
# Time ago with color based on freshness
if age < 120:
    self.html.colored_text("2 minutes ago", "success")
elif age < 300:
    self.html.colored_text("5 minutes ago", "warning")
else:
    self.html.colored_text("10 minutes ago", "danger")
```

**Available colors:**
- `success` - Green (positive states)
- `warning` - Yellow (attention needed)
- `danger` / `error` - Red (critical states)
- `info` - Blue (informational)
- `secondary` - Gray (neutral)
- `primary` - Indigo (brand color)

#### header()

Header with avatar, title, and subtitle.

```python
CompositionElements.header(
    title: str,
    subtitle: str | None = None,
    initials: str | None = None,
    avatar_variant: str = "primary"
) -> SafeString
```

### FormattingElements

Number and UUID formatting.

#### number()

Smart number formatting with precision handling.

```python
FormattingElements.number(
    value: Any,
    precision: int = 8,
    thousands_separator: bool = True,
    strip_zeros: bool = True,
    min_threshold: float | None = None,
    compact: bool = False,              # Use K/M/B/T suffixes
    prefix: str = "",
    suffix: str = "",
    css_class: str = ""
) -> SafeString
```

**Usage:**
```python
# Currency
FormattingElements.number(1234.56, precision=2, prefix="$")  # "$1,234.56"

# Compact notation
FormattingElements.number(1500000, compact=True, prefix="$")  # "$1.5M"

# Crypto balance
FormattingElements.number(0.00012345, precision=8)  # "0.00012345"
```

#### uuid_short()

Shorten UUID with tooltip.

```python
FormattingElements.uuid_short(
    uuid_value: Any,
    length: int = 6,           # Number of characters to show
    show_tooltip: bool = True  # Show full UUID on hover
) -> SafeString
```

### KeyValueElements

Key-value pair utilities.

#### key_value()

Single key-value pair.

```python
KeyValueElements.key_value(
    key: str,
    value: Any,
    icon: str | None = None,
    indent: bool = False,
    divider: bool = False,
    value_variant: str | None = None,
    value_size: str | None = None
) -> SafeString
```

#### breakdown()

Combine multiple key-value pairs.

```python
KeyValueElements.breakdown(*items) -> SafeString
```

#### divider()

```python
KeyValueElements.divider(css_class: str = "my-2") -> SafeString
```

### ProgressElements

Progress bar utilities.

#### segment()

Create progress bar segment.

```python
ProgressElements.segment(
    percentage: float,
    variant: str = 'primary',
    label: str = ''
) -> dict
```

#### progress_bar()

Multi-segment progress bar.

```python
ProgressElements.progress_bar(
    *segments,
    width: str = "w-full max-w-xs",
    height: str = "h-6",
    show_labels: bool = True,
    rounded: bool = True
) -> SafeString
```

**Usage:**
```python
ProgressElements.progress_bar(
    ProgressElements.segment(60, variant='success', label='Available'),
    ProgressElements.segment(40, variant='warning', label='Locked')
)
```

### MarkdownIntegration

Markdown rendering integration.

#### markdown()

Render markdown text.

```python
MarkdownIntegration.markdown(
    text: str,
    css_class: str = "",
    max_height: str | None = None,
    enable_plugins: bool = True
) -> SafeString
```

#### markdown_docs()

Render markdown documentation with collapsible UI.

```python
MarkdownIntegration.markdown_docs(
    content: str | Path,
    collapsible: bool = True,
    title: str = "Documentation",
    icon: str = "description",
    max_height: str | None = "500px",
    enable_plugins: bool = True,
    default_open: bool = False
) -> SafeString
```

## Display Utilities

### UserDisplay

```python
from django_cfg.modules.django_admin.utils.displays import UserDisplay
from django_cfg.modules.django_admin.models.display_models import UserDisplayConfig

# With avatar
UserDisplay.with_avatar(
    user: User,
    config: UserDisplayConfig | None = None
) -> List[str]  # [name, email, initials, avatar_data]

# Simple display
UserDisplay.simple(
    user: User,
    config: UserDisplayConfig | None = None
) -> SafeString
```

**UserDisplayConfig:**
```python
class UserDisplayConfig(BaseModel):
    show_avatar: bool = True
    show_email: bool = False
    avatar_size: str = "md"  # sm, md, lg
```

### MoneyDisplay

```python
from django_cfg.modules.django_admin.utils.displays import MoneyDisplay
from django_cfg.modules.django_admin.models.display_models import MoneyDisplayConfig

# Format amount
MoneyDisplay.amount(
    amount: Decimal | float | int,
    config: MoneyDisplayConfig | None = None
) -> SafeString
```

**MoneyDisplayConfig:**
```python
class MoneyDisplayConfig(BaseModel):
    currency: str = "USD"
    decimal_places: int = 2
    thousand_separator: bool = True
    show_currency_symbol: bool = True
    show_sign: bool = False
    smart_decimal_places: bool = False  # Auto-adjust based on amount
    rate_mode: bool = False             # Special formatting for rates
```

### DateTimeDisplay

```python
from django_cfg.modules.django_admin.utils.displays import DateTimeDisplay
from django_cfg.modules.django_admin.models.display_models import DateTimeDisplayConfig

# Relative time
DateTimeDisplay.relative(
    dt: datetime,
    config: DateTimeDisplayConfig | None = None
) -> SafeString

# Compact display
DateTimeDisplay.compact(
    dt: datetime,
    config: DateTimeDisplayConfig | None = None
) -> SafeString
```

**DateTimeDisplayConfig:**
```python
class DateTimeDisplayConfig(BaseModel):
    datetime_format: str = "%Y-%m-%d %H:%M"
    show_relative: bool = False
```

## Icons

### Icons Class

2234+ Material Design icons with autocomplete.

```python
from django_cfg.modules.django_admin import Icons

# Common icons
Icons.CHECK_CIRCLE
Icons.CANCEL
Icons.EDIT
Icons.DELETE
Icons.VISIBILITY
Icons.SETTINGS
Icons.PERSON
Icons.EMAIL
Icons.BUSINESS
Icons.SHOPPING_CART
Icons.RECEIPT
Icons.CURRENCY_BITCOIN
Icons.ADMIN_PANEL_SETTINGS
Icons.PRIORITY_HIGH
Icons.ARTICLE
Icons.CATEGORY
Icons.SCHEDULE
Icons.ERROR
Icons.WARNING
Icons.MOUSE
Icons.API
Icons.PACKAGE
Icons.HISTORY
Icons.SUPPORT_AGENT
Icons.SMART_TOY
Icons.CAMPAIGN
Icons.NEW_RELEASES
Icons.STAR
Icons.LOCAL_OFFER
Icons.ARROW_UPWARD
Icons.ARROW_DOWNWARD
Icons.REMOVE
Icons.SHOPPING_BAG

# ... 2200+ more icons with full IDE autocomplete
```

### IconCategories

Group icons by category for easier discovery.

```python
from django_cfg.modules.django_admin import IconCategories

IconCategories.ACTIONS      # Common action icons
IconCategories.CONTENT      # Content-related icons
IconCategories.COMMUNICATION  # Communication icons
IconCategories.SOCIAL       # Social icons
IconCategories.PLACES       # Location icons
IconCategories.DEVICE       # Device icons
```

## Widget Registry

Internal registry for widget renderers (advanced usage).

```python
from django_cfg.modules.django_admin import WidgetRegistry

# Register custom widget
WidgetRegistry.register("my_widget", my_render_function)

# Render widget
WidgetRegistry.render("badge", obj, field_name, config)
```

## Pydantic Models

### BadgeVariant

```python
from django_cfg.modules.django_admin import BadgeVariant

class BadgeVariant(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"
```

### BadgeConfig

```python
from django_cfg.modules.django_admin import BadgeConfig

class BadgeConfig(BaseModel):
    variant: BadgeVariant = BadgeVariant.PRIMARY
    icon: str | None = None
    css_classes: List[str] = []
```

## Complete Import Example

```python
from django.contrib import admin
from django.db.models import Count

# Core
from django_cfg.modules.django_admin import (
    AdminConfig,
    FieldsetConfig,
    ActionConfig,
)

# Field types
from django_cfg.modules.django_admin import (
    BadgeField,
    BooleanField,
    CurrencyField,
    DateTimeField,
    ShortUUIDField,
    TextField,
    UserField,
)

# Icons
from django_cfg.modules.django_admin import Icons

# Decorators
from django_cfg.modules.django_admin.utils import (
    computed_field,
    annotated_field,
    badge_field,
    currency_field,
)

# HTML utilities (new modular structure)
from django_cfg.modules.django_admin.utils import (
    BaseElements,           # Basic HTML elements
    CodeElements,          # Code blocks
    BadgeElements,         # Badges
    CompositionElements,   # Element composition
    FormattingElements,    # Number/UUID formatting
    KeyValueElements,      # Key-value pairs
    ProgressElements,      # Progress bars
    MarkdownIntegration,   # Markdown rendering
)

# Display utilities
from django_cfg.modules.django_admin.utils import (
    UserDisplay,
    MoneyDisplay,
    DateTimeDisplay,
    StatusBadge,
    ProgressBadge,
    CounterBadge,
    MarkdownRenderer,
)

# Display configs
from django_cfg.modules.django_admin.models.display_models import (
    UserDisplayConfig,
    MoneyDisplayConfig,
    DateTimeDisplayConfig,
)

# Badge configs
from django_cfg.modules.django_admin.models.badge_models import (
    StatusBadgeConfig,
    BadgeConfig,
)

# Base admin
from django_cfg.modules.django_admin.base import PydanticAdmin
```

## Version

Current version: **2.0.0**

## Next Steps

- **[Overview](./overview.md)** - Learn the philosophy
- **[Quick Start](./quick-start.md)** - Get started in 5 minutes
- **[Configuration](./configuration.md)** - Configuration guide
- **[Filters](./filters.md)** - Complete guide to filters
- **[Examples](./examples.md)** - Real-world examples
