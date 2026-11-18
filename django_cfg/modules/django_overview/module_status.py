"""The Modules tab: is each module on, off, misconfigured or failing, and what to do about it.

**Never a value.** A probe reports booleans ("token set"), names (queue names,
backend class, provider names) and counts. A probe that fails shows the
exception *class* only: a Redis error message can carry the URL with its
password. Each probe is wrapped, so one broken module never hides the others.

The only probe that does I/O is RQ (cron_status reads Redis); it runs on a
thread with a short deadline, so a dead Redis costs the page two seconds, not a
hung worker.
"""

from __future__ import annotations

import concurrent.futures
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

ON, OFF, WARN, ERROR = "on", "off", "warn", "error"
RQ_DEADLINE_SECONDS = 2.0

#: A small fixed pool: a hung Redis call holds one thread, it cannot pile up threads.
_rq_pool = concurrent.futures.ThreadPoolExecutor(max_workers=2, thread_name_prefix="cfg-overview-rq")


@dataclass
class ModuleStatus:
    key: str
    title: str
    state: str
    summary: str
    hint: str = ""
    details: list[tuple[str, str]] = field(default_factory=list)


def _yes(value: Any) -> str:
    return "set" if value else "not set"


def _secret_set(value: Any) -> bool:
    """True when a str or SecretStr holds something, without keeping the value."""
    if value is None:
        return False
    getter = getattr(value, "get_secret_value", None)
    raw = getter() if callable(getter) else value
    return bool(str(raw).strip())


# --- probes -----------------------------------------------------------------


def _mcp(config) -> ModuleStatus:
    mcp = getattr(config, "mcp", None)
    if mcp is None or not getattr(mcp, "enabled", False):
        return ModuleStatus("mcp", "MCP", OFF, "Not enabled.", "mcp=MCPConfigBuilder()...build() in your config turns it on.")
    profiles = getattr(mcp, "profiles", None) or {}
    details = []
    for name, p in profiles.items():
        kinds = []
        if getattr(p, "access_key", None) or getattr(p, "extra_keys", None):
            kinds.append("keys")
        if getattr(p, "key_validator", None):
            kinds.append("personal keys")
        if getattr(p, "oauth", None):
            kinds.append("OAuth")
        details.append((name, f"{p.path} · {', '.join(kinds) or 'no credential'}"))
    return ModuleStatus(
        "mcp", "MCP", ON, f"{len(profiles)} profile(s).",
        "Connect your assistant on the MCP tab.", details,
    )


def _notion(config) -> ModuleStatus:
    notion = getattr(config, "notion", None)
    if notion is None or not getattr(notion, "enabled", False):
        return ModuleStatus("notion", "Notion", OFF, "Not enabled.", "NotionConfig(enabled=True, token=..., targets=...).")
    token = _secret_set(getattr(notion, "token", None))
    targets = list((getattr(notion, "targets", None) or {}).keys())
    details = [("Token", _yes(token)), ("Targets", ", ".join(targets) or "none"),
               ("Telegram copy", "on" if getattr(notion, "notify_telegram", False) else "off"),
               ("Admin email copy", "on" if getattr(notion, "notify_email", False) else "off")]
    if not token:
        return ModuleStatus("notion", "Notion", WARN, "Enabled without a token.",
                            "Leads queue in the outbox and are not written to Notion until NOTION__TOKEN is set.", details)
    if not targets:
        return ModuleStatus("notion", "Notion", WARN, "No target database.", "Add a target to NotionConfig.targets.", details)
    return ModuleStatus("notion", "Notion", ON, f"{len(targets)} target(s).", "", details)


def _telegram(config) -> ModuleStatus:
    tg = getattr(config, "telegram", None)
    if tg is None:
        return ModuleStatus("telegram", "Telegram", OFF, "Not configured.", "TelegramConfig(bot_token=..., chat_id=...).")
    token, chat = _secret_set(getattr(tg, "bot_token", None)), bool(getattr(tg, "chat_id", 0))
    dedupe = getattr(tg, "dedupe", False)
    details = [("Bot token", _yes(token)), ("Chat id", _yes(chat)),
               ("Dedup", f"on, {getattr(tg, 'dedupe_window_seconds', 0)} s window" if dedupe else "off")]
    if not (token and chat):
        return ModuleStatus("telegram", "Telegram", WARN, "Token or chat id missing.",
                            "Set TELEGRAM__BOT_TOKEN and TELEGRAM__CHAT_ID; messages are dropped until then.", details)
    return ModuleStatus("telegram", "Telegram", ON, "Bot and chat set" + (", dedup on." if dedupe else "."), "", details)


