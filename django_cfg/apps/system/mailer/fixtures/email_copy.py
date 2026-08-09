"""Default letter copy shipped with django-cfg.

A fresh install has no ``EmailContent`` rows, and a project that never loads
these still sends correct mail — the template's own wording is the fallback. So
these defaults exist for a different reason: they give a project something to
*edit*. Loading them puts the English text in the admin, where it can be
rewritten and translated without touching a template.

Kept as Python rather than a JSON fixture on purpose: a JSON fixture pins field
names and would break silently the next time the model gains a field, while this
is checked by the same import that loads it.

English only. Translations are a product's own words — and shipping fourteen
machine-translated letters under a framework's name is worse than shipping none,
because nobody knows which ones were reviewed.
"""

from __future__ import annotations

# One entry per letter key. Multi-paragraph fields are newline-separated, which
# is the storage format `EmailContent.as_context` splits.
DEFAULT_EMAIL_COPY: dict[str, dict[str, str]] = {
    "welcome": {
        "subject": "Welcome to {{ project_name }}",
        "greeting": "Hi —",
        "lede": (
            "you just signed up for {{ project_name }} — here is the short version "
            "of what to do with it."
        ),
        "run_intro": "Getting started takes one command:",
        "run_after": (
            "That is the whole setup. Everything else is optional and can wait "
            "until you need it."
        ),
        "points": (
            "If anything does not work the way you expected, that is worth "
            "knowing about — it is usually a sign the setup step was unclear "
            "rather than that you did something wrong."
        ),
        "outro": "It should take about a minute to have something working.",
        "signoff": (
            "I'd genuinely like to know what you make of it — and especially what "
            "breaks. Just reply to this email."
        ),
        "role": "founder of {{ project_name }}",
    },
}
