# 🧩 Django Unfold Dashboard Documentation (LLM-Optimized)

## 🎯 Goal

Create a **single-file**, **token-efficient**, **machine-readable** documentation format that:

- Integrates smoothly with LLMs in Cursor IDE.
- Enables structured code generation and API understanding.
- Captures architecture, logic, and usage flows clearly.

---

## 🧱 Structure

Use the following structure in a single `.md` file:

```
# Overview
# Modules
# APIs (ReadMe.LLM format)
# Flows
# Terms (inline, where needed)
```

Each section should be concise and semantically organized using headings (`##`, `###`).

---

## 📖 Overview

Django Unfold is a modern, responsive Django admin interface that replaces the default Django admin with a beautiful, customizable dashboard. It provides enhanced components, actions, filters, and styling while maintaining full Django admin compatibility.

This documentation provides LLM-readable references for major modules, APIs, and usage flows in Django Unfold. It is optimized for use inside Cursor IDE and for retrieval-augmented prompting (RAG).

---

## 📦 Modules

### @core/installation

**Purpose**:
Core installation and setup module for Django Unfold.

**Dependencies**:
- `django.contrib.admin`
- `unfold` (main package)

**Exports**:
- `ModelAdmin` (replaces `django.contrib.admin.ModelAdmin`)
- `INSTALLED_APPS` configuration

**Used in**:
- All Django admin applications
- `settings.py` configuration

---

### @core/configuration

**Purpose**:
Centralized configuration management for Unfold dashboard customization.

**Dependencies**:
- `django.templatetags.static`
- `django.urls.reverse_lazy`

**Exports**:
- `UNFOLD` settings dictionary
- Configuration callbacks

**Used in**:
- `settings.py`
- Dashboard customization
- Theme management

---

### @actions/decorators

**Purpose**:
Enhanced action system with custom decorators and permissions.

**Dependencies**:
- `unfold.decorators.action`
- `unfold.enums.ActionVariant`

**Exports**:
- `@action` decorator
- `ActionVariant` enum
- Permission handling

**Used in**:
- ModelAdmin classes
- Custom admin actions

---

### @components/templates

**Purpose**:
Reusable component system for dashboard layouts and UI elements.

**Dependencies**:
- `unfold` template tags
- Tailwind CSS classes

**Exports**:
- Component templates (card, button, table, etc.)
- Nested component system

**Used in**:
- Custom dashboard pages
- Admin interface customization

---

### @filters/enhanced

**Purpose**:
Advanced filtering system with input fields and custom filters.

**Dependencies**:
- `unfold.contrib.filters`
- `unfold.admin.ModelAdmin`

**Exports**:
- Custom filter classes
- Input field filters
- Dropdown filters

**Used in**:
- Changelist views
- Data filtering

---

### @decorators/display

**Purpose**:
Enhanced display decorators for admin list views and form fields.

**Dependencies**:
- `unfold.decorators.display`
- Django admin decorators

**Exports**:
- `@display` decorator
- Label styling
- Header formatting

**Used in**:
- ModelAdmin list_display
- Custom field formatting

---

### @inlines/enhanced

**Purpose**:
Enhanced inline editing with improved styling and functionality.

**Dependencies**:
- `unfold.admin.StackedInline`
- `unfold.admin.TabularInline`

**Exports**:
- Enhanced inline classes
- Inline configuration options

**Used in**:
- Related model editing
- Nested form handling

---

### @widgets/forms

**Purpose**:
Custom form widgets and enhanced form elements.

**Dependencies**:
- `unfold.contrib.forms`
- `unfold.contrib.forms.widgets`

**Exports**:
- `WysiwygWidget`
- Custom form widgets

**Used in**:
- Text field enhancement
- Rich text editing

---

### @tabs/navigation

**Purpose**:
Tab-based navigation system for admin interfaces.

**Dependencies**:
- `UNFOLD["TABS"]` configuration
- Django URL routing

**Exports**:
- Tab configuration
- Navigation callbacks

**Used in**:
- Changeform views
- Changelist views

---

### @styles/tailwind

**Purpose**:
Tailwind CSS integration and custom styling system.

**Dependencies**:
- Tailwind CSS
- `UNFOLD["STYLES"]` configuration

**Exports**:
- Custom CSS classes
- Theme configuration

**Used in**:
- Dashboard styling
- Component customization

---

## 🧾 APIs (ReadMe.LLM Format)

%%README.LLM id=installation%%

