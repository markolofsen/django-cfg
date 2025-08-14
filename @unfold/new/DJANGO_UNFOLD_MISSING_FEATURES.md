# 🧩 Django Unfold Missing Features Documentation (LLM-Optimized)

## 🎯 Goal

Additional documentation for all missing Django Unfold dashboard capabilities that were not reflected in the main documentation.

---

## 📦 Missing Modules

### @dashboard/custom-pages

**Purpose**:
Creating custom pages in admin using Unfold UI.

**Dependencies**:
- `unfold.views.UnfoldModelAdminViewMixin`
- `django.views.generic.TemplateView`

**Exports**:
- `UnfoldModelAdminViewMixin`
- Custom page views
- Breadcrumb helpers

**Used in**:
- Custom admin pages
- Extended admin functionality

---

### @dashboard/sections

**Purpose**:
Expandable rows system in changelist with additional content.

**Dependencies**:
- `unfold.sections.TableSection`
- `unfold.sections.TemplateSection`

**Exports**:
- `TableSection` for related data display
- `TemplateSection` for custom templates
- Section configuration

**Used in**:
- Changelist views
- Related data display
- Custom content in rows

---

### @dashboard/conditional-fields

**Purpose**:
Dynamic forms with conditional field display.

**Dependencies**:
- Alpine.js expressions
- ModelAdmin configuration

**Exports**:
- Conditional field logic
- Dynamic form behavior
- Field visibility control

**Used in**:
- Complex form interfaces
- Dynamic user experiences

---

### @dashboard/paginator

**Purpose**:
Optimized pagination for large datasets.

**Dependencies**:
- `unfold.paginator.InfinitePaginator`

**Exports**:
- `InfinitePaginator` class
- Performance optimization
- Large dataset handling

**Used in**:
- Large data tables
- Performance-critical admin interfaces

---

### @dashboard/command

**Purpose**:
Command search and navigation system.

**Dependencies**:
- `unfold.dataclasses.SearchResult`
- Custom search callbacks

**Exports**:
- Command search interface
- Search history
- Custom search results

**Used in**:
- Quick navigation
- Global search functionality

---

### @dashboard/site-dropdown

**Purpose**:
Dropdown menu in sidebar when clicking on site header.

**Dependencies**:
- `UNFOLD["SITE_DROPDOWN"]` configuration

**Exports**:
- Site dropdown navigation
- Custom navigation links
- Icon support

**Used in**:
- Enhanced navigation
- Multi-site admin interfaces

---

### @dashboard/custom-sites

**Purpose**:
Creating custom admin sites with Unfold.

**Dependencies**:
- `unfold.sites.UnfoldAdminSite`
- `django.contrib.admin.apps.AdminConfig`

**Exports**:
- `UnfoldAdminSite` class
- Custom admin site configuration
- Multiple admin sites

**Used in**:
- Multi-site applications
- Custom admin configurations

---

## 🧾 APIs (ReadMe.LLM Format)

%%README.LLM id=custom-pages%%

## 🧭 Library Description

System for creating custom pages in admin using Unfold UI.

## ✅ Rules

- Inherit from `UnfoldModelAdminViewMixin` for custom views.
- Always specify `title` and `permission_required`.
- Use `admin_site.admin_view()` for view registration.

## 🧪 Functions

### Custom View Creation

**Creates custom page in admin.**

```python
from unfold.views import UnfoldModelAdminViewMixin
from django.views.generic import TemplateView

class MyClassBasedView(UnfoldModelAdminViewMixin, TemplateView):
    title = "Custom Title"  # required
    permission_required = ("app.permission",)  # required
    template_name = "app/custom_template.html"
```

### URL Registration

**Registers custom view in ModelAdmin.**

```python
@admin.register(MyModel)
class CustomAdmin(ModelAdmin):
    def get_urls(self):
        custom_view = self.admin_site.admin_view(
            MyClassBasedView.as_view(model_admin=self)
        )
        
        return super().get_urls() + [
            path("custom-path/", custom_view, name="custom_name"),
        ]
```

### Template Structure

**Template structure for custom page.**

```html
{% extends "admin/base.html" %}
{% load admin_urls i18n unfold %}

{% block breadcrumbs %}
    <div class="px-4">
        <div class="container mb-6 mx-auto -my-3 lg:mb-12">
            <ul class="flex flex-wrap">
                {% url 'admin:index' as link %}
                {% trans 'Home' as name %}
                {% include 'unfold/helpers/breadcrumb_item.html' with link=link name=name %}
            </ul>
        </div>
    </div>
{% endblock %}

{% block content %}
    {% trans "Custom page content" %}
{% endblock %}
```

