# Django Management Command Base Classes

Simplified base classes for Django management commands with automatic logger initialization and web execution safety metadata.

## Features

- **Automatic Logger**: No need to manually create loggers - use `self.logger`
- **Security Metadata**: Integrated with django_cfg's web execution security system
- **DRY Principle**: Eliminate boilerplate code in every command
- **Type Safety**: Clear command categorization with semantic base classes

## Available Base Classes

### 1. SafeCommand
For read-only commands safe for web execution.

```python
from django_cfg.management.utils import SafeCommand

class Command(SafeCommand):
    help = 'Display current configuration'

    def handle(self, *args, **options):
        self.logger.info("Showing configuration")
        # Read-only operations
```

**Metadata:**
- `web_executable = True`
- `requires_input = False`
- `is_destructive = False`

**Use for:** show_config, list_urls, check_settings

---

### 2. InteractiveCommand
For commands requiring user input (blocked from web).

```python
from django_cfg.management.utils import InteractiveCommand

class Command(InteractiveCommand):
    help = 'Create superuser with prompts'

    def handle(self, *args, **options):
        self.logger.info("Creating superuser")
        username = input("Username: ")
        # Interactive operations
```

**Metadata:**
- `web_executable = False`
- `requires_input = True`
- `is_destructive = False`

**Use for:** superuser, createsuperuser, any command with `input()` or `questionary`

---

### 3. DestructiveCommand
For commands that modify or delete data (blocked from web).

```python
from django_cfg.management.utils import DestructiveCommand

class Command(DestructiveCommand):
    help = 'Clear all cache data'

    def handle(self, *args, **options):
        self.logger.warning("Clearing cache")
        # Destructive operations
```

**Metadata:**
- `web_executable = False`
- `requires_input = True`
- `is_destructive = True`

**Use for:** clear_constance, flush, clear cache commands

---

### 4. AdminCommand
For administrative commands safe for web execution.

```python
from django_cfg.management.utils import AdminCommand

class Command(AdminCommand):
    help = 'Run database migrations'

    def handle(self, *args, **options):
        self.logger.info("Running migrations")
        # Admin operations
```

**Metadata:**
- `web_executable = True`
- `requires_input = False`
- `is_destructive = False`

**Use for:** migrate, collectstatic, createcachetable

---

## Refactoring Examples

### Before: Manual Logger & Metadata (15 lines)

```python
from django.core.management.base import BaseCommand
from django_cfg.modules.django_logging import get_logger

logger = get_logger('show_config')

class Command(BaseCommand):
    logger = get_logger('show_config')  # Duplicate!

    # Web execution metadata
    web_executable = True
    requires_input = False
    is_destructive = False

    help = 'Show Django Config configuration'

    def handle(self, *args, **options):
        logger.info("Starting command")
        # Command logic
```

### After: Using SafeCommand (5 lines)

```python
from django_cfg.management.utils import SafeCommand

class Command(SafeCommand):
    help = 'Show Django Config configuration'

    def handle(self, *args, **options):
        self.logger.info("Starting command")
        # Command logic
```

**Result: 67% less boilerplate code!**

---

## More Examples

### Example 1: clear_constance.py

**Before:**
```python
from django.core.management.base import BaseCommand
from django_cfg.modules.django_logging import get_logger

class Command(BaseCommand):
    logger = get_logger('clear_constance')

    web_executable = False
    requires_input = True
    is_destructive = True

    help = 'Clear Constance configuration cache'

    def handle(self, *args, **options):
        self.logger.info("Clearing cache")
```

**After:**
```python
from django_cfg.management.utils import DestructiveCommand

class Command(DestructiveCommand):
    command_name = 'clear_constance'  # Optional: for custom logger name
    help = 'Clear Constance configuration cache'

    def handle(self, *args, **options):
        self.logger.info("Clearing cache")
```

---

### Example 2: superuser.py

**Before:**
```python
from django.core.management.base import BaseCommand
from django_cfg.modules.django_logging import get_logger
import questionary

logger = get_logger('superuser')

class Command(BaseCommand):
    web_executable = False
    requires_input = True
    is_destructive = False

    help = 'Create superuser'

    def handle(self, *args, **options):
        logger.info("Starting")
        username = questionary.text("Username:").ask()
```

**After:**
```python
from django_cfg.management.utils import InteractiveCommand
import questionary

class Command(InteractiveCommand):
    help = 'Create superuser'

    def handle(self, *args, **options):
        self.logger.info("Starting")
        username = questionary.text("Username:").ask()
```

