# django_currency

Money and currency model fields with automatic conversion and display helpers.

## Fields

### `MoneyField`

`DecimalField` subclass that auto-creates a companion `CurrencyField` column
and attaches computed descriptors to the model.

```python
from django_cfg.modules.django_currency import MoneyField

class Product(models.Model):
    price = MoneyField(
        default_currency="KRW",   # currency stored in DB
        target_currency="USD",    # currency used for conversion
    )
```

**Auto-created attributes on the model:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `price_currency` | `CharField` (DB column) | ISO 4217 code, e.g. `"KRW"` |
| `price_target` | `Decimal` (descriptor) | Raw converted amount |
| `price_target_rounded` | `Decimal` (descriptor) | Smart-rounded converted amount |
| `price_display` | `str` (descriptor) | Formatted original, e.g. `"₩15,000,000"` |
| `price_target_display` | `str` (descriptor) | Formatted target, e.g. `"$11,500"` |
| `price_full_display` | `str` (descriptor) | Combined, e.g. `"$11,500 (₩15M)"` |

**Do NOT declare `price_currency` manually** — `MoneyField.contribute_to_class()`
adds it automatically. A duplicate declaration causes `column already exists` on migration.

### `CurrencyField`

`CharField(max_length=10)` for ISO 4217 currency codes. Created automatically
by `MoneyField`; only declare standalone if you need a currency column independent
of a money amount.

```python
# Standalone use only — do NOT use alongside MoneyField
currency = CurrencyField(default="USD")
```

## Migration behaviour

### `deconstruct()` — no django_cfg import in migrations

`CurrencyField.deconstruct()` returns `django.db.models.CharField` as the path,
so generated migrations contain no reference to `django_cfg`. This keeps migrations
portable across projects.

### Automatic fake-apply for existing columns

When a project already has the `price_currency` column in the DB (created by an
older `MoneyField` migration that didn't track the companion field), running
`makemigrations` generates an `AddField` migration. Applying it normally would
crash with `column already exists`.

`CurrencyField` registers itself with `FakeMigrationHandler` at import time:

```python
# Happens automatically — nothing to configure
_register_currency_fake_detector()
```

`MigrationManager` (used by `migrate_all`) detects such migrations and runs
`migrate <app> <migration> --fake` instead of a real apply.

## Conversion

Conversion uses `CurrencyRate` records from `django_cfg.apps.tools.currency`.
If no rate exists for a pair, `*_target` descriptors return `None`.

Smart rounding thresholds (`price_target_rounded`):

| Amount | Rounds to |
|--------|-----------|
| < 100 | 1 |
| 100 – 1 000 | 10 |
| 1 000 – 10 000 | 100 |
| 10 000 – 100 000 | 500 |
| > 100 000 | 1 000 |

Override with `round_to=N`:

```python
price = MoneyField(default_currency="IDR", target_currency="USD", round_to=1000)
```

## Admin

```python
from django_cfg.modules.django_currency import MoneyFieldAdminMixin

@admin.register(Product)
class ProductAdmin(MoneyFieldAdminMixin, admin.ModelAdmin):
    pass
```

Adds readonly fields for `price_target`, `price_rate`, `price_rate_at` and
renders `MoneyFieldWidget` (amount + currency dropdown) in edit forms.
