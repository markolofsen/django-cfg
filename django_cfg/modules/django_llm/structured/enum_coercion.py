"""
Deterministic enum coercion for LLM-returned strings.

An LLM asked for an enum routinely echoes the enum's human **label**
("Front-Wheel Drive") instead of its **value** ("fwd") — the label is an
adjacent token on the same prompt line. ``EnumCoercer`` accepts either by
keying a lookup on BOTH value and label, normalized for case and
separators, plus an optional caller-supplied slang map.

Deterministic only — no fuzzy / approximate matching. String distance is
not semantic distance ("fwd"/"rwd" are 66% similar but opposite;
"petrol"/"gasoline" are 0% similar but identical). The bottom of the
ladder is ``None``, never a guess: a confidently-wrong enum corrupts the
DB silently, an empty one does not.

See ``@docs/insights/llm-enum-mapping.md`` for the full design.
"""

from __future__ import annotations

import re
from typing import Iterable, Optional, Union

# A choices source: a Django ``TextChoices``/``Choices`` class (anything
# exposing a ``.choices`` list of ``(value, label)`` pairs) or a plain
# iterable of ``(value, label)`` pairs.
ChoicesSource = Union[type, Iterable[tuple[object, object]]]

_SEPARATORS = re.compile(r"[\s/_-]+")


def _norm_key(s: str) -> str:
    """Collapse case and separators: 'Front-Wheel Drive' -> 'front_wheel_drive'."""
    return _SEPARATORS.sub("_", s.strip().lower()).strip("_")


def _iter_pairs(source: ChoicesSource) -> Iterable[tuple[object, object]]:
    """Yield ``(value, label)`` pairs from a choices source.

    Duck-typed: if the source exposes a ``.choices`` attribute (Django
    ``TextChoices``/``Choices``) that is used; otherwise the source is
    treated directly as an iterable of pairs. No Django import required.
    """
    choices = getattr(source, "choices", None)
    return choices if choices is not None else source  # type: ignore[return-value]


class EnumCoercer:
    """Map an LLM-returned enum string to its canonical value.

    Builds, at construction, a normalized lookup keyed on every enum
    value and its human label (plus optional slang). ``coerce`` resolves
    a raw string against that lookup case/separator-insensitively, or
    returns ``None`` — never a guess.

    Example::

        coercer = EnumCoercer(DriveTypeChoices, slang={"4x4": "4wd"})
        coercer.coerce("Front-Wheel Drive")  # -> "fwd"
        coercer.coerce("4x4")                # -> "4wd"
        coercer.coerce("spaceship")          # -> None
    """

    def __init__(
        self,
        choices: ChoicesSource,
        *,
        slang: Optional[dict[str, str]] = None,
        exclude: Optional[Iterable[str]] = None,
    ) -> None:
        """Build the lookup from a choices source.

        Args:
            choices: A Django ``TextChoices``/``Choices`` class or a plain
                iterable of ``(value, label)`` pairs.
            slang: Extra ``{normalized_input: canonical_value}`` synonyms
                that match neither a value nor a label (e.g.
                ``{"petrol": "gasoline"}``). Keys are normalized on input.
            exclude: Enum values to omit from the lookup entirely.
        """
        self._exclude: frozenset[str] = frozenset(exclude or ())
        self._lookup: dict[str, str] = {}

        for raw_value, raw_label in _iter_pairs(choices):
            value = str(raw_value)
            if value in self._exclude:
                continue
            self._lookup[_norm_key(value)] = value
            self._lookup[_norm_key(str(raw_label))] = value

        for raw_input, canonical in (slang or {}).items():
            canonical = str(canonical)
            if canonical in self._exclude:
                continue
            self._lookup[_norm_key(str(raw_input))] = canonical

    @property
    def lookup(self) -> dict[str, str]:
        """The normalized ``{key: canonical_value}`` map (a copy)."""
        return dict(self._lookup)

    def coerce(self, raw: object) -> Optional[str]:
        """Resolve ``raw`` to a canonical enum value, or ``None``.

        Non-str or empty input returns ``None``. The input is normalized
        (case/separators collapsed) and looked up against value, label
        and slang keys. An unrecognized string returns ``None`` — never a
        fuzzy or best-effort guess.
        """
        if not isinstance(raw, str):
            return None
        key = _norm_key(raw)
        if not key:
            return None
        return self._lookup.get(key)
