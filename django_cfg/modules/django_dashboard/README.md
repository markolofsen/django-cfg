# django_dashboard

Custom tabbed dashboard panels inside the Django Unfold admin overview page.

Each tab is a standard Django view: a plain Python callback returns a `dict`, a Django template renders it. No Streamlit, no iframes, no special base classes.

---

## How it works

```
DjangoConfig.dashboard: DashboardConfig
    └── tabs: List[DashboardTab]
              ├── slug        → URL segment  /cfg/admin/dashboard/<slug>/
              ├── title       → Tab label
              ├── icon        → Material icon name
              ├── callback    → dotted path  fn(request) -> dict
              ├── template    → Django template path
              └── permission  → dotted path  fn(request) -> bool  (default: is_staff)
```

On request the view:
1. Resolves `callback` → calls it with `request` → gets a plain `dict`
2. Renders `template` with that dict as context (+ `current_tab`, `all_tabs`, `dashboard_config`)

---

## Quick start

### 1. Create a dashboard app in your project

```
myproject/
└── dashboard/
    ├── __init__.py
    ├── apps.py
    ├── callbacks/
    │   ├── __init__.py
    │   ├── overview.py      ← callback fn
    │   └── system.py
    └── templates/
        └── dashboard/
            ├── overview.html
            └── system.html
```

### 2. Write a callback

```python
# dashboard/callbacks/overview.py
from django.contrib.auth import get_user_model

def callback(request):
    User = get_user_model()
    return {
        "total_users": User.objects.count(),
        "recent_users": User.objects.order_by("-date_joined")[:5],
    }
```

Callback receives the real `HttpRequest`. Do anything: ORM queries, aggregations, pagination (`request.GET.get("page")`), Redis, gRPC — whatever.

### 3. Write a template

```html
{# dashboard/templates/dashboard/overview.html #}
{% extends dashboard_base %}{# switches between base.html and base_iframe.html automatically #}

{% block tab_content %}
<div class="p-4">
    <p>Total users: {{ total_users }}</p>

    {% for user in recent_users %}
        <div>{{ user.email }} — {{ user.date_joined|date:"d M Y" }}</div>
    {% endfor %}
</div>
{% endblock %}
```

Templates are standard Django templates. Use `{% include %}`, template tags, filters — anything goes.

### 4. Register in config

```python
# api/config.py
from django_cfg import DashboardConfig, DashboardTab

class MyConfig(DjangoConfig):
    project_apps = [..., "dashboard"]   # so Django finds the templates via APP_DIRS

    dashboard = DashboardConfig(
        tabs=[
            DashboardTab(
                slug="overview",
                title="Overview",
                icon="bar_chart",
                callback="dashboard.callbacks.overview.callback",
                template="dashboard/overview.html",
            ),
            DashboardTab(
                slug="system",
                title="System",
                icon="monitor_heart",
                callback="dashboard.callbacks.system.callback",
                template="dashboard/system.html",
                permission="dashboard.permissions.is_superuser",  # optional
            ),
        ],
    )
```

---

## DashboardTab fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `slug` | `str` | ✓ | URL segment. Must be unique. |
| `title` | `str` | ✓ | Tab label shown in the UI. |
| `icon` | `str` | | Material icon name (default: `"dashboard"`). |
| `template` | `str` | ✓ or `callback` | Django template path. |
| `callback` | `str` | ✓ or `template` | Dotted path to `fn(request) -> dict`. |
| `permission` | `str` | | Dotted path to `fn(request) -> bool`. Default: `request.user.is_staff`. |

At least one of `template` or `callback` must be set — validated at startup.

## DashboardConfig fields

| Field | Type | Description |
|-------|------|-------------|
| `tabs` | `List[DashboardTab]` | Ordered list of tabs. |
| `default_tab` | `str \| None` | Slug of the tab shown first. Default: first tab. |
| `tailwind_css` | `str \| None` | Static path to a compiled CSS file for custom styles. |

---

## Tab context

Every template receives:

| Variable | Type | Description |
|----------|------|-------------|
| `current_tab` | `DashboardTab` | The active tab object. |
| `all_tabs` | `List[DashboardTab]` | All configured tabs (used by the tab bar). |
| `dashboard_config` | `DashboardConfig` | The full dashboard config. |
| `title` | `str` | Same as `current_tab.title`. |
| `**callback_result` | `dict` | Everything your callback returned. |

---

## Template inheritance

Built-in base templates:

| Template | Purpose |
|----------|---------|
| `django_dashboard/base.html` | Full page: extends Unfold `admin/base.html`, renders tab bar, `{% block tab_content %}` |
| `django_dashboard/tabs_bar.html` | Tab bar snippet only (included by `base.html`) |
| `django_dashboard/tab_empty.html` | Fallback when no template is set (callback-only tab) |

Your templates should extend `django_dashboard/base.html` and fill `{% block tab_content %}`.

---

## Custom CSS (Tailwind)

If your templates use custom Tailwind classes, point `tailwind_css` to your compiled output:

```python
DashboardConfig(
    tailwind_css="dashboard/css/dashboard.css",   # relative to STATIC_ROOT
    tabs=[...],
)
```

The base template injects `<link rel="stylesheet">` automatically when this is set.

---

## URL structure

| URL | Name | Description |
|-----|------|-------------|
| `/cfg/admin/dashboard/` | `django_cfg_dashboard_index` | Redirects to default tab |
| `/cfg/admin/dashboard/<slug>/` | `django_cfg_dashboard_tab` | Renders a specific tab |

Both require `is_staff`. Per-tab permission callbacks override the default.

---

## Template tags

```html
{% load django_cfg_dashboard %}

{# Returns DashboardConfig or None for current staff user #}
{% get_dashboard_config as dashboard %}
{% if dashboard %}
    {% include "django_dashboard/tabs_bar.html" with all_tabs=dashboard.tabs current_tab=dashboard.tabs.0 dashboard_config=dashboard %}
{% endif %}
```

Also available via `{% load django_cfg %}` (backward-compat shim).

---

## Adding a new tab (checklist)

- [ ] Create `dashboard/callbacks/mypage.py` with `def callback(request) -> dict`
- [ ] Create `dashboard/templates/dashboard/mypage.html` extending `django_dashboard/base.html`
- [ ] Add `DashboardTab(slug="mypage", ...)` to `DashboardConfig.tabs` in `config.py`
- [ ] Done — no migrations, no URL changes, no admin registration
