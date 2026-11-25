"""Telegram and admin-email announcement of a captured lead.

Independent of Notion delivery (own job, own flags on the outbox row) and of each other. Nothing here raises into
the caller. A channel that is not configured (no bot / chat, no admin emails) is skipped silently and counts as
settled; a channel that fails is retried by the sweeper, with the same ``max_attempts`` cap as delivery.
Neither channel touches the Notion token, so the announcement works while Notion is misconfigured or down.

The project key (``keys``) is the first body line of both, and the ``X-Project-Key`` header of the admin email, so the
Hub can name the project of a notice. The subject never changes (the Hub's mailbox silence rows match on it). The
acknowledgement letter to the visitor carries neither.
"""

from __future__ import annotations

import html
import logging
from datetime import timedelta
from typing import Callable, List, Optional, Tuple

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import F, Q
from django.utils import timezone

from . import conf, keys, notify_texts
from .details import PROJECT_KEY_LABEL, build_details
from .lead import NotionLead
from .models import NotionOutbox

logger = logging.getLogger("django_cfg.modules.django_notion")

SENT, SKIPPED, FAILED = "sent", "skipped", "failed"
LEASE_SECONDS = 120  # a claimed row is not claimed again (sweeper vs. fresh job) for this long
MESSAGE_LIMIT = 1500


def _clean(text: str) -> str:
    return " ".join(str(text or "").split())


def display_name(lead: NotionLead) -> str:
    return _clean(lead.name) or _clean(lead.email) or _clean(lead.phone) or "Lead"


def _fields(lead: NotionLead, project: str) -> List[Tuple[str, str]]:
    message = (lead.message or "").strip()
    if len(message) > MESSAGE_LIMIT:
        message = message[:MESSAGE_LIMIT] + "..."
    pairs = [
        ("Name", _clean(lead.name)), ("Email", _clean(lead.email)), ("Phone", _clean(lead.phone)),
        ("Form", _clean(lead.form)), ("Page URL", _clean(lead.page_url)), ("Brand", _clean(lead.brand)),
    ]
    return [(k, v) for k, v in pairs if v] + ([("Message", message)] if message else [])


def _details(lead: NotionLead) -> List[str]:
    text = build_details(lead.extra)
    return text.splitlines()[:30]


NOTION_URL = "https://www.notion.so/{id}"
ACK_WINDOW = timedelta(hours=24)
ACK_EXCERPT = 200


def notion_url(row: NotionOutbox) -> str:
    return NOTION_URL.format(id=row.notion_page_id.replace("-", "")) if row.status == NotionOutbox.Status.SENT and row.notion_page_id else ""


def subject(project: str, lead: NotionLead) -> str:
    return f"[{project}] New lead: {display_name(lead)}"[:200]


PROJECT_KEY_HEADER = "X-Project-Key"


def project_line(lead: NotionLead) -> List[str]:
    """The fixed ``Project key: <key>`` line. In the body as well as the header: a forward may drop the header."""
    key = keys.clean(lead.project)
    return [f"{PROJECT_KEY_LABEL}: {key}"] if key else []


def headers(lead: NotionLead) -> dict:
    key = keys.clean(lead.project)
    return {PROJECT_KEY_HEADER: key} if key else {}


def telegram_text(project: str, lead: NotionLead, link: str = "") -> str:
    esc = html.escape
    lines = [f"<b>[{esc(project)}] New lead: {esc(display_name(lead))}</b>"]
    lines += [esc(line) for line in project_line(lead)]
    lines += [f"{k}: {esc(v)}" for k, v in _fields(lead, project) if k != "Name"]
    lines += [esc(line) for line in _details(lead)]
    if link:
        lines.append(f"Notion: {esc(link)}")
    return "\n".join(lines)[:3800]


def email_text(project: str, lead: NotionLead, link: str = "") -> str:
    lines = project_line(lead) + [f"{k}: {v}" for k, v in _fields(lead, project)]
    lines += _details(lead)
    if link:
        lines.append(f"Notion: {link}")
    return "\n".join(lines)


def _telegram_client():
    from django_cfg.modules.django_telegram import DjangoTelegram

    return DjangoTelegram()


def _email_client():
    from django_cfg.modules.django_email import DjangoEmailService

    return DjangoEmailService()


def _admin_emails() -> List[str]:
    from django_cfg.modules.django_email import get_admin_emails

    return get_admin_emails()