def _email(config) -> ModuleStatus:
    from django.conf import settings

    email = getattr(config, "email", None)
    backend = getattr(settings, "EMAIL_BACKEND", "") or ""
    mailers = getattr(settings, "MAILERS", None)
    details = []
    if isinstance(mailers, dict) and mailers:
        details.append(("MAILERS", ", ".join(
            f"{alias}: {str((m or {}).get('BACKEND', '')).rsplit('.', 1)[-1] or '?'}" for alias, m in mailers.items()
        )))
    elif backend:
        details.append(("EMAIL_BACKEND", backend.rsplit(".", 1)[-1]))
    if email is not None:
        details.append(("Configured backend", str(getattr(email, "backend", ""))))
    kind = (getattr(email, "backend", "") if email is not None else "") or backend
    lowered = kind.lower()
    if email is None and not mailers:
        return ModuleStatus("email", "Email", OFF, "Not configured.", "EmailConfig(backend='smtp', ...) sends real mail.", details)
    if "console" in lowered or "locmem" in lowered or "memory" in lowered or "file" in lowered or "dummy" in lowered:
        return ModuleStatus("email", "Email", WARN, "Mail is not sent (development backend).",
                            "Production needs smtp or gateway.", details)
    if "smtp" in lowered and email is not None and not getattr(email, "host", None):
        return ModuleStatus("email", "Email", WARN, "SMTP without a host.", "Set EMAIL__HOST.", details)
    return ModuleStatus("email", "Email", ON, "Sending through " + (kind.rsplit(".", 1)[-1] or "?") + ".", "", details)


def _cron_status():
    from django_cfg.modules.django_rq.health.status import cron_status

    return cron_status()


def _rq(config) -> ModuleStatus:
    from django.conf import settings

    rq = getattr(config, "django_rq", None)
    if rq is None or not getattr(rq, "enabled", False) or not getattr(settings, "RQ_QUEUES", None):
        return ModuleStatus("rq", "RQ (background jobs)", OFF, "Not enabled.", "DjangoRQConfig(enabled=True) and a Redis URL.")
    queues = list(settings.RQ_QUEUES)
    try:
        schedules = len(rq.get_all_schedules())
    except Exception:
        schedules = len(getattr(rq, "schedules", None) or [])
    details = [("Queues", ", ".join(queues)), ("Schedules", str(schedules))]
    future = _rq_pool.submit(_cron_status)
    try:
        st = future.result(timeout=RQ_DEADLINE_SECONDS)
    except concurrent.futures.TimeoutError:
        return ModuleStatus("rq", "RQ (background jobs)", ERROR, f"Redis did not answer in {RQ_DEADLINE_SECONDS:.0f} s.",
                            "Check that Redis is up; manage.py rq_cron_status prints the same check.", details)
    except Exception as exc:
        return ModuleStatus("rq", "RQ (background jobs)", ERROR, f"Status read failed ({type(exc).__name__}).",
                            "Check Redis; manage.py rq_cron_status prints the same check.", details)
    for q in st.queues:
        wait = "" if q.wait_sec is None else f", oldest {q.wait_sec:.0f} s"
        details.append((f"Queue {q.queue}", f"{q.depth} queued{wait}"))
    hb = "none" if st.heartbeat_age_sec is None else f"{st.heartbeat_age_sec:.0f} s ago"
    details.append(("rqcron heartbeat", hb))
    details.append(("Busy workers", str(len(st.busy))))
    if st.verdict == "cron_dead":
        hint = "Start manage.py rqcron." if schedules else "No schedules declared, so no rqcron is needed."
        state = ERROR if schedules else ON
        summary = "rqcron is not running." if schedules else f"{len(queues)} queue(s); no schedules."
        return ModuleStatus("rq", "RQ (background jobs)", state, summary, hint, details)
    if st.verdict == "starved":
        return ModuleStatus("rq", "RQ (background jobs)", WARN, "Jobs are waiting longer than 2 minutes.",
                            "Workers are busy or missing; see manage.py rq_cron_status.", details)
    return ModuleStatus("rq", "RQ (background jobs)", ON, f"{len(queues)} queue(s), rqcron alive.", "", details)


def _llm(config) -> ModuleStatus:
    keys = getattr(config, "api_keys", None)
    openrouter = _secret_set(getattr(keys, "openrouter", None)) if keys else False
    openai = _secret_set(getattr(keys, "openai", None)) if keys else False
    details = [("OpenRouter key", _yes(openrouter)), ("OpenAI key", _yes(openai))]
    mcp = getattr(config, "mcp", None)
    if mcp is not None and getattr(mcp, "llm_model", None):
        details.append(("MCP agent model", str(mcp.llm_model)))
    if not (openrouter or openai):
        return ModuleStatus("llm", "LLM", OFF, "No provider key.",
                            "API_KEYS__OPENROUTER enables the MCP agent chat and LLM features.", details)
    return ModuleStatus("llm", "LLM", ON, "OpenRouter key set." if openrouter else "OpenAI key set.", "", details)


