"""The task methods. Chains come from ``catalog/tasks.py``; nothing here names a model."""

from __future__ import annotations

import asyncio
import functools
import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, Iterator, Literal, Sequence, TypeVar

from pydantic import BaseModel, Field, create_model

from ..catalog import ModelRole
from ..catalog.tasks import get_task_models, get_task_spec
from ..routing.llm_router import LLMRouter

T = TypeVar("T")
M = TypeVar("M", bound=BaseModel)


@dataclass(frozen=True)
class TaskResult(Generic[T]):
    """What a task method returns: the value and WHO produced it.

    Unpacks as ``(value, model, usage)`` to match ``routing.presets``.
    """

    value: T
    model: str
    usage: dict = field(default_factory=dict)
    task: str = ""

    def __iter__(self) -> Iterator[Any]:
        yield self.value
        yield self.model
        yield self.usage

    @property
    def cost_usd(self) -> float:
        return float((self.usage or {}).get("cost_usd") or 0.0)


# -- routers --------------------------------------------------------------------

@functools.lru_cache(maxsize=64)
def _router_for(chain: tuple[str, ...], role: ModelRole | None) -> LLMRouter:
    """One router per distinct chain (building one loads the catalogue and opens clients)."""
    return LLMRouter(list(chain), role=role)


def _router(task: str, models: Sequence[str] | None) -> LLMRouter:
    spec = get_task_spec(task)
    chain = tuple(models) if models else tuple(get_task_models(task))
    return _router_for(chain, spec.role)


def _budget(task: str, max_tokens: int | None) -> int:
    return max_tokens if max_tokens is not None else get_task_spec(task).max_tokens


def _parse(task: str, schema: type[M], messages: list[dict], system: str | None,
           max_tokens: int | None, models: Sequence[str] | None) -> TaskResult[M]:
    parsed, model, usage = _router(task, models).parse(
        schema=schema, messages=messages, system=system, max_tokens=_budget(task, max_tokens),
    )
    return TaskResult(parsed, model, usage, task)


def _complete(task: str, messages: list[dict], system: str | None,
              max_tokens: int | None, models: Sequence[str] | None) -> TaskResult[str]:
    # The usage carries the bill: `humanize`, `translate` and `chat` reported $0 while it was dropped here.
    text, model, usage = _router(task, models).complete_with_usage(
        messages=messages, system=system, max_tokens=_budget(task, max_tokens),
    )
    return TaskResult(text, model, usage, task)


# -- extract / classify / judge (strict-json) ---------------------------------------

def _humanize_ask(messages: list[dict], system: str, budget: int | None, chain: Sequence[str] | None) -> TaskResult[str]:
    return _complete("humanize", messages, system, budget, chain)


def _humanize_fields(res: TaskResult[M], defaults: dict[str, Any]) -> TaskResult[M]:
    """Rewrite the schema's ``Humanize``-marked fields of an already-parsed answer."""
    from ..features.humanize import apply_humanize  # lazy

    failed: dict[str, str] = {}
    value, results = apply_humanize(res.value, _humanize_ask, defaults=defaults,
                                    on_error=lambda where, exc: failed.__setitem__(where, repr(exc)))
    cost = sum(r.cost_usd for r in results.values())
    usage = dict(res.usage or {})
    usage["cost_usd"] = float(usage.get("cost_usd") or 0.0) + cost
    usage["humanize"] = {
        "fields": {w: {"ok": r.ok, "changed": r.changed, "before": r.before.score, "after": r.after.score,
                       "reason": r.reason} for w, r in results.items()},
        "errors": failed,
    }
    return TaskResult(value, res.model, usage, res.task)


def extract(schema: type[M], text: str, *, system: str | None = None, max_tokens: int | None = None,
            messages: list[dict] | None = None, models: Sequence[str] | None = None,
            humanize: bool | None = None, humanize_options: dict[str, Any] | None = None) -> TaskResult[M]:
    """Structured extraction of ``schema`` from ``text`` (or a full ``messages`` list). ``models`` pins a chain for this call only.

    Fields declared ``Annotated[str, Humanize(...)]`` (also ``list[str]``, nested models) are rewritten after
    parsing; ``humanize=False`` skips that, ``humanize_options`` sets defaults (``voice``, ``domain``,
    ``strength``, ``lang``) for fields that do not name their own. Per-field outcomes are in
    ``result.usage["humanize"]``; a field whose rewrite is unfaithful keeps the extracted text.
    """
    res = _parse("extract", schema, messages or [{"role": "user", "content": text}], system, max_tokens, models)
    if humanize is not False:
        from ..features.humanize import has_marked_fields  # lazy

        if has_marked_fields(schema):
            return _humanize_fields(res, humanize_options or {})
    return res


