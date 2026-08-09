"""Template helpers for database-stored letter copy.

``EmailContent`` rows keep ``{{ project_name }}`` as literal text so the same
copy works for any project. Django does not re-render a variable's *value*, so
without a filter the reader would see the braces.

``render_copy`` interpolates it against the surrounding context. It is
deliberately not ``Template(...).render()``: stored copy is edited in the admin,
and evaluating it as a template would let whoever edits it reach anything the
context holds (``{{ user.email }}``, or a tag) — a stored-template injection in
a letter that goes to every new signup. Only an explicit, closed set of
placeholders is substituted.
"""

from __future__ import annotations

from django import template

register = template.Library()

# The only placeholders stored copy may use. Anything else is left as written,
# so a typo shows up in review instead of silently resolving to something.
ALLOWED = ("project_name", "site_url")


@register.simple_tag(takes_context=True)
def render_copy(context, value):
    """Substitute the allowed placeholders in one stored string."""
    if not value:
        return ""
    text = str(value)
    for name in ALLOWED:
        if name in context:
            replacement = str(context[name] or "")
            text = text.replace("{{ %s }}" % name, replacement)
            text = text.replace("{{%s}}" % name, replacement)
    # Escaped by the caller via `|escape`; copy is plain prose, never markup.
    return text


@register.filter(name="copy_paragraphs")
def copy_paragraphs(value):
    """A stored multi-paragraph block as a list of paragraph strings."""
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [line.strip() for line in str(value).splitlines() if line.strip()]


@register.simple_tag(takes_context=True)
def copy_or(context, copy, field, default=""):
    """``copy[field]`` when a database row supplied it, else ``default``.

    Lets one template serve both a project that loaded fixtures and one that has
    not: the row wins when present, and the template's own wording is the
    fallback rather than an empty letter.
    """
    if copy:
        value = copy.get(field) if isinstance(copy, dict) else getattr(copy, field, None)
        if value:
            return str(value)
    return default
