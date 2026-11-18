# django_notion

Duplicates leads from Django into a Notion **Leads** database. The lead is saved in the project database first (the
source of truth); the module mirrors it and **never** breaks the save. Leads are its only job today; the name is
general so other mirrors can join later.

- Config: `NotionConfig` (`DjangoConfig.notion`), `NotionTarget`. Token from `NOTION__TOKEN`, or per target.
- Wiring: `connect(Model, adapter=..., route=...)`. No hand-written signals.
- Safety: outbox table + RQ delivery + retries + sweeper. Notion down = rows wait, nothing raises.
- Also: Telegram and admin-email copy of every lead (`notify_telegram`, `notify_email`, with the Notion link) and a plain-text acknowledgement to the lead's author (`acknowledge`), independent of Notion.
- Backfill: `manage.py notion_export <app.Model> --to <data source>` moves a model's rows into a data source (one way, dry run by default, re-run safe); built-in preset for the user model. See [Export](#export).
- Checks: `manage.py notion_doctor` (read-only). Admin: *Notion outbox* with a **Retry** action.
- Full guide (public docs): `apps/docs/content/features/modules/django-notion/`. Operations: [`@docs/operations.md`](@docs/operations.md).

## Quick start

```python
# config.py
from django_cfg.modules.django_notion import NotionConfig, NotionTarget

notion = NotionConfig(
    enabled=True,
    project="mls",  # prefix of the idempotency key
    targets={
        "mls":  NotionTarget(data_source_id="419b879d-c730-4c81-9b7f-a80b986a07fd"),  # CRM: MLS / Leads
        "saas": NotionTarget(data_source_id="<CRM: SaaS Leads data source id>"),
    },
)
```

```python
# apps/inquiries/apps.py  (ready())
from django_cfg.modules.django_notion import NotionLead, connect

def to_lead(inq) -> NotionLead:
    return NotionLead(name=inq.name, email=inq.email, phone=inq.phone, message=inq.message, form=inq.form,
                      page_url=inq.page_url, received_at=inq.created_at, extra=inq.payload)

def route(inq):  # None = do not send
    return "mls" if inq.site in {"caribbean-mls", "danmerriam.com"} else "saas"

connect(Inquiry, adapter=to_lead, route=route)
```

`NOTION__TOKEN` in the environment (never in code). `python manage.py migrate` creates the outbox table.

## What reaches Notion

| NotionLead | Column | Notes |
|---|---|---|
| name | Name (title) | falls back to company, email, phone, "Lead" |
| (always) | Status = New, Source (Website by default) | Status is set only on create |
| email, phone, message, form, page_url | Email, Phone, Message, Form, Page URL | bad email / URL goes to Details |
| source_page, locale, company | Source page, Locale, Company | |
| received_at | Received at | |
| ad_click | Ad click | raw string; GCLID, MSCLKID, LinkedIn click ID, UTM source/medium/campaign, Ad click time, Ad consent are parsed from it unless set |
| extra | Details | one `Label: value` line per field |
| (always) | Hub run id | the idempotency key `<project>:<app.model>:<pk>` |

Never written: Owner, Next step, Notes, Client, Conversation summary (people and Hub own them).

**Details rules**: order Company, Source page, Locale, then the rest alphabetically; nested `Budget / Min: 10`; lists
`a, b`; bool `Yes`/`No`; empty values dropped; a value over 1000 characters is cut with a note; Details over ~6000
characters ends with the number of fields not shown. Never copied: `website`, `startedAt`, `elapsedMs`, idempotency keys,
Hub keys, and any name containing password, token, api key, authorization, captcha, cookie (also secret, csrf, turnstile).
A column can be renamed or switched off per target: `NotionTarget(columns={"company": "Firm", "gclid": None})`; a switched-off
column's value moves into Details (into the page body when Details itself is off).

## Delivery

