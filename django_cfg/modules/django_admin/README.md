# Django Admin — Declarative Configuration

> **Status (2026-11-18).** `PydanticAdmin` / `AdminConfig` is the main admin class and django-unfold is the base (pinned `>=0.110,<0.111`).
> Removed (nothing used them): Flash messages (`FlashFieldConfig`, `one_time_flash_fields`, `flash_once`), `ToonField`, `VideoField`, `AvatarField`,
> `CounterBadgeField`, `ResourceConfig`, `BackgroundTaskConfig`. `Icons` and `MoneyFieldWidget` moved out: `from django_cfg import Icons`,
> `django_cfg.modules.django_currency`.

Type-safe admin configurations using Pydantic v2. **60-80% code reduction** vs traditional Django admin.

## Quick Start

```python
from django.contrib import admin
from django_cfg.modules.django_admin import AdminConfig, BadgeField, DateTimeField
from django_cfg import Icons
from django_cfg.modules.django_admin.base import PydanticAdmin

config = AdminConfig(
    model=Vehicle,
    list_display=['photo', 'vehicle_info', 'price', 'status'],
    display_fields=[
        BadgeField(name='status', label_map={'active': 'success', 'sold': 'danger'}),
        DateTimeField(name='created_at', show_relative=True),
    ],
    select_related=['brand'],
    prefetch_related=['photos'],
    search_fields=['listing_id', 'brand__name'],
    list_filter=['status', 'brand'],
)

@admin.register(Vehicle)
class VehicleAdmin(PydanticAdmin):
    config = config
```

---

## Field Types

### StackedField — Composite Column

Combines multiple fields in one compact column:

```python
from django_cfg.modules.django_admin import StackedField, RowItem

StackedField(
    name='vehicle_info',
    title='Vehicle',
    rows=[
        RowItem(field='display_name', bold=True, truncate=30),
        [  # Inline row (horizontal)
            RowItem(field='year'),
            RowItem(field='mileage', suffix=' km'),
        ],
        RowItem(field='fuel_type', widget='badge', label_map={'electric': 'success'}),
    ],
    max_width='280px',
)
```

**RowItem options:**

| Option | Values | Description |
|--------|--------|-------------|
| `widget` | `text`, `badge`, `datetime_relative`, `money_field` | Display widget |
| `show_relative`, `decimal_places`, `icon` | | Per-widget options |
| `bold`, `muted`, `monospace` | `bool` | Text styling |
| `prefix`, `suffix` | `str` | Text decoration |
| `truncate` | `int` | Max character length |
| `label_map` | `dict` | Badge colors `{'value': 'success'\|'warning'\|'danger'\|'info'\|'secondary'}` |
| `true_label`, `false_label` | `str` | Custom labels for boolean values |
| `hide_if_empty` | `bool` | Skip if value is None (default: `True`) |

### BadgeField

```python
BadgeField(
    name='status',
    label_map={'active': 'success', 'inactive': 'secondary', 'sold': 'danger'},
    icon=Icons.INFO,
)

# Boolean badge
BadgeField(
    name='is_verified',
    label_map={True: 'success', False: 'warning'},
    icon=Icons.AUTO_FIX_HIGH,
)
```

### BooleanField

```python
BooleanField(name='is_active', title='Active')  # Renders ✓ / ✗ icon
```

### CurrencyField

```python
# Fixed currency
CurrencyField(name='amount', currency='USD', precision=2)

# Dynamic currency from model field
CurrencyField(
    name='price',
    currency_field='currency',       # Read currency from this model field
    secondary_field='price_usd',     # Show USD equivalent alongside
    secondary_currency='USD',
)
```

### MoneyFieldDisplay

For models using `MoneyField` (auto-detects `_currency`, `_target` fields):

```python
MoneyFieldDisplay(name='price', title='Price')  # Shows: ₩15,700,000 → $10,645
```

### DecimalField

```python
DecimalField(name='rate', decimal_places=8)

DecimalField(
    name='change_percent',
    decimal_places=2,
    suffix='%',
    show_sign=True,       # +5.25% green, -3.14% red
)

DecimalField(name='amount', prefix='$', thousand_separator=True)
```

### DateTimeField

```python
DateTimeField(name='created_at', show_relative=True)  # "2 hours ago"
DateTimeField(name='updated_at', datetime_format='%Y-%m-%d %H:%M')
```

### ShortUUIDField

```python
ShortUUIDField(name='id', length=8, copy_on_click=True)
ShortUUIDField(name='id', is_link=True)  # Styled as a clickable link
```

### TextField

```python
TextField(name='title', truncate=50)
TextField(name='raw_text', truncate=100, monospace=True)
```

### ImagePreviewField

```python
ImagePreviewField(
    name='main_photo_url',
    thumbnail_max_width=80,
    thumbnail_max_height=60,
    border_radius=4,
    zoom_enabled=True,
)
```

### ImageField

