"""Offline tools for testing a chat kind: a scripted model, SSE parsing, a free pricer, a temporary registration.

A scripted model answers each model request from the next step, so a test fixes what the "model" says and calls and
asserts what the harness did with it. No network, no keys. Import from tests only.

Live tests (a real model, real money) are marked `@pytest.mark.live`; enable the marker handling with
`pytest_plugins = ["django_cfg.modules.django_llm.agent.chat.pytest_plugin"]` in the host's conftest.
"""

from __future__ import annotations

import asyncio
import dataclasses
import json
import os
from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import aclosing, contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart
from pydantic_ai.models import Model
from pydantic_ai.models.function import AgentInfo, DeltaToolCall, FunctionModel

from django_cfg.modules.django_llm.agent.bus.events import DoneEvent, ErrorEvent, TextDeltaEvent, UIPayloadEvent
from django_cfg.modules.django_llm.agent.chat import kind as kinds
from django_cfg.modules.django_llm.agent.chat.runner import kind_source
from django_cfg.modules.django_llm.agent.runtime.cost import Pricer, RunCost
from django_cfg.modules.django_llm.agent.runtime.streaming import StreamRunResult

FIXTURE = Path(__file__).resolve().parent.parent / "bus" / "tests" / "fixtures" / "events.json"
TRACE_FIXTURE = FIXTURE.with_name("events-trace.json")  # the optional trace frames: Python-first until the widget decodes them


@dataclass(frozen=True)
class Say:
    text: str
    chunk: int = 6  # characters per streamed delta


@dataclass(frozen=True)
class Call:
    tool: str
    args: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Boom:
    """The model request raises."""

    exc: BaseException


@dataclass(frozen=True)
class Hang:
    """The model request never answers (for timeout and cancel tests)."""


Step = Say | Call | Boom | Hang | list


