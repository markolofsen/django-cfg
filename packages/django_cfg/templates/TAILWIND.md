# Tailwind CSS Semantic Color System

This document explains how the semantic color system works in Django CFG with django_tailwind module and Unfold admin integration.

## Overview

Django CFG uses two color systems:

1. **Semantic Colors** (CSS Variables) - For Unfold admin pages
2. **Standard Tailwind Colors** - For standalone pages outside admin

## Color Architecture

### Unfold Admin (Semantic Colors)

The Unfold admin defines CSS variables that enable theme consistency:

```css
/* Defined by Unfold in its CSS */
--color-base-50: ...;
--color-base-100: ...;
--color-primary-500: ...;
--color-font-default-light: ...;
--color-font-default-dark: ...;
```

These are consumed by Tailwind via the configuration in `django_unfold/tailwind.py`:

```python
"colors": {
    "base": {
        "50": "rgb(var(--color-base-50) / <alpha-value>)",
        ...
    },
    "font": {
        "subtle-light": "rgb(var(--color-font-subtle-light) / <alpha-value>)",
        "default-dark": "rgb(var(--color-font-default-dark) / <alpha-value>)",
        ...
    }
}
```

**Usage in admin templates:**
```html
<div class="bg-base-50 dark:bg-base-900">
    <p class="text-font-default-light dark:text-font-default-dark">
        Content
    </p>
</div>
```

### Standalone Pages (Standard Tailwind)

For pages that don't load Unfold's CSS (like 404.html, route_not_found.html), use standard Tailwind colors:

```html
<div class="bg-gray-50 dark:bg-gray-900">
    <p class="text-gray-700 dark:text-gray-300">
        Content
    </p>
</div>
```

## Color Mapping Reference

| Semantic (Admin) | Standard Tailwind | Usage |
|-----------------|------------------|-------|
| `base-50` | `gray-50` | Light backgrounds |
| `base-100` | `gray-100` | Subtle backgrounds |
| `base-200` | `gray-200` | Borders, dividers |
| `base-700` | `gray-700` | Dark borders |
| `base-900` | `gray-900` | Dark backgrounds |
| `base-950` | `gray-950` | Darkest backgrounds |
| `primary-*` | `indigo-*` | Primary accent color |
| `warning-*` | `amber-*` | Warning states |
| `success-*` | `emerald-*` | Success states |
| `error-*` | `red-*` | Error states |
| `info-*` | `blue-*` | Information states |

### Font Colors (Semantic Only)

| Semantic Class | Dark Mode Class | Standard Equivalent |
|---------------|-----------------|---------------------|
| `text-font-important-light` | `dark:text-font-important-dark` | `text-gray-900 dark:text-gray-100` |
| `text-font-default-light` | `dark:text-font-default-dark` | `text-gray-700 dark:text-gray-300` |
| `text-font-subtle-light` | `dark:text-font-subtle-dark` | `text-gray-500 dark:text-gray-400` |

## Dark Mode

Dark mode is class-based (`darkMode: "class"` in Tailwind config). The `.dark` class is added to `<html>` element.

### Theme Detection

The `django_tailwind/base.html` template detects theme from multiple sources:

```javascript
// Check multiple sources
const unfoldTheme = localStorage.getItem('theme');     // Unfold: 'dark'/'light'
const legacyDarkMode = localStorage.getItem('darkMode'); // Legacy: 'true'/'false'
const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

const isDark = unfoldTheme === 'dark' ||
              legacyDarkMode === 'true' ||
              (!unfoldTheme && !legacyDarkMode && systemPrefersDark);

if (isDark) {
    document.documentElement.classList.add('dark');
}
```

### Using Dark Mode Classes

Always pair light and dark variants:

```html
<!-- Backgrounds -->
<div class="bg-gray-50 dark:bg-gray-900">

<!-- Text -->
<p class="text-gray-700 dark:text-gray-300">

<!-- Borders -->
<div class="border-gray-200 dark:border-gray-700">
```

## django_tailwind Module

The `django_tailwind` module provides:

### Base Templates

- `django_tailwind/base.html` - Full layout with header/footer
- `django_tailwind/simple.html` - Centered card layout

### Template Tags

```django
{% load tailwind_tags %}
{% tailwind_css %}  {# Loads compiled Tailwind CSS #}
```

### Components

```django
{% include 'django_tailwind/components/theme_toggle.html' %}
```

## When to Use Which System

| Context | Color System | Example |
|---------|-------------|---------|
| Unfold admin pages | Semantic (base-*, font-*) | Admin change list |
| Django Tailwind base template | Standard Tailwind | 404 pages |
| Standalone error pages | Standard Tailwind | route_not_found.html |
| Admin widgets/components | Semantic | Image preview modal |

## Best Practices

1. **Admin pages**: Use semantic colors for consistency with Unfold theme
2. **Standalone pages**: Use standard Tailwind colors (gray, amber, blue, etc.)
3. **Always provide dark variants**: Every color class needs a `dark:` counterpart
4. **Test both themes**: Verify appearance in both light and dark modes
5. **Avoid mixing**: Don't mix semantic and standard colors in the same template

## File Locations

- Tailwind config: `django_unfold/tailwind.py`
- Base templates: `modules/django_tailwind/templates/`
- Admin CSS: `static/admin/css/theme.css`
- Prose styles: `static/admin/css/prose-unfold.css`
