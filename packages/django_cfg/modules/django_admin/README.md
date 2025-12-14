# Django Admin - Declarative Configuration with Pydantic 2.x

Type-safe, reusable admin configurations using Pydantic models.
Provides **60-80% code reduction** compared to traditional Django admin.

## Quick Links

- [Full Documentation](../../../docs_public/django_admin/)
  - [Overview](../../../docs_public/django_admin/overview.md) - Philosophy and architecture
  - [Quick Start](../../../docs_public/django_admin/quick-start.md) - Get started in 5 minutes
  - [Configuration](../../../docs_public/django_admin/configuration.md) - Complete configuration reference
  - [Field Types](../../../docs_public/django_admin/field-types.md) - All 8 specialized field types
  - [Filters](../../../docs_public/django_admin/filters.md) - Advanced filtering
  - [Examples](../../../docs_public/django_admin/examples.md) - Production-ready examples
  - [API Reference](../../../docs_public/django_admin/api-reference.md) - Complete API documentation

## Available Icons

**2234 Material Design Icons** available via `Icons` class. See [icons/constants.py](./icons/constants.py) for the full list.

Popular icons: `Icons.DASHBOARD`, `Icons.SETTINGS`, `Icons.PEOPLE`, `Icons.SYNC`, `Icons.CHECK_CIRCLE`, `Icons.ERROR`, `Icons.WARNING`, `Icons.INFO`, `Icons.DELETE`, `Icons.EDIT`, `Icons.ADD`, `Icons.SEARCH`, `Icons.FILTER`, `Icons.DOWNLOAD`, `Icons.UPLOAD`, `Icons.REFRESH`, `Icons.CLOSE`, `Icons.MENU`, `Icons.NOTIFICATION`, `Icons.EMAIL`, `Icons.PHONE`, `Icons.MESSAGE`, `Icons.CALENDAR`, `Icons.CLOCK`, `Icons.LOCATION`, `Icons.STAR`, `Icons.FAVORITE`, `Icons.SHARE`, `Icons.VISIBILITY`, `Icons.LOCK`, `Icons.ACCOUNT_CIRCLE`, `Icons.PAYMENT`, `Icons.SHOPPING_CART`, `Icons.CREDIT_CARD`, `Icons.RECEIPT`, `Icons.BUSINESS`, `Icons.WORK`, `Icons.HOME`, `Icons.SCHOOL`, `Icons.ATTACH_FILE`, `Icons.FOLDER`, `Icons.CLOUD`, `Icons.STORAGE`, `Icons.SECURITY`, `Icons.VPNLOCK`, `Icons.PLAY_ARROW`, `Icons.PAUSE`, `Icons.STOP`, `Icons.SKIP_NEXT`, `Icons.SKIP_PREVIOUS`, `Icons.VOLUME_UP`, `Icons.BRIGHTNESS_HIGH`, `Icons.WIFI`, `Icons.BLUETOOTH`, `Icons.BATTERY_FULL`, and many more.

---

## Basic Example

```python
from django.contrib import admin
from django_cfg.modules.django_admin import AdminConfig, BadgeField, CurrencyField
from django_cfg.modules.django_admin.base import PydanticAdmin

config = AdminConfig(
    model=Payment,
    list_display=["transaction_id", "user", "amount", "status"],
    display_fields=[
        BadgeField(name="status", label_map={"pending": "warning", "completed": "success"}),
        CurrencyField(name="amount", currency="USD", precision=2),
    ],
)

@admin.register(Payment)
class PaymentAdmin(PydanticAdmin):
    config = config
```

---

## Complete Example - All Features Combined

**Full-featured admin using ALL capabilities of django_admin:**

