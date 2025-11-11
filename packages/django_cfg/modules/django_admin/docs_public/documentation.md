---
title: Documentation & Management Commands
description: Auto-discover and display markdown documentation and management commands in Django Admin with DocumentationConfig
sidebar_label: Documentation
sidebar_position: 7
keywords:
  - django admin documentation
  - markdown documentation
  - management commands
  - DocumentationConfig
  - auto-discovery
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Documentation & Management Commands

Automatically display markdown documentation and management commands in your Django Admin interface.

## Overview

The Documentation feature provides:

- **📚 Markdown Documentation**: Auto-discover and render `.md` files from a directory
- **🖥️ Management Commands**: Auto-discover Django management commands with arguments
- **🎨 Beautiful UI**: Collapsible sections with unfold semantic styling
- **📂 Flexible Paths**: Support for relative, absolute, and app-relative paths
- **🌙 Dark Mode**: Full dark mode support with proper contrast

## Quick Start

<Tabs>
  <TabItem value="directory" label="Directory Mode" default>

```python
from django_cfg.modules.django_admin import AdminConfig, DocumentationConfig

coin_admin_config = AdminConfig(
    model=Coin,
    list_display=["symbol", "name", "current_price_usd"],

    # Auto-discover all .md files in docs/ directory
    documentation=DocumentationConfig(
        source_dir="docs",  # Relative to app directory
        title="📚 Coin Documentation",
        show_management_commands=True,  # Show commands too!
    ),
)

@admin.register(Coin)
class CoinAdmin(PydanticAdmin):
    config = coin_admin_config
```

  </TabItem>
  <TabItem value="single-file" label="Single File">

```python
documentation=DocumentationConfig(
    source_file="docs/README.md",
    title="Documentation",
    collapsible=True,
)
```

  </TabItem>
  <TabItem value="string" label="String Content">

```python
documentation=DocumentationConfig(
    source_content="""
# Quick Reference

- Command: `python manage.py import_coins`
- Format: CSV or JSON
    """,
    title="Quick Reference",
)
```

  </TabItem>
</Tabs>

## DocumentationConfig

### Parameters

```python
class DocumentationConfig(BaseModel):
    # Content source (one required)
    source_dir: str | Path | None = None           # Directory to scan
    source_file: str | Path | None = None          # Single file path
    source_content: str | None = None              # Markdown string

    # Display options
    title: str = "Documentation"                   # Main title
    collapsible: bool = True                       # Collapsible sections
    default_open: bool = False                     # Open first section
    max_height: str | None = "600px"               # Max section height

    # Placement
    show_on_changelist: bool = True                # Show on list page
    show_on_changeform: bool = True                # Show on edit page

    # Markdown rendering
    enable_plugins: bool = True                    # Mistune plugins
    sort_sections: bool = True                     # Sort alphabetically

    # Management commands
    show_management_commands: bool = True          # Auto-discover commands
```

### Path Resolution

The system intelligently resolves file paths in this order:

1. **Absolute path**: `/full/path/to/docs`
2. **Project root**: `apps/crypto/docs` (relative to `BASE_DIR`)
3. **App directory**: `docs` (relative to current app)
4. **App search**: Searches through all `INSTALLED_APPS`

:::tip[Recommended: Relative Paths]
Use app-relative paths like `"docs"` for portability and simplicity.
:::

## Directory Mode

Directory mode automatically scans for all `.md` files recursively.

### File Structure

```
apps/crypto/
├── docs/
│   ├── README.md              # → "Overview"
│   ├── coin_documentation.md  # → "Coin Documentation"
│   ├── wallet_documentation.md
│   └── api/
│       ├── endpoints.md       # → "Api / Endpoints"
│       └── authentication.md  # → "Api / Authentication"
```

### Section Titles

Section titles are extracted in this order:

1. **First H1 heading** from file content
2. **README.md** → parent directory name
3. **Nested files** → "Parent / Filename"
4. **Filename** → converted to title case

