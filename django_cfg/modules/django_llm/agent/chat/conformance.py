"""Conformance of a host's `ChatService` to the chat contract: one import, one class, a drift fails in the host's CI.

    from django_cfg.modules.django_llm.agent.chat import conformance
    from apps.chat.service import service

    class TestChatConformance(conformance.ServiceConformance):
        service = service            # the host's ChatService
        kinds = ("film",)            # the registered kinds to drive
        # optional: user_factory, contexts, models = conformance.scripted(...), check_migrations

Everything runs offline: the service's `model_factory` and `pricer` are replaced by a scripted model and a free pricer for the
duration of each test (and put back), uploads go to a temporary storage, the routes are mounted from `urls(service)` under
a private URL module. The host's own settings, auth classes and database are used as they are, so the service must be
"available" in tests. A host passes `contexts={kind: {...}}` when a kind needs a context: it is sent when the thread is created
and with every message.

What is checked (one test method each): the signatures the kit's views call, a send through the routes, attachments, the
trace, the `on_turn` hook, follow/resume/cancel/live, tenancy and refusals, the OpenAPI operations, and that the host's migrations cover the
abstract models' columns (`missing_migrations`). Docs: `@docs/extending.md`, "Conformance".
"""

from __future__ import annotations

import ast
import inspect
import io
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any, ClassVar

import pytest

from django_cfg.modules.django_llm.agent.chat import kind as kinds_registry
from django_cfg.modules.django_llm.agent.chat.testing import Hang, Say, assert_on_wire, free_pricer, parse_sse, run_async, scripted as scripted_model, sse_ids

__all__ = ["ServiceConformance", "missing_migrations", "scripted", "view_calls"]

BASE = "/apix/conformance/"
PREFIX = "conformance"

# The operation ids the kit mounts, without the host's prefix: pinned against `tests/snapshots/chat_api_openapi.json` by the framework's own suite.
OPERATIONS = {
    ("threads/", "get"): "threads_list",
    ("threads/", "post"): "threads_create",
    ("threads/{thread_id}/", "get"): "threads_retrieve",
    ("threads/{thread_id}/messages/", "post"): "messages_create",
    ("threads/{thread_id}/messages/{message_id}/stream/", "get"): "messages_stream",
    ("threads/{thread_id}/messages/{message_id}/cancel/", "post"): "messages_cancel",
    ("threads/{thread_id}/messages/{message_id}/parts/{index}/ack/", "post"): "parts_ack",
}
ATTACHMENT_OPERATIONS = {
    ("attachments/", "post"): "attachments_create",
    ("attachments/limits/", "get"): "attachments_limits",
    ("attachments/{attachment_id}/", "delete"): "attachments_destroy",
    ("attachments/{attachment_id}/content/", "get"): "attachments_content",
}


def scripted(*steps: Any) -> staticmethod:
    """`models = conformance.scripted(Say("hi"))`: every turn is answered by a fresh scripted model with these steps."""
    return staticmethod(lambda chat_kind: scripted_model(*steps))


# -- the calls the views make --------------------------------------------------------------------------

def view_calls() -> list[tuple[str, int, tuple[str, ...]]]:
    """`(method, positional count, keyword names)` of every `self.service.<method>(...)` call in `api/views.py`, read from its source,
    so an argument added to a view fails the host's check the day it is added. Calls with `*args` or `**kwargs` are left out."""
    from django_cfg.modules.django_llm.agent.chat.api import views

    tree = ast.parse(Path(views.__file__).read_text())
    found: list[tuple[str, int, tuple[str, ...]]] = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        owner = node.func.value
        if not (isinstance(owner, ast.Attribute) and owner.attr == "service" and isinstance(owner.value, ast.Name) and owner.value.id == "self"):
            continue
        if any(isinstance(a, ast.Starred) for a in node.args) or any(k.arg is None for k in node.keywords):
            continue
        found.append((node.func.attr, len(node.args), tuple(k.arg for k in node.keywords)))
    return found