## 🧭 Library Description

Django Unfold installation and basic setup. Provides modern admin interface replacement.

## ✅ Rules

- Always add `unfold` before `django.contrib.admin` in INSTALLED_APPS.
- Inherit from `unfold.admin.ModelAdmin` instead of `django.contrib.admin.ModelAdmin`.
- Use poetry for dependency management.

## 🧪 Functions

### INSTALLED_APPS Configuration

**Sets up Unfold in Django project.**

```python
INSTALLED_APPS = [
    "unfold",  # before django.contrib.admin
    "unfold.contrib.filters",  # optional
    "unfold.contrib.forms",  # optional
    "unfold.contrib.inlines",  # optional
    "django.contrib.admin",  # required
]
```

### ModelAdmin Inheritance

**Creates custom admin class with Unfold features.**

```python
from unfold.admin import ModelAdmin

@admin.register(MyModel)
class CustomAdminClass(ModelAdmin):
    pass
```

%%END%%

%%README.LLM id=configuration%%

## 🧭 Library Description

Centralized configuration system for Unfold dashboard customization.

## ✅ Rules

- Configure all settings in `UNFOLD` dictionary in settings.py.
- Use callbacks for dynamic configuration.
- Follow color scheme conventions.

## 🧪 Functions

### UNFOLD Settings Dictionary

**Main configuration object for Unfold dashboard.**

```python
UNFOLD = {
    "SITE_TITLE": "Custom Admin",
    "SITE_HEADER": "Admin Dashboard",
    "SITE_ICON": lambda request: static("icon.svg"),
    "THEME": "dark",  # or "light"
    "DASHBOARD_CALLBACK": "app.dashboard_callback",
}
```

### Dashboard Callback

**Prepares custom variables for dashboard template.**

```python
def dashboard_callback(request, context):
    context.update({
        "custom_data": "value",
    })
    return context
```

### Environment Callback

**Returns environment indicator for header.**

```python
def environment_callback(request):
    return ["Production", "danger"]  # [text, color]
```

%%END%%

%%README.LLM id=actions%%

## 🧭 Library Description

Enhanced action system with custom decorators and permission handling.

## ✅ Rules

- Use `@action` decorator for custom actions.
- Define permissions using `has_{action}_permission` methods.
- Support both global and row-level actions.

## 🧪 Functions

### @action Decorator

**Creates custom admin actions with enhanced features.**

```python
from unfold.decorators import action
from unfold.enums import ActionVariant

@action(
    description="Custom Action",
    icon="person",
    variant=ActionVariant.PRIMARY,
    permissions=["custom_action"]
)
def custom_action(self, request, queryset):
    # Action logic here
    pass
```

### Permission Methods

**Defines custom permission logic for actions.**

```python
def has_custom_action_permission(self, request, obj=None):
    return request.user.is_superuser
```

### Action Types

**Different action placement options.**

```python
# Global actions (changelist top)
# Row actions (each row)
# Detail actions (changeform top)
# Submit line actions (form submit)
```

%%END%%

%%README.LLM id=components%%

## 🧭 Library Description

Reusable component system for dashboard layouts and UI elements.

## ✅ Rules

- Use `{% component %}` template tags.
- Components can be nested infinitely.
- Pass variables using `with` parameter.

## 🧪 Functions

### Component Template

**Includes reusable component in template.**

```html
{% load unfold %}

{% component "unfold/components/card.html" with class="lg:w-1/3" %}
    {% component "unfold/components/title.html" %}
        Card Title
    {% endcomponent %}
{% endcomponent %}
```

### Available Components

**List of built-in components.**

```html
unfold/components/button.html      # Basic button
unfold/components/card.html        # Card container
unfold/components/table.html       # Data table
unfold/components/chart/bar.html   # Bar chart
unfold/components/chart/line.html  # Line chart
unfold/components/cohort.html      # Cohort analysis
unfold/components/container.html   # Layout wrapper
unfold/components/navigation.html  # Navigation menu
unfold/components/progress.html    # Progress bar
unfold/components/tracker.html     # Activity tracker
```

%%END%%

%%README.LLM id=filters%%

## 🧭 Library Description

Enhanced filtering system with input fields and custom filters.

## ✅ Rules

- Add `unfold.contrib.filters` to INSTALLED_APPS.
- Set `list_filter_submit = True` for input filters.
- Use custom filter classes for complex filtering.

## 🧪 Functions

### Filter Configuration

**Enables enhanced filtering in ModelAdmin.**

