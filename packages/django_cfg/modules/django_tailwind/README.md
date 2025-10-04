# Django Tailwind Layouts

Universal layouts for use across the entire django-cfg project.

## 📋 Available Layouts

### 1. `django_tailwind/base.html`
Base layout with minimal markup.

**Usage:**
```django
{% extends 'django_tailwind/base.html' %}

{% block title %}My Page{% endblock %}
{% block content %}
    <h1>Hello World</h1>
{% endblock %}
```

**Blocks:**
- `title` - page title
- `extra_head` - additional tags in head
- `header` - header (empty by default)
- `content` - main content
- `footer` - footer (empty by default)
- `extra_js` - additional JS

---

### 2. `django_tailwind/app.html`
Layout for full-featured applications with header, footer and dark mode.

**Usage:**
```django
{% extends 'django_tailwind/app.html' %}

{% block header_title %}My App{% endblock %}
{% block header_icon %}🚀{% endblock %}

{% block content %}
    <h1>Dashboard</h1>
{% endblock %}
```

**Blocks:**
- `header_title` - title in header (default: "Django CFG")
- `header_icon` - icon in header (default: 💎)
- `header_actions` - buttons in header (default: dark mode toggle)
- `header_nav` - navigation under header
- `content` - main content
- `footer_text` - text in footer

---

### 3. `django_tailwind/simple.html`
Layout for simple pages (success, error, 404, etc).

**Usage:**
```django
{% extends 'django_tailwind/simple.html' %}

{% block icon %}✅{% endblock %}
{% block heading %}Success!{% endblock %}
{% block message %}
    Payment completed successfully
{% endblock %}

{% block actions %}
    <a href="/dashboard" class="btn-primary">
        Go to Dashboard
    </a>
{% endblock %}
```

**Blocks:**
- `icon` - icon (emoji or SVG)
- `heading` - heading
- `message` - message
- `actions` - action buttons

---

## ✨ Features

### Dark Mode
All layouts support dark mode via Alpine.js:
- Theme toggle included in all layouts
- State persisted in localStorage
- Automatic system theme detection
- Prevents flash on load (FOUC)
- Ready-to-use `theme_toggle.html` component

**Using the toggle component:**
```django
<!-- Default variant (with background) -->
{% include 'django_tailwind/components/theme_toggle.html' %}

<!-- Icon only (compact) -->
{% include 'django_tailwind/components/theme_toggle.html' with button_variant="icon" %}

<!-- With text label -->
{% include 'django_tailwind/components/theme_toggle.html' with button_variant="text" %}

<!-- Custom classes -->
{% include 'django_tailwind/components/theme_toggle.html' with button_class="my-custom-class" %}
```

### Tailwind CSS
All layouts use **django-tailwind** via `{% tailwind_css %}`:
- Compilation via django-tailwind app
- PurgeCSS in production
- Hot reload in development

### Alpine.js
Included in all layouts for interactivity:
- Dark mode toggle
- Dynamic components
- Form validation

---

## 📦 Template Tags

### Library Information

```django
{% load tailwind_info %}

{# Library name #}
{% tailwind_lib_name %}  {# Django Tailwind Layouts #}

{# Version #}
{% tailwind_lib_version %}  {# 1.0.0 #}

{# Description #}
{% tailwind_lib_description %}

{# URL #}
{% tailwind_lib_url %}

{# Ready-made HTML for footer #}
{% tailwind_powered_by %}

{# Text for footer #}
{% tailwind_footer_text %}
```

---

## 🎨 Components

### Navbar (Navigation Bar)

Universal navbar with support for navigation links and theme toggle.

**Location:**
```
django_tailwind/components/navbar.html
```

**Parameters:**
- `title` - Navbar title (default: "Django CFG")
- `icon` - Icon (emoji or HTML)
- `nav_items` - List of navigation items
- `show_theme_toggle` - Show dark mode toggle (default: True)
- `show_user_menu` - Show user menu dropdown (default: True)
- `sticky` - Fixed navbar (default: True)

**Usage:**

1. **Simple navbar:**
```django
{% include 'django_tailwind/components/navbar.html' with title="My App" icon="🚀" %}
```

2. **With navigation links:**
```django
{# In view pass: #}
nav_items = [
    {'label': 'Dashboard', 'url': '/dashboard/', 'active': True, 'icon': '📊'},
    {'label': 'Settings', 'url': '/settings/'},
]

{# In template: #}
{% include 'django_tailwind/components/navbar.html' with title="Admin" nav_items=nav_items %}
```

3. **Customization via app.html:**
```django
{% extends 'django_tailwind/app.html' %}

{% block header %}
{% include 'django_tailwind/components/navbar.html' with title="Payment Admin" icon='<span class="material-icons">payment</span>' nav_items=navbar_items %}
{% endblock %}
```

---

### Theme Toggle (Theme Switcher)

Ready-to-use component for switching between dark/light mode.

**Location:**
```
django_tailwind/components/theme_toggle.html
```

**Variants:**

1. **Default** - with background on hover:
```django
{% include 'django_tailwind/components/theme_toggle.html' %}
```

2. **Icon** - icon only (compact):
```django
{% include 'django_tailwind/components/theme_toggle.html' with button_variant="icon" %}
```

3. **Text** - with text label:
```django
{% include 'django_tailwind/components/theme_toggle.html' with button_variant="text" %}
```

4. **Floating button** (for simple pages):
```django
<div class="fixed top-4 right-4 z-50">
    {% include 'django_tailwind/components/theme_toggle.html' %}
</div>
```

---

### User Menu (User Dropdown)