```python
# File: apps/payments/admin/payment_admin.py
from django.contrib import admin
from django.db.models import Count, Sum, Q
from unfold.admin import TabularInline
from unfold.contrib.filters.admin import AutocompleteSelectFilter

from django_cfg.modules.django_admin import (
    AdminConfig,
    ActionConfig,
    BadgeField,
    BooleanField,
    CurrencyField,
    DateTimeField,
    DocumentationConfig,
    FieldsetConfig,
    Icons,
    JSONWidgetConfig,
    ShortUUIDField,
    UserField,
    computed_field,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import Payment, PaymentLog
from .actions import (
    approve_payments,
    reject_payments,
    sync_payment_statuses,
    export_monthly_report,
)
from .filters import PaymentStatusFilter, PaymentAmountFilter
from .resources import PaymentResource


# Inline for payment logs
class PaymentLogInline(TabularInline):
    model = PaymentLog
    extra = 0
    fields = ['created_at', 'status', 'message']
    readonly_fields = ['created_at', 'status', 'message']
    can_delete = False


# Full-featured admin configuration
payment_config = AdminConfig(
    model=Payment,

    # ===== PERFORMANCE OPTIMIZATION =====
    select_related=['user', 'currency'],
    prefetch_related=['transaction_logs'],
    annotations={
        'total_logs': Count('transaction_logs'),
        'total_amount': Sum('amount'),
    },

    # ===== LIST DISPLAY =====
    list_display=[
        'id',
        'user',
        'amount_usd',
        'currency',
        'status',
        'is_confirmed',
        'created_at',
        'updated_at',
    ],
    list_display_links=['id', 'user'],  # Clickable fields
    list_max_show_all=200,  # Max items for "show all"

    # ===== DISPLAY FIELDS (auto-generated methods) =====
    display_fields=[
        ShortUUIDField(name='id', title='Payment ID'),
        UserField(name='user', title='User', header=True),
        CurrencyField(name='amount_usd', title='Amount', currency='USD', precision=2),
        BadgeField(
            name='status',
            title='Status',
            label_map={
                'pending': 'warning',
                'processing': 'info',
                'completed': 'success',
                'failed': 'danger',
                'cancelled': 'secondary',
            },
        ),
        BooleanField(name='is_confirmed', title='Confirmed'),
        DateTimeField(name='created_at', title='Created', show_relative=True),
        DateTimeField(name='updated_at', title='Updated', show_relative=True),
        # ImageField(name='qr_code', title='QR Code', max_height='100px'),  # For image fields
        # MarkdownField(name='description', title='Description'),  # For markdown content
    ],

    # ===== ACTIONS =====
    actions=[
        # Bulk actions (require selection)
        ActionConfig(
            name='approve_payments',
            description='Approve selected payments',
            action_type='bulk',
            variant='success',
            icon=Icons.CHECK_CIRCLE,
            confirmation=True,
            permissions=['payments.can_approve'],
            handler=approve_payments,
        ),
        ActionConfig(
            name='reject_payments',
            description='Reject selected payments',
            action_type='bulk',
            variant='danger',
            icon=Icons.CANCEL,
            confirmation=True,
            handler=reject_payments,
        ),

        # Changelist actions (buttons above listing)
        ActionConfig(
            name='sync_payment_statuses',
            description='🔄 Sync Payment Statuses',
            action_type='changelist',
            variant='primary',
            icon=Icons.SYNC,
            confirmation=True,
            handler=sync_payment_statuses,
        ),
        ActionConfig(
            name='export_monthly_report',
            description='📊 Export Monthly Report',
            action_type='changelist',
            variant='info',
            icon=Icons.DOWNLOAD,
            handler=export_monthly_report,
        ),
    ],

    # ===== FIELDSETS =====
    fieldsets=[
        FieldsetConfig(
            title='Basic Information',
            fields=['internal_payment_id', 'user', 'status'],
        ),
        FieldsetConfig(
            title='Payment Details',
            fields=['amount_usd', 'currency', 'payment_method', 'transaction_id'],
        ),
        FieldsetConfig(
            title='Provider Information',
            fields=['provider', 'provider_payment_id', 'provider_data'],
        ),
        FieldsetConfig(
            title='Blockchain',
            fields=['transaction_hash', 'confirmations_count', 'explorer_link'],
            collapsed=True,
        ),
        FieldsetConfig(
            title='Metadata',
            fields=['metadata', 'admin_notes'],
            collapsed=True,
        ),
        FieldsetConfig(
            title='Timestamps',
            fields=['created_at', 'updated_at', 'expires_at'],
            collapsed=True,
        ),
    ],

    # ===== WIDGETS (for form fields) =====
    widgets=[
        JSONWidgetConfig(
            field='provider_data',
            mode='code',
            height='400px',
            show_copy_button=True,
        ),
        JSONWidgetConfig(
            field='metadata',
            mode='tree',
            height='300px',
        ),
        # TextWidgetConfig(
        #     field='admin_notes',
        #     widget_type='textarea',
        #     rows=5,
        #     cols=80,
        # ),
    ],

    # ===== FILTERS & SEARCH =====
    list_filter=[
        PaymentStatusFilter,
        PaymentAmountFilter,
        'currency',
        'payment_method',
        'created_at',
        ('user', AutocompleteSelectFilter),
    ],
    search_fields=[
        'internal_payment_id',
        'provider_payment_id',
        'transaction_hash',
        'user__email',
        'user__username',
    ],
    autocomplete_fields=['user'],

    # Form field options
    # raw_id_fields=['provider'],  # Raw ID widget for ForeignKey
    # filter_horizontal=['tags'],  # Horizontal filter for M2M
    # filter_vertical=['categories'],  # Vertical filter for M2M
    # prepopulated_fields={'slug': ('name',)},  # Auto-populate slug from name

    # Form field overrides (advanced)
    # formfield_overrides={
    #     models.TextField: {'widget': WysiwygWidget},
    #     models.JSONField: {'widget': JSONEditorWidget},
    # },

    # ===== IMPORT/EXPORT =====
    import_export_enabled=True,
    resource_class=PaymentResource,  # Custom resource class
    # OR use declarative resource_config:
    # resource_config=ResourceConfig(
    #     fields=['id', 'user', 'amount_usd', 'status'],
    #     exclude=['provider_data'],
    #     import_id_fields=['id'],
    #     skip_unchanged=True,
    # ),

    # ===== DOCUMENTATION =====
    documentation=DocumentationConfig(
        source_dir='apps/payments/@docs',
        title='💳 Payment System Documentation',
        show_on_changelist=True,
        show_on_changeform=False,
        collapsible=True,
        default_open=False,
        max_height='600px',
        show_management_commands=True,
        enable_plugins=True,
        sort_sections=True,
    ),

    # ===== BACKGROUND TASKS (optional) =====
    # background_task_config=BackgroundTaskConfig(
    #     enabled=True,
    #     queue_name='payments',
    #     task_timeout=300,
    # ),

    # ===== OTHER SETTINGS =====
    readonly_fields=[
        'id',
        'internal_payment_id',
        'created_at',
        'updated_at',
        'provider_payment_id',
    ],
    ordering=['-created_at'],
    list_per_page=50,
    date_hierarchy='created_at',
    save_on_top=True,  # Show save buttons on top
    save_as=True,  # Enable "save as new"
    preserve_filters=True,  # Preserve filters after save

    # Encrypted fields (django-crypto-fields)
    # show_encrypted_fields_as_plain_text=False,  # Keep encrypted fields masked
)


# Admin class with custom methods
@admin.register(Payment)
class PaymentAdmin(PydanticAdmin):
    """
    Full-featured Payment admin using django_admin declarative approach.

    Demonstrates ALL capabilities:
    - Display fields (auto-generated methods) - 7 types used + 2 commented
    - Bulk actions (require selection) - 2 examples
    - Changelist actions (buttons above listing) - 2 examples
    - Fieldsets (organized form) - 6 sections with collapsed
    - Widgets (JSON editor, textarea) - 2 JSON + 1 text (commented)
    - Filters (standard + autocomplete + custom) - 6 filters
    - Search fields - 5 fields
    - Import/Export - both resource_class and resource_config (commented)
    - Documentation - full config
    - Performance optimization - select_related, prefetch_related, annotations
    - Custom computed fields - 3 examples with self.html
    - Inlines - PaymentLogInline
    - Form options - autocomplete, raw_id (commented), filter_horizontal (commented), prepopulated (commented)
    - Pagination - list_per_page, list_max_show_all
    - Extra options - save_on_top, save_as, preserve_filters, date_hierarchy
    - Background tasks - commented example
    - Encrypted fields - commented example
    """
    config = payment_config

    # Inlines
    inlines = [PaymentLogInline]

    # Custom computed field with self.html
    @computed_field('Payment Link')
    def payment_link_display(self, obj):
        """Display payment URL as clickable link."""
        if not obj.payment_url:
            return self.html.empty()

        return self.html.link(
            obj.payment_url,
            'Open Payment Page',
            target='_blank',
            icon=Icons.OPEN_IN_NEW
        )

    @computed_field('Explorer')
    def explorer_link_display(self, obj):
        """Display blockchain explorer link."""
        if not obj.transaction_hash:
            return self.html.empty()

        link = obj.get_explorer_link()
        if link:
            return self.html.link(
                link,
                f'{obj.transaction_hash[:16]}...',
                target='_blank',
                icon=Icons.SEARCH
            )
        return self.html.code(obj.transaction_hash)

    @computed_field('Confirmations')
    def confirmations_display(self, obj):
        """Display confirmation count with badge."""
        if obj.confirmations_count == 0:
            return self.html.empty()

        # Color based on confirmation count
        if obj.confirmations_count >= 6:
            variant = 'success'
        elif obj.confirmations_count >= 3:
            variant = 'info'
        else:
            variant = 'warning'

        return self.html.badge(
            f'{obj.confirmations_count} confirmations',
            variant=variant,
            icon=Icons.CHECK_CIRCLE
        )
```