```python
ImageField(name='avatar_url', title='Avatar', max_width='40px', border_radius='50%')
```

### UserField

```python
UserField(name='user', title='User', header=True)   # With avatar
UserField(name='created_by', show_email=True)
```

### ForeignKeyField

```python
ForeignKeyField(
    name='currency',
    display_field='code',
    subtitle_field='name',
    link_to_admin=True,
)

ForeignKeyField(
    name='user',
    display_field='username',
    subtitle_template='{email} • {phone}',
    link_icon=Icons.OPEN_IN_NEW,
)
```

### LinkField

```python
LinkField(
    name='location',
    link_field='google_maps_url',
    link_icon=Icons.LOCATION_ON,
)

LinkField(
    name='listing_url',
    static_text='Open',
    link_field='listing_url',
    link_target='_blank',
)
```

### MarkdownField

```python
MarkdownField(
    name='description',
    title='AI Description',
    collapsible=True,
    default_open=True,
    max_height='400px',
    enable_plugins=True,  # Markdown plugins (tables, Mermaid diagrams)
)
```

### StatusBadgesField

Multiple badges from different fields in one column. A `BadgeRule` shows its badge when the model field `condition_field` equals `condition_value`:

```python
StatusBadgesField(
    name='flags',
    badge_rules=[
        BadgeRule(condition_field='status', condition_value='banned', label='Banned', variant='danger'),
        BadgeRule(condition_field='is_verified', condition_value=True, label='Verified', variant='info', icon=Icons.CHECK_CIRCLE),
        BadgeRule(condition_field='subscription_tier', condition_value='pro', label='Pro', variant='warning'),
    ],
)
```

---

## Computed Fields

Custom display methods with `self.html` helpers:

```python
@admin.register(Vehicle)
class VehicleAdmin(PydanticAdmin):
    config = config

    @computed_field('Photos')
    def photos_count(self, obj):
        count = len(obj.photos.all())  # Uses prefetch_related
        if count == 0:
            return self.html.badge('0', variant='secondary')
        return self.html.badge(str(count), variant='info')

    @computed_field('Terms')
    def terms_display(self, obj):
        if obj.is_rental:
            return self.html.badge(obj.rental_period or 'N/A', variant='info')
        return self.html.badge(obj.ownership_type or 'N/A', variant='success')
```

**`self.html` methods:** `badge()`, `span()`, `inline()`, `stacked()`, `link()`, `empty()`, and more (see the API reference)

---

## Actions

### Bulk Actions (require row selection)

```python
config = AdminConfig(
    model=Vehicle,
    actions=[
        ActionConfig(
            name='mark_as_sold',
            description='Mark as sold',
            action_type='bulk',
            variant='danger',
            handler=mark_as_sold,
        ),
    ],
)

def mark_as_sold(modeladmin, request, queryset):
    queryset.update(status='sold')
    messages.success(request, f'{queryset.count()} marked as sold')
```

### Changelist Actions (buttons, no selection required)

```python
ActionConfig(
    name='sync_all',
    description='Sync All',
    action_type='changelist',
    variant='primary',
    handler=sync_all,
)

def sync_all(modeladmin, request):
    call_command('sync_data')
    messages.success(request, 'Synced')
    return redirect(reverse('admin:app_model_changelist'))  # Must return HttpResponse
```

**`variant` values:** `default`, `primary`, `success`, `warning`, `danger`, `info`

---

## Performance

```python
config = AdminConfig(
    model=Property,
    select_related=['source', 'location'],       # ForeignKey optimization
    prefetch_related=['photos'],                  # M2M / reverse FK
    annotations={'total': Count('items')},        # Calculated fields
)
```

---

## Fieldsets

```python
from django_cfg.modules.django_admin import FieldsetConfig

fieldsets=[
    FieldsetConfig(title='Basic', fields=['name', 'status']),
    FieldsetConfig(title='Details', fields=['price', 'description'], collapsed=True),
]
```

---

## List Editable

Edit fields directly in the list view without opening each record:

```python
config = AdminConfig(
    model=Review,
    list_display=['created_at', 'user', 'quote', 'is_published', 'order'],
    list_display_links=['created_at'],
    list_editable=['is_published', 'order'],
)
```

**Rules:**
- Fields in `list_editable` cannot be in `list_display_links`
- Fields in `list_editable` must be in `list_display`
- Display methods are automatically skipped for editable fields

---

## Filters & Search

### Declarative style (recommended)

```python
from django_cfg.modules.django_admin import AdminConfig, FilterConfig

config = AdminConfig(
    model=Order,
    list_filter=[
        FilterConfig(field='status',     type='choices_dropdown'),
        FilterConfig(field='created_at', type='range_date'),
        FilterConfig(field='amount',     type='range_numeric'),
        FilterConfig(field='customer',   type='autocomplete'),  # needs search_fields on CustomerAdmin
        FilterConfig(field='is_active',  type='boolean'),
        # Raw entries still work:
        'currency',
        MyCustomFilter,
    ],
    show_facets=True,   # Show result counts next to filter options (Django 5.0+)
    search_fields=['id', 'customer__email'],
    date_hierarchy='created_at',
)
```

