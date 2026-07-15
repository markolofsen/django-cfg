"""Universal LLM-job lifecycle enum.

Every LLM-driven workflow in this project (ai_photo edits,
normalizer runs, future vision/extract jobs) goes through the same
states: ``pending`` → ``processing`` → ``terminal``. Having one enum
keeps admin filters, polling endpoints, and metric dashboards
consistent across apps.

Specialised middle states (e.g. ai_photo distinguishes ``analyzing``
from ``generating``) can be added per-app via subclassing or by
treating ``processing`` as a parent of both. Most consumers only
care about the terminal taxonomy, which IS standardised here:

  ``completed`` — success; output persisted
  ``skipped``   — declined by policy (analyzer said "no edit needed")
  ``refused``   — declined by the model (safety / no image returned)
  ``failed``    — transport or validation error
"""

from __future__ import annotations

from enum import StrEnum

# Ported from Django's TextChoices → stdlib StrEnum (plan50 §12). The human
# labels TextChoices carried were only for Django admin; dropped here. `.value`
# and string-equality behave the same.


class LLMJobStatus(StrEnum):
    """Lifecycle states for any LLM-driven job."""

    PENDING = "pending"
    PROCESSING = "processing"

    # ── terminal ──
    COMPLETED = "completed"
    SKIPPED = "skipped"
    REFUSED = "refused"
    FAILED = "failed"

    @classmethod
    def terminal_values(cls) -> frozenset[str]:
        return frozenset({
            cls.COMPLETED.value,
            cls.SKIPPED.value,
            cls.REFUSED.value,
            cls.FAILED.value,
        })

    @classmethod
    def is_terminal(cls, value: str) -> bool:
        return value in cls.terminal_values()
