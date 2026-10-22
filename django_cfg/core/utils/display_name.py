"""Validation of human-facing names that end up in mail headers, chat messages and QR labels."""

import re
import unicodedata

# Punctuation people put in real names ("Acme, Inc.", "Bob's Shop", "Foo & Bar",
# "gptkino.com"). Left out on purpose: `"` `\` `<` `>` (header and markup
# delimiters), `:` (separates issuer from account in otpauth labels), `@`
# (a display name that looks like an address is a spoofing tool).
_ALLOWED_PUNCTUATION = frozenset(" .,'&()-_")
_ALLOWED_CATEGORIES = ("L", "N", "M")  # letters, digits, combining marks

_WHITESPACE = re.compile(r"\s+")
_NON_ALNUM = re.compile(r"[^0-9a-zA-Z]+")


def slugify_name(value: str, fallback: str = "django_cfg") -> str:
    """ASCII, lower-case, ``_``-separated identifier for a name (``gptkino.com`` → ``gptkino_com``).

    For places that need an identifier rather than a label: registration names,
    file names, a chat that rejects punctuation. Names with no ASCII letter or
    digit (``Привет``) have nothing to derive from and return ``fallback``.
    """
    return _NON_ALNUM.sub("_", value).strip("_").lower() or fallback


def normalize_display_name(value: str) -> str:
    """Return the NFC-normalised, whitespace-collapsed name, or raise ``ValueError``.

    Control, format (bidi overrides, zero-width) and other symbol characters are
    rejected rather than stripped, so the owner sees what was wrong. Safety at the
    point of use — header quoting, markup escaping — is still done by each sink.
    """
    name = _WHITESPACE.sub(" ", unicodedata.normalize("NFC", value)).strip()
    invalid = sorted(
        {
            c
            for c in name
            if c not in _ALLOWED_PUNCTUATION and not unicodedata.category(c).startswith(_ALLOWED_CATEGORIES)
        }
    )
    if invalid:
        shown = ", ".join(repr(c) for c in invalid)
        raise ValueError(
            f"Name contains unsupported character(s): {shown}. "
            "Allowed: letters, digits, spaces and . , ' & ( ) - _"
        )
    if not any(c.isalnum() for c in name):
        raise ValueError("Name must contain at least one letter or digit")
    return name