**Action handlers** (File: `apps/payments/admin/actions.py`):

```python
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.core.management import call_command
from io import StringIO


# Bulk action (requires queryset)
def approve_payments(modeladmin, request, queryset):
    """Approve selected payments."""
    approved = 0
    for payment in queryset.filter(status='pending'):
        if payment.approve():
            approved += 1

    messages.success(request, f'✅ Approved {approved} payment(s)')


def reject_payments(modeladmin, request, queryset):
    """Reject selected payments."""
    rejected = queryset.update(status='cancelled')
    messages.warning(request, f'❌ Rejected {rejected} payment(s)')


# Changelist action (no queryset, returns HttpResponse)
def sync_payment_statuses(modeladmin, request):
    """Sync payment statuses from provider."""
    try:
        messages.info(request, '🔄 Syncing payment statuses...')

        out = StringIO()
        call_command('sync_payment_statuses', stdout=out)

        output = out.getvalue()
        if output:
            messages.success(request, output)
    except Exception as e:
        messages.error(request, f'❌ Error: {e}')

    return redirect(reverse('admin:payments_payment_changelist'))


def export_monthly_report(modeladmin, request):
    """Export monthly payment report."""
    try:
        messages.info(request, '📊 Generating monthly report...')

        out = StringIO()
        call_command('export_payment_report', '--month=current', stdout=out)

        messages.success(request, '✅ Report exported successfully')
    except Exception as e:
        messages.error(request, f'❌ Error: {e}')

    return redirect(reverse('admin:payments_payment_changelist'))
```

