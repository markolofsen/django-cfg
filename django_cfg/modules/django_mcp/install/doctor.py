"""Diagnosing an MCP setup: the checks whose failures are all invisible.

Every check here exists because the failure it catches looks like success, or
looks like an empty database, from where the operator is standing.

1. **An empty access key OPENS the endpoint.** ``_access_key_required()``
   returns ``bool(access_key)`` — "no key configured" means "no key required".
   Correct on a laptop, catastrophic in production, where every probe answers
   200 instead of 401 and *nothing looks wrong*.
2. **A key with no identity is nobody.** A valid key authenticates as
   ``AnonymousUser`` unless bound to an account, so every tool gated on
   ``user.is_staff`` refuses — and to an agent a refusal reads almost exactly
   like an empty result. That is how half a working surface passes for missing
   data.
3. **``service_username`` takes a ``USERNAME_FIELD`` value.** Where that field
   is ``email``, a bare name matches no row and rejects *every* request rather
   than degrading to anonymous — a total outage from a plausible-looking string.
4. **The endpoint may not be the one you configured.** Local and production
   serve identical tools, so a client aimed at the wrong one connects, lists
   everything, and answers from the other database.

The result is a list of findings rather than a bool, because "the key is set but
authenticates as nobody" is neither pass nor fail — it is the single most
common way this surface half-works.
"""

from __future__ import annotations

from typing import Any, Literal, NamedTuple, Optional

from .console import Console, mask
from .discovery import URL_VAR
from .runner import probe, probe_endpoint
from .targets import Target

Status = Literal["ok", "warn", "fail"]


class Finding(NamedTuple):
    status: Status
    check: str
    detail: str
    fix: Optional[str] = None


def diagnose(config: Any, targets: dict[str, Target], *, skip_probe: bool = False) -> list[Finding]:
    """Run every check. Order is narrative: config, then identity, then network."""
    findings: list[Finding] = []
    findings += _check_key(config)
    findings += _check_identity(config)
    findings += _check_targets(config, targets)
    if not skip_probe:
        findings += _check_reachable(targets)
    return findings


def _check_key(config: Any) -> list[Finding]:
    key = (getattr(config, "access_key", None) or "").strip()
    if not key:
        return [
            Finding(
                "fail",
                "access key",
                "not set — and an empty key does not disable the endpoint. "
                "django_cfg reads 'no key configured' as 'no key required', so "
                "/cfg/mcp/ answers every unauthenticated caller.",
                "set MCP__ACCESS_KEY, or call mcp.set_access_key(...)",
            )
        ]
    return [Finding("ok", "access key", f"set ({mask(key)})")]


def _check_identity(config: Any) -> list[Finding]:
    username = (getattr(config, "service_username", None) or "").strip()

    if not username:
        return [
            Finding(
                "warn",
                "key identity",
                "unbound — a valid key authenticates as AnonymousUser, so every "
                "tool gated on user.is_staff refuses. An agent cannot tell that "
                "refusal from an empty result.",
                "set MCP__SERVICE_USERNAME to a staff service account, if any "
                "tool needs one",
            )
        ]

    try:
        from django.contrib.auth import get_user_model
    except Exception:  # pragma: no cover - Django always importable here
        return [Finding("warn", "key identity", f"bound to {username!r} (unverified)")]

    model = get_user_model()
    field = getattr(model, "USERNAME_FIELD", "username")
    account = model._default_manager.filter(**{field: username}).first()

    if account is None:
        hint = ""
        if field == "email" and "@" not in username:
            # The specific shape of the mistake, named: USERNAME_FIELD is email
            # here, so a bare name matches nothing and rejects every request.
            hint = (
                f" USERNAME_FIELD is {field!r}, but {username!r} is not an "
                "email — a bare name matches no row."
            )
        return [
            Finding(
                "fail",
                "key identity",
                f"bound to {username!r}, which matches no account. A missing "
                f"account is a rejection, not a downgrade: every request 401s."
                + hint,
                f"create the account, or clear MCP__SERVICE_USERNAME to fall "
                "back to anonymous",
            )
        ]

    notes = []
    if not account.is_active:
        notes.append("inactive — requests will be rejected")
    if not getattr(account, "is_staff", False):
        notes.append("not staff — staff-gated tools will still refuse")
    if getattr(account, "is_superuser", False):
        notes.append("SUPERUSER — the key grants full admin rights to anyone holding it")

    if notes:
        status: Status = "fail" if not account.is_active else "warn"
        return [Finding(status, "key identity", f"{username}: " + "; ".join(notes))]
    return [Finding("ok", "key identity", f"{username} (active, staff, not superuser)")]


