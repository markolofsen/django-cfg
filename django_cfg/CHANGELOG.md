# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **Chat attachments: a picture was never read (found in production, reforms 2026-11-10).** Two faults: (1) `chain_sees_images` read the model catalogue cache with no network; a fresh container has an empty cache, so `openai/gpt-5-mini` and `google/gemini-2.5-flash` counted as blind and every image went the OCR way; now the catalogue wins when it knows the slug and a family list (`openai/gpt-4o|4.1|5`, `google/gemini`, `anthropic/claude`, ...) answers when it does not. (2) The OCR default `qwen/qwen-2-vl-7b-instruct` (and the `llama-3.2-11b-vision` preset) were withdrawn from OpenRouter (404); defaults are now `google/gemini-2.5-flash-lite` (balanced `google/gemini-2.5-flash`), and `aread_image_text` falls through `OCR_FALLBACKS` (`openai/gpt-5-nano`, `google/gemma-3-12b-it`) when the default fails; an explicit `model=` still fails loudly. django_llm engine 1.4.1.

### Added
- **Chat attachments: retention and a ready OCR method.** `AttachmentPolicy.keep_days` / `AttachmentsConfig.keep_days` (default 30; `0` = delete the bytes once the answer is stored; `None` = keep): `chat_reap` deletes the bytes of old sent files, the row stays as `status="expired"` with its name and the text read from it; `MessageSerializer.attachments[].expired` (additive, regenerate clients) and an empty `url` for such a file. django_llm (`ENGINE_VERSION` 1.4.0): `aread_image_text(data, mime, *, query=None, mode="base", model=None)` reads an image held in memory as a base64 data URL with the engine's own OCR model; the chat's describe path uses it (`DEFAULT_OCR_MODELS` is removed; `ocr_models` still overrides). Images already reach models as base64 `BinaryContent`: no public URL is needed.
- **Chat attachments** (`django_llm/agent/chat`, ready app `django_cfg.apps.tools.chat`). Files on a user message for authenticated owners: `AbstractAttachment` (a host adds one `CreateModel`), `AttachmentPolicy` on a `ChatKind`, `AttachmentsConfig` on `ChatConfig.attachments` (migration `cfg_chat.0003_attachment`), routes `attachments/`, `attachments/limits/`, `attachments/<id>/`, `attachments/<id>/content/`, problem codes `too_large` (413) and `unsupported_type` (415), `MessageSerializer.attachments` and `SendSerializer.attachments` (additive), `chat_attachments_check`, and reaping of expired uploads. Bytes are sniffed, size is enforced while streaming, storage is the Django `default`. Images reach the model as pixels or, for a text-only chain, through a cheap OCR model. Docs: `agent/chat/@docs/chat-attachments.md`. Client: `@djangocfg/widget-assistant` `loadChatAttachments`; regenerate the TypeScript client after upgrading.
- **Chat kit: a hidden "system feedback" turn, `already_given` as 409, and an ack for a `ui_payload`** (`django_llm/agent/chat`). (1) `ChatKind.empty_text_with` (a `frozenset` of context keys, e.g. `{"feedback"}`): a turn whose context holds a value under one of them may have empty text (`turn.clean_text(..., allow_empty=True)`, `turn.start(..., allow_empty=)`); a turn with neither text nor such a key is still `invalid` / `empty`. The empty user row is stored but skipped when the model's history is built and gives the thread no title; the send body accepts `text: ""` (`ChatSend.text` is `allow_blank`). (2) `InvalidTurn(field, code, status=400)`: with `status=409` (from `make_deps`, `merge_context` or `MessageConstraints.check`) the API answers `409 {code: <code>, field}`; `already_given` joins the problem codes (`CODES`). (3) `POST threads/<id>/messages/<mid>/parts/<n>/ack` `{applied: bool, reason?: str}` stores the browser's verdict as `parts[n].ack` (returned in the transcript), and calls `ChatService(on_ui_payload_accepted=(row, index, part) -> None)` when set; 404 for no such answer or part. Docs: `chat-api-kit.md`, `extending.md`, `chat-storage-contract.md`. Tests: `chat/tests/test_feedback.py`; the OpenAPI snapshot gains the ack operation. TypeScript: `@djangocfg/widget-assistant` `sendFeedback(messageId, payload)` posts such a turn without a user bubble.