This example demonstrates **every major feature** of django_admin working together in a real-world payment admin interface.

---

## Complete Examples (from Production Code)

### 1. Display Fields (Auto-Generated Display Methods)

```python
from django_cfg.modules.django_admin import (
    AdminConfig, BadgeField, BooleanField, CurrencyField,
    DateTimeField, ForeignKeyField, UserField, ShortUUIDField, Icons
)

config = AdminConfig(
    model=Payment,
    list_display=["id", "user", "amount_usd", "status", "created_at"],
    select_related=["user", "currency"],  # Optimize ForeignKey queries
    display_fields=[
        # Short UUID display
        ShortUUIDField(name="id", title="ID"),

        # User with avatar
        UserField(name="user", title="User", header=True),

        # ForeignKey relation with admin link
        ForeignKeyField(
            name="currency",
            display_field="code",
            subtitle_field="name",
            link_to_admin=True,
        ),

        # Currency with formatting
        CurrencyField(name="amount_usd", title="Amount", currency="USD", precision=2),

        # Status badge with conditional colors
        BadgeField(
            name="status",
            title="Status",
            label_map={
                "pending": "warning",
                "completed": "success",
                "failed": "danger",
                "cancelled": "secondary",
            },
        ),

        # Boolean with checkmark icon
        BooleanField(name="is_active", title="Active"),

        # DateTime with relative time ("2 hours ago")
        DateTimeField(name="created_at", title="Created", show_relative=True),
    ],
)
```

