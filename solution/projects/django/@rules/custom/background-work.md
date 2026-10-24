---
title: Background Work — Queues, Schedules, Jobs
status: current
version: "2.0"
audience: backend, platform, operations, agents
last_reviewed: 2026-09-01
---

# Background Work

Redis is a delivery and coordination system, not the durable source of business
state. Jobs are at-least-once and may be late, duplicated, retried, cancelled,
or lost in an explicitly destructive flush.

The universal rules — a task is a thin adapter, enqueue after commit, classify
retries — are in
[`../general/jobs-and-side-effects.md`](../general/jobs-and-side-effects.md).
This page is the local half: which queues exist, where they are declared, and
which commands drain them.

## Where it is declared

`api/settings/builders/background.py`.

> **Retraction — v1 named `api/config.py`.** The declarations were split out of
> it; the queues are in `api/settings/builders/background.py`.
>
> **Second retraction, 2026-09-06.** v1 also said the RQ check moved to
> `api/settings/builders/checks.py`. There is no such file here and no
> project-wide check module: this service puts checks in the app that owns the
> invariant (`apps/catalog/checks.py`), which is the same principle stated
> about a different location.

**`settings.RQ_QUEUES` is the single source of truth.** Never hand-copy the
list anywhere.

## Six queues, not five

> **Retraction.** v1's RQ page listed five queues and omitted **`torrents`**.
> That page had already recorded, in its own header, that a hand-written queue
> list is what documented an outage as the design — and then carried a
> hand-written queue list. There are six.

Declared in `api/settings/builders/background.py` under `django_rq.queues` —
that is the only authoritative list. Redis DB **12** (carapis 11, listingapis
4, cmdop 3; distinct DBs stop the schedulers clashing).

**The queues are not on the cache's database.** `REDIS_URL` puts the cache on
DB 1 and `redis_db=12` overrides it for RQ only. Inspecting DB 1 for a stuck
job shows an empty database, which reads as "nothing is enqueued".

| Queue | Timeout | Result TTL | Operational contract |
|---|---:|---:|---|
| `high` | 360 | 500 | short user-blocking follow-up, strict latency |
| `default` | 360 | 500 | ordinary bounded background work |
| `low` | 600 | 800 | cleanup, reconciliation, non-urgent maintenance |
| `normalization` | 120 | 300 | LLM ingestion: raw listing text → `Asset`; also valuations, geocode and dedup maintenance |
| `ai_photo` | 600 | 300 | photo editing |

`normalization` carries the scheduled work in `django_rq.schedules`:
`compute_pending_valuations` (hourly), `backfill_geocodes`, `backfill_cities`
and `daily_dedup_maintenance` (daily).

> **Do not hand-write this table from memory.** A previous version of this page
> listed `marketplace_ingest`, `torrents` and `crm` — none of which exist in
> this service. Read `api/settings/builders/background.py`.

**Known inconsistency (2026-09-02):** `make rq` starts a worker on
`high intelligence normalization photo_edit crm billing orders default low` —
five of those (`intelligence`, `photo_edit`, `crm`, `billing`, `orders`) are
**not** declared in `django_rq.queues`. A worker listening to an undeclared
queue is not automatically wrong (jobs can still be enqueued by name), but the
Makefile and the config disagree about what this service runs. Reconcile before
trusting either as the queue roster.

Adding a queue costs configuration **plus** worker deployment, scheduler and
monitoring, a runbook, and a capacity owner. It is not a one-line change.

## `_UNWORKED_QUEUES`

**Not present in this service.** `_UNWORKED_QUEUES` described a deliberately
worker-less `marketplace_ingest` queue in a different codebase; neither the set
nor that queue exists here.

Every queue in `django_rq.queues` is expected to have a listener. A declared
queue with `worker_count=0` is a real finding here, not a known-good state.

Health thresholds are tuned per queue in `django_rq.health.queue_overrides` —
`low` is allowed a 1-day-old job before warning and 7 days before critical,
because cleanup work is legitimately slow to drain.

**MUST**: re-monitor a queue the moment a worker consumes it again — remove it
from the set in the same change that starts the worker.

Health config derives `monitored_queues` from `queues` rather than listing them
by hand, because an empty `monitored_queues` means "all of them" and a
hand-written list silently drops every queue added later.
`min_consecutive_breaches=3` filters transient post-rebuild noise while a
sustained breach still pages after ~3 minutes.

## A queue with no worker is silent