```markdown
<!-- coin_documentation.md -->
# Coin Model Documentation

This becomes the section title!
```

### Example

```python
documentation=DocumentationConfig(
    source_dir="docs",              # Scans apps/crypto/docs/**/*.md
    title="📚 Crypto Documentation",
    collapsible=True,
    default_open=False,              # First section collapsed
    max_height="600px",              # Scrollable sections
    sort_sections=True,              # A-Z sorting
    enable_plugins=True,             # Tables, syntax highlighting
    show_management_commands=True,   # Commands section
)
```

## Management Commands

Automatically discovers and displays Django management commands from your app.

### Discovery

Commands are discovered from `<app>/management/commands/*.py`:

```
apps/crypto/
└── management/
    └── commands/
        ├── update_coin_prices.py
        ├── import_coins.py
        └── generate_report.py
```

### Command Information

For each command, the system extracts:

- **Command name**: `python manage.py command_name`
- **Help text**: From `help` attribute
- **Arguments**: From `add_arguments()` method
  - Argument names (`--arg`, `positional`)
  - Help text
  - Required/optional status
  - Default values

### Example Command

```python title="apps/crypto/management/commands/update_coin_prices.py"
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Update cryptocurrency prices from CoinGecko API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--coin',
            type=str,
            help='Update specific coin by symbol (e.g., BTC, ETH)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of coins to update',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if data is recent',
        )

    def handle(self, *args, **options):
        # Implementation
        pass
```

This renders as:

```
🖥 Management Commands                    [3 commands]  ▼

python manage.py update_coin_prices
  Update cryptocurrency prices from CoinGecko API

  Arguments:
    --coin          Update specific coin by symbol (e.g., BTC, ETH)
    --limit         Maximum number of coins to update  default: 100
    --force         Force update even if data is recent
```

## Markdown Features

Full markdown support via mistune 3.1.4:

### Supported Features

<Tabs>
  <TabItem value="basic" label="Basic Syntax" default>

```markdown
# Headings
## Level 2
### Level 3

**Bold text**
*Italic text*
`Inline code`

- Lists
- Items

1. Numbered
2. Lists
```

  </TabItem>
  <TabItem value="code" label="Code Blocks">

````markdown
```python
def example():
    return "Syntax highlighted!"
```

```bash
python manage.py update_coin_prices --limit 50
```
````

  </TabItem>
  <TabItem value="tables" label="Tables">

```markdown
| Feature | Supported | Notes |
|---------|-----------|-------|
| Tables  | ✅        | Full  |
| Images  | ✅        | Yes   |
| Links   | ✅        | All   |
```

  </TabItem>
  <TabItem value="advanced" label="Advanced">

```markdown
> Blockquotes

---

Horizontal rules

[Links](https://example.com)

![Images](/path/to/image.png)
```

  </TabItem>
</Tabs>

## UI Components

### Collapsible Sections

Each markdown file becomes a collapsible section:

```
┌─────────────────────────────────────────────────────┐
│ 📄 Coin Documentation              [4 sections]     │
├─────────────────────────────────────────────────────┤
│ ▶ Coin Documentation        Click to expand         │
│ ▶ Exchange Documentation    Click to expand         │
│ ▶ Overview                   Click to expand         │
│ ▶ Wallet Documentation      Click to expand         │
└─────────────────────────────────────────────────────┘
```

### Dark Mode

All components use unfold semantic colors for perfect dark mode support:

- Background: `bg-base-50` / `dark:bg-base-950`
- Borders: `border-base-200` / `dark:border-base-700`
- Text: Semantic font colors (`text-font-*`)
- Code blocks: Proper contrast
- Tables: Styled borders and hover

### Scrollable Content

Long content automatically becomes scrollable:

```python
documentation=DocumentationConfig(
    source_dir="docs",
    max_height="600px",  # Sections max 600px height
)
```