# -- migrations ----------------------------------------------------------------------------------------

def missing_migrations(*app_labels: str) -> list[str]:
    """What `makemigrations` would still write for these apps, one line each; empty when the migrations cover the models.

    A host that subclasses the abstract chat models owns a migration for every column the framework adds (`trace` is
    `0007_message_trace` in the hosts that adopted it). An app with no migrations at all is reported as one line.
    """
    from django.apps import apps
    from django.db.migrations.autodetector import MigrationAutodetector
    from django.db.migrations.loader import MigrationLoader
    from django.db.migrations.questioner import NonInteractiveMigrationQuestioner
    from django.db.migrations.state import ProjectState

    labels = set(app_labels)
    loader = MigrationLoader(None, ignore_no_migrations=True)
    lines = [f"{label}: the app has no migrations" for label in sorted(labels - loader.migrated_apps)]
    detector = MigrationAutodetector(loader.project_state(), ProjectState.from_apps(apps), NonInteractiveMigrationQuestioner(specified_apps=labels, dry_run=True))
    for label, migrations in detector.changes(graph=loader.graph, trim_to_apps=labels & loader.migrated_apps).items():
        lines += [f"{label}: {operation.describe()}" for migration in migrations for operation in migration.operations]
    return lines


# -- the test class ------------------------------------------------------------------------------------