### 2. Actions (Bulk - Require Selection)

```python
from django_cfg.modules.django_admin import ActionConfig, Icons

config = AdminConfig(
    model=Lead,
    actions=[
        ActionConfig(
            name="mark_as_contacted",
            description="Mark as contacted",
            action_type="bulk",  # Default - requires item selection
            variant="warning",
            icon=Icons.PHONE,
            confirmation=False,
            handler="apps.leads.admin.actions.mark_as_contacted",
        ),
        ActionConfig(
            name="delete_permanently",
            description="Delete permanently",
            action_type="bulk",
            variant="danger",
            icon=Icons.DELETE_FOREVER,
            confirmation=True,  # Show confirmation dialog
            permissions=["leads.delete_lead"],
            handler="apps.leads.admin.actions.delete_permanently",
        ),
    ],
)

# Handler signature for bulk actions:
# File: apps/leads/admin/actions.py
from django.contrib import messages

def mark_as_contacted(modeladmin, request, queryset):
    """Bulk action handler - requires queryset parameter."""
    updated = queryset.update(status='contacted')
    messages.success(request, f"Marked {updated} leads as contacted")
```

### 3. Changelist Actions (Buttons Above Listing - No Selection)

```python
from django_cfg.modules.django_admin import ActionConfig, Icons

config = AdminConfig(
    model=Proxy,
    actions=[
        # Changelist action - button above listing
        ActionConfig(
            name="sync_all_providers",
            description="🔄 Sync All Providers",
            action_type="changelist",  # No item selection required!
            variant="primary",
            icon=Icons.SYNC,
            confirmation=True,
            handler="apps.proxies.admin.actions.sync_all_providers",
        ),
        ActionConfig(
            name="sync_proxy6",
            description="Sync Proxy6",
            action_type="changelist",
            variant="info",
            icon=Icons.CLOUD_SYNC,
            handler="apps.proxies.admin.actions.sync_proxy6",
        ),
    ],
)

# Handler signature for changelist actions:
# File: apps/proxies/admin/actions.py
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.core.management import call_command
from io import StringIO

def sync_all_providers(modeladmin, request):
    """
    Changelist action handler - no queryset parameter.
    MUST return HttpResponse (redirect).
    """
    try:
        messages.info(request, "🔄 Syncing proxies from all providers...")
        out = StringIO()
        call_command('sync_proxy_providers', provider='all', stdout=out)

        output = out.getvalue()
        if output:
            messages.success(request, output)
    except Exception as e:
        messages.error(request, f"❌ Failed to sync providers: {e}")

    # IMPORTANT: Must return HttpResponse
    return redirect(reverse('admin:proxies_proxy_changelist'))
```

