"""Which language to write to a person in.

Separate from both the user model and the welcome letter on purpose:

- **Not the user manager.** ``UserManager.clean_language`` normalises *one* tag
  (``'EN'`` -> ``'en'``) and belongs there. Parsing an ``Accept-Language``
  header — q-weights, ordering, region subtags — is HTTP work, and a model
  manager has no reason to know about it. Using the normaliser as if it were a
  parser is what produced the bugs this module exists to prevent.
- **Not services/welcome.py.** "Which locale" is not specific to one letter. Put
  it there and the second letter either imports across a feature boundary or
  grows its own copy that drifts.

The supported set is a **mailer** concern: it lists the locales the platform can
actually write a letter in, which is what makes a fallback to English correct
rather than arbitrary.
"""

from __future__ import annotations

from typing import Optional

# The locales the platform ships letters for. Mirrors the frontend SSoT,
# ``packages/i18n/src/locales/index.ts`` (re-exported as ``DEFAULT_LOCALES``
# from ``packages/nextjs/src/i18n/routing.ts``). Kept as an explicit list
# because the TS ``LocaleCode`` type is ``'en' | 'ru' | 'ko' | string`` and so
# constrains nothing — the file list is the real contract.
#
# ``pt-BR`` carries a region on purpose. There is no bare ``pt``, which is why
# ``match_supported`` must not blindly reduce a tag to two letters the way
# ``UserManager.clean_language`` does — that would map a Brazilian user to
# ``pt`` and match nothing at all.
SUPPORTED_LOCALES: tuple[str, ...] = (
    "en", "ru", "ko", "ja", "de", "fr", "zh", "it", "es",
    "nl", "ar", "tr", "pt-BR", "pl", "sv", "no", "da",
)

DEFAULT_LOCALE = "en"

# Languages written right-to-left. Base languages only: a region subtag never
# changes direction, so ``ar-EG`` is as RTL as ``ar``.
RTL_LANGUAGES: frozenset[str] = frozenset({"ar", "he", "fa", "ur"})


def match_supported(tag: str) -> Optional[str]:
    """Best supported locale for one BCP-47 tag, or None.

    Exact match wins (so ``pt-BR`` resolves to ``pt-BR``); otherwise the tag's
    base language is matched against both bare and region-carrying entries, so
    ``pt`` and ``pt-PT`` both reach ``pt-BR`` rather than falling back to
    English.
    """
    tag = (tag or "").strip().replace("_", "-")
    if not tag:
        return None

    lowered = tag.lower()
    by_lower = {loc.lower(): loc for loc in SUPPORTED_LOCALES}
    if lowered in by_lower:
        return by_lower[lowered]

    base = lowered.split("-")[0]
    if base in by_lower:
        return by_lower[base]
    for loc in SUPPORTED_LOCALES:
        if loc.lower().split("-")[0] == base:
            return loc
    return None


def parse_accept_language(header: str) -> list[str]:
    """Tags from an ``Accept-Language`` header, most-preferred first.

    Honours ``q`` weights; ``*`` is dropped. An unweighted tag is ``q=1.0``,
    which is why taking the header's first tag is wrong: in
    ``de;q=0.7,ru,en;q=0.9`` the preferred language is ``ru``, listed second.

    Django's own ``get_language_from_request`` is not used because it filters
    against ``settings.LANGUAGES``, which this package never populates.
    """
    tags: list[tuple[float, int, str]] = []
    for index, part in enumerate(header.split(",")):
        piece = part.strip()
        if not piece:
            continue
        tag, _, params = piece.partition(";")
        tag = tag.strip()
        if not tag or tag == "*":
            continue
        quality = 1.0
        for param in params.split(";"):
            key, _, value = param.partition("=")
            if key.strip() == "q":
                try:
                    quality = float(value)
                except ValueError:
                    quality = 0.0
        # index keeps the header's own order stable among equal weights
        tags.append((-quality, index, tag))
    return [tag for _, _, tag in sorted(tags)]


def best_supported(header: str) -> Optional[str]:
    """The best supported locale an ``Accept-Language`` header asks for, or None.

    Returns None rather than the default when nothing matches, so a caller can
    tell "the browser wants a language we do not ship" from "the browser wants
    English" — the first must not be stored as a preference.
    """
    for tag in parse_accept_language(header or ""):
        matched = match_supported(tag)
        if matched:
            return matched
    return None


def text_direction(locale: Optional[str]) -> str:
    """``rtl`` or ``ltr`` for a locale tag.

    Derived centrally so no template or translator has to remember it: a letter
    that forgets ``dir`` renders Arabic left-aligned with its punctuation
    stranded on the wrong side.
    """
    base = (locale or "").strip().replace("_", "-").split("-")[0].lower()
    return "rtl" if base in RTL_LANGUAGES else "ltr"