%%END%%

%%README.LLM id=sections%%

## 🧭 Library Description

Expandable rows system in changelist with additional content.

## ✅ Rules

- Use `TableSection` for related data.
- Use `TemplateSection` for custom templates.
- Optimize queries with `prefetch_related`.

## 🧪 Functions

### TableSection Configuration

**Creates section with related data table.**

```python
from unfold.sections import TableSection

class CustomTableSection(TableSection):
    verbose_name = "Related Records"  # Section title
    height = 300  # Table height
    related_name = "related_set"  # Related field name
    fields = ["pk", "title", "custom_field"]  # Fields to display
    
    def custom_field(self, instance):
        return instance.pk  # Custom field
```

### TemplateSection Configuration

**Creates section with custom template.**

```python
from unfold.sections import TemplateSection

class CardSection(TemplateSection):
    template_name = "app/section_template.html"
```

### ModelAdmin Integration

**Integrates sections into ModelAdmin.**

```python
@admin.register(SomeModel)
class SomeAdmin(ModelAdmin):
    list_sections = [
        CardSection,
        CustomTableSection,
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            "related_field_set",
            "related_field__another_field",
        )
```

%%END%%

%%README.LLM id=conditional-fields%%

## 🧭 Library Description

Dynamic forms with conditional field display.

## ✅ Rules

- Use Alpine.js expressions for conditions.
- Configure `conditional_fields` in ModelAdmin.
- Support complex conditional logic.

## 🧪 Functions

### Conditional Fields Configuration

**Configures conditional field display.**

```python
@admin.register(User)
class UserAdmin(ModelAdmin):
    conditional_fields = {
        "country": "different_address == true",
        "city": "different_address == true",
        "address": "different_address == true",
    }
```

### Complex Conditions

**Creates complex display conditions.**

```python
conditional_fields = {
    "field1": "type == 'advanced'",
    "field2": "status == 'active' && role == 'admin'",
    "field3": "!is_archived && has_permission",
}
```

### Model Example

**Example model with conditional fields.**

```python
class User(AbstractUser):
    different_address = models.BooleanField(_("different address"), default=False)
    country = models.CharField(_("country"), max_length=255, null=True, blank=True)
    city = models.CharField(_("city"), max_length=255, null=True, blank=True)
    address = models.CharField(_("address"), max_length=255, null=True, blank=True)
```

%%END%%

%%README.LLM id=paginator%%

## 🧭 Library Description

Optimized pagination for large datasets.

## ✅ Rules

- Use `InfinitePaginator` for large tables.
- Disable `show_full_result_count` for performance.
- Optimize queries with `prefetch_related`.

## 🧪 Functions

### InfinitePaginator Setup

**Configures infinite pagination.**

```python
from unfold.admin import ModelAdmin
from unfold.paginator import InfinitePaginator

class YourAdmin(ModelAdmin):
    paginator = InfinitePaginator
    show_full_result_count = False
    list_per_page = 20  # Recommended for large tables
```

### Performance Optimization

**Optimizes queries for large tables.**

```python
def get_queryset(self, request):
    return (
        super()
        .get_queryset(request)
        .prefetch_related(
            "related_field_set",
            "related_field__another_field",
        )
    )
```

%%END%%

%%README.LLM id=command%%

## 🧭 Library Description

Command search and navigation system.

## ✅ Rules

- Activate command search with `cmd + K` (Mac) or `ctrl + K` (Windows/Linux).
- Configure `search_models` for model data search.
- Use `search_fields` in ModelAdmin for search.

## 🧪 Functions

### Command Configuration

**Configures command search.**

```python
UNFOLD = {
    "COMMAND": {
        "search_models": True,  # Search through model data
        "search_callback": "utils.search_callback",  # Custom search
        "show_history": True,  # Search history
    },
}
```

### Custom Search Callback

**Creates custom search.**

```python
from unfold.dataclasses import SearchResult

def search_callback(request, search_term):
    # Custom search logic
    return [
        SearchResult(
            title="Some title",
            description="Extra content",
            link="https://example.com",
            icon="database",
        )
    ]
```

### Model Search Configuration

**Configures search for model.**

```python
class MyModelAdmin(ModelAdmin):
    search_fields = ["title", "description", "content"]
```

%%END%%

%%README.LLM id=site-dropdown%%