def classify(text: str, labels: Sequence[str] | None = None, *, schema: type[M] | None = None,
             system: str | None = None, max_tokens: int | None = None,
             models: Sequence[str] | None = None) -> TaskResult[Any]:
    """Classify ``text``: ``labels=[...]`` returns the chosen label string; ``schema=`` returns that model instance."""
    if (labels is None) == (schema is None):
        raise ValueError("classify needs exactly one of labels= or schema=")
    if labels is not None:
        uniq = tuple(dict.fromkeys(labels))
        if len(uniq) < 2:
            raise ValueError("classify needs at least two distinct labels")
        label_schema = create_model("Label", label=(Literal[uniq], ...))  # type: ignore[valid-type]
        system = system or f"Classify the text into exactly one of: {', '.join(uniq)}. Answer with the label only."
        res = _parse("classify", label_schema, [{"role": "user", "content": text}], system, max_tokens, models)
        return TaskResult(res.value.label, res.model, res.usage, "classify")
    return _parse("classify", schema, [{"role": "user", "content": text}], system, max_tokens, models)


class _Choice(BaseModel):
    choice: int | None = Field(description="1-based number of the matching candidate, or null when none matches")
    reason: str = Field(description="one short sentence")


@dataclass(frozen=True)
class JudgeVerdict:
    """``index`` is 0-based into ``candidates``; ``None`` means no candidate matches."""

    index: int | None
    candidate: str | None
    reason: str


_JUDGE_SYSTEM = (
    "You adjudicate. Given a question and a numbered list of candidates, answer with the number of the single "
    "candidate that is the right answer, or null when none is. Be conservative: null beats a doubtful match."
)


def judge(question: str, candidates: Sequence[str], *, system: str | None = None,
          max_tokens: int | None = None, models: Sequence[str] | None = None) -> TaskResult[JudgeVerdict]:
    """Pick the candidate that answers ``question`` (or none). The adjudication pattern."""
    items = list(candidates)
    if not items:
        return TaskResult(JudgeVerdict(None, None, "no candidates"), "", {}, "judge")
    listing = "\n".join(f"{i}. {c}" for i, c in enumerate(items, start=1))
    prompt = f"{question}\n\nCandidates:\n{listing}"
    res = _parse("judge", _Choice, [{"role": "user", "content": prompt}], system or _JUDGE_SYSTEM, max_tokens, models)
    pick = res.value.choice
    idx = pick - 1 if isinstance(pick, int) and 1 <= pick <= len(items) else None
    verdict = JudgeVerdict(idx, items[idx] if idx is not None else None, res.value.reason)
    return TaskResult(verdict, res.model, res.usage, "judge")


# -- text tasks -------------------------------------------------------------------------

def translate(text: str, target: str, source: str | None = None, domain: str | None = None, *,
              system: str | None = None, max_tokens: int | None = None,
              models: Sequence[str] | None = None) -> TaskResult[str]:
    """Translate ``text`` into ``target`` (language name or ISO code); ``domain`` names the subject so short values are read in context."""
    if not text or not text.strip():
        return TaskResult(text, "", {}, "translate")
    src = f" from {source}" if source else ""
    ctx = f" The text comes from: {domain}. Use that domain's standard terminology." if domain else ""
    sys_prompt = system or (
        f"You are a professional translator. Translate the user's text{src} into {target}.{ctx} "
        "Preserve numbers, URLs, units and formatting. Return ONLY the translation, no comments."
    )
    res = _complete("translate", [{"role": "user", "content": text}], sys_prompt, max_tokens, models)
    return TaskResult(res.value.strip(), res.model, res.usage, "translate")


def humanize(text: str, *, lang: str | None = None, voice: str | None = None, domain: str | None = None,
             strength: str = "medium", rounds: int = 2, target: float = 25.0, keep: Sequence[str] = (),
             force: bool = False, max_tokens: int | None = None,
             models: Sequence[str] | None = None) -> TaskResult[Any]:
    """Rewrite ``text`` so it stops reading as machine-written. ``value`` is a ``HumanizeResult``.

    ``.value.text`` is the text to publish: the rewrite when it kept every number, URL and name of
    the source, otherwise the source itself (``.value.ok`` is False). Text already under ``target``
    (local score 0-100, higher = more machine-like) costs no call unless ``force``. ``keep`` names
    extra strings that must survive. See ``@docs/humanize.md``.
    """
    from ..features.humanize import humanize as _humanize  # lazy

    result = _humanize(text, _humanize_ask, lang=lang, voice=voice, domain=domain, strength=strength,  # type: ignore[arg-type]
                       rounds=rounds, target=target, keep=keep, force=force, max_tokens=max_tokens, models=models)
    model = result.models[-1] if result.models else ""
    return TaskResult(result, model, {"cost_usd": result.cost_usd}, "humanize")


def chat(messages: list[dict], *, system: str | None = None, max_tokens: int | None = None,
         models: Sequence[str] | None = None) -> TaskResult[str]:
    """A general assistant turn (the multi-tool-chat ladder). Returns the text."""
    return _complete("chat", messages, system, max_tokens, models)


def escalate(messages: list[dict], *, system: str | None = None, max_tokens: int | None = None,
             models: Sequence[str] | None = None) -> TaskResult[str]:
    """Quality-over-cost turn, for what a cheaper model got wrong."""
    return _complete("escalate", messages, system, max_tokens, models)


# -- embeddings --------------------------------------------------------------------------