def _constance(config) -> ModuleStatus:
    from django.conf import settings

    if "constance" not in settings.INSTALLED_APPS:
        return ModuleStatus("constance", "Constance", OFF, "Not installed.", "")
    fields = getattr(settings, "CONSTANCE_CONFIG", None) or {}
    backend = str(getattr(settings, "CONSTANCE_BACKEND", "") or "").rsplit(".", 1)[-1]
    details = [("Settings", str(len(fields))), ("Backend", backend or "default")]
    if not fields:
        return ModuleStatus("constance", "Constance", WARN, "Installed, no settings declared.", "", details)
    return ModuleStatus("constance", "Constance", ON, f"{len(fields)} live setting(s).", "", details)


def _oauth(config) -> ModuleStatus:
    from django_cfg.modules.base import BaseCfgModule

    base = BaseCfgModule()
    on = [name for name in ("github", "google") if base.is_oauth_provider_enabled(name)]
    details = [(name.title(), "configured" if name in on else "not configured") for name in ("github", "google")]
    mcp = getattr(config, "mcp", None)
    if mcp is not None and getattr(mcp, "enabled", False):
        signed = [n for n, p in (getattr(mcp, "profiles", None) or {}).items() if getattr(p, "oauth", None)]
        details.append(("MCP sign-in", ", ".join(signed) or "off"))
    if not on:
        return ModuleStatus("oauth", "OAuth sign-in", OFF, "No provider.", "Set GITHUB_OAUTH__CLIENT_ID and GITHUB_OAUTH__CLIENT_SECRET, or the GOOGLE_OAUTH__ pair.", details)
    return ModuleStatus("oauth", "OAuth sign-in", ON, ", ".join(n.title() for n in on) + ".", "", details)


def _analytics(config) -> ModuleStatus:
    from django_cfg.modules.base import BaseCfgModule

    analytics = getattr(config, "analytics", None)
    if not BaseCfgModule().is_analytics_enabled():
        return ModuleStatus("analytics", "Analytics", OFF, "Disabled.", "AnalyticsConfig(enabled=True).")
    details = [("Ingest path", str(getattr(analytics, "ingest_path", "") or "default")),
               ("Do Not Track", "respected" if getattr(analytics, "respect_dnt", False) else "ignored")]
    return ModuleStatus("analytics", "Analytics", ON, "Collecting.", "Reports are on the Analytics tab.", details)


def _logging(config) -> ModuleStatus:
    from django.conf import settings

    cfg = getattr(config, "logging", None)
    logging_setting = getattr(settings, "LOGGING", None) or {}
    handlers = list((logging_setting.get("handlers") or {}).keys())
    details = [("Handlers", ", ".join(handlers[:8]) or "none")]
    if cfg is not None:
        for label, attr in (("Level", "level"), ("Format", "format"), ("Directory", "dir"), ("Retain days", "retain_days")):
            value = getattr(cfg, attr, None)
            if value not in (None, ""):
                details.append((label, str(value)))
    if not handlers:
        return ModuleStatus("logging", "Logging", WARN, "No handlers configured.", "Django's defaults apply.", details)
    return ModuleStatus("logging", "Logging", ON, f"{len(handlers)} handler(s).", "", details)


PROBES: list[tuple[str, str, Callable[[Any], ModuleStatus]]] = [
    ("mcp", "MCP", _mcp),
    ("notion", "Notion", _notion),
    ("telegram", "Telegram", _telegram),
    ("email", "Email", _email),
    ("rq", "RQ (background jobs)", _rq),
    ("llm", "LLM", _llm),
    ("constance", "Constance", _constance),
    ("oauth", "OAuth sign-in", _oauth),
    ("analytics", "Analytics", _analytics),
    ("logging", "Logging", _logging),
]


def collect(config: Optional[Any] = None) -> list[ModuleStatus]:
    """Every probe, in a fixed order. Never raises."""
    if config is None:
        from django_cfg.core.state import get_current_config

        config = get_current_config()
    out = []
    for key, title, probe in PROBES:
        try:
            out.append(probe(config))
        except Exception as exc:
            logger.exception("Overview: module probe %r failed", key)
            out.append(ModuleStatus(key, title, ERROR, f"Status check failed ({type(exc).__name__}).",
                                    "See the server log."))
    return out