This is the single most dangerous failure mode here, and the *why* matters:
`get_queue()` succeeds, `enqueue()` succeeds — **RQ never verifies a consumer
exists** — so nothing raises, nothing logs, and any `except`-based inline
fallback never fires.

**A queue that does not exist is strictly safer than one nobody drains**,
because a missing queue fails loudly on the first enqueue.

The measured cost when this happened: `crm` was registered with no listener,
and **536 jobs accumulated in Redis over months** — client and message
embeddings, IMAP inbox sync, SLA scans, ticket auto-close, follow-ups. Semantic
search over Clients and Messages simply returned nothing, and no error anywhere
said why.

### `rq.W001` warns; it does not fail

> **Retraction — this is the most important correction on this page.** v1 said
> `rq.W001` "**fails** `manage.py check`" and presented it as the executable
> guarantee that replaced a rule people forget. It does not fail.
>
> It is a `django.core.checks.Warning`. `manage.py check` **still exits 0**
> with it printed. And it is **skipped entirely when no worker is running** —
> the check returns `[]` before examining anything.

The design is deliberate and defensible: a dev box legitimately runs no worker
at all, so erroring would make `manage.py` unusable. What it refuses to
tolerate is the condition being *invisible*. It makes `manage.py check` say it
out loud; it does not make anything stop.

**MUST**: read the output of `manage.py check`, not its exit code, when a queue
is in scope.

**MUST**: run it somewhere a worker is actually running. On a laptop with no
worker it reports nothing, and that silence is not evidence.

It also does nothing about "you started no worker" — only about "you started a
worker that ignores one of your queues", which is the trap, because then the
operator believes the work is being done.

**Depth without progress is the diagnostic.** A growing queue with zero
failures is very often *unconsumed*. Check for a listening worker before tuning
anything; healthy Redis says nothing about whether work is happening.

## Deterministic `job_id`

An enqueue keyed on a row (`post_save` → embed, → reindex, → enrich) **MUST**
pass a deterministic id. Without it, a row saved N times queues N identical
jobs.

**The grammar is `<domain>-<verb>-<pk>`.**

> **Corrected 2026-09-06.** This said "20+ enqueue sites" and listed four, all
> in a sibling service. This service has **one** deduplicated enqueue site:

```python
job_id = job_id_for(asset_id)   # apps/catalog/search/tasks/embed.py:35
```

One site, and the measurement below is why it exists — the rule earns its
keep at the first site, not the twentieth.

Measured cost of omitting it: **4,417 queued `embed_task` jobs for 265 rows** —
17 duplicates each. An idempotency guard *inside* the task (a content hash)
made each duplicate cheap but did nothing about queue depth, worker time or
Redis memory: draining the backlog embedded 265 rows and discarded 94% of the
work.

**In-task idempotency and enqueue-time deduplication solve different problems.
You need both.**

The canonical shape — fetch, treat a live job as coverage, replace a dead one:

```python
job_id = f"crm-embed-client-{row_id}"
existing = queue.fetch_job(job_id)
if existing is not None:
    if existing.get_status(refresh=True) not in {FAILED, STOPPED, CANCELED}:
        return existing          # queued/running -> the work is covered
    existing.delete()            # a FAILED job must not block the row forever
queue.enqueue(task_path, str(row_id), job_id=job_id, ...)
```

Reference implementation here: `apps/catalog/search/tasks/embed.py`. Its
`job_id_for()` derives a stable id per asset, and the fetch/inspect/delete
dance above is in `enqueue_embed` — written after enqueueing the same `job_id`
twice raised queue depth by two rather than one.

**RQ `job_id` deduplication is coordination, not a business guard.** Registries
expire and failed jobs can be requeued. Pair it with database uniqueness, a
version compare-and-set, a lease, or a provider idempotency key.

### One enqueue helper per concern, not one per app

`clients`, `conversations` and `todos` each had a private copy of the same
eight-line `_enqueue`. They drifted: `todos` alone targeted `default` instead
of `crm`. When the worker turned out not to drain `crm`, **`todos` kept working
precisely because it had deviated** — and no single file could have told you
that.

Copy-pasted infrastructure does not stay identical; it stays *plausible*.
Extract it.

## The schedule

`background.py` is roughly half comment, and that is the point: each entry
records **why** it runs at its interval. Current schedules, by queue:

| Interval | Queue | Job |
|---|---|---|
| 60s | `low` | recover pending push delivery handoffs |
| 60s | `default` | publication ingest/route sweep |
| 900s | `default` | customer storage reclamation sweep |
| 1h | `low` | reconcile pending payments |
| 1h | `low` | sync Stripe subscriptions |
| 3h | `low` | generate reviews |
| 24h | `low` | cost-per-call trend alarm |
| 24h | `low` | purge telemetry events >90d |
| 24h | `low` | purge push delivery audit rows >30d |

Two of those comments are worth carrying:

- **Stripe subscription sync exists because webhooks are not sufficient
  evidence of delivery.** A wrong signing secret silently 400'd every
  subscription event for a month and nothing paged, because the rejection was
  only a `logger.warning`. Webhooks stay the source of truth; the poll catches
  deliveries that never arrive, and it does not care *why* delivery broke.
- **Storage reclamation is a backstop, not the delete path.** The happy path
  enqueues on commit; the 15-minute sweep catches deletes lost between commit
  and the provider call, dangling multipart uploads (which are billed), and
  orphaned staging objects no row claims. That is why it is 15 minutes and not
  one.

The Marketplace ingestion schedule is **commented out**, deliberately,
alongside the paused worker. The queue stays registered because `enqueue()`
sites still resolve it.

**MUST**: give every schedule one owner. Scheduler restarts and clock drift can
overlap executions, so a scheduled task needs a DB lease, a watermark, or an
idempotent scan. Process bounded pages; advance the cursor only after durable
success.

**MUST NOT** register the same schedule in django-cfg, an extension manifest,
cron and infrastructure. A management command is an operator entrypoint, not a
second recurring scheduler.

## Worker commands

Verified against the `Makefile` on 2026-09-02:

```bash
make rq            # rq-clear, then rqscheduler + one worker across
                   # high intelligence normalization photo_edit crm billing orders default low
make rq-crm        # isolated: crm only
make rq-scheduler  # rqscheduler
make rq-clear      # redis-cli -n 11 FLUSHDB  ← see warning below
make rq-stats      # rqstats
```

Workers use `--worker-class rq.SimpleWorker` and set
`OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES` — macOS forking crashes the default
worker.

> **Both fixed, verified 2026-09-06.** This page carried two warnings that no
> longer describe the Makefile:
>
> - *"`make rq` clears the queues first"* — `rq-clear` is no longer a
>   dependency of `rq`. Starting a worker no longer flushes pending jobs.
> - *"`rq-clear` flushes Redis DB 11 while this service runs on DB 12"* — it
>   now takes its connection from `get_connection('default')`, so it flushes
>   whatever the settings resolve to and cannot target a neighbour's database.
>
> `rq-clear` is still destructive on purpose; it is simply destructive to the
> right database now.

`make rq` **refuses to start** if it cannot read `settings.RQ_QUEUES` — it will
not launch a worker that drains nothing. Workers use
`--worker-class rq.SimpleWorker`.

**MUST NOT** hand-write a queue list into a worker command. A Docker `CMD`, a
systemd unit, or a typed `manage.py rqworker high default` reintroduces exactly
the drift that cost 536 jobs. Pass every declared queue, or derive the list the
way the Makefile does.

`make rq` only starts a worker. **Startup must never clear pending work.**

## `make rq-clear` is destructive

It resolves the `default` RQ connection through Django and executes
**`FLUSHDB`** against that logical database (currently DB 3). That deletes RQ
jobs **plus every other key deliberately sharing that DB**, including the CRM
WhatsApp bridge list.

**MUST NOT** use it to restart workers or clear one failed job. It requires
explicit destructive intent.

## Verification

- Test duplicate, delayed, stale and concurrent execution.
- Test enqueue-after-commit, and rollback.
- Test every retry classification and the exhaustion path.
- Assert that saving one row twice enqueues **one** job.
- Run `manage.py check` where a worker runs, and **read** the `rq.W001` line.
- Confirm the logs show enqueue, start, retry and final outcome.
- `docker logs --since 24h cmdop-rq-worker` for production job evidence.

Monitor queue depth and age, oldest job, execution latency, retry and terminal
failure, worker heartbeat, scheduler heartbeat, and poison jobs.

## Review checklist

- Does every registered queue have a worker — or an entry in
  `_UNWORKED_QUEUES` with a stated reason?
- Does every row-keyed enqueue pass `job_id=f"<domain>-<verb>-<pk>"`?
- Is the enqueue helper shared, or is this the fourth private copy?
- Does a new schedule have one owner and a lease or idempotent scan?
- Did you read `manage.py check` output rather than its exit code?
- Is any worker command carrying a hand-written queue list?