def send_telegram(project: str, lead: NotionLead, row: NotionOutbox, link: str = "") -> str:
    tg = _telegram_client()
    configured = tg.is_configured
    if callable(configured):
        configured = configured()
    if not configured or not tg._resolve_chat_id():
        return SKIPPED
    from django_cfg.modules.django_telegram.types import TelegramParseMode

    ok = tg.send_message(telegram_text(project, lead, link), parse_mode=TelegramParseMode.HTML, fail_silently=False)
    return SENT if ok else FAILED


def send_email(project: str, lead: NotionLead, row: NotionOutbox, link: str = "") -> str:
    recipients = [r for r in _admin_emails() if r]
    if not recipients:
        return SKIPPED
    ok = _email_client().send_simple(
        subject=subject(project, lead), message=email_text(project, lead, link), recipient_list=recipients,
        fail_silently=False, headers=headers(lead),
    )
    return SENT if ok else FAILED


class _Safe(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def _fill(template: str, **values) -> str:
    try:
        return template.format_map(_Safe(values))
    except Exception:
        return template


def _site() -> Tuple[str, str]:
    """(project name for display, site url when it is http(s))."""
    from django_cfg.core.state import get_current_config

    config = get_current_config()
    name = _clean(getattr(config, "project_name", "") or "") if config else ""
    url = str(getattr(config, "site_url", "") or "").strip() if config else ""
    return name, url if url.startswith(("http://", "https://")) else ""


def _own_addresses() -> set:
    """Admins and our own sender: an auto-reply must never go there (loops, self-mail)."""
    from email.utils import parseaddr

    own = {a.strip().lower() for a in _admin_emails() if a}
    try:
        own.add(parseaddr(_email_client()._get_default_from_email(None))[1].strip().lower())
    except Exception:
        pass
    return {a for a in own if a}


def ack_texts(project: str, lead: NotionLead, cfg) -> Tuple[str, str]:
    """(subject, plain-text body) of the acknowledgement letter, in the language of the lead's Locale."""
    t = notify_texts.TEXTS[notify_texts.pick((lead.extra or {}).get("Locale"))]
    display, site = _site()
    display = display or project
    name = _clean(lead.name)[:80]
    values = dict(name=name, project=display, site=site)
    subj = _clean(_fill(cfg.acknowledge_subject, **values)) if cfg.acknowledge_subject else t["subject"].format(project=display)
    main = _fill(cfg.acknowledge_body, **values).strip() if cfg.acknowledge_body else t["body"]
    lines = [t["hello_name"].format(name=name) if name else t["hello"] + ",", "", main]
    if cfg.acknowledge_reply_within.strip():
        lines.append(t["within"].format(within=_clean(cfg.acknowledge_reply_within)))
    recap = []
    if _clean(lead.form):
        recap.append(f"{t['form']}: {_clean(lead.form)[:100]}")
    excerpt = _clean(lead.message)
    if excerpt:
        recap.append(f"{t['message']}: {excerpt[:ACK_EXCERPT]}{'...' if len(excerpt) > ACK_EXCERPT else ''}")
    if recap:
        lines += ["", t["recap"], *recap]
    lines += ["", t["reply"], "", "-- ", display]
    if site:
        lines.append(site)
    return subj[:200], "\n".join(lines)


def send_ack(project: str, lead: NotionLead, row: NotionOutbox, link: str = "") -> str:
    """Plain-text 'we received your request' letter to the lead's author. Never carries the Notion link."""
    address = _clean(lead.email).lower()
    try:
        validate_email(address)
    except ValidationError:
        return SKIPPED
    if address in _own_addresses():
        return SKIPPED
    recent = NotionOutbox.objects.filter(ack_email=address, ack_notified_at__gte=timezone.now() - ACK_WINDOW).exclude(pk=row.pk)
    if recent.exists():
        return SKIPPED  # one letter per address per 24 h
    subj, body = ack_texts(project, lead, conf.get_notion_config())
    admins = [a for a in _admin_emails() if a]
    ok = _email_client().send_html(
        subject=subj, html_message="", text_message=body, recipient_list=[address], text_only=True,
        reply_to=admins[:1] or None, fail_silently=False,
    )
    if not ok:
        return FAILED
    NotionOutbox.objects.filter(pk=row.pk).update(ack_email=address)
    return SENT


def _pending_q(cfg) -> Q:
    q = Q(pk__in=[])
    if cfg.notify_telegram:
        q |= Q(telegram_notified_at__isnull=True)
    if cfg.notify_email:
        q |= Q(email_notified_at__isnull=True)
    if cfg.acknowledge:
        q |= Q(ack_notified_at__isnull=True)
    return q


def _claim(row_id: int, cfg) -> bool:
    now = timezone.now()
    n = NotionOutbox.objects.filter(_pending_q(cfg), pk=row_id, notify_next_at__lte=now, notify_attempts__lt=cfg.max_attempts).update(
        notify_attempts=F("notify_attempts") + 1, notify_next_at=now + timedelta(seconds=LEASE_SECONDS)
    )
    return n == 1


def _any_channel(cfg) -> bool:
    return bool(cfg.notify_telegram or cfg.notify_email or cfg.acknowledge)


def _expects_notion(row: NotionOutbox, cfg) -> bool:
    """Is a Notion page still to come for this row (configured, not dead, not sent)?"""
    if row.status in (NotionOutbox.Status.SENT, NotionOutbox.Status.DEAD):
        return False
    target = cfg.targets.get(row.target)
    return bool(target is not None and (target.token or cfg.token))


def _grace_until(row: NotionOutbox, cfg):
    """When the admin/Telegram announcement may stop waiting for the Notion link (None = send now)."""
    if cfg.notify_link_wait_seconds <= 0 or not _expects_notion(row, cfg):
        return None
    until = row.created_at + timedelta(seconds=cfg.notify_link_wait_seconds)
    return until if until > timezone.now() else None


def wake(row_id: int) -> None:
    """Called when Notion delivery succeeded: let a waiting announcement go now (only before its first real attempt)."""
    NotionOutbox.objects.filter(pk=row_id, notify_attempts=0, notify_next_at__gt=timezone.now()).update(notify_next_at=timezone.now())


def notify(row_id: int) -> str:
    """Announce one lead on the channels still open. Returns 'done', 'retry', 'waiting' (held for the Notion link) or 'skipped'. Never raises."""
    try:
        cfg = conf.get_notion_config()
        if not _any_channel(cfg):
            return "skipped"
        row = NotionOutbox.objects.filter(pk=row_id).first()
        if row is None:
            return "skipped"
        announce_open = (cfg.notify_telegram and not row.telegram_notified_at) or (cfg.notify_email and not row.email_notified_at)
        until = _grace_until(row, cfg) if announce_open and row.notify_attempts == 0 else None
        if until is not None:  # Notion is expected to deliver soon: hold the announcement for the link, up to the grace
            NotionOutbox.objects.filter(pk=row.pk, notify_attempts=0).update(notify_next_at=until)
            return "waiting"
        if not _claim(row_id, cfg):
            return "skipped"
        row = NotionOutbox.objects.get(pk=row_id)
        link = notion_url(row)
        lead = NotionLead(**row.payload)
        project = conf.project_name(cfg)
        channels: List[Tuple[str, bool, Callable[..., str], Optional[object]]] = [
            ("telegram", cfg.notify_telegram, send_telegram, row.telegram_notified_at),
            ("email", cfg.notify_email, send_email, row.email_notified_at),
            ("ack", cfg.acknowledge, send_ack, row.ack_notified_at),
        ]
        errors, now = [], timezone.now()
        for name, enabled, send, done_at in channels:
            if not enabled or done_at:
                continue
            try:
                result = send(project, lead, row, link)
            except Exception as exc:  # one channel must not stop the other
                result, detail = FAILED, f"{type(exc).__name__}: {exc}"
            else:
                detail = "refused"
            if result == FAILED:
                errors.append(f"{name}: {detail}"[:500])
                logger.warning("django_notion: %s notification failed for %s (%s)", name, row.key, detail)
            else:
                NotionOutbox.objects.filter(pk=row.pk).update(**{f"{name}_notified_at": timezone.now()})
        if not errors:
            NotionOutbox.objects.filter(pk=row.pk).update(notify_error="")
            return "done"
        backoff = min(30 * 2 ** max(row.notify_attempts, 0), cfg.max_backoff_seconds)  # row.notify_attempts is pre-claim
        NotionOutbox.objects.filter(pk=row.pk).update(
            notify_error="; ".join(errors)[:2000], notify_next_at=now + timedelta(seconds=backoff)
        )
        return "retry"
    except Exception:
        logger.exception("django_notion: notify failed for outbox row %s", row_id)
        return "skipped"


def due_ids(cfg, limit: int = 200) -> List[int]:
    """Rows with an open channel whose retry time has come and whose attempts are not used up."""
    if not _any_channel(cfg):
        return []
    return list(
        NotionOutbox.objects.filter(_pending_q(cfg), notify_next_at__lte=timezone.now(), notify_attempts__lt=cfg.max_attempts)
        .order_by("notify_next_at").values_list("pk", flat=True)[:limit]
    )