## 🧭 Library Description

Dropdown menu in sidebar when clicking on site header.

## ✅ Rules

- Configure `SITE_DROPDOWN` in UNFOLD configuration.
- Use icons and links for navigation.
- Support external and internal links.

## 🧪 Functions

### Site Dropdown Configuration

**Configures site dropdown menu.**

```python
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD = {
    "SITE_DROPDOWN": [
        {
            "icon": "diamond",
            "title": _("My site"),
            "link": "https://example.com",
        },
        {
            "icon": "home",
            "title": _("Admin Home"),
            "link": reverse_lazy("admin:index"),
        },
    ]
}
```

%%END%%

%%README.LLM id=custom-sites%%

## 🧭 Library Description

Creating custom admin sites with Unfold.

## ✅ Rules

- Use `UnfoldAdminSite` instead of standard AdminSite.
- Configure custom URL patterns.
- Register models with custom site.

## 🧪 Functions

### Custom Admin Site Creation

**Creates custom admin site.**

```python
from django.contrib import admin
from unfold.sites import UnfoldAdminSite

class CustomAdminSite(UnfoldAdminSite):
    pass

custom_admin_site = CustomAdminSite(name="custom_admin_site")
```

### URL Configuration

**Configures URLs for custom site.**

```python
# urls.py
from django.urls import path
from .sites import custom_admin_site

urlpatterns = [
    path("admin/", custom_admin_site.urls),
]
```

### Model Registration

**Registers models with custom site.**

```python
from unfold.admin import ModelAdmin

@admin.register(User, site=custom_admin_site)
class UserAdmin(ModelAdmin):
    model = User
```

### App Config Override

**Overrides standard AdminConfig.**

```python
# settings.py
INSTALLED_APPS = [
    "unfold.apps.BasicAppConfig",  # Doesn't override django.contrib.admin.site
    "django.contrib.admin",
    "your_app",
]

# apps.py
from django.contrib.admin.apps import AdminConfig

class MyAdminConfig(AdminConfig):
    default_site = "myproject.sites.CustomAdminSite"
    
    def get_urls(self):
        urls = super().get_urls()
        urls += [
            path("my-custom-view/", self.admin_view(self.my_custom_view), name="my_custom_view"),
        ]
        return urls
    
    def my_custom_view(self, request, extra_context=None):
        # Custom logic
        pass
```

%%END%%

---

## 🔁 Flows

### Custom Page Creation Flow

1. Create view class inheriting from `UnfoldModelAdminViewMixin`.
2. Specify `title` and `permission_required`.
3. Create template extending `admin/base.html`.
4. Register view in `get_urls()` ModelAdmin.
5. Add link to sidebar through UNFOLD settings.

**Modules**:
- `@dashboard/custom-pages`
- `@core/configuration`

---

### Sections Implementation Flow

1. Create `TableSection` or `TemplateSection` class.
2. Configure fields and related data.
3. Add sections to `list_sections` ModelAdmin.
4. Optimize queries with `prefetch_related`.
5. Configure pagination for performance.

**Modules**:
- `@dashboard/sections`
- `@dashboard/paginator`

---

### Conditional Fields Flow

1. Create model with fields for conditional display.
2. Configure `conditional_fields` in ModelAdmin.
3. Use Alpine.js expressions for conditions.
4. Test dynamic form behavior.

**Modules**:
- `@dashboard/conditional-fields`
- `@core/configuration`

---

### Command Search Flow

1. Configure `COMMAND` in UNFOLD configuration.
2. Enable `search_models` for model data search.
3. Configure `search_fields` in ModelAdmin.
4. Create custom `search_callback` if needed.
5. Enable `show_history` for search history.

**Modules**:
- `@dashboard/command`
- `@core/configuration`

---

### Custom Admin Site Flow

1. Create class inheriting from `UnfoldAdminSite`.
2. Configure URL patterns for custom site.
3. Register models with custom site.
4. Override `AdminConfig` if needed.
5. Add custom views in `get_urls()`.

**Modules**:
- `@dashboard/custom-sites`
- `@dashboard/custom-pages`

---

## 🧠 Notes

- **Alpine.js** is used for dynamic form behavior in conditional fields.
- **InfinitePaginator** eliminates expensive COUNT operations for large tables.
- **Sections** allow displaying related data without additional pages.
- **Command search** provides quick navigation through admin.
- **Custom sites** allow creating multiple admin interfaces.
- **Site dropdown** improves navigation between different sections. 