def embed(texts: str | list[str], *, quality: bool = False) -> TaskResult[Any]:
    """Embed one text (-> ``list[float]``) or a list (-> ``list[list[float]]``), 1536-dim.

    Walks the task chain on an exception; an empty vector means "no embedding" (empty
    input, or no provider key) exactly as in ``features.embeddings``.
    """
    from ..features.embeddings import embed_texts  # lazy: pulls LLMClient

    task = "embed_quality" if quality else "embed"
    dims = get_task_spec(task).params.get("dimensions")
    batch = [texts] if isinstance(texts, str) else list(texts)
    last: Exception | None = None
    for model in get_task_models(task):
        try:
            vectors = embed_texts(batch, model=model, dimensions=dims)  # type: ignore[arg-type]
        except Exception as exc:  # noqa: BLE001 - next model in the chain
            last = exc
            continue
        return TaskResult(vectors[0] if isinstance(texts, str) else vectors, model, {}, task)
    assert last is not None
    raise last


# -- vision (OCR) -----------------------------------------------------------------------

async def aocr(data: bytes, mime: str = "image/png", *, mode: str = "base", query: str | None = None,
               max_tokens: int | None = None, client: Any = None,
               models: Sequence[str] | None = None) -> TaskResult[str]:
    """Text of an image held in memory (bytes travel as a data URL, no public address)."""
    from ..features.vision.read_text import aread_image_text  # lazy: pulls Pillow

    chain = list(models) if models else get_task_models("ocr")
    last: Exception | None = None
    for model in chain:
        try:
            text = await aread_image_text(
                data, mime, query=query, mode=mode, model=model,  # type: ignore[arg-type]
                max_tokens=_budget("ocr", max_tokens), client=client,
            )
        except Exception as exc:  # noqa: BLE001 - next vendor
            last = exc
            continue
        return TaskResult(text, model, {}, "ocr")
    assert last is not None
    raise last


# -- audio ------------------------------------------------------------------------------

def _openrouter_call() -> Callable[[str, dict], Any]:
    """``call(path, payload)`` over the OpenRouter client; failures carry ``.status`` for the transcribe classifier."""
    from ..client import LLMClient

    client = LLMClient().provider_manager.get_client("openrouter")

    def call(path: str, payload: dict) -> Any:
        try:
            return client.post(path, body=payload, cast_to=object)
        except Exception as exc:  # noqa: BLE001
            status = getattr(exc, "status_code", None)
            if isinstance(status, int):
                exc.status = status  # type: ignore[attr-defined]
            raise

    return call


def transcribe(audio: bytes, *, audio_format: str = "mp3", duration_s: float | None = None,
               context: str = "", ask: Any = None, models: Sequence[str] | None = None) -> TaskResult[Any]:
    """Transcribe one recording piece. ``value`` is the transcribe ``Result`` (``.text``, ``.gaps``, ``.cost_usd``).

    For long audio cut it yourself and use ``features.transcribe.transcribe`` with
    ``get_task_models("transcribe")``; this is the one-piece convenience. ``ask`` injects the transport (tests).
    """
    from ..features.transcribe import ChainEntry, Policy, make_ask, transcribe_range

    chain = [ChainEntry(m) for m in (models or get_task_models("transcribe"))]
    result = transcribe_range(
        0.0, float(duration_s or 1.0), lambda _offset, _seconds: audio,
        ask or make_ask(_openrouter_call(), audio_format=audio_format), chain,
        policy=Policy(chunk_s=max(float(duration_s or 1.0), 1.0), rounds=2, pause_s=1.0), context=context,
    )
    return TaskResult(result, (result.models or [""])[-1], {"cost_usd": float(result.cost_usd)}, "transcribe")


# -- async twins (sync cascade on a worker thread: one source of truth) ------------------

def _twin(fn: Callable[..., Any], name: str) -> Callable[..., Any]:
    @functools.wraps(fn)
    async def inner(*args: Any, **kwargs: Any) -> Any:
        return await asyncio.to_thread(fn, *args, **kwargs)

    inner.__name__ = name
    inner.__qualname__ = name
    inner.__doc__ = f"Async ``{fn.__name__}`` (awaits it on a worker thread)."
    return inner


aextract = _twin(extract, "aextract")
aclassify = _twin(classify, "aclassify")
ajudge = _twin(judge, "ajudge")
atranslate = _twin(translate, "atranslate")
achat = _twin(chat, "achat")
ahumanize = _twin(humanize, "ahumanize")
aescalate = _twin(escalate, "aescalate")
aembed = _twin(embed, "aembed")
atranscribe = _twin(transcribe, "atranscribe")


def ocr(data: bytes, mime: str = "image/png", **kwargs: Any) -> TaskResult[str]:
    """Sync ``aocr`` (runs its own event loop on a private thread, safe inside a running loop)."""
    box: dict[str, Any] = {}

    def run() -> None:
        try:
            box["ok"] = asyncio.run(aocr(data, mime, **kwargs))
        except BaseException as exc:  # noqa: BLE001
            box["err"] = exc

    thread = threading.Thread(target=run)
    thread.start()
    thread.join()
    if "err" in box:
        raise box["err"]
    return box["ok"]