```python
from unfold.contrib.filters import (
    RangeNumericListFilter,
    TextListFilter,
    DropdownFilter,
)

class MyModelAdmin(ModelAdmin):
    list_filter = [
        ("field_name", RangeNumericListFilter),
        ("text_field", TextListFilter),
        ("choice_field", DropdownFilter),
    ]
    list_filter_submit = True  # Required for input filters
```

### Custom Filter Classes

**Creates specialized filter implementations.**

```python
class CustomFilter(admin.SimpleListFilter):
    title = "Custom Filter"
    parameter_name = "custom"
    
    def lookups(self, request, model_admin):
        return [("value", "Label")]
    
    def queryset(self, request, queryset):
        # Filter logic here
        return queryset
```

%%END%%

%%README.LLM id=display%%

## 🧭 Library Description

Enhanced display decorators for admin list views and form fields.

## ✅ Rules

- Use `@display` decorator for custom field formatting.
- Support label styling and header formatting.
- Maintain Django admin compatibility.

## 🧪 Functions

### @display Decorator

**Creates custom display methods with enhanced styling.**

```python
from unfold.decorators import display

@display(
    description="Status",
    ordering="status",
    label={
        "ACTIVE": "success",
        "PENDING": "warning",
        "INACTIVE": "danger",
    }
)
def show_status(self, obj):
    return obj.status
```

### Header Display

**Shows multiple values in single cell.**

```python
@display(header=True)
def display_user_info(self, obj):
    return [
        obj.full_name,
        obj.email,
        obj.initials,
        {"path": obj.avatar.url, "squared": True}
    ]
```

### Dropdown Display

**Creates interactive dropdown in list view.**

```python
@display(description="Actions", dropdown=True)
def display_actions(self, obj):
    return {
        "title": "Actions",
        "items": [
            {"title": "Edit", "link": f"/admin/edit/{obj.id}"},
            {"title": "Delete", "link": f"/admin/delete/{obj.id}"},
        ]
    }
```

%%END%%

%%README.LLM id=inlines%%

## 🧭 Library Description

Enhanced inline editing with improved styling and functionality.

## ✅ Rules

- Use Unfold inline classes instead of Django defaults.
- Configure inline options for better UX.
- Support both stacked and tabular inlines.

## 🧪 Functions

### StackedInline

**Creates stacked inline form with enhanced styling.**

```python
from unfold.admin import StackedInline

class MyStackedInline(StackedInline):
    model = RelatedModel
    extra = 1
    fields = ["field1", "field2"]
```

### TabularInline

**Creates tabular inline form with enhanced styling.**

```python
from unfold.admin import TabularInline

class MyTabularInline(TabularInline):
    model = RelatedModel
    extra = 0
    fields = ["field1", "field2"]
```

### Inline Options

**Configures inline behavior and appearance.**

```python
class MyInline(StackedInline):
    model = RelatedModel
    extra = 1
    max_num = 5
    min_num = 1
    can_delete = True
    verbose_name = "Related Item"
    verbose_name_plural = "Related Items"
```

%%END%%

%%README.LLM id=widgets%%

## 🧭 Library Description

Custom form widgets and enhanced form elements.

## ✅ Rules

- Add `unfold.contrib.forms` to INSTALLED_APPS.
- Use `formfield_overrides` for widget replacement.
- Support rich text editing with WysiwygWidget.

## 🧪 Functions

### WysiwygWidget

**Rich text editor powered by Trix.**

```python
from unfold.contrib.forms.widgets import WysiwygWidget

class MyModelAdmin(ModelAdmin):
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }
```

### ArrayWidget

**Handles array field editing.**

```python
from unfold.contrib.forms.widgets import ArrayWidget

class MyModelAdmin(ModelAdmin):
    formfield_overrides = {
        ArrayField: {
            "widget": ArrayWidget,
        }
    }
```

%%END%%

%%README.LLM id=tabs%%

## 🧭 Library Description

Tab-based navigation system for admin interfaces.

## ✅ Rules

- Configure tabs in `UNFOLD["TABS"]` settings.
- Use `detail: True` for changeform tabs.
- Support permission-based tab visibility.

## 🧪 Functions

### Tabs Configuration

**Sets up tab navigation in admin interface.**

```python
UNFOLD = {
    "TABS": [
        {
            "models": [
                {
                    "name": "app_label.model_name",
                    "detail": True,  # For changeform tabs
                },
            ],
            "items": [
                {
                    "title": "Custom Tab",
                    "link": reverse_lazy("admin:app_model_changelist"),
                    "permission": "app.permission_callback",
                },
            ],
        },
    ],
}
```