@pytest.mark.django_db
class ServiceConformance:
    """Subclass as `Test<Something>Conformance` in the host's tests; set `service` and `kinds`."""

    service: ClassVar[Any]  # the host's ChatService
    kinds: ClassVar[tuple[str, ...]]  # registered kind names to drive
    contexts: ClassVar[dict[str, dict]] = {}  # per kind: the context its threads need; sent when the thread is created and with every message
    user_factory: ClassVar[Callable[[str], Any] | None] = None  # `user_factory("name") -> user`; default: `create_user` with a name and an email
    models: ClassVar[Any] = None  # `conformance.scripted(...)` or `staticmethod(lambda chat_kind: model)`; default: a one-line scripted answer
    text: ClassVar[str] = "hello"
    check_migrations: ClassVar[bool] = True

    # -- plumbing ----------------------------------------------------------------------------------------

    @pytest.fixture(autouse=True)
    def _conformance_env(self, db, tmp_path):
        from django.conf import settings
        from django.test import override_settings
        from rest_framework.test import APIClient

        service = self.service
        saved = (service.model_factory, service.pricer)
        service.model_factory = self._model_for
        service.pricer = free_pricer
        storages = {**getattr(settings, "STORAGES", {}), "default": {"BACKEND": "django.core.files.storage.FileSystemStorage", "OPTIONS": {"location": str(tmp_path)}}}
        try:
            with override_settings(ROOT_URLCONF=self._mount(), STORAGES=storages):
                self.owner = self._user("owner")
                self.stranger_user = self._user("stranger")
                self.client = APIClient()
                self.client.raise_request_exception = False  # a crashing view is a 500 to assert on, not a traceback
                self.client.force_authenticate(self.owner)
                self.stranger = APIClient()
                self.stranger.raise_request_exception = False
                self.stranger.force_authenticate(self.stranger_user)
                self.anonymous = APIClient()
                self.anonymous.raise_request_exception = False
                yield
        finally:
            service.model_factory, service.pricer = saved

    def _mount(self) -> str:
        import sys
        import types

        from django.urls import include, path

        from django_cfg.modules.django_llm.agent.chat.api import urls

        name = f"_chat_conformance_{uuid.uuid4().hex}"
        module = types.ModuleType(name)
        module.urlpatterns = [path(BASE.lstrip("/"), include((urls(self.service, operation_id_prefix=PREFIX, tag=PREFIX), PREFIX)))]
        sys.modules[name] = module
        return name

    def _model_for(self, chat_kind):
        factory = inspect.getattr_static(type(self), "models")
        factory = factory.__func__ if isinstance(factory, staticmethod) else factory
        return factory(chat_kind) if factory is not None else scripted_model(Say("hello back"))

    def _user(self, name: str):
        if self.user_factory is not None:
            factory = inspect.getattr_static(type(self), "user_factory")
            return (factory.__func__ if isinstance(factory, staticmethod) else factory)(name)
        from django.contrib.auth import get_user_model

        unique = f"conf-{name}-{uuid.uuid4().hex[:8]}"
        return get_user_model().objects.create_user(username=unique, email=f"{unique}@example.test", password="pw-for-conformance")

    def _kind(self, name: str):
        try:
            return kinds_registry.get(name)
        except kinds_registry.UnknownKind:
            pytest.fail(f"kind {name!r} is not registered: import the module that registers it before the test, or fix `kinds`")

    def _new_thread(self, kind: str, client=None) -> str:
        body: dict[str, Any] = {"kind": kind}
        if self.contexts.get(kind):
            body["context"] = self.contexts[kind]  # a kind that refuses a thread without its context (a document, a film) is created with it
        r =(client or self.client).post(f"{BASE}threads/", body, format="json")
        assert r.status_code == 201, f"[{kind}] POST threads/ answered {r.status_code}: {r.content[:300]!r}"
        return r.json()["id"]

    def _send(self, thread_id: str, kind: str, client=None, **extra):
        body = {"text": self.text, "client_id": str(uuid.uuid4()), "context": self.contexts.get(kind, {}), "attachments": [], **extra}
        return (client or self.client).post(f"{BASE}threads/{thread_id}/messages/", body, format="json", HTTP_ACCEPT="text/event-stream")

    @staticmethod
    def _body(response) -> str:
        async def go():
            return b"".join([chunk async for chunk in response]).decode()

        return run_async(go)

    def _answer(self, kind: str, **extra) -> tuple[str, str, str]:
        """Send one message through the route: (thread id, answer message id, raw body). Fails unless it streamed 200."""
        thread_id = self._new_thread(kind)
        response = self._send(thread_id, kind, **extra)
        assert response.status_code == 200, f"[{kind}] send answered {response.status_code}: {response.content[:300]!r}"
        assert response["Content-Type"].startswith("text/event-stream"), f"[{kind}] send answered {response['Content-Type']}"
        body = self._body(response)
        run = parse_sse(body)[0]
        return thread_id, run["message_id"], body

    # -- 1. signatures -----------------------------------------------------------------------------------

    def test_service_methods_accept_the_calls_the_views_make(self):
        calls = view_calls()
        seen = {name for name, _, _ in calls}
        assert {"begin", "frames", "attach", "cancel"} <= seen, f"the views no longer call begin/frames/attach/cancel as `self.service.<m>(...)` (found {sorted(seen)}): update `view_calls`"
        for name, count, keywords in calls:
            method = getattr(self.service, name, None)
            assert callable(method), f"{type(self.service).__qualname__} has no method {name!r} that the views call"
            try:
                inspect.signature(method).bind(*[object()] * count, **{k: object() for k in keywords})
            except TypeError as err:
                pytest.fail(f"{type(self.service).__qualname__}.{name}() cannot be called as the views call it ({count} positional, keywords {list(keywords)}): {err}")

    # -- 2. send -----------------------------------------------------------------------------------------

    def test_a_send_streams_run_first_and_done_last_with_wire_frames(self):
        for kind in self.kinds:
            self._kind(kind)
            _, _, body = self._answer(kind)
            frames = parse_sse(body)
            for frame in frames:
                assert_on_wire(frame)
            assert frames[0]["type"] == "run" and frames[-1]["type"] == "done", f"[{kind}] frames: {[f['type'] for f in frames]}"

    def test_on_turn_runs_once_per_new_turn_with_the_stored_message(self, monkeypatch):
        import dataclasses

        for name in self.kinds:
            chat_kind = self._kind(name)
            if chat_kind.on_turn is None:
                continue
            calls: list = []

            def spy(deps, turn, _real=chat_kind.on_turn, _calls=calls):
                _calls.append(turn)
                return _real(deps, turn)

            monkeypatch.setitem(kinds_registry._KINDS, name, dataclasses.replace(chat_kind, on_turn=spy))
            thread = self.service.get(self.owner, uuid.UUID(self._new_thread(name)))
            client_id = uuid.uuid4()
            opened = self.service.begin(self.owner, thread, self.text, client_id, self.contexts.get(name, {}), attachments=[])
            assert len(calls) == 1, f"[{name}] on_turn ran {len(calls)} times for one new turn"
            turn = calls[0]
            assert turn.text == self.text and turn.user_seq == opened.turn.user.seq and turn.window == chat_kind.history_window, f"[{name}] on_turn got {turn!r}"
            assert isinstance(turn.history, tuple) and isinstance(turn.context, chat_kind.context_schema)
            assert opened.deps is not None, f"[{name}] on_turn must return the deps to use, or None to keep them"
            self.service.begin(self.owner, thread, self.text, client_id, self.contexts.get(name, {}), attachments=[])  # a resend of the running answer is served from storage
            assert len(calls) == 1, f"[{name}] on_turn ran again for a resend"

    # -- 3. attachments ----------------------------------------------------------------------------------

    def test_attachments_are_staged_bound_and_listed_or_refused_by_the_kind(self):
        for kind in self.kinds:
            policy = self._kind(kind).attachments
            if policy is None:
                thread_id = self._new_thread(kind)
                r = self._send(thread_id, kind, attachments=[{"id": str(uuid.uuid4())}])
                assert r.status_code == 400 and r.json().get("field") == "attachments" and r.json().get("detail") == "not_enabled", f"[{kind}] has no attachment policy, a send with a file must answer 400 invalid/not_enabled: {r.status_code} {r.content[:200]!r}"
                continue
            assert self.service.attachment_store is not None, f"[{kind}] has an attachment policy but the service has no attachment table"
            name, data = self._upload_sample(policy)
            if data is None:
                continue  # a policy for kinds the sampler cannot make (documents): the framework suite covers them
            thread_id = self._new_thread(kind)
            from django.core.files.uploadedfile import SimpleUploadedFile

            up = self.client.post(f"{BASE}attachments/", {"file": SimpleUploadedFile(name, data, content_type="application/octet-stream"), "kind": kind}, format="multipart")
            assert up.status_code == 201, f"[{kind}] upload answered {up.status_code}: {up.content[:300]!r}"
            file_id = up.json()["id"]
            sent = self._send(thread_id, kind, attachments=[{"id": file_id}])
            assert sent.status_code == 200, f"[{kind}] send with a file answered {sent.status_code}: {sent.content[:300]!r}"
            assert parse_sse(self._body(sent))[-1]["type"] == "done"
            stored = self.client.get(f"{BASE}threads/{thread_id}/").json()["messages"]
            users = [m for m in stored if m["role"] == "user"]
            assert [a["id"] for a in users[0]["attachments"]] == [file_id], f"[{kind}] the stored message does not list the file: {users[0]}"

    @staticmethod
    def _upload_sample(policy) -> tuple[str, bytes | None]:
        kinds = set(policy.kinds)
        if "text" in kinds:
            return "note.txt", b"hello from the conformance test"
        if "image" in kinds:
            from PIL import Image

            out = io.BytesIO()
            Image.new("RGB", (4, 4), (200, 30, 30)).save(out, "PNG")
            return "pixel.png", out.getvalue()
        return "", None

    # -- 4. trace ----------------------------------------------------------------------------------------

    def test_trace_frames_and_the_stored_trace_follow_the_kinds_level(self):
        for kind in self.kinds:
            level = self._kind(kind).trace_level
            _, message_id, body = self._answer(kind)
            frames, ids = parse_sse(body), sse_ids(body)
            steps = [f for f in frames if f["type"] == "trace_step"]
            stored = self.service.message_model.objects.get(pk=message_id).trace
            if level == 0:
                assert not steps and stored is None, f"[{kind}] trace_level 0 must send and store nothing"
                continue
            assert steps, f"[{kind}] trace_level {level} sent no trace_step frame"
            assert ids == list(range(1, len(frames) + 1)), f"[{kind}] the frames carry no ordered SSE ids: {ids}"
            assert all(f["event_seq"] == ids[frames.index(f)] for f in steps), f"[{kind}] a trace_step's event_seq differs from its SSE id"
            assert stored and stored["status"] == "done", f"[{kind}] no trace stored on the answer row (missing `trace` column or sink?)"
            live = {f["step"]["step_id"]: f["step"] for f in steps}
            assert {s["step_id"]: s for s in stored["steps"]} == live, f"[{kind}] the stored trace differs from the last live frame of its steps"

    # -- 5. resume, cancel, live -------------------------------------------------------------------------

    def test_follow_replays_only_what_the_client_lacks_and_cancel_reports_an_ended_answer(self):
        for kind in self.kinds:
            thread_id, message_id, body = self._answer(kind)
            row = self.service.message_model.objects.get(pk=message_id)
            url = f"{BASE}threads/{thread_id}/messages/{message_id}/stream/"
            full = self.client.get(url, HTTP_ACCEPT="text/event-stream")
            assert full.status_code == 200, f"[{kind}] follow answered {full.status_code}: {full.content[:300]!r}"
            frames = parse_sse(self._body(full))
            assert frames[0]["type"] == "run" and frames[0].get("resume") is True and frames[-1]["type"] == "done", f"[{kind}] follow: {[f['type'] for f in frames]}"
            assert "".join(f["delta"] for f in frames if f["type"] == "text_delta").strip() == row.text.strip(), f"[{kind}] a follow from zero does not replay the stored text"
            held = len(row.text.encode("utf-16-le")) // 2 + 1
            after = self.client.get(url, {"after": max(sse_ids(body)), "text_offset": held}, HTTP_ACCEPT="text/event-stream")
            assert [f["type"] for f in parse_sse(self._body(after))] == ["run", "done"], f"[{kind}] a client that holds everything is sent more than run and done"
            stop = self.client.post(f"{BASE}threads/{thread_id}/messages/{message_id}/cancel/")
            assert stop.status_code == 200 and stop.json() == {"status": "done"}, f"[{kind}] cancel of an ended answer: {stop.status_code} {stop.content[:200]!r}"

    def test_a_running_answer_is_followed_resent_into_live_and_cancelled(self):
        import asyncio

        from asgiref.sync import sync_to_async

        from django_cfg.modules.django_llm.agent.chat import turn as rules
        from django_cfg.modules.django_llm.agent.runtime.driver import DriverConfig

        fast = DriverConfig(ping_s=0.1, max_run_s=10, flush_s=0.02, cancel_poll_s=0.02)
        service = self.service
        for kind in self.kinds:
            self._kind(kind)
            service.model_factory = lambda chat_kind: scripted_model([Say("one two three ", chunk=4), Hang()])
            thread = service.create(self.owner, kind, context=self.contexts.get(kind))
            client_id = uuid.uuid4()
            opened = service.begin(self.owner, thread, self.text, client_id, self.contexts.get(kind, {}))
            answer_id = opened.turn.assistant.id
            row = service.message_model.objects

            async def scenario():
                first = asyncio.ensure_future(_drain(service.frames(opened, driver_config=fast)))
                for _ in range(200):
                    if await sync_to_async(lambda: row.filter(pk=answer_id, text__startswith="one").exists())():
                        break
                    await asyncio.sleep(0.02)
                else:
                    raise AssertionError(f"[{kind}] the answer never started streaming into its row")
                again = await sync_to_async(service.begin)(self.owner, thread, self.text, client_id, self.contexts.get(kind, {}))
                stopped = await sync_to_async(self.client.post)(f"{BASE}threads/{thread.pk}/messages/{answer_id}/cancel/")
                await asyncio.wait_for(first, 10)
                return again, stopped

            again, stopped = run_async(scenario)
            assert again.turn.kind is rules.TurnKind.LIVE and again.turn.assistant.id == answer_id, f"[{kind}] a resend of a running client_id must attach (LIVE), got {again.turn.kind}"
            assert stopped.status_code == 202 and stopped.json() == {"status": "cancelling"}, f"[{kind}] cancel of a running answer: {stopped.status_code} {stopped.content[:200]!r}"
            assert row.get(pk=answer_id).status == "cancelled", f"[{kind}] a cancelled run is stored as {row.get(pk=answer_id).status!r}"

    # -- 6. tenancy and refusals -------------------------------------------------------------------------

    def test_another_users_thread_is_not_found_and_refusals_are_problem_json(self):
        from django_cfg.modules.django_llm.agent.chat.api import CODES, PROBLEM_MEDIA_TYPE

        def problem(response, status, code):
            assert response.status_code == status, f"expected {status}, got {response.status_code}: {response.content[:200]!r}"
            assert response["Content-Type"].startswith(PROBLEM_MEDIA_TYPE), f"a refusal must be {PROBLEM_MEDIA_TYPE}, got {response['Content-Type']}"
            body = response.json()
            assert body["code"] == code and body["code"] in CODES and body["status"] == status

        kind = self.kinds[0]
        thread_id, message_id, _ = self._answer(kind)
        mine = f"{BASE}threads/{thread_id}/"
        problem(self.stranger.get(mine), 404, "not_found")
        problem(self._send(thread_id, kind, client=self.stranger), 404, "not_found")
        problem(self.stranger.get(f"{mine}messages/{message_id}/stream/", HTTP_ACCEPT="text/event-stream"), 404, "not_found")
        problem(self.stranger.post(f"{mine}messages/{message_id}/cancel/"), 404, "not_found")
        problem(self.client.get(f"{BASE}threads/{uuid.uuid4()}/"), 404, "not_found")
        problem(self.anonymous.get(f"{BASE}threads/"), 401, "unauthorized")
        problem(self.client.post(f"{BASE}threads/", {"kind": "no-such-kind-" + uuid.uuid4().hex[:6]}, format="json"), 400, "invalid")

    # -- 7. schema ---------------------------------------------------------------------------------------

    def test_the_mounted_operations_are_the_frameworks(self):
        import json

        from django.urls import include, path
        from drf_spectacular.generators import SchemaGenerator

        from django_cfg.modules.django_llm.agent.chat.api import urls

        patterns = [path(BASE.lstrip("/"), include((urls(self.service, operation_id_prefix=PREFIX, tag=PREFIX), PREFIX)))]
        document = json.loads(json.dumps(SchemaGenerator(patterns=patterns).get_schema(request=None, public=True), default=str))
        found = {(route[len(BASE):], method): op["operationId"].removeprefix(f"{PREFIX}_") for route, item in document["paths"].items() for method, op in item.items()}
        wanted = dict(OPERATIONS)
        if self.service.attachment_model is not None:
            wanted.update(ATTACHMENT_OPERATIONS)
        assert found == wanted, f"operations differ from the framework's: missing {sorted(set(wanted.items()) - set(found.items()))}, extra {sorted(set(found.items()) - set(wanted.items()))}"

    # -- 8. migrations -----------------------------------------------------------------------------------

    def test_the_hosts_migrations_cover_the_chat_models(self):
        if not self.check_migrations:
            pytest.skip("check_migrations is off for this host")
        models = [self.service.thread_model, self.service.message_model, self.service.attachment_model]
        labels = sorted({m._meta.app_label for m in models if m is not None})
        pending = missing_migrations(*labels)
        assert not pending, "the chat models are ahead of the migrations (a column the framework added needs a host migration: run `makemigrations`):\n  " + "\n  ".join(pending)


async def _drain(stream) -> list[str]:
    return [chunk async for chunk in stream]