### Removed
- **DPoP (RFC 9449 sender-constrained tokens) is removed, in django-cfg and in `@djangocfg/*`.** It was opt-in, off by default (`DJANGO_CFG_DPOP_ENABLED`, `NEXT_PUBLIC_DPOP_ENABLED`) and no project we run enabled it. No flag, alias or shim is left. Removed: `middleware/dpop.py` (moved with its tests to `middleware/@archive/dpop/`), the `JWTConfig.dpop_enabled` field and the `DJANGO_CFG_DPOP_ENABLED` setting, the `cnf`/`jkt` binding at every mint point (OTP, TOTP and backup-code verify, password grant, OAuth; they now call `RefreshToken.for_user` and `.access_token`), the proof check in `JWTAuthenticationWithLastLogin`, the `cnf` re-stamp in `CustomTokenRefreshView` (now the stock SimpleJWT refresh), the `dpop` entry of the default CORS allowed headers, and in the generated TypeScript client the P-256 key, IndexedDB store, proof signing and the proof on the refresh call and the 401 retry (the block is kept as `ts/wrapper/templates/@archive/dpop/dpop_block.ts.txt`). npm: `dpopEnabled` is no longer exported from `@djangocfg/api`, `createBaseNextConfig` has no `dpop` option and no longer inlines `NEXT_PUBLIC_DPOP_ENABLED`, `ErrorsTracker` has no DPoP hint and its Copy cURL always carries the Bearer token. **Migration: a project that never set any of this changes nothing but must regenerate its client (`make gen` / `manage.py gen`, or `make generate`) after upgrading, so `helpers/auth.ts` loses the dormant proof code. A project that set `JWTConfig(dpop_enabled=...)` must delete the line (`JWTConfig` rejects unknown fields, so startup fails with a validation error otherwise); one that set `dpop: true` in `next.config` or `NEXT_PUBLIC_DPOP_ENABLED` removes them.** Tokens already issued with a `cnf` claim keep working: the claim is ignored and a token is never rejected because of it, with or without a `DPoP` header (tests: `tests/middleware/test_cnf_claim_is_ignored.py`). The `cryptography` requirement stays (PyJWT's EC/RSA backend). Docs: *Security* (canonical "DPoP was removed"), *JWT Configuration*, *Django settings*, *Data layer*, *Generated clients*, *Django monitor*, *Deployment security*, the `v2.3.0` release page (note added), package READMEs and `@docs`; plan `@dev/planned/remove-dpop/PLAN.md`.
- **The logger wrapper is gone: `get_logger`, `DjangoLogger` and `DjangoCfgLogger` (`django_logging`).** No alias and no deprecation window. **Migration: replace `get_logger(name)` with `logging.getLogger(name)` (or `logging.getLogger(__name__)`) and drop the import.** Removed: `django_cfg.get_logger`, `django_cfg.DjangoLogger`, `django_cfg.utils.get_logger`, `django_cfg.modules.django_logging.{get_logger, DjangoLogger, logger}` and the `log_*` helpers of the old Rich logger (`logger.success`, `.timer`, `.config_built` ...). The old `get_logger` rewrote a short name to `django_cfg.<caller path>`; a plain name is now used as given (django-cfg's own modules use `__name__`, so they stay under `django_cfg.` and keep the generated `LOGGING` handlers; the telegram, email and monitor loggers keep their `django_cfg.*` names). Kept as plain functions in `django_logging/utils.py`, still importable from `django_cfg.modules.django_logging`: `sanitize_extra`, `clean_old_logs`, `RESERVED_LOG_ATTRS`; the generated `LOGGING` dict (`config.build_logging_config`) and the prune logic are unchanged. 54 call sites in django-cfg migrated. Docs: the *Django Logging* page is the canonical one; *logging*, *monitoring*, *modules overview*, *architecture* and *registry* pages fixed.

### Changed
- **Logs: django-cfg decides where they go, and every file is bounded (`django_logging`, `django_monitor`).** (1) New typed `DjangoConfig.logging` block (`DjangoLoggingConfig`): `dir` (default None), `level`, `format`, `rotate_mb` (10), `backups` (5), `retain_days` (14). Precedence for each: explicit config, then env (`DJANGO_CFG_LOG_DIR`, `_LEVEL`, `_FORMAT`, `_ROTATE_MB`, `_BACKUPS`, `_RETAIN_DAYS`), then the built-in default. The old config field `log_dir` is now `dir`. (2) Defaults need no setup: general logs are stdout JSON (text at a terminal) with no file. Monitor events also get their own small rotating file `djangocfg/monitor.log` (10 MB x 5) so `monitor_tail` has a source that outlives `docker logs`; its directory is `logging.dir` / `DJANGO_CFG_LOG_DIR`, else `/var/log/<app>` if writable, else the per-user state dir (`~/.local/state/<app>/log` on Linux, `~/Library/Logs/<app>` on macOS). If none is writable there is no file, events go to stdout and one warning is logged. A default inside the project tree is never used. A general `django.log` exists only when `dir` is set. (3) **Removed, no deprecation window and no alias:** the `<cwd>/logs` fallback (and its warning), the `<cwd>/.cache` cache fallback (the cache dir is `logging`-independent: config `cache_dir`, `DJANGO_CFG_CACHE_DIR`, else the per-user cache dir), and the env vars `DJANGO_CFG_LOG_FILE`, `DJANGO_CFG_LOG_ROTATE`, `DJANGO_CFG_LOG_MAX_BYTES` (use `_ROTATE_MB`) and `DJANGO_CFG_LOG_KEEP_DAYS` (use `_RETAIN_DAYS`). **A project that bind-mounts `/app/logs` can drop the mount; to keep `django.log` somewhere it sets `logging.dir` / `DJANGO_CFG_LOG_DIR`.** (4) Monitor events are no longer written twice when a directory is set (they went to `monitor.log` and, by propagation, `django.log`). (5) File handlers are size-rotated by django-cfg (`LazySizeRotatingFileHandler`), safe with several workers (rename under an `flock`); `rotate_mb=0` leaves rotation to logrotate. (6) New `python manage.py log_prune [--dir --days --keep --max-mb --apply]` (dry run by default) and a boot self-check: in a background thread, at most once a day per directory, rotated django-cfg files older than `retain_days` or past `backups` are deleted, then the oldest until the directory is under 500 MB (`DJANGO_CFG_LOG_DIR_MAX_BYTES`), one warning if it is still over; `DJANGO_CFG_LOG_PRUNE=0` turns it off; it never blocks boot. (7) `Telegram is not configured` is one WARNING per process instead of an ERROR per send. (8) Stale docs (`<cwd>/logs/djangocfg/monitor.log`, midnight rotation, 30 backups) corrected in `django_monitor/@docs`, `django_logging/@docs` and the public docs.
- **Browser events are one flat JSON line, and the ingest endpoint is bounded (`django_monitor`).** (1) With the JSON format the event fields (`event_type`, `fingerprint`, `level`, `message`, `url`, ...) are top-level keys of the line instead of JSON inside `message`; the text format is unchanged; `monitor_tail` reads both shapes. (2) A fingerprint repeating within 60 s is logged once and counted in the Django cache; one `django_cfg.monitor.repeat` line carries the count (server and browser events). A missing fingerprint is derived from type, normalised message and first stack frame. (3) Browser events below `warning` (info/debug, `PAGE_VIEW`, `PERFORMANCE`, `CONSOLE`) are no longer logged unless `MONITOR_LOG_VERBOSE` is on; `devtools.ping()` always is. (4) Limits: body over 64 KB is 413; 60 requests and 300 events a minute per client (429); 3000 events a minute per project (dropped, counted in `monitor_status`, still 202); `message` 2000, `stack_trace` 8000, `extra` 4 KB and 3 levels, one line 16 KB, with `truncated: true`. (5) The client is the socket peer unless `MONITOR_CLIENT_IP_HEADER` names the header of your own proxy (`CF-Connecting-IP`, `X-Forwarded-For` read from the right, `MONITOR_CLIENT_IP_HOPS`); the first `X-Forwarded-For` entry is never trusted. `RealIPMiddleware` now keeps the socket peer in `META["DJANGO_CFG_PEER_ADDR"]`. The `origin` header is logged. Not done: Redis window, `monitor_top`, Telegram escaping (plan slices L4-L7).

### Added
- **`monitor_tail --stdin`: read monitor events from a pipe (`django_monitor`).** In containers events go to stdout and no file is written, so `docker logs <container> 2>&1 | python manage.py monitor_tail --stdin [-n N] [--frontend] [--user ID] [--fingerprint HEX] [--session ID]` now works (`-` is the same as `--stdin`). Only JSON lines whose logger starts with `django_cfg.monitor` count; banners, tracebacks and other loggers are skipped silently. Filters, the `-n` cut (after the filters) and the output are identical to file mode. stdin is read only with `--stdin`/`-`, never otherwise (a TTY with `--stdin` prints a message instead of blocking). Without `--stdin` and without a log file the command prints where it looked and the exact `docker logs <container> 2>&1 | ...` line. Existing projects: nothing changes. Docs: *Management commands*, *Django Logging*. Tests: `django_monitor/tests/test_monitor_tail.py`.
- **Browser errors carry the signed-in user (`django_monitor`, `@djangocfg/devtools`).** (1) `POST /cfg/monitor/ingest/` now tries the Bearer JWT (the project's `JWTAuthenticationWithLastLogin`) and, when it is valid, puts `user_id` (`request.user.pk` as text: integer or uuid; never an e-mail or a name) on the flat event line next to `session_id`. It is soft: no header, wrong scheme, bad, expired or revoked token, deactivated user or a database error leaves the request anonymous and still 202; the endpoint never answers 401/403, and a session cookie is never used (no CSRF). Anonymous events have no `user_id` field; a `user_id` in the request body is ignored. The token is read after the cheap limits and the payload check, so junk traffic costs no user lookup. (2) Rate limits stay per client address and now also count the signed-in user (60 requests, 300 events a minute, 429), so one account cannot hide behind many addresses. (3) A repeat inside the 60 s dedupe window is counted, not logged: the line carries the user of the first occurrence, and the `monitor.repeat` line has no user. (4) `@djangocfg/devtools`: a regular flush sends `Authorization: Bearer <cfg.auth.access_token>` (cookie, else local, else session storage) when there is one; the body is unchanged; the unload flush stays header-free (text/plain, no preflight) and is therefore anonymous. `authorization` is in the default `cors_allow_headers`; a project that replaced that list must add it. (5) `monitor_tail --user <id> --fingerprint <hex> --session <id>` (combinable, applied before `-n`) and `user=<id>` in the output. **Privacy: a primary key is a personal identifier; a project with a privacy page should say that browser errors are reported with the user id when signed in.** Existing projects: nothing to change; ids appear after the django-cfg release is deployed and the devtools package is updated (an older devtools sends no token, so events stay anonymous). Docs: *django_monitor* overview ("Which user hit the error"), *Frontend devtools* ("Who was signed in"), *Management commands*, *Analytics privacy*, module `@docs`. Tests: `django_monitor/tests/test_ingest_user.py`, `test_monitor_tail.py`, `devtools/src/__tests__/ingestAuth.test.ts`.
- **Browser error reporting is hard to misconfigure and easy to verify (`@djangocfg/devtools`, `@djangocfg/layouts`, `django_monitor`).** (1) With `ingest` on and no base URL (`devtools={{ baseUrl }}`, `NEXT_PUBLIC_API_URL`), devtools no longer drops events silently: it logs one console warning naming the fix, counts the dropped events as `failed` with a `lastError`. (2) `window.devtools.status()` now returns `{ ingest, baseUrl, queued, sent, failed, lastError, lastSentAt, circuitOpen }` (type `DevtoolsStatus`; it still prints). (3) New `devtools.ping()`: sends one info event `devtools ping` and resolves with `status()`; django_monitor logs it and never alerts. (4) `BaseApp` derives the devtools `baseUrl` from `auth.apiUrl`, and takes a new `apiUrl` prop for `auth={false}` apps; precedence `devtools.baseUrl`, `apiUrl`, `auth.apiUrl`, `NEXT_PUBLIC_API_URL` (`resolveDevtoolsBaseUrl` is exported). (5) New `python manage.py monitor_tail [-n N] [--frontend]` prints the last events from `monitor.log` (both log formats) so an operator can verify without docker and grep. Browser events were already logged at every level (not only errors) and Telegram stays errors-only: now covered by a test that posts a batch to `/cfg/monitor/ingest/` and finds it in the log. No persistence added, wire format unchanged. Existing projects: nothing breaks; an app with `auth={false}` and no env var now warns in the console, fix it with `apiUrl`. Docs: `django_monitor/@docs`, *Frontend devtools* and *Management commands* pages, `@djangocfg/devtools` and `AppLayout` READMEs. Tests: `django_monitor/tests/test_frontend_visibility.py`, `test_monitor_tail.py`, `devtools/src/__tests__/ingestStatus.test.ts`, `layouts/.../devtoolsBaseUrl.test.ts`.
- **Single sign-in cannot loop.** The sign-in host marks the `next` it sends a signed-in visitor back to with `sso_ret=1`; a follower that sees the marker and still has no session (the shared cookie did not reach it) goes to the host with `sso_error=cookie`, and the host then shows the form with a notice instead of sending the visitor back again (middleware and `AuthProvider` both honour it; the marker is stripped from the address bar once the session is there). A stale cookie costs one extra hop, not a loop. Exports: `markReturn`, `hasReturnMarker`, `stripReturnMarker`, `SSO_RETURN`, `SSO_ERROR`. Docs: *One sign-in host* page (+ "Why it cannot loop"), `@djangocfg/api` `@docs/AUTHENTICATION.md`, `AuthLayout` README, `@docs/LAYOUTS.md`.
- **One sign-in host for the whole family (`auth={{ sso: true }}`).** The host is derived: `auth.` + the registrable domain of `NEXT_PUBLIC_SITE_URL` (`deriveAuthHost`); `sso: { authHost, authLabel }` or `NEXT_PUBLIC_AUTH_HOST` override; no variable is needed. A dedicated host (`auth.`/`id.`, any name) holds the only sign-in page; every other host, the public apex site included, is a follower; on the auth host the same setting means "I am the sign-in" (no redirect, no loop). `sso.host` stays as an alias. The cookie `Domain` is forced to the apex when it is on, so a Google sign-in ending on the auth host leaves the session on `.apex`. Off unless set; the shared cookie session (2.3.372) is unchanged. With `auth={{ sso: { host: 'reforms.ai' } }}` in `BaseApp` or the variable, a follower host (`my.`, `hub.`, ...) never renders `/auth`: `useCfgRouter` turns every hop to the auth route (guard, `RedirectPage`, expired session) and a direct visit into `https://auth.reforms.ai/auth?next=<page>`; the host saves the validated `next` as its back-url, so the existing post-sign-in navigation returns the visitor; sign-out goes to the host without `next`. `AuthLayout` shows a preloader on a follower; `useAuth().sso` exposes `{ enabled, isAuthHost, authOrigin, apex, reason }`. Outside the apex (localhost, `*.vercel.app`) it is ignored with one console line and the old per-host sign-in runs. One Google redirect URI (`https://auth.reforms.ai/auth?provider=google`): followers never start OAuth. `next` is accepted only as a plain path or `https://` + the apex or a subdomain (no `//`, `\`, userinfo, ports, other schemes, control characters, nested `/auth?next=`, > 2048 chars): `safeNext` in `@djangocfg/api` (`auth/utils/sso.ts`, also from `@djangocfg/api/storage`) and its twin `django_cfg.core.site.safe_next_url` (Site registry, `accept_subdomains`, no `api.`/`mcp.` hosts). New `@djangocfg/nextjs/auth/middleware`: `createSsoMiddleware({ authHost, protect, allow })` answers a protected path without the cookie pair with a 307 to the host, and sends a signed-in visitor of `/auth?next=` straight back (edge-safe, reads the forwarded host). `AuthConfig.sso.cookieDomain` forces the cookie domain. Not built: an `HttpOnly` session issued by the API (Django reads only the `Authorization` header by design; see docs). Docs: `apps/docs/content/frontend/single-sign-in-host.mdx`. Tests: `sso.test.ts`, `ssoRouter.test.ts`, `nextjs/src/auth/middleware.test.ts`, `tests/core/test_safe_next_url.py`.
- **Settings → API keys: copy button.** The masked key now has a copy button (tooltip "Copy to clipboard", check mark for 2 s). The full key is fetched at the click through the reveal call (it does not rotate the key and the mask stays on screen); a just-regenerated key is copied as shown. `useApiKey().reveal({ show })` now resolves to the full key; `show: false` copies without displaying it.
- **widget-assistant: floating window, ⌘J, new button.** The chat is a **floating window bottom right** on tablets (not modal: no backdrop, the page stays usable) and a full-screen sheet on phones; closing slides it out. `AssistantFrame` takes `onOpenChange` and `hotkey` (default `ASSISTANT_TOGGLE` = `mod+j`, ⌘J / Ctrl+J, works from inside a text field; Esc is deliberately not bound, so a draft is never lost to a stray key; the chat stays mounted, the unsent draft survives close). `AssistantMark` (the "AI" tile, `currentColor`, follows the theme) is the button's icon, the signed-out view's mark and the greeting mark in stories (`icon` prop replaces it), its name and tooltip come from the bundled `fabLabel` in 17 languages (`label` optional), and the tooltip shows the name and the combination for the viewer's system; Help lists the key (`helpToggle`). `createAssistantUi` takes `restoreFrom` (default 1280): a remembered "open" no longer reopens as a full-screen chat after a reload in a narrow window.
- **ui-core: `Button` / `ButtonLink` take `tooltip`; `useCanHover`; `TooltipHint`.** `<Button tooltip="Open">` or `tooltip={{ content, hotkey: 'mod+j', side, align, sideOffset, delay, hoverable }}` (`TooltipConfig`) replaces the `Tooltip` + `TooltipTrigger` + `TooltipContent` wrapper. It is drawn only where the device can hover (new hook `useCanHover`: `(hover: hover) and (pointer: fine)`), mounts no provider, closes when the pointer leaves, and wraps a disabled button in a span so it can be hovered. `TooltipHint` is the base for non-buttons. widget-chat `PanelIconButton` (round ghost button, label + hotkey tooltip) is now the one control of the chat header: Help, "...", new chat, sessions and Close, and `PanelCloseButton` forwards its ref so a `DialogClose asChild` works. The account menu no longer shows `⇧⌘,` next to Account: nothing ever bound it, so the hint promised a key that did nothing. Almost every `Tooltip` wrapper around a button in the packages (devtools, forms, diagram, data, map, media, editor, agent, sidebar) is now `tooltip` / `TooltipHint`; `CopyButton` takes `tooltip` too. widget-chat: `ComposerButton` takes `tooltip` (send, think, mic, dictation language), message actions and "jump to latest" use `TooltipHint`, `ChatTooltip` / `ComposerTooltip` are removed; widget-player buttons use `tooltip` instead of the native `title`. The Notion popover shadow is shorter and softer; the close button's right gap equals its vertical gap.
- **ui-core: tooltip surface is a token, touch targets keep field sizes.** `--tooltip-bg` / `--tooltip-fg` / `--tooltip-border` (default: inverse; the Notion preset uses the popover surface with a hairline). The 44px rule below 768px no longer inflates checkbox, switch, radio, combobox and tab (they got a 44px hit area from an invisible `::after` instead): fields keep one height. `Tooltip` is no longer hoverable (it closes when the pointer leaves the trigger; `disableHoverableContent={false}` restores it). The `PrivateLayout` sidebar button has a tooltip with the ⌘B / Ctrl+B combination and the resize line is a 2px primary line on the divider. `SidePanel` ignores presses and Esc that belong to a nested menu or popover (closing a menu closed the panel) and takes `backdrop`.
- **widget-assistant: one signed-out view and one placement rule, both in the frame.** `AssistantFrame` and `ChatDock` take `requireAuth` and `lock`: a signed-in reader gets the chat, a reader still being identified an empty body, anyone else a big icon, a reason and a **Sign in** button (saves the page, goes to the django-cfg auth route through `useAuth` / `useCfgRouter` of `@djangocfg/api/auth`, now a peer dependency), centred in the column; `lock` (`AssistantLockOptions`) changes words, icon, action or replaces the block. New exports `AssistantAuthGate`, `useAssistantAccess`, `useSignIn`. `AssistantFrame` also takes `dockFrom` (default **1280**, a host passes nothing; `0` turns self-docking off): a column from that window width, the side panel or sheet below it, so a host renders no `ChatDock` and no media query (the chat no longer competes with the page on a narrow window). Also: the time and copy row is hidden under the newest message while its answer streams and for an empty row; the sidebar of `PrivateLayout` has no group dividers and a denser rhythm (`--sidebar-item-h`, `--sidebar-item-gap`). Docs refreshed: widget `README`, `@docs/{interface,connect,customization,architecture}`, rules `assistant.md`. Hosts (reforms, docman, gptkino) switch after the npm release and `make update`.
- **Chat knowledge base: the cross-language gate is met without embeddings (chat-knowledge-base K4).** The agent now searches in the KB language: the prompt block says the index holds `<language>` text only, translate before every `kb_search`, search with a few key terms, 2-3 phrasings, "no matches" means wrong wording, and call `kb_search` first every time; the `kb_search` tool description says the same, and a search with no hits answers with a sentence naming the KB language (`KbSession.language`). A hyphenated query word also searches its joined form (`non-profit` finds `nonprofits`). `evalkit` lists the queries the model searched for next to each miss. Live eval (`google/gemini-2.5-flash`, 40 questions, en/ru/ko/de/es): recall@8 75% (MRR 0.63; en 8, de 7, es 6, ko 5, ru 4 of 8) -> 100% (MRR 0.99, every language 8/8; a second run 100%, 0.97). Decision: the embedding lane is not built. The live vectorisation check (S8) passed: a Russian query ranks the English chunk first; the embedder reads its key from `DJANGO_LLM_KEYS__OPENROUTER`. Docs: `chat-knowledge.md`, `vectorisation.md`.
- **Chat: optional multilingual vectorisation, never one vector per message (universal-chat S8, D6).** New `django_llm.agent.chat.vectors`: `chunking.chunk_lines` (runs of at most 20 consecutive messages, also cut by a token budget; closed chunks never change, the tail is re-embedded when it grows), `embedder.llm_embedder` over `embed_texts` (OpenRouter `openai/text-embedding-3-small`, batches of 64), `rank`, `AbstractChatChunk` (FK to the host's Thread; vector as JSON, pgvector is a host override) and `service.sync_threads` / `sync_pending` (job and backfill, one batched call, a hash decides what is re-embedded) / `search` (owner-scoped, cosine in memory). The ready app gets `cfg_chat.ThreadChunk` (migration `0002`), `ChatConfig.vectors` (default off) with `vector_model`, `vector_chunk_messages`, `vector_token_budget`, `vector_interval`, the `tasks.vectorise` schedule and `GET /cfg/chat/search/`; the kit's `urls(..., search=)` mounts the route for any host; command `chat_vectorise --chunk-model app.Model [--all]`. The knowledge base's optional embedding lane is meant to reuse `chunking`/`embedder`/`rank` (not built). Offline tests use a fake embedder; the live Russian-to-English check (`CHAT_VECTORS_LIVE=1`) is skipped, the OpenRouter key being dead. Docs: `agent/chat/@docs/vectorisation.md`.
- **The ready chat: `ChatConfig` and `django_cfg.apps.tools.chat` (universal-chat S7, D1).** `chat = ChatConfig()` in a project's `DjangoConfig` installs a thin app (label `cfg_chat`: concrete `Thread`/`Message`, tables `cfg_chat_thread`/`cfg_chat_message`, migration `0001`), registers a default kind (`assistant`, from `instructions`/`models`/`max_tokens`/`history_window`/`knowledge_dir`), builds `ChatService` with its policy read from config on every request (`messages_per_day`, `max_text_chars`, `title_models`, kill switch `paused`, site `daily_token_budget` through `TokenBreaker`), mounts the API kit at `/cfg/chat/` (via `django_cfg.apps.urls`), registers the text-free admin, appends a generated-client group `chat` to the host's `openapi_client.groups`, and schedules the reaper (`reap_interval`, default 60 s) and nightly prune (`prune_days`, default 180) through the RQ schedule collector (`ChatConfig.get_rq_schedules()` -> `apps/tools/chat/tasks.py` -> `chat.ops`). Existing hosts (Docman, GPT-Kino, Reforms) keep their tables and never set `chat`. `add_django_cfg_urls` no longer mounts a `django_cfg.*` app of a client group a second time under the api prefix (it duplicated the URL namespace). Docs: `django_llm/agent/chat/@docs/chat-app.md`. Tests: `agent/chat/tests/test_chat_app.py` (15; install, migrate check, scripted turn, kill switch, budget, schedules, tasks, commands, client group, knowledge). The test project turns the app on with `ChatConfig(models=["test/model"])`.
- **Typed SSE stream in the generated TypeScript client (chat-sse-codegen C0-C2).** A `text/event-stream` operation now gets `_<group>/streams.ts` (flat layout `streams.ts`) with `stream<OperationId>(options)`: an `AsyncGenerator` of the 200 frame union (`switch (frame.type)` narrows), the SDK method's options (`path`, `body`, `signal`, `auth`, `fetch`), no retry, and a typed `StreamHttpError` (`status`, `retryAfter` seconds, `problem`) for a refusal before the stream (409, 429 ...) and for a lost connection, thrown after the frames already received. Why it was needed (spike, hey-api 0.99.0): the raw SDK method retried forever, threw an untyped `Error("SSE failed: 409 Conflict")` and, because drf-spectacular types the discriminator as a one-value enum component, the `oneOf` union collapsed to `never`. New `postprocess.discriminator_literals` rewrites those properties to `{type: string, const}` for the hey-api input only (zod, python and go still see the enum; a spec without a discriminated union is passed through byte for byte). New `OpenAPIConfig.generate_sse_streams` (default on; emits nothing for a group without an SSE operation, removes a stale file); `ts_extras` extra `"streams"`. Existing generated clients are unchanged (`make gen` in the reference project: empty diff). `HEY_API_VERSION` stays `latest`. Hosts regenerate when they adopt the kit; the widget's own transport is untouched. Nothing released. Docs: `django_generator/.../ts/README.md` ("streams/"), `chat-api-kit.md` ("Generated TypeScript client"). Tests: `openapi_processor/tests/ts/test_streams.py`.
- **Chat: the S3 items that were deferred (universal-chat S3, second half).** `ChatKind.closing_payloads(deps, final_text) -> payloads | None` sends ui payloads computed from the finished text (Reforms citations) between the last `text_delta` and `done`, stored in `parts`, replayed, held to `payload_kinds`, a failing hook keeps the answer. `ChatKind.after_tool(deps, tool_name, output_text) -> payloads | None` (sync or async) runs after each tool result and may add parts; `stream_agent_run(after_tool=)` is the lower-level seam. `ChatKind.message_constraints=MessageConstraints(max_text_chars, min_text_chars, context_keys, check)` validates the incoming message before the quota and before anything is stored; the kit answers 400 `invalid` + `field`. `ChatService.list_for(nonempty=True, limit=)` (and `only_with_messages`) no longer joins messages: `message_count` is `last_seq`, `last_message_at` is `updated_at` (`ThreadQuerySet.nonempty()`). New `chat.admin` (`ThreadAdminMixin`, `MessageAdminMixin`: read-only, JSON fields, filters, cost and token totals, text-free unless `show_text = True`). One INFO line per run from `ChatService` (`chat run kind= status= model= tokens_in= tokens_out= cost_usd= latency_ms= tools= thread= message=`; no user text, no tool arguments). Backward compatible: every new field defaults to off. Still open: `message_constraints(prefix)` for constraint names, `chat_prune` predicate, `table_pricer`. Nothing released. Docs: `@docs/agent/chat-api-kit.md`, `chat-harness.md`. Tests: `agent/chat/tests/test_s3_deferred.py`.
- **Chat knowledge base: the gaps found adopting it in Docman, GPT-Kino and Reforms (K5).** `Knowledge(tool_prefix="kb_")` renames the four tools, their error sentences and the prompt (`library_search` ...); a host tool with a `kb_*` name now fails the answer with a log line naming the clash and the fix. Front matter with an unquoted `: ` in a value is read as plain `key: value` lines and `kb_check` warns `front-matter-lenient` with the line and key and "quote values that contain a colon"; any other YAML error is an error naming line and key. `check_dir(path, strict=False) -> Report` (`Report.ok()`, `.summary()`), `Page.__str__` / `Page.find_line(sub)`, `chat.testing.instructions_of(model)`, `override(kind, **fields)` (context manager) and `find_line(base, path, text)`. A kind with knowledge on and no folder logs one WARNING per worker naming the expected path; the first build of a disk base logs the resolved root at INFO. `kb_check` ends with one greppable line `kb_check: OK|FAILED errors=N warnings=N files=N ...`. The kb tools already shared `KindLimits.tool_calls_soft` with the host's tools (now tested with a host tool, and documented, including the `Tool.prepare` note). Nothing released. Docs: `@docs/agent/chat-knowledge.md`. Tests: `agent/chat/tests/test_knowledge_core.py`, `test_knowledge_chat.py`.
- **Chat knowledge base eval (knowledge-base K4).** `django_llm.agent.chat.knowledge.evalkit`: `run_index` (deterministic, English-translated query from the fixture) and `run_agent` (real model through `kind_source`) report recall@8 and MRR per language; a gold path missing from the base fails the run instead of shrinking the denominator. Fixture `chat/tests/kb_eval/` (25 nested English files, 40 questions in en/ru/ko/de/es). Agent mode runs only with `KB_EVAL_AGENT=1` and a working OpenRouter key. Nothing released. Docs: `@docs/agent/chat-knowledge.md`. Tests: `agent/chat/tests/test_knowledge_eval.py`.
- **Chat knowledge base: `ChatKind(knowledge=...)`, a folder of markdown every harness chat can search and cite (knowledge-base K1-K3).** New package `django_llm.agent.chat.knowledge`. Files stay the source of truth (no tables, no migrations); `DiskKnowledgeBase` scans the folder (`.md`/`.mdx`/`.txt`, front matter `title`/`description`/`aliases`, `_index.md` per directory) and keeps an in-process SQLite FTS5 index per worker, rebuilt when names, sizes or mtimes change (checked at most every 5 s); heading-aware chunker with absolute line numbers; Porter stemming plus a first-five-letters match for Cyrillic, so a Russian query finds English text through `aliases`. `KnowledgeBase` Protocol, `StubKnowledgeBase`, `ScopedKnowledgeBase`. The kind gets four read-only tools with hard caps (`kb_tree`, `kb_search` <= 15 hits, `kb_outline`, `kb_read` <= 200 lines / 12k chars with a `[lines 1-200 of 3412; continue with start_line=201]` footer), a per-answer read budget (40k chars), "already read" dedup, output wrapped as quotation, and the collapsed folder tree (depth 2, <= 6k chars, deterministic, hash-versioned) in the system prompt after the kind's own text; a "cited file never opened" note is appended to an answer that cites one; the existing soft/hard tool caps apply, and compaction defaults to 6 kept tool results when the kind sets none. `ChatKind.knowledge`: `True`, a subfolder, an absolute path, a base, `Knowledge(source, language, caps, guard)` or a callable of the deps (audience scoping); default off, a missing folder is off, a failing base is logged and skipped. Settings `CHAT__KNOWLEDGE_DIR` (default `<BASE_DIR>/knowledge`) and `CHAT__KNOWLEDGE_LANGUAGE`. Security: HTML comments and zero-width characters stripped on load (lines do not move), no absolute paths / `..` / dotfiles / other extensions, symlinks neither listed nor followed. Commands `kb_check` (front matter, dead links, duplicate titles, oversize, tree size, skipped files; `--strict` for CI), `kb_tree`, `kb_search`. Nothing released; no host adopts it yet. Not built: eval (K4), host adoption (K5), persistent index / Postgres / several roots (K6). Docs: `@docs/agent/chat-knowledge.md`. Tests: `agent/chat/tests/test_knowledge_core.py`, `test_knowledge_chat.py`.
- **Chat hooks and framework gaps (universal-chat S3).** `ChatService(thread_model, policy, *, resolve_thread=, on_answer=, title_job=)`: `resolve_thread(service, actor, id)` is the tenancy rule (default the owner's thread; `None` = the one 404), `create(..., fields={...})` sets host columns, `KindScope.thread` hands `make_deps` the Thread row; `ChatPolicy.check_quota(actor, thread, now)` replaces the daily cap and may raise the new `QuotaExceeded(detail, code=, status=, retry_after=)` (`RateLimited` is its 429 subclass; the kit answers with its status); `on_answer(stored_row, RunOutcome)` runs after the answer is stored and cannot lose it; `ChatKind.title_of(text)` (default collapses whitespace, cuts at 80) and **LLM titles** (`ChatPolicy.title_models`, default off): a cheap model titles the thread after its first answer, off the request (`chat.titles`, daemon thread or the host's `title_job`), first exchange only, in the user's language, fallback to the trimmed text on any failure. Gaps from the three adoption reads: `KindLimits.tool_calls_soft` (soft tool cap), `tool_result_chars` / `keep_tool_results` (compaction, `chat.compaction`), `model_settings`; `ChatKind.capabilities`, `retries`, `transient_context` (per-turn context keys never stored on the thread); `ChatService(policy=callable)` read on every use; `ChatPolicy.available` (503 before anything is stored; kit checks it on send) and `chat.limits.TokenBreaker` (UTC-day site token budget in the cache, settable key); `ChatPolicy.fallback_prices` / `default_price` (an unpriced run is estimated, never NULL) and `models` accepting `"a/b, c/d"` (`parse_chain`). `ServiceUnavailable` moved to `chat.errors` (still exported from `chat.api`). `chat.testing.ScriptedModel` now answers non-streamed requests and records `tools_offered`. The abstract models are unchanged. Deferred items since built (next entry), except `table_pricer`. Nothing released. Docs: `@docs/agent/chat-api-kit.md`. Tests: `agent/chat/tests/test_hooks.py`, `test_api.py`.
- **Chat API kit: `django_llm.agent.chat.api`, the HTTP half of the chat harness (universal-chat S1).** `urls(service, *, operation_id_prefix, tag, trailing_slash=True, default_kind=None, throttle_classes=(), send_throttle_classes=None, authentication_classes=None, permission_classes=None, gate=None)` mounts `GET/POST threads`, `GET threads/<uuid>` and `POST threads/<uuid>/messages` (a host needs about 10 lines). The stream is `text/event-stream` over `ChatService.frames` (widget wire) and is declared in OpenAPI as a `oneOf` of eight frame schemas discriminated on `type` (`ChatFrame`), not excluded; the `type` set is pinned to the shared `events.json` both ways. Every refusal before the stream is `application/problem+json` with the six wire codes (`unauthorized`, `busy`, `invalid`+`field`, `rate_limited`+`Retry-After`, `unavailable`, `not_found`), whichever layer raised it; `ServiceUnavailable` and `gate(request)` give a host a 503 kill switch; DRF throttles become the 429. Operation ids are `<prefix>_threads_list|threads_create|threads_retrieve|messages_create`. New `ChatService.list_for(..., only_with_messages=True)` (the sessions list of the wire contract). New commands `chat_reap` (close `running` answers older than `--older-than`, default 120 s, as `error/failed`) and `chat_prune` (`--days` 180, `--kind`, `--batch`, `--dry-run`; counts only), over `agent/chat/ops.py`. The abstract models are unchanged (no column or help_text change: Docman's `kind` help text names its own `modules.harness.kind`, so aligning it would put a wrong path in the framework, and the `related_name` state change is needed anyway). Nothing released; no host adopts it yet. Docs: `@docs/agent/chat-api-kit.md`. Tests: `agent/chat/tests/test_api.py`, `test_api_schema.py` (snapshot `tests/snapshots/chat_api_openapi.json`), `test_ops.py`.
- **Agent plane: the chat harness (`django_llm.agent.chat`), moved up from docman.** Product-free, engine 1.3.0. `ChatKind` (+ `KindLimits`, `KindContext`, `KindScope`, registry) declares a chat; `kind_source(kind, deps, history, prompt, model=)` runs it on `stream_agent_run(wire="widget")` with limits, the model chain with fall-over, `require_answer`, captured `out.tool_calls`; `AbstractThread` / `AbstractMessage` (+ `ThreadQuerySet`, `MessageQuerySet`) are the persisted-turn tables (seq under a row lock, partial-unique `client_id`, one running assistant message per thread, `for_owner` tenancy, no delete); `DjangoTurnStore` + `ChatService` / `ChatPolicy` give sessions (many threads per user, `message_count`, `last_message_at`), the daily cap, history windows, `begin` / `frames` (flush while streaming, shielded finalize, replay, `reap_stale`). Testing kit `chat.testing` (`scripted` `FunctionModel`, `Conversation`, `free_pricer`, `parse_sse`, `assert_on_wire`) and `chat.pytest_plugin` (the `live` marker: deselected by default, skipped without `ASSISTANT_LIVE=1` and a key). Wire: new `reasoning_delta` / `reasoning_end` frames (`ReasoningDeltaEvent`, `ReasoningEndEvent`; the shared fixture now has them); `ui_payload.data` is any JSON and `UiPayload(kind, data)` with `payload_kinds=` is the open form of the closed payload set; `ToolCallEvent` / `ToolResultEvent` carry `tool_call_id`, `DoneEvent` carries `model` (neither on a wire). Pricing: `price_run(..., offline=, fallback_prices=, default_price=)`, `RunCost.estimated`, async `aprice_run` (thread + timeout, never raises), `ModelsCache.get_model(fetch=)` / `calculate_cost_from_usage(fetch=)`. **Breaking, widget wire only:** an `error` frame now carries the per-code default message instead of the exception text. `RunCost` gained a field (`estimated`, default False). Docs: `@docs/agent/chat-harness.md`, `features/modules/django-llm/chat-harness`. Tests: `agent/chat/tests/`, `agent/runtime/tests/test_harness_additions.py` (a concrete host lives in `tests/chat_harness`).
- **django_mcp: `mcp_tools(...)` and `McpToolProvider` hand registry tools to a pydantic-ai `Agent`; `ProxyTool` passes images through.** Annotations become `ToolMeta` (`meta_from_annotations`), the provider filters by prefix, names or `MCPProfile`, tools run off the loop with the caller's `MCPContext`, image blocks come back as `BinaryContent`. Docs: django_mcp `@docs/remote-frontend.md`. Tests: `tests/test_agent_tools.py`.
- **django_mcp: a non-Django app can publish its own MCP tools, resources, prompts and instructions.** `MCPConfigBuilder.add_remote_manifest(url, secret, prefix="", public=False)` lazily fetches `<url>/mcp-manifest.json` (cached 300 s; a failure hides the app's entries and logs a warning, startup is never affected); its tools run as `ProxyTool`, a POST of `{tool, arguments, user_id}` to `<url>/mcp-call` with a 60 s HS256 bearer (`iss=django-cfg`, `aud`=origin). New `ResourceRegistry` / `PromptRegistry` (text, file or callable); `prompts/list` and `prompts/get` are served, `resources/read` consults the registry before `django://`. `initialize` now sends `instructions` (`set_instructions` on the builder or a profile) and advertises `resources` / `prompts` only when non-empty (before: `prompts` followed introspection and `prompts/list` errored). `/info/` adds `instructions`, `resources` and `prompts`. Docs: django_mcp `@docs/remote-frontend.md`. Tests: `tests/test_remote_manifest.py`.
- **`django_llm.features.transcribe`: transcription that survives content-filter refusals.** `transcribe(duration_s, cut, ask, chain, policy=...)` runs a chain of models per piece. A refusal in a 200 body (`PROHIBITED_CONTENT`, `finish_reason` `content_filter`, `promptFeedback.blockReason`) is `ContentBlocked`: that model is not asked again for the same audio and the next entry is tried; 429/5xx/network wait with backoff and jitter; 401/402 stop at once. A piece blocked by every model is halved (bounded) and the halves run on their own; one still blocked at the floor becomes a `Gap` and the job goes on (`NothingTranscribed` only when no text came out). Finished pieces are kept (`done=`), so a rerun asks only the missing ranges. Every charged call is summed: `Result.cost_usd` is the whole bill, each segment's cost is everything spent on its piece and names the model that answered. `DEFAULT_CHAIN` is data (`defaults.py`), chosen by measurement on a piece Gemini 2.5 refused: qwen3.8-omni-flash, gpt-audio-mini, gemini-3.5-flash-lite, gemini-3.1-flash-lite; `engine="stt"` entries use `/audio/transcriptions` (SDKRouter answers 404 there). Touching halves that failed the same way are reported as one `Gap`. `transcribe_range` runs one piece for callers that store each piece as it is done. Engine 1.2.0. Docs: `features/modules/django-llm/transcription`. Tests: `tests/test_transcribe_plane.py`. Replaces Reforms' private copy.
- **`useQueryState` shallow mode: write a query parameter without a navigation.** `@djangocfg/ui-core` router: `shallow?: boolean` on the hook options and on each `setValue` call (precedence: call, hook, false; default false, so nothing changes). A shallow write goes through `RouterAdapter.shallow?(url, { replace })` (new optional method; default and Next adapters write with the History API and a `null` state, others fall back to `push`/`replace` with bar and scroll off): no RSC request, no loading bar, no scroll. Also `useNavigate().shallow(href, { replace })`. Setters now read the live URL at call time, so two calls in one tick keep both parameters and functional updaters see the earlier write, in normal mode too. Tests in `useQueryState.test.tsx` and `adapters/nextjs.test.tsx`; README section "Shallow writes". Not yet checked in a live Next 16 `force-dynamic` page (no local servers).
- **Agent plane: `bus/events.py` speaks the widget's wire (second dialect), pinned by a shared fixture.** New `RunEvent` (`thread_id`, `message_id`, `client_id`, `seq`, `version=WIRE_VERSION`) and `StatusEvent` (`thinking` / `searching` / `answering`); `DoneEvent` gained `finish_reason` and `replayed`, `ErrorEvent` gained `code` (`unavailable` / `timeout` / `failed`) and `retryable`. Every event has `to_wire()` (the dict `@djangocfg/widget-assistant` decodes: `done` as `tokens_in` / `tokens_out` / `cost_usd` / `finish_reason`, `error` as `code` / `message` / `retryable`; `None` for `tool_call`, `tool_result`, `directive`, `approval_required`, so a public chat cannot leak the tool surface); `encode_sse(event, wire="admin" | "widget")` and `event_from_wire(dict)` are new, `SSE_HEADERS` and `PING` are exported. **Compatibility:** the default dialect is the admin one and `to_sse()` is byte for byte what it was (a test pins it); the admin chat and `django_mcp` are untouched. `agent/bus/tests/fixtures/events.json` is a committed copy of the widget's `src/wire/fixtures/events.json`; `test_wire_contract.py` fails when the copy differs, when a fixture frame does not round-trip or when events built by hand stop encoding to the fixture frames (it skips only where the widget is not beside the tree: the mirror, an installed wheel). The widget fixture's `_note` now names the Python copy. Docs: django_llm `@docs/agent/widget-wire-and-driver.md`, widget `@docs/wire-contract.md` and `server.md`.
- **`stream_agent_run(wire="widget")`, configurable limits, injectable payload types.** `wire="widget"` yields the widget's sequence (optional `run_info` first, `status thinking`, one `status` per phase change per tool call with `phase_for_tool={tool: phase}` or a callable, `status answering` before the text, a blank line between text parts after tool calls, coded `ErrorEvent`, `done.finish_reason` the model's own reason, `stop` when it gives none), never yields tool events unless `deps.expose_tool_events` is set, and ends an approval request with a non-retryable `error{failed}`. `limits=` takes `RunLimits` or a dict (`request_limit`, `tool_calls_limit`, `input_tokens_limit`, `output_tokens_limit`, `total_tokens_limit`, `per_request_input_tokens_limit`); resolution: argument, `deps.run_limits`, `set_default_run_limits(...)` (process default), then `RunLimits()`, whose `request_limit=15` is the old hard-coded value, so nothing changes by default; an unknown key raises `TypeError`. `payload_types=` (or `deps.ui_payload_types`) replaces the closed vehicle/tax-shaped `UI_PAYLOAD_TYPES` for a run (default unchanged); a payload may be a pydantic model or a dataclass with `kind`. `AgentDeps` gained optional `run_limits`, `ui_payload_types`, `expose_tool_events` (`None` keeps the caller's default, so admin chat still exposes tool events). New `runtime/limits.py` and `runtime/errors.py` (`error_code_for`, `DEFAULT_ERROR_MESSAGES`). Tests: `runtime/tests/test_streaming_widget.py`.
- **Agent plane: `RunDriver`, a product-free run driver for the widget's server half.** `agent/runtime/driver.py`: `RunDriver(DriverConfig(ping_s=15, max_run_s=60, flush_s=1), lock=CacheRunLock(), hooks=RunHooks(on_event, on_flush, on_finish))`; `await driver.open(source, run=RunEvent(...), key=...)` returns a run whose `frames()` is the SSE body. It sends `run` first, pings after `ping_s` of silence, ends a run past `max_run_s` as `error{timeout}`, runs `on_finish(RunOutcome)` exactly once in a shielded task whatever ended the run (done, error, timeout, the browser closing the connection, task cancellation, `abort()`) before it sends `done` / `error`, saves partial answers through `on_flush` (about every `flush_s` and after each payload), keeps tool events off the wire (they reach `on_event`), and holds a run lock per key (`CacheRunLock` on Django's cache with an owner-only release and a TTL, `InMemoryRunLock`, or any `RunLock`): a held lock raises `RunBusy` (answer `409 busy`) before an agent is built. `agent_source(...)` is `stream_agent_run(wire="widget")`. Replay by `client_id`, storage, models and rate limits stay with the host. GPT-kino, docman and reforms can drop their copies in a later change; nothing here edits them. Tests: `runtime/tests/test_driver.py` (order, ping cadence, wall-clock cut, consumer gone, cancelled task, abort, error mapping, lock).
- **Docs: `@docs/agent/chat-storage-contract.md`.** The thread/message storage contract the widget's server half needs (fields, constraints, writer, QuerySet methods, lifecycle, reaper, retention, endpoints, tests), written from GPT-kino, docman and reforms. Spec only: the three thread tables differ and the message payload column is `parts` or `widgets`, so no models or migrations are shipped.
- **Logs go to stdout and caches leave the project tree; `import django_cfg` writes nothing.** One resolver, `django_cfg.core.utils.runtime_paths`: log dir = config `logging.log_dir`, then `DJANGO_CFG_LOG_DIR`, then none (stdout/stderr); cache root = config `cache_dir`, then `DJANGO_CFG_CACHE_DIR`, then `platformdirs.user_cache_dir(project)` (`project` = top package of `DJANGO_SETTINGS_MODULE`, else the working directory name). `DjangoConfig` gained `logging: DjangoLoggingConfig` (`level`, `format` `text|json`, `log_dir`) and `cache_dir`. Logging is the generated `LOGGING` dict (`modules/django_logging/config.py`): a file is opt-in (`DJANGO_CFG_LOG_DIR`, or `DJANGO_CFG_LOG_FILE=1` for the per-user log dir), `WatchedFileHandler` so `logrotate` owns rotation (`DJANGO_CFG_LOG_ROTATE=1` keeps in-process daily rotation, single process only), `DJANGO_CFG_LOG_FORMAT=json` for one object per line, `DJANGO_CFG_LOG_LEVEL`. Directories are created at the first write, with a fallback to stdout (logs) or the temp dir (cache) and one warning when not writable. `get_logger()` adds no handlers; the first call no longer clears root handlers, creates `./logs` or crashes in a read-only working directory. The LLM models catalogue, `llm/` response cache, translator cache, vision image cache (was `~/.cache/...`, ignored the env var) and the `FileBasedCache` default (`<cache>/django/<prefix>_<alias>`, was `tmp/django_cache/...`) all resolve through it. `get_logs_path()`, `Environment.logs_dir`, the startup banner and `monitor_status` use the resolver; the first two return `None` when logs go to stdout. New dependency: `platformdirs`. Docs: `features/modules/django-logging`, `deployment/logging`, `features/modules/django-llm/caching`. Tests: `tests/core/test_runtime_paths.py`.

### Changed
- **Docs only: `@djangocfg/widget-assistant` has an `@docs` folder.** `widgets/assistant/@docs` (architecture, wire contract, the Python server half, connecting a new project, customization, troubleshooting) verified against the widget source and the gptkino, docman and reforms servers; the README links to it, and the agent plane `@docs/agent/README.md` points to the server page. It records the framework gaps found: `bus/events.py` is not the widget's wire, no run driver, `stream_agent_run` hard-codes `request_limit=15` and a closed payload set. No code, version or behaviour change.
- **Our own top loading bar replaces `nextjs-toploader` and `nprogress`; query-only navigation no longer scrolls or flashes the bar; a page can switch both off.** New `@djangocfg/ui-core/route-progress` (engine, view, link-click triggers, provider; progress model derived from nprogress, MIT, see its `NOTICE`). `RouterAdapter.push/replace(url, { scroll?, progress? })` (new `RouterNavigateOptions`), also on `useNavigate()`. `NextRouterAdapter` forwards `scroll` to Next (priority: call, page, `defaultScroll`, Next's default) and starts the bar only when the pathname changes, or `progress: true`; every committed navigation ends it, with a 15 s ceiling. The old `nextjs-toploader/app` router compared the full URL with the pathname, so every `?tab=2` change started the bar and never stopped it. `useQueryState` defaults to `scroll: false, progress: false`. `useNavigationBehavior({ scroll, progress })`: a page or section declares it once while mounted; it lives in the app's `RouteProgressProvider`, not in a global, and covers `<Link>` clicks and `useScrollToTop`. `BaseApp progressBar` is `false` (no bar), or `{ color, height, shouldShow(from, to) }`. **Removed:** the `nextjs-toploader` dependency of `@djangocfg/ui-core` and `@djangocfg/layouts`, and the `useRouter` re-export from `@djangocfg/layouts` (it was `nextjs-toploader/app`'s; use `useRouter` from `next/navigation` or `@djangocfg/ui-core/hooks`: the bar now starts on its own). Style hook `#nprogress` is gone; use `--route-progress-color`, `--route-progress-height`, `--route-progress-z`.
- **Assistant column opens and closes with a soft animation.** `@djangocfg/widget-assistant`: the docked column no longer pops in and out. `--assistant-w` is now a registered CSS length transitioned over 380ms on the iOS sheet curve `cubic-bezier(0.32, 0.72, 0, 1)`; the page eases to its new width, the column is revealed from the right edge at full width (no reflow inside) with a short fade, and fixed host elements that read `--assistant-w` follow the same curve. The column stays mounted until the close ends. Resizing by hand and the first paint after a page load are not animated; `prefers-reduced-motion` turns it off. Browsers without `@property` keep the old instant change.
- **`PrivateLayout` top bar no longer hides on scroll.** The bar (phone, and desktop while the sidebar is collapsed) stays in place at every width; the `useNavbarScroll` auto-hide, its `data-hidden` attribute and the slide transition are removed from `PrivateContent`. `PublicLayout`'s own `hideNavOnScroll` is unchanged (off by default). Layouts `@docs` and tests follow. Owner decision 2026-11-05.
- **OTP letter has a constant subject and the code leads the body.** The subject is `🔐 Your login code` for every letter (was `Your OTP code: {code}`, which made each one a new Gmail thread). The template starts with a hidden preheader, `{code} is your {site} login code. Expires in N minutes.`, so the inbox preview and notification banner show the code before the brand name and heading. A stored per-locale `EmailContent` subject is ignored for this letter (`use_stored_subject=False`). Owner decision 2026-11-05; `apps/system/accounts/@docs/notifications.md` updated.
- **Dependencies refreshed across the frontend workspace; no more npm deprecation warnings from our own packages.** `recharts` 2.15.4 (deprecated upstream) -> 3.10.1 in `@djangocfg/ui-core` (`ChartTooltipContent` / `ChartLegendContent` props retyped, the `ChartContainer` API is unchanged); `eslint` 9.39.5 (deprecated) -> 10.14 with `@djangocfg/eslint-config` on `@eslint/js` 10, `typescript-eslint` 8.72, `eslint-plugin-react-hooks` 7 (classic rules only) and an `@eslint/compat` shim around `eslint-plugin-react` (7.37.5 crashes on ESLint 10); `react`/`react-dom` 19.3.1, `next` 16.4.5, `vitest` 5, `lucide-react` 1.68 (brand icons removed upstream: footer social links use inline glyphs; widget peer `lucide-react` is now `1.68.0`), `react-day-picker` 10 (`Calendar` keeps `fromDate`/`toDate`/`initialFocus`), `maplibre-gl` 6, `mermaid` 12, `@stripe/*`, `tsup` 9, plus all minor/patch bumps. `@djangocfg/nextjs` now declares `engines.node >=22` (`chalk` 6, `conf` 16). Deferred: `react-resizable-panels` 4, `react-zoom-pan-pinch` 4, `@dicebear/core` 10 (blocked by `@dicebear/collection`), `typescript` 7 and `@types/node` 26. Remaining transitive deprecations (docs/storybook only): `mathjax-full`, `@xmldom/xmldom`, `tsconfck`.
- **Migration: log and cache locations (one release of fallback).** Before, django-cfg wrote `./logs/` (`django.log`, `djangocfg/*.log`), a `/tmp/djangocfg/debug.log` mirror and `./.cache/` into the working directory. Now: if no override is set and `./logs` or `./.cache` exists in the working directory, it is still used and ONE warning names the env var; the next release drops that fallback and the default becomes stdout / the per-user cache dir. Projects that mount a log folder (`../files/logs:/app/logs`) add `DJANGO_CFG_LOG_DIR=/app/logs` and `DJANGO_CFG_CACHE_DIR=/app/.cache` to their env, no compose change; a container that must keep the models catalogue across restarts points `DJANGO_CFG_CACHE_DIR` at a volume. Anything reading `logs/` on the host (`make logs-*`, agents) needs `DJANGO_CFG_LOG_DIR` first. `DJANGO_LOG_TO_TMP` is ignored (one warning; the mirror is gone). `CMDOP_LLM_CACHE_DIR` still works as the LLM cache folder (one warning); use `DJANGO_CFG_CACHE_DIR`, which names the root of all caches. `django_cfg.LoggingConfig` (never used by `DjangoConfig`) is a deprecated no-op shim, and `DjangoLoggingConfig` lost its unread `enabled`, `file_enabled`, `file_rotation_days` (still accepted and ignored, one warning); both go in the next release. `django_monitor` events are JSON lines on the `django_cfg.monitor` logger (stdout, plus `<log dir>/djangocfg/monitor.log` when a log dir is set). Per-module `djangocfg/<module>.log` files are gone: one `django.log` for the `django_cfg` logger.

### Fixed
- **django_generator: `fix_go_imports` no longer rewrites clean files.** It stripped every import line and rebuilt the block without indent, so each `make gen` dirtied every generated Go file (117 lines of whitespace in gptkino) even when no path needed the module prefix. Lines now stay as written and only a bare path gets the prefix, with its indent kept. Tests: `tests/django_generator/test_go_imports.py`.
- **`@djangocfg/widget-assistant` styles: the widget's `@source` lines work in an installed tree and in the monorepo.** `styles/widget.css` pointed at `../../../../node_modules/@djangocfg/widget-*`, which matched nothing in either layout (checked with Tailwind 4.3: no widget class was scanned), so every host needed its own `@source`. The paths are now relative to the file (`../../../widget-chat|kit|media/src` for an installed flat or hoisted tree, `../../../chat|kit|media/src` for the monorepo; a path that matches nothing is harmless). Verified against a flat install, a pnpm install and the monorepo layout. A strict pnpm install without hoisting still cannot reach `widget-kit` / `widget-media` from the package: keep the host `@source "../node_modules/@djangocfg/widget-*/src"` and make the three widgets direct dependencies (widget `@docs/connect.md`, `@docs/troubleshooting.md`).
- **`toon_format` floor is the stable `1.0.0`, so a project no longer has to name `toon-format` to lock django-cfg.** The floor was the pre-release `0.9.0b1`, and `uv` considers pre-releases only for a package the project's own `pyproject.toml` requires; without that line it silently resolved django-cfg 2.2.101 (which lacks symbols the settings import) and the first `uv sync` of a new project failed with `ImportError: FileCleanupConfig`. `toon_format` 1.2.0 `encode`/`decode` verified. Both pins ([ai] and [full]) are now `>=1.0.0,<2.0`. Projects can drop their `toon-format>=0.9.0b1` line after the next release.
- **`BaseApp` warns in dev when the app has no web manifest.** With `pwaMeta` on, a one-time `console.warn` after mount points to `app/manifest.ts` with `createManifest` (`@djangocfg/nextjs/pwa/manifest`) when `<head>` lacks `<link rel="manifest">`; production is untouched. Layouts `@docs/PWA_AND_MOBILE.md` got a Manifest section (template, icons, server viewport, prod checks).
- **Installed iOS PWA no longer stops short of the screen height.** With `viewport-fit=cover` and a translucent status bar, iOS standalone reports `100%` / `100svh` / `100dvh` as the screen minus the top inset, so the `PrivateLayout` shell (and the locked `html`/`body` rule, which used `height: 100%`) ended early with a dead band at the bottom. `--app-height` is now `100lvh` in standalone/fullscreen from the first paint, and new `syncAppHeight()` (ui-core, mounted by `UiProviders`) measures the real height (largest of `lvh`, `dvh`, `innerHeight`, capped at the screen) and publishes it on `<html>`; the private shell lock uses `var(--app-height)`, and the provider wrapper, sidebar wrapper/rail and `ForbiddenState` read it instead of `svh`. Docs: layouts `@docs/PWA_AND_MOBILE.md`.
- **Apps no longer need to set the installed-app meta tags.** `BaseApp` (prop `pwaMeta`, default on) adds `viewport-fit=cover`, `apple-mobile-web-app-capable`, `mobile-web-app-capable` and `apple-mobile-web-app-status-bar-style=black-translucent` to `<head>` through an inline script when the app's own `viewport`/`metadata` lack them (never overrides). `createViewport()` (`@djangocfg/nextjs`) now defaults to `viewportFit: 'cover'`. Per-app `viewportFit: "cover"` in `layout.tsx` can be removed after upgrading.
- **`PrivateLayout` product name is bolder and links home.** Brand name is semibold (desktop 16px, was 14px medium; phone 14px semibold), logo 32px desktop / 28px phone. The brand (sidebar header, phone drawer header) and the default top bar title link to the new `header.href` (`header.href` > `sidebar.homeHref` > the auth `routes.defaultCallback` AppLayout/BaseApp configures (the private landing page, default `/private`) > `/` outside the auth provider) through the router `Link`; the drawer closes on click. Custom `brand` nodes and `topBar.title` are not wrapped. Without `header.title` the brand shows the `project` name `BaseApp` already receives (new `useProjectName` / `ProjectNameProvider`, safe outside `BaseApp`); with neither, only the monogram shows (the old "Dashboard" default is gone).
- **One account menu for public and private layouts.** New shared `components/account/` (`AccountMenu`, `AccountAvatarTrigger`, `AccountFooterTrigger`, `AccountInline`, `useAccountModel`, `useAccountMenuItems`, `UserAvatar`). The sidebar footer, the private bar avatar, the public navbar `UserMenu` (desktop and mobile drawer) and `AccountMenuButton` all render it; same groups, i18n keys, sign-in button for guests (`authPath`), plan subtitle and initials fallback. `UserMenu`, `UserAvatar`, `useAccountMenuItems` and every prop stay exported; the duplicated private/public menu code is removed.
- **`PrivateLayout` sidebar toggle no longer hover-opens the sidebar.** Only the left screen edge zone peeks it open; the toggle shows its tooltip, click and Cmd/Ctrl+B are unchanged.
- **`PrivateLayout` phone drawer header has no toggle button.** Below md the header is the brand only (same 48px + safe-top row, brand on the nav icon column). The drawer closes by backdrop tap, swipe, Escape, or navigating; the ui-core drawer keeps its `sr-only` title and description. The desktop sidebar toggle and the bar toggle are unchanged.
- **`@docs` of the layouts package refreshed** (unified bar, shared account menu, brand and home resolution, tokens, drawer, touch targets, decisions, testing and device checklist) with a new `MIGRATION.md` for apps upgrading from 2.1.607.
- **`PrivateLayout` sidebar toggle has no tooltip.** The desktop tooltip was removed (and the native `title`); the button keeps its `aria-label`, focus behaviour and the Cmd/Ctrl+B shortcut. Hover-open stays only on the left screen edge zone. Applies to the sidebar header toggle and the top bar toggle.
- **`PrivateLayout` phone drawer is compact.** Header is the top bar's row (48px under `--safe-top`, toggle first at the bar's position, brand centred), nav rows are 40px (was 44) with a 44px hit area via `::after`, 20px icons, half the air between groups, 48px footer account. Desktop unchanged.
- **`PrivateLayout` on a phone has a plain auto-hiding top bar.** On a phone (below md) the layout draws a plain top bar: `safe-top + 3rem` tall (`--layout-bar-height`, `0px` from md up and without a sidebar), `bg-background` with a 1px bottom border, holding the sidebar toggle (the same ghost button as in the sidebar header) and `header.title`. It overlays the content column and slides away (`transform`, 200ms) on scroll-down and back on scroll-up or at the top, using the same `useNavbarScroll` policy as `PublicLayout` driven by the content scroller; it stays while the drawer is open, a field has focus, or the page is not scrollable. Content starts below the bar for every page, so pages do nothing; apps may use `--layout-bar-height` to offset their own sticky elements. `PrivateLayout` takes `topBar={{ title, actions }}` (types: `PrivateTopBarConfig`): `title` replaces `header.title` in the bar, `actions` is a ReactNode on the right (vertically centred, never shrinks the toggle; the title takes the rest and truncates). Recommended actions are compact ghost icon `Button`s (36px); several are fine, keep them few. The global 44px mobile min-size is lifted inside `[data-sidebar="topbar-actions"]` (the 44px hit area is kept by an invisible pseudo-element). The toggle stays left and is not configurable. The bar is now ONE component at every width, shown whenever the sidebar is not visible (always on a phone, on desktop while collapsed, never while docked); auto-hide stays phone-only, `--layout-bar-height` is `0px` only when no bar is shown, and the old desktop toggle-only strip is gone. A signed-in user gets an account avatar at the right end of the bar (same menu as the sidebar footer, opened downward and right-aligned); the phone drawer then has no footer account. `topBar.account={false}` removes the avatar and keeps the drawer footer account. Replaces the floating trigger and its tokens (`--layout-trigger-inset/-gutter/-row/-zone`, `LAYOUT_TRIGGER_*`); apps can delete every trigger-gutter padding. `useNavbarScroll` gained `target` and `respectReducedMotion` options.
- **Error screen showed two "Refresh Page" buttons, and stale tabs crashed after a deploy.** `BaseApp`'s fallback rendered a filled button wired to `reset()` and an outlined one wired to `location.reload()`, both labelled `layouts.errors.refreshPage`. There is now one shared `AppErrorFallback` with a single hard-reload button (also used by `ErrorBoundary`). New: a chunk-load failure (ChunkLoadError, "Loading chunk N failed", dynamic import failure, cancelled `/_next/static` fetch) triggers ONE automatic reload instead of the fallback, via `Boundary`, `UiProviders` window listeners and `<ErrorLayout error={error} />` for `global-error.tsx`; loop guard in `sessionStorage` (`djangocfg:chunk-reload-at`, 30 s). Helpers in `@djangocfg/ui-core/lib`. Hosts with their own stale-chunk copy can delete it; `global-error.tsx` should pass `error` to `ErrorLayout`. Docs: `frontend/recipes/error-screens`, `layouts/components/errors/README.md`.
- **`PrivateLayout` mobile drawer no longer clips in an installed iOS PWA.** The sidebar drawer was `h-[100dvh]`; in
  standalone mode `100dvh` can differ from the visible area (top inset missing, bottom row cut under the home
  indicator, grey strip). Its height is now pinned with `fixed inset-y-0` (`!h-auto`), so it matches the real viewport
  in a browser tab and in a PWA; the width stays 88vw (max 22rem) with the dimmed tap-to-close strip. Header and footer
  padding is safe-area aware on all sides; side padding on phones is tighter (container 6px + row 8px). Desktop
  sidebar unchanged. Docs: `PrivateLayout/README.md`.
- **Display mode (PWA) detection.** `useDisplayMode()` / `useIsPwa()` (`@djangocfg/ui-core/hooks`: `display-mode`
  media query, iOS `navigator.standalone`, Android TWA referrer; SSR value `browser`, one shared listener set).
  `UiProviders` (hence `BaseApp`) sets `<html data-display-mode>`. New CSS tokens `--safe-top/right/bottom/left` (read
  `--app-safe-*` first, then `env(safe-area-inset-*)`) and `--app-height` in ui-core `base.css`. Hosts need
  `viewportFit: "cover"`; see `PrivateLayout/README.md`.
- **Mobile sidebar drawer: pinned header/footer, one scroller, tighter gutters.** `DrawerContent` wrapped every child in
  a padded (`px-5`) scroll container, so the whole drawer scrolled as one block with 20px extra side gutter. New
  `DrawerContent bare` renders children directly; the sidebar drawer uses it and is `overflow-hidden`, so only the nav
  scrolls (header gets a hairline once scrolled; footer has a full-width top border and its own background). Phone
  gutters: 8px container, 10px rows (icon column and logo at 18px), group hairlines inset to the gutter, brand row at
  least 1.25rem / safe-top + 0.5rem from the top. Desktop sidebar unchanged.
- **Overlay primitives read the PWA tokens.** `Drawer`, `Sheet`, `Dialog`, `Toaster` and `Boundary` use `--app-height`
  and `--safe-*` instead of `100vh` / bare `env()`; side drawers and sheets are pinned with `inset-y-0 h-auto`;
  sheets, drawers and fullscreen dialogs pad by the safe areas, toasts are offset by them (all zero without
  `viewport-fit=cover`, so browsers and desktop are unchanged). Docs: "Build a PWA-safe overlay".
- **Native-app touch behaviour by default.** ui-core base styles: `touch-action: manipulation` (no double-tap zoom,
  pinch kept), `text-size-adjust: 100%`, no tap highlight, text fields floored at 16px on `pointer: coarse` (no iOS focus
  zoom; `.input-compact` opts out), and in an installed app no overscroll bounce and non-selectable chrome (`.selectable`
  / `.app-chrome` utilities). `createViewport()` no longer sets `maximumScale: 1` (pinch-zoom
  is now allowed, WCAG 1.4.4); `createViewport({ appLike: true })` restores `maximumScale: 1` + `userScalable: false`.
  New opt-in `useBlockGestureZoom()` (ui-core hooks). Behaviour note for existing projects: inputs below 16px grow to
  16px on phones. Docs: `frontend/recipes/pwa-and-mobile-layout`, `pwa-behaviour-checklist`.
- **`PrivateLayout` no longer makes the document scrollable (installed PWA rubber-band).** The shell was
  `SidebarProvider`'s `min-h-svh`, so content grew the page past the viewport (top bar + content > viewport) and holding
  the top bar and dragging moved the whole document. The shell is now `h-[var(--app-height,100dvh)] overflow-hidden`
  (top bar `shrink-0`, content `flex-1 min-h-0` scrolling on its own), `<html data-private-shell>` is set while it is
  mounted and base.css locks html/body in installed display modes for those pages only. Behaviour note for existing
  projects: scrolling now happens in the content region (sticky/`window.scrollTo` relate to it; the layout resets it on
  `pathname` change); remove `min-h-screen` / `h-screen` wrappers around the layout.
- **Storybook: Display mode and Safe area toolbar items** (browser vs installed app, iPhone island insets) plus phone
  viewports; PrivateLayout PWA stories. Display mode `Auto (real)` is the default and emulation is ignored on a real touch
  device (no fake island over the real browser chrome). The `... Drawer Open` stories now open the drawer. Docs:
  `apps/storybook/README.md`.
- **`PrivateLayout` on a phone: top bar and drawer metrics.** (1) Pages with `contentPadding="none"` (full-height panes)
  had no room reserved for the sidebar trigger, which floated over their first row and left their top controls under
  the status bar; the trigger now sits in an in-flow 48px top bar (safe-area aware) whenever the sidebar is not docked,
  padded page or not. (2) Sidebar rows used `text-base` (desktop) and `text-lg` (drawer) because the geometry
  classes overrode the row default; rows are now `text-sm` with 16px (desktop) / 18px (drawer) icons, group labels
  `text-xs`, side padding 8px (was 10-12px), larger vertical padding, drawer header/footer at least 1rem from the
  safe-area edges, no-icon rows aligned to the label column. Docked and collapsed desktop keep their behaviour.
  Docs: `PrivateLayout/README.md` (Sidebar states). Hosts need `viewportFit: "cover"` for the safe-area insets.
- **Sign-in buttons no longer vanish after one failed request.** `useOAuthProviders` (`@djangocfg/api/auth`) asked
  `GET /cfg/accounts/oauth/providers/` once, with no retry; one dropped mobile connection or a gateway 502 left the list
  empty for the whole visit, so `AuthLayout` rendered only the email form (no provider buttons, no "or" divider) while
  the same site showed them on desktop. The request is now retried twice (after 1s and 2s); `isReady` stays false
  meanwhile, so the form keeps the room of the buttons, and the hook gives up as empty only after the retries fail.
  No config or prop change.
- **OAuth / MCP-consent origin gate follows the subdomain rule.** `Site.accepts()` matched the request origin exactly
  against `site.origins`, so a site declaring only `https://my.carapis.com` answered `{"error":"origin_not_allowed"}`
  to sign-in started from `https://carapis.com`, although hosts, CORS and CSRF already accepted every subdomain
  (2.3.372). `accepts()` now reuses `registrable_domain`: an origin is accepted when it is declared, or (with
  `accept_subdomains`, default True) its host shares the registrable domain of one of the site's own web origins and the
  scheme and port are equal. Decisions: (1) both directions, because the existing rule keys on the registrable domain
  (`.carapis.com` plus `*.carapis.com`), so declaring `my.carapis.com` accepts `carapis.com` as hosts/CORS/CSRF already
  did; (2) `api.*`, `mcp.*` and the site's API host are not web origins, as in site derivation; (3) only the site's own
  origins count, so sites of a multi-site Django do not accept each other; (4) public suffixes are never opened;
  (5) `accept_subdomains=False` restores exact matching. Covers `resolve_redirect_uri` and every `site.accepts` caller.
  **Security note:** this is django-cfg's gate only; Google and GitHub still require each redirect URI registered
  exactly. `manage.py oauth_check` now prints, per provider, the origins accepted by the subdomain rule and the URI
  pattern to register before users sign in from them. A project that added its apex to `security_domains` only for
  sign-in can remove that entry.

### Changed
- **JWT: long sessions are the default.** `JWTConfig()` now gives 1-year access and refresh tokens (was 30 minutes
  access). `JWTConfig.long_lived()` and `JWTConfig.short_lived(access_minutes=30)` name the two postures. To keep short
  access tokens set `access_token_lifetime_minutes=30`.
- **MCP connect widget is grouped by app** (`@djangocfg/widget-mcp`, next release). The first screen is one tile per app
  (Claude, ChatGPT, Codex, Gemini, Notion, Perplexity, Cursor, VS Code, LM Studio, Goose, Other app); opening an app lists each
  way to connect it (Claude: web/desktop connector and Claude Code). Replaces the separate "Code editor or terminal" tile.
  Docs: `connect-assistants`. `initialView` values changed (see the widget CHANGELOG).

### Added
- **CORS: custom request headers need no setup.** A preflight from an origin that is already trusted (the response
  carries `Access-Control-Allow-Origin`) now gets the headers it asks for in `Access-Control-Allow-Headers`, next to
  the static list, plus `Vary: Access-Control-Request-Headers`. Before, a frontend sending `X-Holder`,
  `X-Content-SHA256` or `Idempotency-Key` was blocked with an opaque "CORS error" and the server saw only
  `OPTIONS 200`. New `CorsRequestHeadersMiddleware` sits between `PublicAPICORSMiddleware` and `CorsMiddleware`;
  untrusted origins are never touched, `*` is never sent, names are sanitized (token syntax, 64 names, 100 chars).
  New `cors_extra_headers: List[str]` extends the default list; `cors_reflect_request_headers=False` is strict mode
  (static list only). Each reflected `(origin, header)` logs once at INFO, strict mode logs a WARNING once.
  `idempotency-key` joins the default list.
  **Behavioural note:** projects that set `cors_allow_headers` get the reflection too. It is strictly more
  permissive only for origins that were already trusted; set `cors_reflect_request_headers=False` to keep the old
  fixed behaviour. Projects that replaced `cors_allow_headers` just to add a header can drop that workaround.
  No migration needed.
- **`manage.py logout_all [--email X] [--dry-run]`** ends sessions everywhere: blacklists live refresh tokens, sets
  the new `CustomUser.tokens_valid_after` (migration `0028`) and clears Django sessions. `JWTAuthenticationWithLastLogin`
  rejects access tokens issued at or before that cutoff (`token_revoked`), which the refresh-token blacklist alone
  could not do. API keys are untouched.

### Security
- **MCP OAuth: the consent page shows where the grant goes, and codes are single use.** The signed consent
  request (now uncompressed) carries `dest`, the validated redirect host (`claude.ai`, `127.0.0.1:3118`,
  `cursor://anysphere.cursor-mcp`), next to the client name; `<McpConsent>` shows both from that signed value
  ("Sends the result to ..."). Authorization codes are spent once through the Django cache (`cache.add`, no
  table); an unwritable cache refuses the exchange. Refresh tokens stay reusable; Renew key revokes them.

### Fixed
- **`POST /cfg/monitor/ingest/` answered 500 to a browser-like `Accept` header.** `MonitorIngestViewSet` had no
  `serializer_class`, and DRF's browsable-API renderer (picked for `Accept: text/html`) asks the view for one:
  `AssertionError: 'MonitorIngestViewSet' should either include a serializer_class`. The view now declares
  `serializer_class = IngestBatchSerializer` and answers JSON whatever `Accept` says. URL and payload are unchanged;
  a malformed body is a 400. Every other `GenericViewSet` in the package already declares its serializer.
- **Storage cleanup: a rollback no longer loses files, and shared files are kept.** `FileCleanupMixin.delete()`
  and `FileCleanupQuerySet.delete()` delete files in `transaction.on_commit` (they used to delete first, so a
  rolled-back delete lost the files while the row survived). The `post_delete` signal now honours
  `check_shared_files`, as its docs always said.
- **MCP: `McpKey` / `McpGrant` reverse names no longer clash with a project's own MCP models.** The user
  relations were `mcp_keys` / `mcp_grants` (Django check E304/E305 in projects that keep models of the same
  name); they are now `django_cfg_mcp_keys` / `django_cfg_mcp_grants` (in `0002` itself).
  The index names (`mcp_key_user_revoked_idx`, `mcp_grant_user_revoked_idx`, check E030) are prefixed
  `dcfg_` for the same reason: PostgreSQL index names are schema-wide, so a migration that creates
  `mcp_key_user_revoked_idx` fails when the project already has one.

### Added
- **MCP OAuth: `enable_public_profile(oauth=True)` needs no consent URL.** The approval page defaults to the Settings
  dialog of `DjangoConfig.site_url` (`<site_url>/#settings/mcp`); `oauth_consent_url` stays as an override and still
  enables OAuth on its own. `ProfileBuilder.enable_oauth()` takes `consent_url=None` too.
- **Storage delete sync (opt-in): row deleted, files in R2/S3 deleted, CDN purged.** `FileCleanupConfig(outbox=True)`
  writes `StorageDeletion` rows inside the transaction (new table, migration `0001` of `django_cleanup`); a worker
  (RQ schedule, `manage.py storage_outbox --drain`) deletes the files with retries and backoff, behind an
  `allowed_prefixes` allowlist, with `dry_run` and a `queue_only` mode for files another service owns.
  `register_owned_files(Model, keys=...)` declares prefixes or keys a model owns; `StorageConfig(cdn=CDNPurgeConfig(...))`
  purges the URLs from Cloudflare afterwards; `manage.py storage_orphans` reports files no owner claims (report only).
  Nothing changes until a project opts in. See `modules/django_cleanup/@docs/outbox.md`.
- **MCP tool hints.** `MCPTool` gains `read_only`, `destructive`, `idempotent`, `open_world`
  and `title`; `tools/list` now carries `title` and all four `annotations`. Claude and ChatGPT
  run a read-only tool without a per-call confirmation, so every built-in reader
  (`query_model`, `get_object`, `list_apps`, `aggregate_model`, ...) is marked, and a tool that
  declares nothing stays a prompting writer. `@mcp_tool` and `mcp.tool` accept `read_only=True`.

### Removed
- **MCP: the `McpKey` / `McpGrant` tables, the keys / connections / usage manage API (`django_mcp/manage`),
  the `AccessStore` protocol, `access_store=` / `stateful_oauth=`** (shipped in 2.3.352 to 2.3.354; one user,
  gptkino). The MCP credential is now the user's existing `UserAPIKey`. Migration `0003` drops
  `django_cfg_mcp_mcpkey` and `django_cfg_mcp_mcpgrant`; keys issued from them stop working, users copy
  their `UserAPIKey` instead. No new tables.

### Changed
- **MCP: the default key validator is the user's `UserAPIKey`.** `enable_public_profile()` with neither
  `key_validator` nor `public_keys` (and `ProfileBuilder.use_user_api_keys()`) accepts the key UUID, as
  `Authorization: Bearer` or `X-MCP-Access-Key`, through `auth.validate_user_api_key` (one indexed lookup,
  active users only). "Renew" is the existing `POST cfg/accounts/api-key/regenerate/`. An explicit
  `key_validator` is unchanged; the `operator` profile never accepts user keys.
- **MCP OAuth: tokens carry the key generation (`kg`).** Access and refresh tokens hold
  `UserAPIKey.reissued_at` in integer microseconds (0 when never regenerated or no key row); a token whose
  generation differs from the user's current one is refused (refresh answers `invalid_grant`), so
  regenerating the key ends every OAuth connection too. Tokens without `kg` count as generation 0, so
  tokens issued before this release keep working until the user regenerates. One extra query per check.
- **One browser-storage key scheme: `cfg.<area>.<name>`** (lower case, dots,
  `snake_case`). The generated client gains `helpers/keys.ts`: a registry of every
  key (`CFG_KEYS`, `CFG_FAMILIES`), guarded `read/write/remove` (SSR, private
  mode, quota), `clearAll()` for sign-out, `onChange()` for other tabs, and
  `createStorage('<owner>')` for apps (`storage.key('area', 'name')`).
  `helpers/auth.ts` uses it; the DPoP IndexedDB is now `cfg.auth.dpop`.
  Exported light from `@djangocfg/api/storage`. Rules: `@djangocfg/api/@docs/STORAGE_KEYS.md`.
  - **Breaking, no migration:** old keys (`cfg.access_token`, `auth_email`,
    `user_profile_cache`, `fm_session_id`, `djc.chat.*`, …) are not read. Signed-in
    users sign in once; the DPoP key is regenerated.
  - The Django-served admin bridge (`auth_token`, `refresh_token`), `NEXT_LOCALE`
    and `sidebar_state` keep their names.

### Added
- **MCP: OAuth 2.1 sign-in on a profile** (`django_mcp/oauth.py`). Claude (web,
  Desktop), ChatGPT, Claude Code, Codex, Cursor and VS Code connect by URL and
  sign in, with no pasted key. `mcp.enable_public_profile(..., oauth_consent_url=
  "https://my.example.com/mcp/connect", oauth_issuer="https://mcp.example.com")`
  or `ProfileBuilder.enable_oauth()`.
  - Stateless: client ids (RFC 7591), consent requests, codes and tokens are
    signed with `SECRET_KEY`; nothing is stored, no migration. PKCE S256 only.
  - Discovery at the host root: `/.well-known/oauth-protected-resource[/<path>/]`
    and `/.well-known/oauth-authorization-server`; endpoints under the profile
    (`<path>oauth/register|authorize|approve|token/`). A 401 on that profile
    answers `WWW-Authenticate: Bearer resource_metadata=...`.
  - The project's frontend identifies the user: `authorize` redirects to
    `consent_url?request=<signed>&client=<name>`, the page signs in with
    django-cfg auth and POSTs `{request, allow}` to `oauth/approve/` with the
    user's JWT, then navigates to the returned `redirect_to`.
  - Redirects only to the clients' own callbacks (claude.ai, chatgpt.com,
    platform.openai.com, `cursor://anysphere.cursor-mcp`, vscode.dev) or
    loopback. Checked against Claude Code 2.1 and Codex 0.146 on a local
    server; a test per client's callback shape.
  - The metadata does not advertise `authorization_response_iss_parameter_supported`
    (`iss` is still sent): Codex requires `iss` when it is advertised, then drops
    it from its loopback callback and fails the sign-in.
  - Guide: `@docs/connect-assistants.md` and the docs site page "Connect
    assistants" (backend line, consent-page contract, install-button links).
    A ready-made consent page and install widget for the frontend packages are
    not part of this release.
  - Every MCP endpoint now also reads the credential from `Authorization:
    Bearer`, so a per-user key works in bearer-only clients too.

### Changed (BREAKING)
- **MCP: authorisation is mandatory, there is no anonymous mode.** No MCP route
  answers without a credential: JSON-RPC, `GET <path>info/` and the agent chat
  all return `401` (`WWW-Authenticate: MCPAccessKey`) without a valid
  `X-MCP-Access-Key`. The only unauthenticated MCP routes are OAuth discovery
  and sign-in on a profile that enables OAuth (see Added).
  - Removed `access="anonymous"` (`MCPProfile`, `MCPConfigBuilder.profile`),
    `public_info` (config, profile, `set_public_info`) and
    `enable_public_profile(operator_public_info=...)`. Each raises `ValueError`
    with migration advice.
  - An enabled config with no key (no `access_key`, no `extra_keys`) now raises
    at build instead of serving open. `/info/` always needs the key.
  - `enable_public_profile()` needs a key path and the profile is key-protected:
    `key_validator="pkg.mod.func"` (`callable(key) -> user | True | None`, for
    per-user API keys in the project's DB) and/or `public_keys={"label": key}`.
    It serves only `public = True` tools; operator keys do not open it.
  - New `MCPProfile.key_validator` / `ProfileBuilder.set_key_validator`, and one
    credential check (`django_mcp/auth.py`) shared by JSON-RPC, `/info/` and
    agent chat. Static keys, `extra_keys` and `service_username` work as before.
  - Migration: keep `set_access_key()` for the operator, and give the public
    surface keys, e.g. `mcp.enable_public_profile(key_validator="api.mcp.validate_key")`.

### Added
- **`admin_access`: where the Django admin lives and who may reach it.**
  `AdminAccessConfig` on `DjangoConfig.admin_access`. Scanners probe `/admin/`
  on every host; the location and availability are now core-config settings,
  not a line hard-wired in each project's `urls.py`.
  - `enabled` (default `True`): `False` mounts nothing, so the route answers
    404, nothing links to it, and management commands are unaffected.
  - `path` (default `"admin/"`): the URL prefix. No leading slash, ends with a
    slash, URL-safe characters only, no `..`; anything else fails at startup.
  - `allowed_networks` (default `[]`): a CIDR allowlist (IPv4/IPv6). When set,
    any request under the admin prefix from outside it gets **404, never
    403**. The address is `REMOTE_ADDR`, which `RealIPMiddleware` rewrites from
    `CF-Connecting-IP` / `X-Forwarded-For`; that is only trustworthy when the
    app is reachable through the proxy alone. Defence in depth: the primary
    control belongs at the proxy (Traefik, Cloudflare).
  - Env, the same nested `__` style as `DATABASE__URL`: `ADMIN_ACCESS__ENABLED`,
    `ADMIN_ACCESS__PATH`, `ADMIN_ACCESS__ALLOWED_NETWORKS` (comma-separated or a
    JSON list). It works for a project that never mentions `admin_access`; a
    value passed in code wins over env.
  - One-line wiring: `*admin_urlpatterns()` (`from django_cfg import
    admin_urlpatterns`) replaces `path("admin/", admin.site.urls)` and returns
    `[]` when disabled. The old line keeps working untouched.
  - The framework's own staff surface under `/cfg/admin/` (dashboard tabs, the
    Next.js admin) follows the same `enabled` / allowlist rules.
  - New system checks, both warnings: `django_cfg.W011` (production with the
    admin at the default `/admin/`; suggests `secrets.token_urlsafe`) and
    `django_cfg.W012` (`admin_access` asks for a path or `enabled=False` but the
    admin is still mounted elsewhere, e.g. a hard-coded `path("admin/", ...)`,
    so setting only the env var would change nothing). **W011 becomes an error
    in a later release**; existing projects start unchanged today.
  - Anything that assumed `/admin/` now reads the configured prefix:
    `PublicEndpointsMiddleware`, admin login notifications, `NoIndexMiddleware`
    (no-store), dashboard quick actions, the `get_admin_url` tag, extension
    navigation links, the URL list and endpoint-status tools, the Unfold search
    and badge callbacks. With the admin disabled the dashboard quick actions
    omit it and `get_admin_url` returns `""`.
  - **Behaviour change:** `/cfg/admin/dashboard/` (staff-only, opened inside the
    admin) now answers 404 to anyone who is not staff, where it used to redirect
    to `admin:login`. The redirect failed with the admin disabled, and with a
    moved admin it told an anonymous scanner where the admin lives.
- **IndexNow — push changed sitemap URLs to Bing, Yandex, Seznam, Naver.**
  `IndexNowConfig` on `DjangoConfig.indexnow`. It reads the registered
  sitemap sources with the feed's template and fields, so IndexNow never
  announces a URL the sitemap would not list. How a run decides what to send
  is under **Changed** below.
  - RQ schedule, registered from the config (`schedule_interval`, `0` to turn
    it off). `manage.py indexnow_submit` runs it by hand.
  - `extra_urls`: a dotted path to `callable(since) -> list[str]` for pages
    the sitemap cannot see, such as deleted ones, 410s or redirects.
  - The key file is served at `/cfg/sitemap/indexnow/<key>.txt`; any other
    name returns 404. `indexNowKeyRewrite()` in `@djangocfg/nextjs/config`
    rewrites `/<key>.txt` to it, so the key lives in one place.
  - `indexnow.submit(urls)` never raises: it is meant for request paths, and
    an engine being down must not fail a save. `submit_changed()` raises
    `IndexNowError` on a refusal, so a failing job shows as failed.
  - Several sites on one backend: `sites=[IndexNowSite(host=…,
    source_suffix="-caribbean"), …]`. Each host takes its own sources and is
    submitted in its own request; one key serves every host.
  - Replaces two hand-rolled copies, one in carapis and one in cmdop, that
    had already diverged on error handling and on where the key lived.
- **Geo: selective country population.** `GeoConfig` gains a `countries`
  allow-list of ISO2 codes; `geo_populate` also accepts `--countries BB,BS,KY`
  (the flag overrides the config). States and cities cascade automatically to
  the selected countries.
  - Previously the only option was the full dr5hn dataset — ~250 countries,
    ~5,000 states, ~150,000 cities. A project serving a handful of markets had
    to import all of it, which bloats the database and lets reverse-geocoding
    resolve assets to places outside its coverage.
  - Measured on a five-market Caribbean project: **5 countries / 62 states /
    514 cities** instead of the full set.
  - Unknown ISO2 codes raise rather than silently importing nothing, and
    `GeoConfig` rejects country *names* (`"Barbados"`) at validation time — a
    typo that quietly dropped a market would otherwise surface much later as
    unresolved cities.
  - Default behaviour is unchanged: an empty list imports everything.

- **Payments engine — `django_cfg.apps.payments`** (production-lifted from a
  live SaaS): config-gated app driven by `PaymentsConfig` on `DjangoConfig`.
  - Provider abstraction (Stripe-first); the SDK is an optional extra:
    `pip install django-cfg[payments]` (also included in `[full]`).
  - One-time checkout with idempotency keys, zero-amount rejection, and
    TOCTOU race recovery.
  - Webhook ingestion: signature verification (secret rotation via
    comma-separated `STRIPE__WEBHOOK_SECRET`), `PaymentEvent` log with
    `event_id` idempotency, replay command.
  - Refunds, stuck-payment reconciliation (missed-webhook safety net), and a
    `payments_doctor` health report.
  - Host seams instead of hard couplings: swappable **owner model**
    (`CFG_PAYMENTS_OWNER_MODEL`, AUTH_USER_MODEL mechanism), **fulfillment
    hook** (dotted path + `payment_succeeded`/`payment_failed` signals),
    **owner resolver** for API views, **dunning mailer** hook.
  - Public in-memory `FakeProvider` at `django_cfg.apps.payments.testing` —
    a testable payments stack with no Stripe account.
  - Management commands: `payments_doctor`, `payments_listen`,
    `payments_reconcile`, `payments_refund`, `payments_replay_webhook`.
  - Subscriptions (Stripe Billing lifecycle) land in a later phase; the
    webhook path already accepts and safely skips those events.
- `payments` optional-dependency extra (`stripe>=15.3,<16`).

### Changed
- **Media stays on local disk outside production.** `StorageConfig.backend`
  now takes effect only when `env_mode` is production. Before this, a dev run
  or a test suite uploaded into the real bucket, and cleanup signals deleted
  objects there. In development and test every write and delete goes to
  `MEDIA_ROOT=<base_dir>/media`, with no opt-out. When the declared backend
  has a `custom_domain`, the default storage is
  `django_cfg.core.backends.storage.LocalStorageWithRemoteURLs`: `url()` of a
  file that is not on local disk returns the remote public URL
  (`custom_domain` + `environment`/`location`), so a database restored from a
  production dump still shows its media. Only `url()` falls back; `open()`,
  `exists()`, `size()` and `delete()` stay local. Without a `custom_domain` it
  is plain `FileSystemStorage`. `MEDIA_URL` is no longer derived from
  `custom_domain` outside production. Production settings are unchanged.
- **IndexNow remembers what it sent.** It used to submit whatever had a
  `lastmod` in a 25-hour window, which lost changes whenever a run failed and
  could not see removals. Each run now diffs every host's sitemap sources
  against `IndexNowUrl`, the last accepted state, and sends new, changed and
  removed URLs.
  - Only an accepted batch is recorded, so a failed run is retried.
  - The first run for a host records and sends nothing.
  - A source error, an empty read, or a shrink of more than `shrink_share`
    sends nothing.
  - At most `max_urls_per_run` per host per run; runs hold a cache lock.
  - Every POST is logged in `IndexNowSubmission`. Hosts and submissions show
    read-only in admin.
  - **Needs `manage.py migrate`** (`django_sitemap.0001`). The first run after
    upgrading seeds and sends nothing.
  - `IndexNowSite(key=…)` gives a host its own key. The key route answers
    every configured key.
  - `extra_urls(since)` now gets the host's last fully successful run.
  - `indexnow_submit` gains `--host` and `--reseed`.
  - **Removed:** `window_hours`, `--hours` and `changed_urls()`.
    `schedule_interval` now defaults to 3600 s. The func path is unchanged,
    but the job ID includes the interval. A project upgrading from 2.3.326
    keeps the old daily job in Redis beside the new hourly one; cancel
    `schedule_submit_changed_*` with `interval=86400` once.
  - `indexnow` is now a package (`urls`, `transport`, `state`, `sweep`); the
    public names import from it as before.

### Fixed

- **API datetimes were shifted by the visitor's UTC offset while labelled
  `Z`.** `REST_FRAMEWORK["DATETIME_FORMAT"]` is `%Y-%m-%dT%H:%M:%SZ` (literal
  `Z`), but DRF converts an aware datetime to the *active* timezone before
  formatting, and `TimezoneMiddleware` activates the visitor's zone from
  `X-Timezone` (the generated TS SDK sends it). A visitor at +08:00 got local
  wall-clock time marked as UTC: `expires_at` 8 hours late, timers firing 8
  hours late. Plain curl without the header was correct, a browser was not.
  - Fix: `DateTimeField.to_representation` now renders under
    `timezone.override(UTC)`. The wire format is unchanged (literal `Z`).
  - Chosen over a serializer/base-class override because patching DRF's own
    `DateTimeField` covers plain `serializers.DateTimeField()`, ModelSerializer
    fields and subclasses with no project changes. It is applied when
    `django_cfg.middleware.timezone` is imported (that is, whenever the
    middleware is installed); `AppConfig.ready` is not used because
    `django_cfg/apps/` shadows `apps.py`, so `ready()` never runs.
  - Not changed: `TimezoneMiddleware` still activates the zone for templates,
    admin and ORM-side code. Input parsing is untouched, so a naive datetime
    in a request body is still read as visitor-local. A field with an explicit
    `default_timezone=` keeps it.
  - Visible effect: clients that worked around the shift will now show
    correct times; clients that did not were showing wrong ones.
- **A schedule removed from the config no longer keeps firing.** rq-scheduler
  keeps a job until something cancels it. Before this fix a dropped
  `RQScheduleConfig` stayed in Redis, and once its function was deleted it
  raised an ImportError on every run. Registration now records the schedule
  IDs it registered in a per-project Redis set. On the next start it cancels
  any ID in that set that is no longer configured. Jobs enqueued from code,
  and jobs registered by another project on the same Redis DB, are never in
  the set, so they are never touched. Schedules registered before this
  release are not in the set yet; cancel those by hand once.
- **DRF throttles keyed on raw X-Forwarded-For.** Generated `REST_FRAMEWORK`
  now defaults `NUM_PROXIES` to `0` while `RealIPMiddleware` is in
  `MIDDLEWARE`, so `get_ident` returns the resolved `REMOTE_ADDR`. With `None`,
  DRF returned the whole XFF string (`client,edge`) and one client spread over
  a bucket per Cloudflare edge. An explicit `NUM_PROXIES` is kept. Per-project
  `get_ident` overrides that return `REMOTE_ADDR` are no longer needed.

## [2.2.x] — 2025-10 → 2026-07 (consolidated)

> Changelog maintenance resumed at 2.2.95. The gap since 1.2.25 spans the
> whole 2.x line; its user-facing highlights are consolidated here rather
> than reconstructed per release.

### Added
- **Typed API client generation**: TypeScript, Python, and Go clients emitted
  from the live DRF OpenAPI schema (`python manage.py gen`), with grouped
  clients via `OpenAPIGroupConfig`.
- **Config-gated built-in apps**: `currency` (exchange rates + RQ schedule)
  and `geo` (countries/states/cities with select2/nearby/geocode API).
- **Accounts**: `UserAPIKey` manager seam with non-rotating reveal endpoint,
  TOTP app, webmail provider mapping for magic-link UX.
- **Modules**: MCP server for AI assistants, gRPC services (optional HTTP/3
  frontend via `[grpc-h3]`), Centrifugo integration, OG-image rendering,
  sitemap, frontend monitor ingest, admin dashboard tabs, LLM utilities
  (structured output with validate-and-repair, OpenRouter registry).
- **Encryption**: AES-256-GCM response encryption helpers.

### Changed
- Packaging modernized: 15 `requirements-*.txt` files consolidated into
  `pyproject.toml` extras; pytest/pyright/bandit configs consolidated into
  `pyproject.toml`; Python 3.12+ / Django 5.2+ floors.
- Old payment-provider prototype (NowPayments/Cryptomus era) retired to
  archived development logs; superseded by the new payments engine above.

### Removed
- Streamlit support (dead code, package-wide).

### Security
- Dependency floors track 2026 CVE fixes (Django 5.2.14, simplejwt 5.5.1,
  requests 2.33, lxml 6.1, aiohttp 3.13.4, cryptography 46.0.7, and others —
  see comments in `pyproject.toml`).
- Leaked-secret redaction pass; vulnerability reports moved out of the
  package tree.

## [1.2.25] - 2025-09-24

### Added
- **Payment System Enhancements**: Unified payment provider configurations
  - New `PaymentsConfig` model with provider-specific settings
  - Enhanced validation utilities for API keys and subscription access
  - Improved webhook handling and reliability
  - Support for multiple payment providers (NowPayments, Cryptomus, etc.)
- **Template System**: Enhanced project template management
  - Improved template extraction and project name replacement
  - Better integration with CLI `create-project` command
  - More reliable template archiving system

### Changed
- **Project Structure**: Reorganized template location
  - Moved Django sample project to `examples/django_sample`
  - Improved template packaging for better distribution
- **Dependencies**: Updated dependency management
  - Better version constraint handling
  - Improved package compatibility

### Fixed
- **Payment Validation**: Enhanced security for payment processing
  - Improved API key validation
  - Better webhook verification
  - Fixed subscription access control issues
- **CLI Tools**: Improved reliability of project creation
  - Fixed template extraction issues
  - Better error handling for project setup
  - Improved project name replacement logic

### Security
- **Payment Processing**: Enhanced security measures
  - Stronger API key validation
  - Improved webhook verification
  - Better access control for subscription features

## [Previous Versions]

### [1.2.24] and earlier
- Core Django-CFG functionality
- Basic payment provider support
- Configuration management system
- CLI tools for project creation
- Health monitoring modules
- Database and Redis integration

---

**Note**: This changelog focuses on user-facing features and API changes in the Django-CFG package.