### FilterType quick reference

| `type` | Use case |
|--------|----------|
| `choices_dropdown` / `choices_checkbox` / `choices_radio` | Field with `choices=` |
| `boolean` | `BooleanField` |
| `related_dropdown` / `related_checkbox` | `ForeignKey` |
| `autocomplete` / `autocomplete_multiple` | `ForeignKey` with search |
| `range_numeric` / `slider` | Numeric from/to |
| `range_date` / `range_datetime` | Date/datetime from/to |
| `text` | Text `icontains` search |
| `dropdown` / `dropdown_multiple` | Custom `SimpleListFilter` |

### Raw style (still works)

```python
list_filter=['status', MyCustomFilter, ('created_at', RangeDateFilter)]
```

`FilterSpec = str | type | tuple[str, type] | FilterConfig`

---

## Widget Configs (Form Fields)

Override form widgets declaratively:

```python
from django_cfg.modules.django_admin import JSONWidgetConfig, TextWidgetConfig, ImagePreviewWidgetConfig

config = AdminConfig(
    model=MyModel,
    widgets=[
        JSONWidgetConfig(field='config_schema', mode='tree', height='500px'),
        TextWidgetConfig(field='description', rows=10, placeholder='Enter text…'),
        ImagePreviewWidgetConfig(field='photo', thumbnail_max_width=200, zoom_enabled=True),
    ],
)
```

| Widget | Key Options |
|--------|-------------|
| `JSONWidgetConfig` | `mode` (`code`/`tree`/`view`), `height`, `width`, `show_copy_button` |
| `TextWidgetConfig` | `placeholder`, `max_length`, `rows` |
| `ImagePreviewWidgetConfig` | `thumbnail_max_width/height`, `zoom_enabled`, `pan_enabled`, `show_info` |

---

## Import/Export

```python
from import_export import resources

class VehicleResource(resources.ModelResource):
    class Meta:
        model = Vehicle
        fields = ('id', 'listing_id', 'brand__name', 'model__name', 'price')

config = AdminConfig(
    model=Vehicle,
    import_export_enabled=True,
    resource_class=VehicleResource,
)
```

---

## Icons

2200+ Material Design Icons via `Icons`:

```python
from django_cfg import Icons

Icons.CHECK_CIRCLE, Icons.ERROR, Icons.WARNING, Icons.INFO
Icons.LOCATION_ON, Icons.TRENDING_UP, Icons.AUTO_FIX_HIGH
Icons.KEY, Icons.LOCK, Icons.VISIBILITY, Icons.OPEN_IN_NEW
```

See `django_cfg/icons/constants.py` for the full list (generated by `scripts/icons/generate_icons.py`).

---

## Type Aliases

| Name | Type | Use Case |
|------|------|----------|
| `FieldConfigType` | Discriminated union of the 16 field configs plus the base `FieldConfig` | `display_fields` annotation |
| `FilterSpec` | `str \| type \| tuple[str, type] \| FilterConfig` | `list_filter` annotation |
| `FilterConfig` | Pydantic model | Declarative `list_filter` entry |
| `FilterType` | `Literal[17 values]` | Valid `FilterConfig.type` keys |
| `DjangoFieldsets` | `tuple[tuple[str \| None, dict], ...]` | Django admin fieldsets format |
| `FieldsetTuple` | `tuple[str \| None, dict]` | Single fieldset entry |
| `FieldsetOptions` | `dict[str, Any]` | Fieldset options dict |

---

## File Structure

```
apps/your_app/admin/
  __init__.py        # Register admins
  model_admin.py     # AdminConfig + PydanticAdmin
  actions.py         # Action handlers
  resources.py       # Import/Export resources
```

**Module internals:**

```
modules/django_admin/
  base/
    pydantic_admin/
      mixin.py                  # PydanticAdminMixin — core orchestrator
      display_methods/          # Auto-generated display method factories
        json_methods.py         # create_jsonfield_display_methods()
        image_methods.py        # create_imagefield_display_methods()
        markdown_methods.py     # create_markdownfield_display_methods()
        fieldsets.py            # apply_replacements_to_fieldsets()
  config/
    field_config/               # All 16 FieldConfig subclasses
    documentation/              # DocumentationConfig (dir/file/content modes)
  utils/
    displays/
      geo/                      # CountryDisplay, CityDisplay, CoordinatesDisplay
      stacked/                  # StackedDisplay + renderers (badge/text/datetime/money)
  widgets/
    registry.py                 # WidgetRegistry — maps ui_widget → render handler
```

---

## See Also

- [Full Documentation](https://djangocfg.com/docs/features/modules/django-admin/overview)
- [Currency Module](../django_currency/) — MoneyField, exchange rates
