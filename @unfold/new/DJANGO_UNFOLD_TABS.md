# 🧩 Django Unfold Tabs System Documentation (LLM-Optimized)

## 🎯 Goal

Comprehensive documentation for Django Unfold tabs system covering all tab types, configuration, and implementation patterns.

---

## 📦 Modules

### @tabs/changelist

**Purpose**:
Tab navigation system for changelist views with model-specific configuration.

**Dependencies**:
- `UNFOLD["TABS"]` configuration
- Django URL routing system

**Exports**:
- Changelist tab navigation
- Model-specific tab configuration
- Permission-based tab visibility

**Used in**:
- Admin list views
- Model navigation
- Cross-model relationships

---

### @tabs/changeform

**Purpose**:
Tab navigation system for changeform views with detail-specific configuration.

**Dependencies**:
- `UNFOLD["TABS"]` configuration with `detail: True`
- Django URL routing system

**Exports**:
- Changeform tab navigation
- Detail view tab configuration
- Permission-based tab visibility

**Used in**:
- Admin detail views
- Model editing interfaces
- Related model navigation

---

### @tabs/dynamic

**Purpose**:
Dynamic tab generation using custom callbacks and template rendering.

**Dependencies**:
- Custom callback functions
- `tab_list` template tag
- `unfold` template tags

**Exports**:
- Dynamic tab generation
- Custom tab rendering
- Template-based tab display

**Used in**:
- Custom admin pages
- Dynamic navigation
- Template-based interfaces

---

### @tabs/fieldsets

**Purpose**:
Organizing fieldsets into tabs for better form organization.

**Dependencies**:
- ModelAdmin fieldsets configuration
- CSS `tab` class

**Exports**:
- Fieldset tab navigation
- Form organization
- CSS-based tab grouping

**Used in**:
- Complex form interfaces
- Field organization
- User experience improvement

---

### @tabs/inline

**Purpose**:
Organizing inline forms into tabs for better form management.

**Dependencies**:
- `StackedInline` or `TabularInline` classes
- `tab = True` attribute

**Exports**:
- Inline tab navigation
- Related model organization
- Form management

**Used in**:
- Related model editing
- Complex form interfaces
- Inline form organization

---

## 🧾 APIs (ReadMe.LLM Format)

%%README.LLM id=changelist-tabs%%

## 🧭 Library Description

Tab navigation system for changelist views with model-specific configuration.

## ✅ Rules

- Configure tabs in `UNFOLD["TABS"]` settings.
- Use model names in lowercase format.
- Implement permission callbacks for tab visibility.

## 🧪 Functions

### Basic Changelist Tabs Configuration

**Configures tabs for changelist views.**

```python
# settings.py
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD = {
    "TABS": [
        {
            # Models that will display tab navigation
            "models": [
                "app_label.model_name_in_lowercase",
            ],
            # List of tab items
            "items": [
                {
                    "title": _("Your custom title"),
                    "link": reverse_lazy("admin:app_label_model_name_changelist"),
                    "permission": "sample_app.permission_callback",
                },
                {
                    "title": _("Another custom title"),
                    "link": reverse_lazy("admin:app_label_another_model_name_changelist"),
                    "permission": "sample_app.permission_callback",
                },
            ],
        },
    ],
}

# Permission callback for tab item
def permission_callback(request):
    return request.user.has_perm("sample_app.change_model")
```

%%END%%

%%README.LLM id=changeform-tabs%%

## 🧭 Library Description

Tab navigation system for changeform views with detail-specific configuration.

## ✅ Rules

- Use `detail: True` for changeform tabs.
- Configure models as dictionaries with detail flag.
- Implement permission callbacks for tab visibility.

## 🧪 Functions

### Changeform Tabs Configuration

**Configures tabs for changeform views.**

```python
# settings.py
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD = {
    "TABS": [
        {
            # Which changeform models will display tab navigation
            "models": [
                {
                    "name": "app_label.model_name_in_lowercase",
                    "detail": True,  # Displays tab navigation on changeform page
                },
            ],
            # List of tab items
            "items": [
                {
                    "title": _("Your custom title"),
                    "link": reverse_lazy("admin:app_label_model_name_changelist"),
                    "permission": "sample_app.permission_callback",
                },
                {
                    "title": _("Another custom title"),
                    "link": reverse_lazy("admin:app_label_another_model_name_changelist"),
                    "permission": "sample_app.permission_callback",
                },
            ],
        },
    ],
}

# Permission callback for tab item
def permission_callback(request):
    return request.user.has_perm("sample_app.change_model")
```

%%END%%

%%README.LLM id=dynamic-tabs%%

## 🧭 Library Description

Dynamic tab generation using custom callbacks and template rendering.

## ✅ Rules

- Use callback functions for dynamic tab generation.
- Implement `tab_list` template tag for rendering.
- Configure unique `page` identifiers.

## 🧪 Functions

### Dynamic Tabs Callback

**Creates dynamic tab navigation structure.**