### 4. Fieldsets (Organize Form Fields)

```python
from django_cfg.modules.django_admin import FieldsetConfig

config = AdminConfig(
    model=Payment,
    fieldsets=[
        FieldsetConfig(
            title="Basic Information",
            fields=["internal_payment_id", "status", "description"],
        ),
        FieldsetConfig(
            title="Payment Details",
            fields=["amount_usd", "currency", "pay_amount", "actual_amount"],
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at", "completed_at"],
            collapsed=True,  # Collapsed by default
        ),
    ],
)
```

### 5. Widgets (Form Field Configuration - NOT for list_display)

```python
from django_cfg.modules.django_admin import JSONWidgetConfig

config = AdminConfig(
    model=Bot,
    # Widgets are for FORM FIELDS, not list_display!
    widgets=[
        JSONWidgetConfig(
            field="settings",  # Field name in model
            mode="code",  # tree, code, or view
            height="400px",
            show_copy_button=True,
        ),
        JSONWidgetConfig(
            field="config_schema",
            mode="code",
            height="500px",
            show_copy_button=True,
        ),
    ],
)
```

### 6. Import/Export (via django-import-export)

```python
from django_cfg.modules.django_admin import AdminConfig

# Define resource in separate file (standard django-import-export)
# File: apps/leads/admin/resources.py
from import_export import resources, fields
from import_export.widgets import DateTimeWidget, ForeignKeyWidget

class LeadResource(resources.ModelResource):
    user_email = fields.Field(
        column_name='user_email',
        attribute='user__email',
        widget=ForeignKeyWidget(User, field='email')
    )

    class Meta:
        model = Lead
        fields = ('id', 'name', 'email', 'status', 'user_email')
        import_id_fields = ('email', 'site_url', 'created_at')
        skip_unchanged = True

# Use in AdminConfig
config = AdminConfig(
    model=Lead,
    import_export_enabled=True,
    resource_class=LeadResource,  # Reference to resource class
)
```

### 7. Documentation (Auto-Discover Management Commands)

```python
from django_cfg.modules.django_admin import DocumentationConfig

config = AdminConfig(
    model=Exchange,
    documentation=DocumentationConfig(
        source_dir="apps/exchanges/@docs",  # Auto-discover .md files
        title="📚 Exchange Documentation",
        show_on_changelist=True,
        show_on_changeform=False,
        collapsible=True,
        default_open=False,
        max_height="600px",
        show_management_commands=True,  # Show available commands
        enable_plugins=True,  # Mermaid diagrams, etc.
        sort_sections=True,
    ),
)
```

### 8. Performance Optimization

```python
from django.db.models import Count, Sum, Q

config = AdminConfig(
    model=Payment,
    # JOIN optimization
    select_related=["user", "currency"],

    # M2M optimization
    prefetch_related=["items"],

    # Annotations for calculated fields
    annotations={
        "total_items": Count("items"),
        "total_amount": Sum("items__price"),
    },
)
```

### 9. Custom Display Methods with Decorators

```python
from django_cfg.modules.django_admin import computed_field, Icons
from django_cfg.modules.django_admin.base import PydanticAdmin

class PaymentAdmin(PydanticAdmin):
    config = payment_config

    @computed_field("Payment Method", ordering="payment_method")
    def payment_method_display(self, obj):
        """Custom display method with self.html helpers."""
        return self.html.badge(
            obj.get_payment_method_display(),
            variant="info",
            icon=Icons.PAYMENT
        )

    @computed_field("Status")
    def status_display(self, obj):
        """Status display with conditional icons."""
        icon_map = {
            'pending': Icons.SCHEDULE,
            'running': Icons.PLAY_ARROW,
            'completed': Icons.CHECK_CIRCLE,
            'failed': Icons.ERROR,
        }
        variant_map = {
            'pending': 'warning',
            'running': 'info',
            'completed': 'success',
            'failed': 'danger',
        }

        return self.html.badge(
            obj.get_status_display(),
            variant=variant_map.get(obj.status, 'secondary'),
            icon=icon_map.get(obj.status, Icons.HELP)
        )
```