---

### Example 3: migrate_all.py

**Before:**
```python
from django.core.management.base import BaseCommand
from django_cfg.modules.django_logging import get_logger

class Command(BaseCommand):
    logger = get_logger('migrate_all')

    web_executable = True
    requires_input = False
    is_destructive = False

    help = 'Run migrations'

    def handle(self, *args, **options):
        self.logger.info("Running migrations")
```

**After:**
```python
from django_cfg.management.utils import AdminCommand

class Command(AdminCommand):
    help = 'Run migrations'

    def handle(self, *args, **options):
        self.logger.info("Running migrations")
```

---

## Custom Logger Name

By default, the logger name is auto-detected from the module name. To override:

```python
class Command(SafeCommand):
    command_name = 'my_custom_logger_name'
    help = 'My command'
```

---

## Quick Selection Guide

```
┌─────────────────────────────────────┬─────────────────────┐
│ Command Type                        │ Use This            │
├─────────────────────────────────────┼─────────────────────┤
│ Read-only (no modifications)        │ SafeCommand         │
│ Requires input() or questionary     │ InteractiveCommand  │
│ Deletes or modifies data            │ DestructiveCommand  │
│ Admin tasks (migrations, etc)       │ AdminCommand        │
└─────────────────────────────────────┴─────────────────────┘
```

---

## Security Integration

These base classes integrate with django_cfg's security system:

1. **commands_security.py** - Analyzes `web_executable`, `requires_input`, `is_destructive` attributes
2. **commands_service.py** - Filters commands based on safety metadata
3. **API views** - Blocks unsafe commands from web execution

When you use these base classes, your commands are automatically categorized and protected.

---

## Refactoring Checklist

When refactoring existing commands:

- [ ] Remove `from django_cfg.modules.django_logging import get_logger`
- [ ] Remove `logger = get_logger('...')` (both global and in class)
- [ ] Choose appropriate base class (SafeCommand, InteractiveCommand, etc)
- [ ] Import base class: `from django_cfg.management.utils import SafeCommand`
- [ ] Change inheritance: `class Command(SafeCommand):`
- [ ] Remove metadata attributes (if they match base class defaults)
- [ ] Replace `logger.info()` with `self.logger.info()`
- [ ] Add `command_name = '...'` if custom logger name needed
- [ ] Test the command

---

## Migration Strategy

### Find All Commands to Refactor

```bash
# Find all commands with manual metadata
find . -name "*.py" -path "*/management/commands/*" -exec grep -l "web_executable" {} \;
```

### Refactor by Priority

1. **Start with SafeCommand** - Easiest wins, most common
2. **Then InteractiveCommand** - Clear pattern with input()
3. **Then DestructiveCommand** - Important for security
4. **Finally AdminCommand** - Review case-by-case

### Testing

```bash
# Test command help
python manage.py <command> --help

# Test command execution
python manage.py <command>

# Test logger
# Should see: "Command initialized: <name> (web_executable=..., ...)"
```

---

## Advanced: Override Metadata

If you need custom metadata different from base class defaults:

```python
from django_cfg.management.utils import SafeCommand

class Command(SafeCommand):
    # Override defaults if needed
    web_executable = False  # Make it non-web-executable
    is_destructive = True   # Mark as destructive

    help = 'Special command'
```

Though generally, if you need different metadata, choose a different base class.

---

## Benefits Summary

| Feature | Before | After |
|---------|--------|-------|
| Lines of boilerplate | ~15 lines | ~3 lines |
| Logger setup | Manual | Automatic |
| Metadata | Manual | Automatic |
| Type safety | None | Built-in |
| Code clarity | Low | High |
| Maintenance | Hard | Easy |

---

## FAQ

**Q: Can I still use `BaseCommand` directly?**
A: Yes, but you'll need to manually add logger and metadata.

**Q: What if I need different metadata than the base classes?**
A: Choose the closest base class or override the attributes you need.

**Q: Does this work with existing Django commands?**
A: Yes, these are just base classes that extend `BaseCommand`.

**Q: Can I use multiple inheritance?**
A: Not needed - each base class already has everything you need.

**Q: What about existing code using the old approach?**
A: Both approaches work. Refactor gradually as you touch files.

---

## Support

For issues or questions:
- Check `commands_security.py` for security system details
- Review `commands_service.py` for filtering logic
- See `mixins.py` source code for implementation

---

**Last Updated:** 2025-01-04
**Version:** 1.0.0