```python
# settings.py
UNFOLD = {
    "TABS": "your_project.admin.tabs_callback"
}

# admin.py
from django.http import HttpRequest

def tabs_callback(request: HttpRequest) -> list[dict[str, Any]]:
    return [
        {
            # Unique tab identifier to render tabs in custom templates
            "page": "custom_page",
            
            # Applies for the changeform view
            "models": [
                {
                    "name": "app_label.model_name_in_lowercase",
                    "detail": True
                },
            ],
            "items": [
                {
                    "title": _("Your custom title"),
                    "link": reverse_lazy("admin:app_label_model_name_changelist"),
                    "active": True  # Configure active tab
                    # "active": lambda request: True
                },
                {
                    "title": _("Inline tab"),
                    "link": reverse_lazy("admin:app_label_model_name_changelist"),
                    "inline": "corresponding-fragment-url"
                },
            ],
        },
    ]
```

### Template Rendering

**Renders tabs in custom templates.**

```html
{% extends "admin/base_site.html" %}
{% load unfold %}

{% block content %}
    {% tab_list "custom_page" %}
{% endblock %}
```

### Static Tabs Configuration

**Configures static tabs for template rendering.**

```python
UNFOLD = {
    "TABS": [
        {
            "page": "custom_page",  # Unique tab identifier
            "items": [
                {
                    "title": _("Your custom title"),
                    "link": reverse_lazy("admin:app_label_model_name_changelist"),
                },
            ],
        }
    ]
}
```

%%END%%

%%README.LLM id=fieldsets-tabs%%

## 🧭 Library Description

Organizing fieldsets into tabs for better form organization.

## ✅ Rules

- Add `tab` CSS class to fieldsets.
- Provide fieldset names for tab titles.
- Use in ModelAdmin fieldsets configuration.

## 🧪 Functions

### Fieldset Tabs Configuration

**Organizes fieldsets into tabs.**

```python
# admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

@admin.register(MyModel)
class MyModelAdmin(ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": [
                    "field_1",
                    "field_2",
                ],
            },
        ),
        (
            _("Tab 1"),
            {
                "classes": ["tab"],
                "fields": [
                    "field_3",
                    "field_4",
                ],
            },
        ),
        (
            _("Tab 2"),
            {
                "classes": ["tab"],
                "fields": [
                    "field_5",
                    "field_6",
                ],
            },
        ),
    )
```

**Note:** These tabs are displayed in the main content area, not at the top of the page.

%%END%%

%%README.LLM id=inline-tabs%%

## 🧭 Library Description

Organizing inline forms into tabs for better form management.

## ✅ Rules

- Set `tab = True` in inline class definition.
- Works only for changeform pages.
- Independent from main tab system.

## 🧪 Functions

### Inline Tabs Configuration

**Organizes inline forms into tabs.**

```python
# admin.py
from django.contrib.auth.models import User
from unfold.admin import StackedInline, TabularInline

class MyTabularInline(TabularInline):
    model = User
    tab = True

class MyStackedInline(StackedInline):
    model = User
    tab = True
```

%%END%%

---

## 🔁 Flows

### Changelist Tabs Setup Flow

1. Configure `UNFOLD["TABS"]` in settings.py.
2. Define models that should display tabs.
3. Create tab items with titles and links.
4. Implement permission callbacks if needed.
5. Test tab navigation in changelist views.

**Modules**:
- `@tabs/changelist`
- `@core/configuration`

---

### Changeform Tabs Setup Flow

1. Configure `UNFOLD["TABS"]` with `detail: True`.
2. Define models as dictionaries with detail flag.
3. Create tab items for changeform navigation.
4. Implement permission callbacks for tab visibility.
5. Test tab navigation in changeform views.

**Modules**:
- `@tabs/changeform`
- `@core/configuration`

---

### Dynamic Tabs Implementation Flow

1. Create callback function for dynamic tab generation.
2. Configure `UNFOLD["TABS"]` to use callback.
3. Implement `tab_list` template tag in custom templates.
4. Configure unique `page` identifiers.
5. Test dynamic tab rendering.

**Modules**:
- `@tabs/dynamic`
- `@core/configuration`

---

### Fieldset Tabs Setup Flow

1. Configure ModelAdmin fieldsets.
2. Add `tab` CSS class to relevant fieldsets.
3. Provide fieldset names for tab titles.
4. Test tab organization in changeform.
5. Verify tab navigation in main content area.

**Modules**:
- `@tabs/fieldsets`
- `@core/configuration`

---

### Inline Tabs Setup Flow

1. Create inline classes (StackedInline or TabularInline).
2. Set `tab = True` in inline class definition.
3. Add inlines to ModelAdmin.
4. Test inline tab navigation in changeform.
5. Verify independent tab system functionality.

**Modules**:
- `@tabs/inline`
- `@core/configuration`

---

## 🧠 Notes

- **Changelist tabs** provide navigation between different models in list views.
- **Changeform tabs** enable navigation in detail/edit views with `detail: True` flag.
- **Dynamic tabs** allow custom logic for tab generation using callbacks.
- **Fieldset tabs** organize form fields into tabs using CSS classes.
- **Inline tabs** organize related model forms into tabs independently.
- **Template rendering** uses `{% tab_list %}` tag for custom tab display.
- **Permission callbacks** control tab visibility based on user permissions.
- **Active tab configuration** can be static or dynamic using lambda functions. 