def _check_targets(config: Any, targets: dict[str, Target]) -> list[Finding]:
    if not targets:
        return [
            Finding(
                "warn",
                "install targets",
                "none declared, so `mcp_install` accepts only an explicit --url",
                'mcp.add_target("local") and mcp.add_target("prod", "<deploy>/.env")',
            )
        ]

    findings = [
        Finding("ok", "install targets", ", ".join(f"--{k} → {t.name}" for k, t in sorted(targets.items())))
    ]

    key = (getattr(config, "access_key", None) or "").strip()
    for kind, target in sorted(targets.items()):
        if target.env_files and not target.url:
            findings.append(
                Finding(
                    "fail",
                    f"target {kind}",
                    f"no {URL_VAR} in its env files, so the endpoint cannot be "
                    "derived and installing it is refused",
                    f"add {URL_VAR} to one of those files, or pass url=... to "
                    "add_target",
                )
            )
            continue

        from .keys import resolve as resolve_key

        # Ask the same resolver `mcp_install` asks, with the same arguments.
        # Re-deriving the answer here is how this check came to disagree with
        # what the install command actually writes: it reported a target with a
        # declared key as "uses this process's own config", which is the exact
        # confusion — a remote target silently falling back to the development
        # key — that this whole check exists to catch.
        resolved = resolve_key(
            target.env_files, declared=target.access_key, fallback=key or None
        )

        if not resolved.value:
            findings.append(
                Finding("warn", f"target {kind}", f"no key resolvable — {resolved.source}")
            )
            continue

        # A remote target serving under this process's key is almost never
        # intended: on a laptop that key is the development one, so the
        # registration connects, lists every tool, and 401s on the first real
        # call inside an assistant where nobody reads status codes.
        if target.is_remote and key and resolved.value == key and not target.access_key:
            findings.append(
                Finding(
                    "warn",
                    f"target {kind}",
                    "would register under THIS process's key — correct only if "
                    "this process is that deployment",
                    "declare the deployment's own key: "
                    f'add_target("{kind}", access_key=...)',
                )
            )
            continue

        if key and resolved.value != key and target.is_remote:
            # Worth saying out loud: a remote target whose key disagrees with
            # the key this process runs under is either a pending rotation or
            # the wrong source, and both produce a registration that 401s later.
            findings.append(
                Finding(
                    "ok",
                    f"target {kind}",
                    f"key {mask(resolved.value)} from {resolved.source} "
                    "(differs from this process's — expected for a remote)",
                )
            )
            continue

        findings.append(
            Finding("ok", f"target {kind}", f"key {mask(resolved.value)} from {resolved.source}")
        )
    return findings


def _check_reachable(targets: dict[str, Target]) -> list[Finding]:
    """Two different questions, and they need two different requests.

    ``probe`` asks ``/info/``. **Since 2.2.158 that route is gated by the same
    key as JSON-RPC** unless the project opts out with ``public_info``, so its
    status code no longer answers the same question it used to:

    ==========  ====================================================
    ``200``     up, and this profile serves its listing anonymously
    ``401``     up, and gated — the normal shape for a keyed endpoint
    ==========  ====================================================

    Both are healthy. Reading either as "the endpoint serves unauthenticated"
    is the wrong route: this check once reported a correctly-locked production
    deployment as wide open, with the alarming wording and all, while ``POST
    /cfg/mcp/`` was answering 401 to everyone. A false "your secrets are
    exposed" is not a harmless over-warning — it either sends someone into an
    emergency that does not exist, or teaches them that this line is noise,
    which is worse, because the real thing looks identical.

    So: ``/info/`` answers *is it up*, and the guarded endpoint answers *is it
    locked*. Only the second may claim the endpoint is open.
    """
    findings: list[Finding] = []
    for kind, target in sorted(targets.items()):
        code = probe(target.url)
        if code == 200:
            # Alive. Now ask the route that is supposed to refuse us.
            guarded = probe_endpoint(target.url)
            if guarded == 401:
                findings.append(
                    Finding(
                        "ok",
                        f"reachable {kind}",
                        f"{target.url} → up, and the endpoint answers 401 without a key",
                    )
                )
            elif guarded == 200:
                findings.append(
                    Finding(
                        "fail",
                        f"reachable {kind}",
                        f"{target.url} answers 200 WITHOUT a key — it is serving "
                        "every caller. An empty access key does not disable this "
                        "endpoint, it opens it.",
                        "set MCP__ACCESS_KEY in that deployment and redeploy",
                    )
                )
            else:
                findings.append(
                    Finding(
                        "warn",
                        f"reachable {kind}",
                        f"{target.url} → up ({target.url}info/ answered 200), but "
                        f"the endpoint itself answered {guarded}",
                    )
                )
        elif code == 401:
            # Also healthy: some deployments gate /info/ too.
            findings.append(
                Finding("ok", f"reachable {kind}", f"{target.url} → 401 (up, authenticating)")
            )
        elif code is None:
            findings.append(
                Finding("warn", f"reachable {kind}", f"{target.url} → no response")
            )
        elif code == 403:
            # Django answers an unauthenticated probe 401, not 403. A 403 here
            # is therefore usually the edge, not the app — Cloudflare blocked
            # this exact probe on a fully healthy deployment while curl got 200.
            findings.append(
                Finding(
                    "warn",
                    f"reachable {kind}",
                    f"{target.url} → 403, which this app does not return to an "
                    "unauthenticated probe — most likely a WAF in front of it",
                    "compare with `curl -s -o /dev/null -w '%{http_code}' "
                    f"{target.url.rstrip('/')}/info/` — **200 or 401** there "
                    "means the deployment is fine and only the probe was "
                    "refused. 401 is the normal answer for a keyed endpoint "
                    "since 2.2.158; only a 403 points at the edge",
                )
            )
        else:
            findings.append(
                Finding("warn", f"reachable {kind}", f"{target.url} → {code}")
            )
    return findings


def report(findings: list[Finding], console: Console) -> int:
    """Print findings; return an exit code (non-zero only for hard failures)."""
    emit = {"ok": console.ok, "warn": console.warn, "fail": console.err}
    width = max((len(f.check) for f in findings), default=0)

    for finding in findings:
        emit[finding.status](f"{finding.check.ljust(width)}  {finding.detail}")
        if finding.fix and finding.status != "ok":
            console.plain(f"    {'→':>{width}} {finding.fix}")

    failures = sum(f.status == "fail" for f in findings)
    warnings = sum(f.status == "warn" for f in findings)
    console.plain()
    if failures:
        console.err(f"{failures} failing, {warnings} warning(s)")
        return 1
    if warnings:
        console.warn(f"no failures, {warnings} warning(s)")
        return 0
    console.bold("All checks passed.")
    console.plain("A passing config still proves nothing about the tools — call one.")
    return 0