class ScriptedModel(FunctionModel):
    """A `FunctionModel` that records what each request was sent in `requests` and the tools offered in `tools_offered`."""

    def __init__(self, steps: tuple[Step, ...]):
        self._steps = list(steps)
        self.requests: list[list[ModelMessage]] = []
        self.tools_offered: list[list[str]] = []  # per request: the tool names the model was offered
        super().__init__(function=self._call, stream_function=self._stream, model_name="scripted")

    async def _call(self, messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        """A non-streamed request (`agent.run`): the step's `Say` text, no tool calls. Raises a step's `Boom`."""
        self.requests.append(list(messages))
        self.tools_offered.append([t.name for t in info.function_tools])
        if len(self.requests) > len(self._steps):
            raise AssertionError(f"script exhausted: model request #{len(self.requests)} but {len(self._steps)} steps")
        step = self._steps[len(self.requests) - 1]
        items = step if isinstance(step, list) else [step]
        for item in items:
            if isinstance(item, Boom):
                raise item.exc
        return ModelResponse(parts=[TextPart("".join(i.text for i in items if isinstance(i, Say)))])

    async def _stream(self, messages: list[ModelMessage], info: AgentInfo) -> AsyncIterator[Any]:
        self.requests.append(list(messages))
        self.tools_offered.append([t.name for t in info.function_tools])
        if len(self.requests) > len(self._steps):
            raise AssertionError(f"script exhausted: model request #{len(self.requests)} but {len(self._steps)} steps")
        step = self._steps[len(self.requests) - 1]
        for i, item in enumerate(step if isinstance(step, list) else [step]):
            if isinstance(item, Say):
                for at in range(0, len(item.text), item.chunk):
                    yield item.text[at : at + item.chunk]
            elif isinstance(item, Call):
                yield {i: DeltaToolCall(name=item.tool, json_args=json.dumps(item.args), tool_call_id=f"call-{len(self.requests)}-{i}")}
            elif isinstance(item, Boom):
                raise item.exc
            elif isinstance(item, Hang):
                await asyncio.sleep(3600)


def scripted(*steps: Step) -> ScriptedModel:
    return ScriptedModel(steps)


def free_pricer(usage: Any, model: str) -> RunCost:
    """A pricer that never reaches the registry: 1 USD per million tokens."""
    tin, tout = int(getattr(usage, "input_tokens", 0) or 0), int(getattr(usage, "output_tokens", 0) or 0)
    return RunCost(tin, tout, (tin + tout) / 1_000_000, model)


def run_async(coro_fn: Callable[[], Any]) -> Any:
    """Run `async def` test code so that `sync_to_async` DB calls reuse the test's own connection and transaction."""
    from asgiref.sync import async_to_sync

    return async_to_sync(coro_fn)()


def collect(agen: AsyncIterator[Any]) -> list[Any]:
    async def go() -> list[Any]:
        return [item async for item in agen]

    return run_async(go)


def _data_of(block: str) -> str | None:
    for line in block.split("\n"):
        if line.startswith("data: "):
            return line[len("data: ") :]
    return None


def parse_sse(body: str | bytes) -> list[dict]:
    """Decoded `data:` frames of an SSE body; comments (pings) are skipped and an `id:` line is ignored."""
    text = body.decode() if isinstance(body, bytes) else body
    return [json.loads(data) for block in text.split("\n\n") if (data := _data_of(block)) is not None]


def sse_ids(body: str | bytes) -> list[int | None]:
    """The SSE `id:` of each data frame of a body, in order (None for a frame sent without one)."""
    text = body.decode() if isinstance(body, bytes) else body
    out: list[int | None] = []
    for block in text.split("\n\n"):
        if _data_of(block) is None:
            continue
        found = [line[4:].strip() for line in block.split("\n") if line.startswith("id: ")]
        out.append(int(found[0]) if found else None)
    return out


def fixture_frames() -> list[dict]:
    """The wire fixtures: the one shared with the widget (`events.json`) plus the trace frames (`events-trace.json`)."""
    frames = json.loads(FIXTURE.read_text())["frames"]
    return frames + json.loads(TRACE_FIXTURE.read_text())["frames"]


def assert_on_wire(frame: dict) -> None:
    """The frame has exactly the keys of a fixture frame of its type, with the same value types (None matches anything)."""
    twins = [f for f in fixture_frames() if f["type"] == frame["type"]]
    assert twins, f"no fixture frame of type {frame['type']!r}"
    assert any(_same_shape(frame, twin) for twin in twins), f"{frame} matches no fixture frame of its type"


def _same_shape(a: dict, b: dict) -> bool:
    if a.keys() != b.keys():
        return False
    return all(a[k] is None or b[k] is None or type(a[k]) is type(b[k]) or {type(a[k]), type(b[k])} <= {int, float} for k in a)


@contextmanager
def registered(*chat_kinds: kinds.ChatKind) -> Iterator[None]:
    for k in chat_kinds:
        kinds.register(k)
    try:
        yield
    finally:
        for k in chat_kinds:
            kinds.unregister(k.name)


@contextmanager
def override(name: str, **fields: Any) -> Iterator[kinds.ChatKind]:
    """Run with the registered kind `name` replaced by a copy with `fields` changed (`knowledge=None`, `limits=...`), then put
    the original back. `with override("film", knowledge=None): ...` proves "no knowledge, no kb tools" without touching the registry."""
    original = kinds.get(name)
    changed = dataclasses.replace(original, **fields)
    kinds.unregister(name)
    kinds.register(changed)
    try:
        yield changed
    finally:
        kinds.unregister(name)
        kinds.register(original)


def instructions_of(model: ScriptedModel, n: int = 0) -> str:
    """The system instructions the scripted model was sent on its `n`th request (what the kind said plus the knowledge block)."""
    for message in reversed(model.requests[n]):
        text = getattr(message, "instructions", None)
        if text:
            return text
    raise AssertionError(f"request #{n} carried no instructions")


def find_line(base: Any, path: str, needle: str) -> int:
    """The line number of the first line of `path` containing `needle`, for a citation test (`path:line`). Raises if absent."""
    start = 1
    while True:
        page = base.read(path, start)
        found = page.find_line(needle)
        if found is not None:
            return found
        if page.end >= page.total:
            raise AssertionError(f"{needle!r} is not in {path}")
        start = page.end + 1


# -- live tests: real models, run by hand ---------------------------------------------------------------------

LIVE_ENV = "ASSISTANT_LIVE"


def live_blocker() -> str | None:
    """Why a live test cannot run here, or `None`. Live tests cost money: they need `ASSISTANT_LIVE=1` AND a model key."""
    if os.environ.get(LIVE_ENV) != "1":
        return f"live model tests are off: set {LIVE_ENV}=1"
    from django_cfg.modules.django_llm import get_api_keys

    if not any(get_api_keys().values()):
        return "no model key: set OPENROUTER_API_KEY / API_KEYS__OPENROUTER (or the OpenAI one)"
    return None


@dataclass
class Answer:
    """One answer of a kind, run through the real loop: what was said, what was sent, and what it cost."""

    text: str
    payloads: list[dict]
    tool_calls: list[dict]
    tokens_in: int
    tokens_out: int
    cost_usd: float
    latency_ms: int
    error: str = ""


class Conversation:
    """A chat across turns without a database: keeps the history in the shape the service stores (as an app does)."""

    def __init__(self, chat_kind: kinds.ChatKind, model: Model, pricer: Pricer | None = free_pricer):
        self.kind, self.model, self.pricer = chat_kind, model, pricer
        self._turns: list[tuple[str, str, list[dict]]] = []  # (prompt, answer text, tool calls)

    def _history(self) -> list[dict]:
        window = self.kind.limits.replay_tool_calls_of
        out: list[dict] = []
        for i, (prompt, text, calls) in enumerate(self._turns):
            reply: dict = {"role": "assistant", "content": text}
            done = [c for c in calls if c.get("output") is not None]
            if done and i >= len(self._turns) - window:
                reply["tool_calls"] = done
            out += [{"role": "user", "content": prompt}, reply]
        return out

    def ask(self, deps: Any, text: str) -> Answer:
        async def go() -> Answer:
            return await self._ask(deps, text)

        return run_async(go)

    async def _ask(self, deps: Any, text: str) -> Answer:
        import time

        out = StreamRunResult()
        t0 = time.monotonic()
        source = kind_source(self.kind, deps, self._history(), text, model=self.model, out=out, pricer=self.pricer)
        said: list[str] = []
        payloads: list[dict] = []
        done: DoneEvent | None = None
        failed = ""
        async with aclosing(source):
            async for event in source:
                if isinstance(event, TextDeltaEvent):
                    said.append(event.delta)
                elif isinstance(event, UIPayloadEvent):
                    payloads.append({"kind": event.kind, "data": event.data})
                elif isinstance(event, DoneEvent):
                    done = event
                elif isinstance(event, ErrorEvent):
                    failed = event.code
        answer = "".join(said).strip()
        self._turns.append((text, answer, list(out.tool_calls)))
        return Answer(
            answer, payloads, list(out.tool_calls), (done.tokens_input or 0) if done else 0, (done.tokens_output or 0) if done else 0,
            float((done.cost_usd or 0) if done else 0), round((time.monotonic() - t0) * 1000), failed or ("" if done else "no done frame"),
        )


def update_baseline(path: Path, prompt_version: str, model: str, results: dict[str, list[bool]], cost_usd: float, when: str) -> dict:
    """Record pass counts under `prompt_version` x `model` (replacing that cell) and return the whole baseline."""
    data = json.loads(path.read_text()) if path.exists() else {}
    runs = max((len(v) for v in results.values()), default=0)
    data.setdefault(prompt_version, {})[model] = {
        "at": when, "runs": runs, "cost_usd": round(cost_usd, 4),
        "passed": sum(sum(v) for v in results.values()), "total": sum(len(v) for v in results.values()),
        "scenarios": {name: [sum(v), len(v)] for name, v in sorted(results.items())},
    }
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    return data