### 10. Inlines (Standard Django Inlines)

```python
from django.contrib import admin
from unfold.admin import TabularInline

class BotLogInline(TabularInline):
    """Inline for bot logs."""
    model = BotLog
    extra = 0
    fields = ['created_at', 'level', 'event_type', 'message']
    readonly_fields = ['created_at', 'level', 'event_type', 'message']
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False

config = AdminConfig(
    model=Bot,
    # Inlines are set in admin class, not in config
    inlines=[BotLogInline],
)

@admin.register(Bot)
class BotAdmin(PydanticAdmin):
    config = bot_config
    # Note: inlines can also be set here if using @admin.register
```

### 11. ForeignKey Display (New Field Type)

```python
from django_cfg.modules.django_admin import ForeignKeyField, Icons

config = AdminConfig(
    model=Session,

    # Optimize ForeignKey queries
    select_related=["machine", "workspace", "user"],

    list_display=["id", "machine", "workspace", "status"],

    display_fields=[
        # Basic FK display with admin link
        ForeignKeyField(
            name="machine",
            display_field="name",
            link_to_admin=True,
        ),

        # FK with subtitle
        ForeignKeyField(
            name="workspace",
            display_field="name",
            subtitle_field="description",
            link_to_admin=True,
        ),

        # FK with template subtitle and icon
        ForeignKeyField(
            name="user",
            display_field="username",
            subtitle_template="{email} • {phone}",
            link_icon=Icons.OPEN_IN_NEW,
        ),
    ],
)
```

### 12. Filters (Standard Django Filters + Unfold)

```python
from unfold.contrib.filters.admin import AutocompleteSelectFilter

config = AdminConfig(
    model=Lead,
    list_filter=[
        "status",  # Simple field filter
        "contact_type",
        "created_at",
        ("user", AutocompleteSelectFilter),  # Autocomplete filter
    ],
    autocomplete_fields=["user"],  # Enable autocomplete
)
```

---

## Key Concepts

### Action Types

1. **Bulk Actions** (default)
   - Require item selection in changelist
   - Signature: `def handler(modeladmin, request, queryset)`
   - Use `messages` for notifications
   - Example: mark selected items, delete selected items

2. **Changelist Actions** ⭐ NEW
   - Buttons above listing, no selection required
   - Signature: `def handler(modeladmin, request)` - NO queryset!
   - **MUST** return `HttpResponse` (usually `redirect()`)
   - Use `call_command()` for management commands
   - Example: sync data, export all, run maintenance tasks

### Display Fields vs Widgets

- **Display Fields**: Auto-generate display methods for `list_display` (listing view)
  - `BadgeField`, `CurrencyField`, `DateTimeField`, `UserField`, etc.
  - Shows data in changelist table

- **Widgets**: Configure form field widgets (detail/edit view)
  - `JSONWidgetConfig`, `TextWidgetConfig`
  - Used in forms, not in listing

### Import/Export

Uses standard `django-import-export` library:
- Define `Resource` class separately
- Set `import_export_enabled=True`
- Pass `resource_class` to `AdminConfig`

---

## File Structure

Recommended project structure for admins:

```
apps/
  your_app/
    admin/
      __init__.py           # Register all admins
      model_admin.py        # Admin config for Model
      actions.py            # Action handlers (bulk & changelist)
      resources.py          # Import/Export resources
      filters.py            # Custom filters
```

---

## See Also

- [Full Documentation](../../../docs_public/django_admin/)
- [Icons Reference](./icons/constants.py) - All 2234 Material Design Icons
- [Unfold Admin](https://github.com/unfoldadmin/django-unfold) - UI framework
- [Django Import-Export](https://django-import-export.readthedocs.io/) - Import/Export functionality
