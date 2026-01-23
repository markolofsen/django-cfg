# Django Admin - Declarative Configuration

Type-safe admin configurations using Pydantic. **60-80% code reduction** vs traditional Django admin.

## Quick Start

```python
from django.contrib import admin
from django_cfg.modules.django_admin import (
    AdminConfig, BadgeField, DateTimeField, StackedField, RowItem, Icons, computed_field
)
from django_cfg.modules.django_admin.base import PydanticAdmin

config = AdminConfig(
    model=Vehicle,
    select_related=['source', 'brand'],
    prefetch_related=['photos'],
    list_display=['main_photo', 'vehicle_info', 'pricing_info', 'status_info'],
    display_fields=[
        StackedField(
            name='vehicle_info',
            title='Vehicle',
            rows=[
                RowItem(field='display_name', bold=True, truncate=30),
                [RowItem(field='year'), RowItem(field='mileage', suffix=' km')],
                RowItem(field='fuel_type', widget='badge', label_map={'electric': 'success'}),
            ],
        ),
    ],
)

@admin.register(Vehicle)
class VehicleAdmin(PydanticAdmin):
    config = config
```

---

## Field Types

### StackedField (Composite Column)

Combines multiple fields in one compact column:

```python
StackedField(
    name='property_info',
    title='Property',
    rows=[
        RowItem(field='title', bold=True, truncate=35),
        [  # Inline row (horizontal)
            RowItem(field='listing_type', widget='badge', label_map={'rent': 'info', 'sale': 'success'}),
            RowItem(field='property_type__name', muted=True),
        ],
        RowItem(field='location__name', icon='location_on', muted=True),
    ],
    max_width='280px',
)
```

**RowItem options:**
- `widget`: `text` (default), `badge`, `datetime_relative`, `money_field`
- `bold`, `muted`, `monospace`: styling
- `prefix`, `suffix`, `truncate`: text formatting
- `label_map`: badge colors `{value: 'success'|'warning'|'danger'|'info'|'secondary'}`
- `true_label`, `false_label`: custom labels for boolean badges
- `hide_if_empty`: skip if value is None (default: True)

### BadgeField

```python
BadgeField(
    name='status',
    title='Status',
    label_map={'active': 'success', 'inactive': 'secondary', 'sold': 'danger'},
    icon=Icons.INFO,
)

# Boolean badge
BadgeField(
    name='is_normalized',
    label_map={True: 'success', False: 'warning'},
    icon=Icons.AUTO_FIX_HIGH,
)
```

### BooleanField

```python
BooleanField(name='is_active', title='Active')  # Checkmark/cross icon
```

### CurrencyField

```python
# Fixed currency
CurrencyField(name='amount', currency='USD', precision=2)

# Dynamic currency from model field
CurrencyField(
    name='price',
    currency_field='currency',      # Get currency from model
    secondary_field='price_usd',    # Show USD equivalent
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
# Basic
DecimalField(name='rate', decimal_places=8)

# With formatting
DecimalField(
    name='change_percent',
    decimal_places=2,
    suffix='%',
    show_sign=True,  # +5.25% green, -3.14% red
)

# Currency prefix
DecimalField(name='amount', prefix='$', thousand_separator=True)
```

### DateTimeField

```python
DateTimeField(name='created_at', show_relative=True)  # "2 hours ago"
DateTimeField(name='updated_at', format='%Y-%m-%d %H:%M')
```

### ShortUUIDField

```python
ShortUUIDField(name='id', length=8, copy_on_click=True)
ShortUUIDField(name='id', is_link=True)  # Styled as clickable link
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

### UserField

```python
UserField(name='user', title='User', header=True)  # With avatar
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
    target='_blank',
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
    enable_plugins=True,  # Tables, Mermaid diagrams
)
```

### AvatarField

```python
AvatarField(name='avatar', size=40, fallback_icon=Icons.PERSON)
```

### StatusBadgesField

Multiple badges from different fields:

```python
StatusBadgesField(
    name='badges',
    rules=[
        BadgeRule(field='status', label_map={'active': 'success'}),
        BadgeRule(field='is_verified', true_label='Verified', variant='info'),
    ],
)

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

**`self.html` methods:** `badge()`, `span()`, `inline()`, `stacked()`, `link()`, `image()`, `empty()`

---

## Actions

### Bulk Actions (require selection)

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

### Changelist Actions (buttons, no selection)

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

---

## Performance

```python
config = AdminConfig(
    model=Property,
    select_related=['source', 'location'],      # ForeignKey optimization
    prefetch_related=['photos'],                 # M2M / reverse FK
    annotations={'total': Count('items')},       # Calculated fields
)
```

---

## Fieldsets

```python
fieldsets=[
    FieldsetConfig(title='Basic', fields=['name', 'status']),
    FieldsetConfig(title='Details', fields=['price', 'description'], collapsed=True),
]
```

---

## Filters & Search

```python
config = AdminConfig(
    model=Property,
    list_filter=['status', 'listing_type', 'source'],
    search_fields=['title', 'listing_id', 'address'],
    autocomplete_fields=['source', 'location'],
    ordering=['-created_at'],
    date_hierarchy='created_at',
)
```

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

2234 Material Design Icons via `Icons` class:

```python
from django_cfg.modules.django_admin import Icons

Icons.CHECK_CIRCLE, Icons.ERROR, Icons.WARNING, Icons.INFO
Icons.LOCATION_ON, Icons.TRENDING_UP, Icons.AUTO_FIX_HIGH
```

See [icons/constants.py](./icons/constants.py) for full list.

---

## File Structure

```
apps/your_app/admin/
  __init__.py        # Register admins
  model_admin.py     # AdminConfig + PydanticAdmin
  actions.py         # Action handlers
  resources.py       # Import/Export
```

---

## See Also

- [Full Documentation](../../../docs_public/django_admin/)
- [Currency Module](../django_currency/) - MoneyField, exchange rates