1. `post_save(created)` writes a `NotionOutbox` row **inside the lead's transaction** (in a savepoint) with the lead payload.
2. `transaction.on_commit` queues the RQ job `django_notion.tasks.deliver_outbox`.
3. The job creates the page under the target's **data source** (API `2025-09-03`) and stores `notion_page_id`.
4. Failure: `failed` + `next_attempt_at` (30 s, 60 s, 120 s ... up to `max_backoff_seconds`); 429 waits `Retry-After` and does not
   count as an attempt; a Notion 400 (validation) is `dead` at once; after `max_attempts` a row is `dead`. **Retry** in the admin resets it.
5. The sweeper (RQ schedule added automatically, every `sweep_interval_seconds`) queues due rows, recovers rows stuck in
   `sending`, and purges sent rows older than `retention_days`. If Redis is down when the lead is saved, the sweeper still delivers it.

A page that has a `notion_page_id` is never created again.

## Configuration

```python
from django_cfg import NotionConfig, NotionLead, NotionTarget   # also exported from the package root

notion = NotionConfig(
    enabled=True,
    targets={"mls": NotionTarget(data_source_id="...", token=None)},  # token=SecretStr(...) = this target's own integration
    enrich=True,            # Project, Environment, Site, API host (Brand defaults to the project name)
    notify_telegram=True,   # Telegram copy of every lead
    notify_email=True,      # email copy to the administrators
    notify_link_wait_seconds=30,  # wait this long for the Notion page link
    acknowledge=True,       # plain-text 'we received your request' to the lead's author
    acknowledge_reply_within="2 business hours",  # optional
)
```

- **Token**: `NOTION__TOKEN` is the default for every target. A `NotionTarget(token=SecretStr(...))` uses its own integration
  instead (one workspace per brand); neither ever appears in `repr`, logs or errors.
- **Enrich** (`enrich=True`): the project name, environment, site and API host are added to every lead; a value the adapter
  set is never overwritten.
- **Request context**: when `notion.enabled`, `django_notion.context.RequestContextMiddleware` is installed automatically. While a
  request is handled it keeps the page (`Referer`), campaign parameters (UTM, `gclid`, `msclkid`) and `Accept-Language`; the
  lead gets them as `page_url` and `extra` (Details), again without overwriting what the adapter set. Outside a request
  (shell, RQ job) nothing is added.

## Telegram, admin email and the author's acknowledgement

Every captured lead is also announced, once, on three channels that need no new settings:

| Channel | Goes through | Skipped silently when | Switch |
|---|---|---|---|
| Telegram | `django_telegram` (`DjangoConfig.telegram`: bot token and chat id), HTML parse mode, all fields escaped | no bot token or no chat id | `notify_telegram` |
| Admin email | `django_email`, to `get_admin_emails()` (`config.admin_emails`, then Django `ADMINS`), subject `[<project>] New lead: <name>` | no recipients | `notify_email` |
| Acknowledgement | `django_email` `send_html(text_only=True)`: a **plain-text** letter to the lead's own address, subject `We received your request — <project>` | the lead has no syntactically valid email, the address is an admin or our own sender, or it already got one in the last 24 h | `acknowledge` |

Telegram and the admin email carry Name, Email, Phone, Form, Page URL, Brand, the Message (cut at 1500 characters), the
Details lines (never secrets or the Notion token) and, when the page exists, `Notion: https://www.notion.so/<page id without dashes>`.

**Notion link without waiting for Notion.** The announcement job runs right after the lead is saved. When a Notion page is still to
come (target configured with a token, row not `sent`/`dead`), Telegram and the admin email wait up to
`notify_link_wait_seconds` (default 30; 0 = never wait) counted from the lead's creation. A successful delivery wakes them at once
with the link; if the grace ends first (Notion slow, failing or down) they go **without** the link, and never a second message
later. With no Notion token for the lead nothing waits. The acknowledgement waits with them (same job) and **never** contains the
link.