Dropdown user menu with avatar, information and links.

**Location:**
```
django_tailwind/components/user_menu.html
```

**Features:**
- Shows only for authenticated users
- Avatar with initials (auto-generated from name or username)
- Display name and email
- Admin panel link (automatically for staff users)
- Optional links: profile, logout
- Alpine.js dropdown with animation

**Parameters:**
- `show_admin`: Show admin link (default: auto for staff)
- `show_profile`: Show profile link (default: False)
- `show_logout`: Show logout link (default: False)
- `profile_url`: Profile URL (default: /profile/)
- `logout_url`: Logout URL (default: /accounts/logout/)

**Usage:**

1. **Default** (admin link for staff only):
```django
{% include 'django_tailwind/components/user_menu.html' %}
```

2. **With profile and logout:**
```django
{% include 'django_tailwind/components/user_menu.html' with show_profile=True show_logout=True %}
```

3. **With custom URLs:**
```django
{% include 'django_tailwind/components/user_menu.html' with
    show_profile=True
    show_logout=True
    profile_url="/dashboard/profile/"
    logout_url="/auth/logout/" %}
```

4. **In navbar** (already included by default):
```django
{# User menu automatically included in navbar #}
{% include 'django_tailwind/components/navbar.html' with title="My App" %}

{# Disable user menu #}
{% include 'django_tailwind/components/navbar.html' with show_user_menu=False %}

{# With profile and logout #}
{% include 'django_tailwind/components/navbar.html' with
    show_profile=True
    show_logout=True %}
```

**Template Tags:**

User menu uses special templatetags from `tailwind_info`:

```django
{% load tailwind_info %}

{# Get admin URL from settings or default #}
{% get_admin_url as admin_url %}

{# Get user display name #}
{% get_user_display_name as user_name %}

{# Get initials for avatar #}
{% get_user_initials as initials %}
```

---

## 📦 Usage Examples

### Example 1: Success Page
```django
{% extends 'django_tailwind/simple.html' %}

{% block icon %}✅{% endblock %}
{% block heading %}Payment Successful{% endblock %}
{% block message %}
    We received your payment and will process it shortly.
{% endblock %}
```

### Example 2: Dashboard with Navigation

**View (dashboard.py):**
```python
def dashboard_view(request):
    nav_items = [
        {'label': 'Overview', 'url': '/dashboard/', 'active': True},
        {'label': 'Users', 'url': '/dashboard/users/'},
        {'label': 'Settings', 'url': '/dashboard/settings/'},
    ]

    context = {
        'navbar_title': 'Admin Dashboard',
        'navbar_icon': '📊',
        'navbar_items': nav_items,
    }
    return render(request, 'dashboard.html', context)
```

**Template (dashboard.html):**
```django
{% extends 'django_tailwind/app.html' %}

{% block content %}
<div class="grid grid-cols-3 gap-6">
    <!-- Stats cards -->
</div>
{% endblock %}
```

### Example 3: Custom Layout
```django
{% extends 'django_tailwind/base.html' %}

{% block header %}
<header class="custom-header">
    <!-- Your custom header -->
</header>
{% endblock %}

{% block content %}
<!-- Your content -->
{% endblock %}
```

---

## 🎨 Customization

### Overriding Styles
```django
{% extends 'django_tailwind/app.html' %}

{% block extra_head %}
<style>
    .custom-btn {
        @apply px-6 py-3 bg-purple-600 text-white rounded-lg;
    }
</style>
{% endblock %}
```

### Adding Custom Blocks
```django
{% extends 'django_tailwind/app.html' %}

{% block header_actions %}
    {{ block.super }}  <!-- Keep dark mode toggle -->
    <button class="btn">Notifications</button>
{% endblock %}
```

---

## 🚀 Migrating Existing Templates

### Before (CDN):
```django
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <h1>Hello</h1>
</body>
</html>
```

### After (django-tailwind):
```django
{% extends 'django_tailwind/simple.html' %}

{% block heading %}Hello{% endblock %}
```

**Benefits:**
- ✅ Less code
- ✅ Unified style
- ✅ Dark mode out of the box
- ✅ Production-ready (PurgeCSS)
- ✅ Hot reload in dev

---

## 📁 File Structure

```
modules/django_tailwind/
├── templates/
│   └── django_tailwind/
│       ├── base.html       # Base layout
│       ├── app.html        # Layout for applications
│       ├── simple.html     # Layout for simple pages
│       └── components/
│           ├── navbar.html       # Universal navbar
│           ├── theme_toggle.html # Dark mode toggle
│           └── user_menu.html    # User dropdown menu
└── templatetags/
    └── tailwind_info.py    # Template tags for library info
```

---

## 🌙 Dark Mode Implementation

All layouts use **class-based dark mode** via Alpine.js:

1. **Initialization** (in `base.html`):
   - Reads from localStorage or system preference
   - Applies `.dark` class to `<html>` immediately to prevent flash
   - Sets up Alpine.js reactive state

2. **CSS Overrides**:
   - Ensures `dark:` classes only work with `.dark` class
   - Prevents conflicts with media query dark mode
   - Smooth transitions on theme change

3. **Toggle Component**:
   - Updates Alpine.js state
   - Persists to localStorage
   - Toggles `.dark` class on `<html>`

**Why class-based?**
- Full control over theme switching
- No dependency on system preferences (unless user wants it)
- Works with compiled Tailwind CSS
- Prevents flash of unstyled content (FOUC)

---

**Last Updated**: 2025-10-03
**Version**: 1.0.0
**Author**: Django-CFG Team
