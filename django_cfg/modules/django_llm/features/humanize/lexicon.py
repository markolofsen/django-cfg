"""Tells of machine-written prose, per language. Data only.

Each entry is ``(regex, weight, hint)``. A hit is a *finding*: the rewrite prompt
names the exact phrase, so the model is told what to cut instead of "sound human".
Weights: 1 = mild (common in people too), 2 = typical, 3 = near-certain tell.
Add a language by adding a key; unknown languages fall back to the structural
metrics alone (``metrics.py``), which need no lexicon.
"""

from __future__ import annotations

import re
from typing import Final

Tell = tuple[re.Pattern[str], int, str]


def _t(pattern: str, weight: int, hint: str) -> Tell:
    return re.compile(pattern, re.IGNORECASE | re.UNICODE), weight, hint


LEXICON: Final[dict[str, tuple[Tell, ...]]] = {
    "en": (
        _t(r"\bdelve[sd]?\b|\bdelving\b", 3, "say 'look at' or just state the point"),
        _t(r"\btapestry\b", 3, "drop the metaphor"),
        _t(r"\btestament to\b", 3, "say what it shows, plainly"),
        _t(r"\bin today'?s (?:fast-paced|digital|modern|ever-\w+)[\w\s-]*", 3, "cut the scene-setting opener"),
        _t(r"\bit(?:'s| is) (?:important|worth|crucial|essential) to (?:note|mention|remember|understand)\b", 3, "just say the thing"),
        _t(r"\bnavigat(?:e|ing) the (?:complexit|landscape|world|challenge)\w*", 3, "name the actual difficulty"),
        _t(r"\bgame[- ]chang(?:er|ing)\b", 2, "give the concrete effect"),
        _t(r"\bunlock(?:ing)? (?:the )?(?:full )?(?:potential|power)\b", 3, "state what becomes possible"),
        _t(r"\bseamless(?:ly)?\b", 2, "say what actually works without friction"),
        _t(r"\brobust\b", 1, "give the specific property"),
        _t(r"\bleverag(?:e|es|ed|ing)\b", 2, "say 'use'"),
        _t(r"\belevat(?:e|es|ed|ing)\b", 2, "say what improves"),
        _t(r"\bembark(?:s|ed|ing)? on (?:a|an|your) (?:journey|adventure)\b", 3, "drop it"),
        _t(r"\b(?:realm|landscape) of\b", 2, "name the field directly"),
        _t(r"\bpivotal\b|\bparamount\b", 2, "say 'important' once, or show why"),
        _t(r"\bever[- ](?:evolving|changing)\b", 3, "drop it"),
        _t(r"\b(?:vibrant|bustling|nestled|boasts?)\b", 2, "plain verb, concrete detail"),
        _t(r"\bnot (?:just|only)\b[^.!?]{0,80}\bbut (?:also )?\b", 2, "state the claim once, directly"),
        _t(r"\b(?:in conclusion|to sum up|in summary|overall,)", 3, "end on the last real point, no recap"),
        _t(r"\bwhether you(?:'re| are)\b[^.!?]{0,60}\bor\b", 2, "address one reader, one case"),
        _t(r"\bstands? as a\b|\bserves? as a\b", 2, "say 'is'"),
        _t(r"\bat the end of the day\b|\bthe bottom line\b", 1, "drop it"),
        _t(r"\bI hope this (?:helps|finds you)\b|\bfeel free to\b", 2, "drop the assistant sign-off"),
    ),
    "ru": (
        _t(r"в (?:современном|наше|сегодняшнем) (?:мире|время|digital)[\w\s-]{0,30}", 3, "убрать вступление-декорацию"),
        _t(r"(?:стоит|важно|необходимо|следует|нужно) (?:отметить|подчеркнуть|помнить|учитывать),? (?:что)?", 3, "сказать сразу по сути"),
        _t(r"не секрет,? что|ни для кого не секрет", 3, "убрать"),
        _t(r"\bявля(?:ется|ются|лся|лась|лись)\b", 1, "заменить на тире или обычный глагол"),
        _t(r"играет?\s+(?:ключевую|важную|важнейшую|значительную)\s+роль", 3, "сказать, что именно он делает"),
        _t(r"(?:в заключение|подводя итог|резюмируя|таким образом),?", 3, "закончить последним фактом, без пересказа"),
        _t(r"в рамках\b", 2, "заменить на 'в', 'при', 'по'"),
        _t(r"\bсвоего рода\b|\bцелый ряд\b|\bшироки[йе] спектр\b", 2, "назвать конкретно"),
        _t(r"\b(?:уникальн\w+|бесшовн\w+|инновационн\w+|комплексн\w+ подход\w*)\b", 2, "дать конкретное свойство"),
        _t(r"\bпогрузитесь\b|\bоткройте для себя\b|\bоткрыва(?:ет|ют) новые (?:возможности|горизонты)\b", 3, "убрать рекламный зачин"),
        _t(r"\bидеальн\w+ (?:выбор|решение|вариант)\b", 2, "сказать, для кого и почему"),
        _t(r"не только\b[^.!?]{0,80}\bно и\b", 2, "сказать один раз, прямо"),
        _t(r"\bэто не просто\b[^.!?]{0,60}\bэто\b", 3, "убрать риторический контраст"),
        _t(r"\bпоистине\b|\bтщательно (?:продуман|отобран|подобран)\w*", 2, "убрать"),
        _t(r"\bв мире\b\s+\w+", 1, "назвать область прямо"),
        _t(r"\bосуществля(?:ть|ется|ют)\b|\bпроизвод(?:ить|ится)\b", 1, "обычный глагол вместо отглагольного"),
    ),
}

#: Words a sentence-opening repeat is not counted for (articles, single particles).
OPENER_STOP: Final[frozenset[str]] = frozenset(
    {"the", "a", "an", "и", "в", "на", "it", "this", "это", "он", "она", "они"}
)

EMOJI_RE: Final = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