## Complete Example

```python title="apps/crypto/admin/coin_admin.py"
from django.contrib import admin
from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    CurrencyField,
    DocumentationConfig,
    FieldsetConfig,
    Icons,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from apps.crypto.models import Coin

coin_admin_config = AdminConfig(
    model=Coin,

    # List display
    list_display=[
        "symbol",
        "name",
        "current_price_usd",
        "market_cap_usd",
        "is_active"
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="symbol",
            title="Symbol",
            variant="primary",
            icon=Icons.CURRENCY_BITCOIN
        ),
        CurrencyField(
            name="current_price_usd",
            title="Price",
            currency="USD",
            precision=2
        ),
    ],

    # Filters and search
    list_filter=["is_active", "created_at"],
    search_fields=["symbol", "name"],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="Basic Information",
            fields=["symbol", "name", "slug"]
        ),
        FieldsetConfig(
            title="Market Data",
            fields=["current_price_usd", "market_cap_usd"]
        ),
    ],

    # 📚 Documentation Configuration
    documentation=DocumentationConfig(
        source_dir="docs",              # Auto-discover all .md files
        title="📚 Coin Documentation",
        collapsible=True,
        default_open=False,
        max_height="600px",
        show_on_changelist=True,        # Above the list
        show_on_changeform=True,        # Before fieldsets
        enable_plugins=True,            # Full markdown features
        sort_sections=True,             # A-Z sorting
        show_management_commands=True,  # Show commands
    ),
)

@admin.register(Coin)
class CoinAdmin(PydanticAdmin):
    """
    Enhanced admin with auto-discovered documentation and commands.
    """
    config = coin_admin_config
```

## Best Practices

:::tip[Documentation Organization]

**Directory Structure**
```
apps/crypto/docs/
├── README.md           # Overview (shown first)
├── models.md           # Model documentation
├── api.md              # API reference
└── management.md       # Management commands guide
```

**File Naming**
- Use lowercase with underscores: `coin_model.md`
- Or kebab-case: `coin-model.md`
- First H1 becomes section title

:::

:::warning[Path Resolution]

**Relative paths** are resolved in this order:
1. Project root (`BASE_DIR`)
2. Current app directory
3. All installed apps

**Recommendation**: Use app-relative paths like `"docs"` for simplicity.

:::

:::info[Performance]

**Caching**: Rendered markdown is computed on each request.

**Optimization**:
- Keep markdown files reasonably sized
- Use `max_height` for long content
- Consider splitting large files into multiple sections

:::

## Troubleshooting

### Documentation Not Showing

1. **Check path resolution**:
   ```python
   # Debug: Print resolved path
   doc_config = DocumentationConfig(source_dir="docs")
   app_path = Path(__file__).parent.parent  # App directory
   print(doc_config._resolve_path("docs", app_path))
   ```

2. **Verify file exists**:
   ```bash
   ls -la apps/crypto/docs/
   ```

3. **Check file permissions**: Ensure `.md` files are readable

### Commands Not Appearing

1. **Check directory structure**:
   ```
   apps/crypto/management/commands/
   ├── __init__.py
   └── my_command.py
   ```

2. **Verify Command class**:
   ```python
   class Command(BaseCommand):
       help = 'Command description'
       # ...
   ```

3. **Enable command discovery**:
   ```python
   documentation=DocumentationConfig(
       show_management_commands=True,  # Must be True
   )
   ```

### Styling Issues

1. **Dark mode**: All styles use unfold semantic colors automatically
2. **Code blocks**: Ensure language is specified for syntax highlighting
3. **Tables**: Use standard markdown table syntax

## See Also

- [Field Types Reference](./field-types.md)
- [Configuration Guide](./configuration.md)
- [Unfold Admin](https://unfoldadmin.com/)
- [Mistune Documentation](https://mistune.lepture.com/)
