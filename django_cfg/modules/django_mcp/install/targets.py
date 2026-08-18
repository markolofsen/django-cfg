"""Which endpoint, under which name — and who gets to decide.

This module holds the *mechanism*. The facts — that production is
``api.example.com``, that its key sits in ``deploy/.env`` — belong to the
project, and are declared in its ``mcp/__init__.py`` beside the key itself.
django_cfg hardcoding one deployment's hostnames would make the framework know
about one product.

**A target is a registration, not a setting.** Local and production land under
different server names so both can be installed at once and any answer is
attributable to one of them. Sharing a name, they silently replace each other:
installing local deregisters production without a word, and the assistant then
reports ConnectionRefused for a server nobody touched.

**There is deliberately no default target.** Both ends serve the same tools over
the same protocol, so a client aimed at the wrong one does not fail — it
connects, lists everything, and answers from the other environment's database. A
wrong guess is invisible; one extra word makes it impossible.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, NamedTuple, Optional

#: Header the MCP endpoint authenticates with. One spelling, framework-wide:
#: the server reads it in ``views.py`` and both assistants must send exactly it.
ACCESS_KEY_HEADER = "X-MCP-Access-Key"

#: 127.0.0.1, never "localhost". On macOS that name resolves to IPv6 ``::1``
#: first while ``manage.py runserver`` binds IPv4 only, so an assistant reports
#: ConnectionRefused against a server ``curl`` reaches without trouble. It cost
#: an afternoon once; it is a constant now.
DEFAULT_LOCAL_URL = "http://127.0.0.1:8000/cfg/mcp/"


class Target(NamedTuple):
    """One named registration: an endpoint, and where its key comes from.

    ``env_files`` is ordered, highest priority first, and may be empty — a
    custom URL passed on the command line has no file to read, because nothing
    here knows which deployment it is.
    """

    kind: str
    url: str
    name: str
    env_files: tuple[Path, ...] = ()
    #: The key this deployment uses, when the project stated it outright.
    #: Outranks every other source: nothing else knows a remote deployment's key.
    access_key: Optional[str] = None

    @property
    def is_remote(self) -> bool:
        return not self.url.startswith(
            ("http://127.0.0.1", "http://localhost", "http://[::1]")
        )


class TargetError(ValueError):
    """The target could not be resolved. The message is for the operator."""


def local_target(
    *, name: str, url: str = DEFAULT_LOCAL_URL, env_files: Iterable[Path] = ()
) -> Target:
    return Target("local", url, name, tuple(env_files))


def remote_target(
    *, kind: str, name: str, url: str, env_files: Iterable[Path] = ()
) -> Target:
    """A non-local registration — production, staging, whatever the project has.

    ``kind`` is free-form on purpose: a project with three deployments should
    not have to pretend one of them is "prod".
    """
    if kind == "local":
        raise TargetError("use local_target() for the local endpoint")
    return Target(kind, url, name, tuple(env_files))


def resolve(
    registry: dict[str, Target],
    *,
    kind: Optional[str] = None,
    url: Optional[str] = None,
    name: Optional[str] = None,
) -> Target:
    """Pick one target from the project's registry, or build a custom one.

    Refuses rather than guesses in every ambiguous case, because each of those
    guesses produces a working-looking registration pointed at the wrong data.
    """
    if kind and url:
        raise TargetError(f"pick one target, not both: --{kind} and --url")

    if url:
        # A custom URL must not borrow a registered name: writing it under an
        # existing one silently replaces that registration with a third
        # endpoint, and nothing in a later answer would say so.
        if not name:
            raise TargetError(
                "--url also needs --name (a custom endpoint must not reuse a "
                "declared server name — it would overwrite that registration)"
            )
        if name in {t.name for t in registry.values()}:
            raise TargetError(
                f"--name {name!r} is already declared for the {_kind_of(registry, name)!r} "
                "target; pick a different name or drop --url to use it"
            )
        return Target("custom", url, name)

    if not kind:
        raise TargetError(_no_target_message(registry))

    if kind not in registry:
        known = ", ".join(f"--{k}" for k in sorted(registry)) or "(none declared)"
        raise TargetError(f"unknown target --{kind}; this project declares: {known}")

    target = registry[kind]
    return target._replace(name=name) if name else target


def _kind_of(registry: dict[str, Target], name: str) -> str:
    return next((k for k, t in registry.items() if t.name == name), "?")


def _no_target_message(registry: dict[str, Target]) -> str:
    if not registry:
        return (
            "no MCP targets are declared for this project, so there is nothing "
            "to install by name.\n"
            "  Pass --url <url> --name <name>, or declare targets in your\n"
            "  mcp/__init__.py so `--local` and `--prod` mean something here."
        )
    lines = [f"  --{kind:<8} {t.url}  → {t.name}" for kind, t in sorted(registry.items())]
    return (
        "pick a target:\n"
        + "\n".join(lines)
        + "\nthere is no default: these are separate registrations, and guessing "
        "wrong\nanswers with the wrong environment's data rather than failing"
    )