**Acknowledgement letter.** Plain text only, no HTML part, no template, no tracking. Language from the lead's `Locale`
(`Accept-Language`, filled by the request-context middleware): en, ru, ko, de, fr, es, pt, zh, ja, ar, else English; the words live
in `notify_texts.py`. Content: greeting (by name when known), "we received your request", optionally "We usually reply within
`acknowledge_reply_within`" (free text such as `2 business hours`, not translated; omitted when empty), a recap (form, message
excerpt of at most 200 characters), a signature with the project name and `site_url` (the only link). `Reply-To` is the first admin
email. `acknowledge_subject` and `acknowledge_body` (placeholders `{name} {project} {site}`) replace the subject and the main
paragraph; a broken template falls back to itself, never breaks the send. The 24 h limit counts letters actually sent per address
(`NotionOutbox.ack_email`); two simultaneous leads from one address may both pass it.

- **Independent.** Own RQ job (`tasks.notify_outbox`), queued next to the delivery job. A Notion failure, a missing Notion
  token or Notion being down does not stop any channel, and a failing channel never stops the others or the lead save.
- **Once.** `telegram_notified_at`, `email_notified_at`, `ack_notified_at` settle a channel (sent, or skipped on purpose) and are never
  cleared; a Notion retry never repeats an announcement. A failed channel is retried by the sweeper with backoff (30 s doubling to
  `max_backoff_seconds`) and the `max_attempts` cap, only for the channel that failed (`notify_attempts`, `notify_error`).
  Rows that existed before the migrations are marked settled, so an upgrade announces nothing old.
- **Limits.** Telegram and email are handed to their own queue / thread, so "sent" means accepted for sending; a later
  provider error is in their logs, not in the outbox. A lead is still captured only for a configured Notion target (the outbox row
  belongs to one), so a project that wants only Telegram and email still sets `notion.enabled` and one target. A crash between
  sending and writing the flag can announce one lead twice. The auto-reply goes to an address the visitor typed: keep the 24 h limit on.

## Enabling on a project: mandatory steps

1. **Turn off Hub intake for that form first.** Hub (`crm/`, `/apix/crm/leads/<public_id>/`) already writes site forms into the
   same Notion bases; with both on, every lead lands twice. This module becomes the single writer for Django projects.
2. Create a separate Notion integration with **Insert content** only, share the Leads database with it, set `NOTION__TOKEN`.
3. Check on staging (see [`@docs/operations.md`](@docs/operations.md)), then `python manage.py notion_doctor`.
4. Mention in the privacy policy that contact details (email, phone, message) are processed in Notion.

## Tests

`tests/modules/test_django_notion.py` (fake client, no network): `DJANGO_SETTINGS_MODULE=tests.settings PYTHONPATH=. .venv/bin/python -m pytest tests/modules/test_django_notion.py -q`.

## Export

`export/` holds the generic core (`throttle.py`, `mapping.py`, `runner.py`, `registry.py`) and `management/commands/notion_export.py`
is its command. Public guide: `apps/docs/content/features/modules/django-notion/export.mdx`.

- Layers: `build_plan` (ORM, select only) -> `scan` (key column of the data source) -> `execute` (`pages.create` through a client object, so
  tests pass a fake). Nothing is updated or deleted; Notion is never read back into Django.
- Mapping: `ExportMapping(model, key, fields, exclusions, queryset, batch_column, allow_secret)`; `register_export`, `user_export(...)`.
- Guards (each from the carapis backfill): the join key is always written and read back from the create response (a key not stored
  stops the run); rich text is cut at 2000 UTF-16 units; a secret-looking field cannot be mapped without `allow_secret`;
  report and manifest carry counts, primary keys and page ids only. A source named like an action (`delete`, `save`) or a method with `alters_data` is refused; an exclusion rule that raises leaves the row out and the plan goes on; the manifest is appended row by row (`execute(..., manifest_path=)`), so an interrupted run keeps it.
- Origin: extracted from carapis `apps/leads/services/notion_import.py`. Carapis still runs its own copy until it moves to this release
  (`@dev/planned/notion-model-export/PLAN.md`, step N2).