### Permission Callback

**Controls tab visibility based on permissions.**

```python
def permission_callback(request):
    return request.user.has_perm("app.change_model")
```

%%END%%

%%README.LLM id=styles%%

## 🧭 Library Description

Tailwind CSS integration and custom styling system.

## ✅ Rules

- Use Tailwind 4.x for Unfold 0.57+.
- Configure colors to match UNFOLD["COLORS"].
- Add custom styles to UNFOLD["STYLES"].

## 🧪 Functions

### Tailwind Configuration

**Sets up Tailwind CSS with Unfold colors.**

```javascript
// tailwind.config.js
module.exports = {
  darkMode: "class",
  content: ["./your_project/**/*.{html,py,js}"],
  theme: {
    extend: {
      colors: {
        base: {
          50: "rgb(var(--color-base-50) / <alpha-value>)",
          // ... other base colors
        },
        primary: {
          50: "rgb(var(--color-primary-50) / <alpha-value>)",
          // ... other primary colors
        },
      }
    }
  }
};
```

### Custom Styles Loading

**Adds custom CSS to admin interface.**

```python
UNFOLD = {
    "STYLES": [
        lambda request: static("css/custom.css"),
    ],
}
```

### Color Configuration

**Customizes Unfold color scheme.**

```python
UNFOLD = {
    "COLORS": {
        "primary": {
            "500": "168, 85, 247",
            "600": "147, 51, 234",
        },
        "base": {
            "50": "249, 250, 251",
            "900": "17, 24, 39",
        },
    },
}
```

%%END%%

---

## 🔁 Flows

### Dashboard Setup Flow

1. Install `django-unfold` via poetry.
2. Add `unfold` to INSTALLED_APPS before `django.contrib.admin`.
3. Inherit from `unfold.admin.ModelAdmin` in admin classes.
4. Configure `UNFOLD` settings in settings.py.
5. Customize dashboard using components and callbacks.

**Modules**:
- `@core/installation`
- `@core/configuration`
- `@components/templates`

---

### Custom Action Flow

1. Define action method in ModelAdmin class.
2. Apply `@action` decorator with parameters.
3. Implement permission method if needed.
4. Handle action logic and redirect appropriately.

**Modules**:
- `@actions/decorators`
- `@core/configuration`

---

### Component Dashboard Flow

1. Create custom dashboard template.
2. Use `{% component %}` tags for layout.
3. Pass data via `DASHBOARD_CALLBACK`.
4. Nest components for complex layouts.

**Modules**:
- `@components/templates`
- `@core/configuration`

---

### Enhanced Filtering Flow

1. Add `unfold.contrib.filters` to INSTALLED_APPS.
2. Configure `list_filter` with custom filter classes.
3. Set `list_filter_submit = True` for input filters.
4. Implement custom filter logic.

**Modules**:
- `@filters/enhanced`
- `@core/installation`

---

### Rich Text Editing Flow

1. Add `unfold.contrib.forms` to INSTALLED_APPS.
2. Use `formfield_overrides` to apply WysiwygWidget.
3. Configure widget options for specific fields.
4. Handle media uploads separately.

**Modules**:
- `@widgets/forms`
- `@core/installation`

---

### Tab Navigation Flow

1. Configure `UNFOLD["TABS"]` in settings.py.
2. Define models and tab items.
3. Implement permission callbacks if needed.
4. Create custom views for tab content.

**Modules**:
- `@tabs/navigation`
- `@core/configuration`

---

### Custom Styling Flow

1. Install Tailwind CSS in project.
2. Configure tailwind.config.js with Unfold colors.
3. Create custom CSS file with Tailwind directives.
4. Add styles to `UNFOLD["STYLES"]`.

**Modules**:
- `@styles/tailwind`
- `@core/configuration`

---

## 🧠 Notes

- **RAG** (Retrieval-Augmented Generation) refers to using this documentation for AI-assisted development.
- **LLM-first** documentation is optimized for machine readability and token efficiency.
- All Unfold components maintain Django admin compatibility while adding enhanced features.
- The dashboard system supports both light and dark themes with automatic switching.
- Custom components can be nested infinitely for complex layouts.
- Permission system supports both Django built-in and custom permission methods.
- Tailwind CSS integration provides consistent design system across all components. 