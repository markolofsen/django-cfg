"""The task table — ONE place that says which models do which job.

A *task* is what a caller wants done (``extract``, ``translate``, ``ocr`` ...).
Callers name the task and never a model; the models live here and in the role
ladders of ``catalog/models.py`` (``_RECOMMENDED``). This file only wires the two
together and owns the override path:

    get_task_models("translate")   # -> ["openai/gpt-4o-mini", ...]

Two kinds of entry:

* **role tasks** (``extract``, ``classify``, ``translate``, ``judge``, ``chat``,
  ``escalate``, ``reply``) point at a ``ModelRole``; the chain is the role's
  ladder in ``catalog/models.py`` (so ``routing.presets`` and the task methods
  can never disagree).
* **plane tasks** (``ocr``, ``transcribe``, ``embed``, ``embed_quality``) have no
  ``ModelRole`` and carry their chain right here. The vision, transcribe and
  embeddings modules derive their defaults FROM these constants.

Override order, first hit wins (all optional, none needed):

1. ``set_task_models(task, [...])``                  runtime / tests
2. Django ``settings.DJANGO_LLM_TASKS``               THE documented per-project place
3. env ``DJANGO_LLM_TASKS`` (JSON) or ``DJANGO_LLM_TASK_<NAME>`` (comma list)
4. the table default below

``DJANGO_LLM_TASKS = {"translate": ["google/gemini-2.5-flash", "openai/gpt-4o-mini"]}``

An override REPLACES the chain (it is the caller's whole ordered ladder). A
retired ``@cf-*`` alias is refused loudly: aliases are gone, slugs are
``vendor/model`` OpenRouter ids.

Pure data layer: imports only ``catalog``; the Django settings read is lazy and
guarded, so the module still works with no Django installed.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Final, Iterable, Mapping

from .models import recommend
from .roles import ModelRole

logger = logging.getLogger(__name__)

# -- Plane chains (no ModelRole). The ONLY literal slugs outside catalog/models.py --

#: OCR / image reading. Checked against OpenRouter's catalogue 2026-11-10:
#: `qwen/qwen-2-vl-7b-instruct` and `meta-llama/llama-3.2-11b-vision-instruct`
#: were withdrawn (404), so a default is a dated fact and the rest are fallbacks
#: on other vendors.
OCR_MODELS: Final[tuple[str, ...]] = (
    "google/gemini-2.5-flash-lite",
    "openai/gpt-5-nano",
    "google/gemma-3-12b-it",
)

#: Audio transcription: cheapest first, a different vendor each step, because
#: content filters differ by vendor. Bench: `features/transcribe/defaults.py`.
TRANSCRIBE_MODELS: Final[tuple[str, ...]] = (
    "qwen/qwen3.8-omni-flash",
    "openai/gpt-audio-mini",
    "google/gemini-3.5-flash-lite",
    "google/gemini-3.1-flash-lite",
)

EMBED_FAST_MODELS: Final[tuple[str, ...]] = ("openai/text-embedding-3-small",)
EMBED_QUALITY_MODELS: Final[tuple[str, ...]] = ("openai/text-embedding-3-large",)
EMBEDDING_DIMENSIONS: Final = 1536


@dataclass(frozen=True)
class TaskSpec:
    """One row of the table."""

    name: str
    kind: str                                  # structured | text | embedding | vision | audio
    doc: str
    role: ModelRole | None = None              # ladder lives in catalog/models.py
    models: tuple[str, ...] = ()               # plane tasks: the chain itself
    max_tokens: int = 4096                     # default completion budget (reasoning floor is automatic per slug)
    strict_json: bool = False                  # provider-enforced json_schema output
    params: Mapping[str, object] = field(default_factory=dict)

    def default_models(self) -> list[str]:
        if self.role is not None:
            return recommend(self.role)
        return list(self.models)


TASKS: Final[Mapping[str, TaskSpec]] = MappingProxyType({
    s.name: s for s in (
        TaskSpec(name="extract", kind="structured", role=ModelRole.EXTRACTION, strict_json=True, max_tokens=4096,
                 doc="Pull a pydantic schema out of text."),
        TaskSpec(name="classify", kind="structured", role=ModelRole.CLASSIFY, strict_json=True, max_tokens=1024,
                 doc="Cheap labelling into an enum / small schema."),
        TaskSpec(name="translate", kind="text", role=ModelRole.TRANSLATE, max_tokens=2048,
                 doc="Faithful translation of listing text or UI strings."),
        TaskSpec(name="judge", kind="structured", role=ModelRole.JUDGE, strict_json=True, max_tokens=2000,
                 doc="Adjudication: pick the matching candidate or none, with a reason."),
        TaskSpec(name="chat", kind="text", role=ModelRole.TOOL_CHAT, max_tokens=4096,
                 doc="General assistant turn / multi-tool chat."),
        TaskSpec(name="escalate", kind="text", role=ModelRole.ESCALATION, max_tokens=4096,
                 doc="Quality-over-cost completion for hard or customer-facing turns."),
        TaskSpec(name="reply", kind="text", role=ModelRole.REPLY, max_tokens=4096,
                 doc="Email reply from private text (zero-retention endpoints only); used by the agent harness."),
        TaskSpec(name="ocr", kind="vision", models=OCR_MODELS, max_tokens=1500,
                 doc="Text of an image held in memory."),
        TaskSpec(name="transcribe", kind="audio", models=TRANSCRIBE_MODELS,
                 doc="Speech to text through chat models that accept input_audio."),
        TaskSpec(name="embed", kind="embedding", models=EMBED_FAST_MODELS,
                 params={"dimensions": EMBEDDING_DIMENSIONS}, doc="Default embedding, 1536-dim."),
        TaskSpec(name="embed_quality", kind="embedding", models=EMBED_QUALITY_MODELS,
                 params={"dimensions": EMBEDDING_DIMENSIONS}, doc="High-precision embedding, 1536-dim."),
    )
})

#: Reverse map used by `LLMRouter.for_role`, so the legacy role entry points
#: (`routing.presets`) honour the same overrides as the task methods.
TASK_FOR_ROLE: Final[Mapping[ModelRole, str]] = MappingProxyType({
    s.role: s.name for s in TASKS.values() if s.role is not None
})

# -- Overrides ------------------------------------------------------------------

_runtime: dict[str, list[str]] = {}
_lock = threading.Lock()


def _normalize(task: str, value: object) -> list[str]:
    """``"a, b"`` or ``["a", "b"]`` -> validated slug list."""
    if isinstance(value, str):
        items: Iterable = [p.strip() for p in value.replace(";", ",").split(",")]
    elif isinstance(value, (list, tuple)):
        items = [str(p).strip() for p in value]
    else:
        raise ValueError(
            f"DJANGO_LLM_TASKS[{task!r}] must be a list of slugs or a comma string, got {type(value).__name__}"
        )
    chain = [s for s in items if s]
    if not chain:
        raise ValueError(f"DJANGO_LLM_TASKS[{task!r}] is empty")
    for slug in chain:
        if slug.startswith("@") or "/" not in slug:
            raise ValueError(
                f"DJANGO_LLM_TASKS[{task!r}]: {slug!r} is not an OpenRouter slug "
                f"('vendor/model'); the @cf-* aliases were retired 2026-11-10"
            )
    return list(dict.fromkeys(chain))


def _settings_overrides() -> Mapping[str, object]:
    """``settings.DJANGO_LLM_TASKS`` if Django is importable and configured, else {}.

    The one lazy touch of Django in the transport plane; guarded so a Django-less
    process (a script, a test) just gets no override.
    """
    try:
        from django.conf import settings  # noqa: PLC0415

        value = getattr(settings, "DJANGO_LLM_TASKS", None)
    except Exception:  # noqa: BLE001 - not installed / settings not configured
        return {}
    return value if isinstance(value, Mapping) else {}


def _env_override(task: str) -> object | None:
    per_task = os.environ.get(f"DJANGO_LLM_TASK_{task.upper()}")
    if per_task:
        return per_task
    raw = os.environ.get("DJANGO_LLM_TASKS")
    if raw:
        try:
            data = json.loads(raw)
        except ValueError:
            logger.error("DJANGO_LLM_TASKS env is not valid JSON; ignored")
            return None
        if isinstance(data, dict):
            return data.get(task)
    return None


def set_task_models(task: str, models: list[str] | str | None) -> None:
    """Override (or, with ``None``, clear the override of) ``task`` for this process."""
    get_task_spec(task)
    with _lock:
        if models is None:
            _runtime.pop(task, None)
        else:
            _runtime[task] = _normalize(task, models)


def reset_task_overrides() -> None:
    """Drop every runtime override (tests)."""
    with _lock:
        _runtime.clear()


def get_task_spec(task: str) -> TaskSpec:
    try:
        return TASKS[task]
    except KeyError:
        raise KeyError(f"unknown LLM task {task!r}; known: {', '.join(sorted(TASKS))}") from None


def get_task_models(task: str) -> list[str]:
    """The ordered OpenRouter slug chain for ``task``: override, else table default."""
    spec = get_task_spec(task)
    with _lock:
        runtime = _runtime.get(task)
    if runtime:
        return list(runtime)
    configured = _settings_overrides().get(task)
    if configured is None:
        configured = _env_override(task)
    if configured is not None:
        return _normalize(task, configured)
    return spec.default_models()


def task_chain_for_role(role: ModelRole) -> list[str]:
    """Chain for a role, honouring the task override (``LLMRouter.for_role`` uses this)."""
    task = TASK_FOR_ROLE.get(role)
    return get_task_models(task) if task else recommend(role)


__all__ = [
    "EMBEDDING_DIMENSIONS", "EMBED_FAST_MODELS", "EMBED_QUALITY_MODELS", "OCR_MODELS",
    "TASKS", "TASK_FOR_ROLE", "TRANSCRIBE_MODELS", "TaskSpec",
    "get_task_models", "get_task_spec", "reset_task_overrides", "set_task_models", "task_chain_for_role",
]
