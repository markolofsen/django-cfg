"""
Template helpers for the DRF Tailwind theme.

Return FULL Tailwind utility strings (not component class names): the Tailwind v4
Play CDN has no @apply, so it scans rendered markup for utilities. Badges follow a
Vercel-style outline pill — thin border + subtle tint + coloured text, not a loud fill.
"""

from django import template

register = template.Library()

_BADGE_BASE = (
    "inline-flex items-center rounded-full border px-2 py-0.5 "
    "text-[11px] font-medium tracking-wide uppercase"
)

_METHOD_COLORS = {
    "GET":    "border-blue-200 dark:border-blue-900 bg-blue-50 dark:bg-blue-950/50 text-blue-700 dark:text-blue-400",
    "POST":   "border-green-200 dark:border-green-900 bg-green-50 dark:bg-green-950/50 text-green-700 dark:text-green-400",
    "PUT":    "border-amber-200 dark:border-amber-900 bg-amber-50 dark:bg-amber-950/50 text-amber-700 dark:text-amber-400",
    "PATCH":  "border-violet-200 dark:border-violet-900 bg-violet-50 dark:bg-violet-950/50 text-violet-700 dark:text-violet-400",
    "DELETE": "border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/50 text-red-700 dark:text-red-400",
}
_METHOD_NEUTRAL = "border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 text-zinc-600 dark:text-zinc-400"

_STATUS_COLORS = {
    2: "border-green-200 dark:border-green-900 bg-green-50 dark:bg-green-950/50 text-green-700 dark:text-green-400",
    3: "border-blue-200 dark:border-blue-900 bg-blue-50 dark:bg-blue-950/50 text-blue-700 dark:text-blue-400",
    4: "border-amber-200 dark:border-amber-900 bg-amber-50 dark:bg-amber-950/50 text-amber-700 dark:text-amber-400",
    5: "border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/50 text-red-700 dark:text-red-400",
}


@register.filter
def method_badge(method: str) -> str:
    """Full Tailwind class string for an HTTP-method badge (outline pill)."""
    color = _METHOD_COLORS.get((method or "").upper(), _METHOD_NEUTRAL)
    return f"{_BADGE_BASE} {color}"


@register.filter
def status_badge(status_code) -> str:
    """Full Tailwind class string for a response-status badge (outline pill)."""
    try:
        bucket = int(status_code) // 100
    except (TypeError, ValueError):
        bucket = 2
    color = _STATUS_COLORS.get(bucket, _STATUS_COLORS[2])
    return f"{_BADGE_BASE} {color}"


@register.filter
def add_class(field, css_class: str):
    """Add a CSS class to a bound form field's widget."""
    return field.as_widget(attrs={"class": css_class})
