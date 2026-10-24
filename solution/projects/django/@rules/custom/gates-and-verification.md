---
title: Gates and Verification
status: current
version: "1.0"
audience: backend, platform, qa, agents
last_reviewed: 2026-09-01
---

# Gates and Verification

**There is no CI in this organisation and there never will be.** A standing
owner decision, not a gap. Every check on this list runs when a person runs it,
with exactly one exception, and that exception runs inside a Docker build.

Two consequences, restated from [`../CLAUDE.md`](../CLAUDE.md) because they
bite hardest here:

- **A green check is a claim about what it read**, never about your change.
- **A gate that can skip can lie.** A check exiting 0 because a tool is missing
  is not a pass, and nothing else runs it.

## Every gate, and who runs it

| Gate | Command | Protects | Trigger |
|---|---|---|---|
| ~~django-cfg contract~~ | ~~`scripts/check_djangocfg_contract.py`~~ | — | **ABSENT — see the correction below** |
| RQ consumers | `manage.py check` → `rq.W001` | a registered queue has a worker listening | a person runs `make check` |
| Editable install | `manage.py check_editable --strict` | the venv's django-cfg is the one you think it is | prerequisite of `make test` (`Makefile:115`) |
| venv architecture | `make check-venv-arch` | no mixed-arch `site-packages` | prerequisite of `make install` / `make install-local` (`Makefile:89`) |
| ~~Docs staleness~~ | ~~`scripts/check_docs_staleness.py`~~ | — | **ABSENT — see the correction below** |
| Commit safety | `make commit` | no detached HEAD, no in-progress rebase/merge/cherry-pick/revert, no unresolved conflicts, branch is `main` | a person runs `make commit` |
| Lint | `ruff check` | see the selection story below | a person runs it |
| Tests | `python -m pytest <app dirs>`, or `make test` for all of it | the suite — see [`testing.md`](./testing.md) | a person runs it |
| E2E | `pytest e2e/` | live paths against a running server | a person runs it |

There is **no `.pre-commit-config.yaml`** in this repository. Nothing runs on
commit except what `make commit` itself checks.

> **Corrected 2026-09-10 — two gates in that table do not exist here.**
> There is no `scripts/` directory at all, so neither
> `check_djangocfg_contract.py` nor `check_docs_staleness.py` is present, and
> the Makefile has no `docs-check` target. They belong to the sibling service
> this handbook was adapted from — as did the `pytest.ini` and E2E
> descriptions below.
>
> The consequence is the one this page warns about in its own opening: the
> django-cfg contract row claimed **the only non-human trigger** in the whole
> standard. Nothing enforces that contract in this tree. A new symbol imported
> from an unreleased django-cfg fails at container start, not at build.
>
> `check_editable` and `migrate_all` were verified present.

**MUST NOT** write, in a comment or a document, that any of these "runs in CI"
or "the CI will catch it". Nothing does.

## The django-cfg contract gate

`pyproject.toml` requests `django-cfg[full]` **unpinned**, deliberately. That
means a local checkout can compile against an editable working tree and still
crash-loop on the server, because the published release lacks the symbol.

**Nothing checks this here.** The static import check described in the sibling
service (`scripts/check_djangocfg_contract.py`, run from the image build) has
no counterpart in this tree — there is no `scripts/` directory.

So the risk is unguarded: a symbol that exists only in a local editable
checkout passes every check a person can run, and fails at container start
after deploy.

**MUST**: release django-cfg *before* merging code that imports a new symbol
from it. Here that is a discipline, not a gate — nothing will stop the deploy.

`make check` still catches the runtime half through Django's own system checks,
but only for symbols reached during startup.

## `check_editable --strict`

`make test` runs `manage.py check_editable --strict` before the suite. It costs
about one Django startup.

`--strict` is required and is the whole point: **without it the command reports
a mismatch and still exits 0**, so a prerequisite would never bite.

What a failure means: the venv's django-cfg is not the one your work assumes —
typically because `uv sync` or `uv run` reverted an editable install back to
the published wheel. Re-run `make install-local`, then use `.venv/bin/python`
directly.

It is safe on a machine that never wanted an editable install: with no
`~/djangocfg` and no `DJANGO_CFG_EDITABLE_EXPECTED`, "editable expected" is
false and it exits 0. **That exit 0 is a skip, not a pass** — it proves nothing
about the framework version on a machine that does have a checkout.

## `rq.W001` does not exist here

> **Retraction, 2026-09-06.** This section described `rq.W001` — a check that
> warns when a queue has no worker — with two `MUST` rules about reading
> `manage.py check` output rather than its exit code. **There is no such
> check**, in this repository or in the vendored django-cfg. It came from the
> sibling service this page was adapted from, along with a path
> (`api/settings/builders/checks.py`) that does not exist either.
>
> A rule about a gate that does not run is worse than no rule: it is followed,
> and it tells someone a queue with no worker will announce itself.

What this service actually registers is three warnings in
`apps/catalog/checks.py`, all about the portal dimension — the sitemap roster
against the active portals, and active `Source` / `PublicMarket` rows with no
portal. They are `Warning`, so `manage.py check` prints them and exits 0.

The general principle the old section got right, and which those three inherit:
**read the output, not the exit code**, when a warning is what a check emits.
And they read the database, so they are silent before `migrate` has run — a
clean `check` on a fresh box proves nothing.

## Lint: a narrow selection, chosen by measurement

`pyproject.toml` records the measurement rather than a preference. Run against
this tree:

```text
select = ["F", "E9", "B", "UP"]   → 1171 findings
  of which UP* (style modernisation) → ~740
           F401 unused-import        →  165
```

A thousand findings on a repository nobody has linted is not a quality gate; it
is a wall of red that gets switched off within a day, taking the real findings
with it. The live selection is therefore only what points at a defect:

```text
["F821", "F811", "F841", "E9", "B"]
```

- `F821` undefined name — the nine here are string annotations missing a
  `TYPE_CHECKING` import: harmless at runtime, fatal to every type-aware tool.
- `F811` redefinition — the second `def` silently wins.
- `F841` unused variable — usually an assignment that was meant to be used.
- `E9` syntax / IO errors.
- `B` bugbear — mutable default args, bare `except`, loop-variable capture.

**`F401` is deliberately excluded**, despite catching two real orphans during
the settings split: Django settings modules and `__init__.py` re-export names
for their side effects, so it fires on working code.

**SHOULD**: run `ruff check --select F401 <path>` **by hand after moving code**.
That is the case F401 is good at and the reason it is not always-on.

Excluded from linting entirely: `.venv`, `build`, `dist`, `**/migrations`,
`**/@archive`, `**/generated`. A lint pass will never tell you that you are
editing an archived app.

**Line length is 180, and it is one number in four places** — `[tool.black]`,
`[tool.ruff]`, isort, and `.vscode/settings.json`. When they disagree the
formatter silently wins on every save and the editor's ruler becomes a lie.
**MUST**: change all four or none.

180 rather than 88 is also a measured choice: this codebase contains
single-line declarations that do not decompose — `NavigationItem(...)` menus in
`builders/admin.py`, enum-name-to-dotted-path maps in `builders/openapi.py`.
Wrapping those to 88 splits one fact across three lines.

## Tests

Full page: [`testing.md`](./testing.md). The gate-level facts:

`pytest.ini` sets `DJANGO_SETTINGS_MODULE = api.settings.base`, two markers
(`e2e`, `slow`), `--reuse-db`, and `norecursedirs` for `e2e/` and
`modules/.arhcive/` — both fail at import, and a collection error aborts the
run before one test executes.

> **Corrected 2026-09-10.** This section described a different service. It
> claimed `api.settings.test` (no such module exists here), `asyncio_mode`,
> `--strict-markers`, six markers including `marketplace_live`, and a
> `testpaths` naming `apps/ai_chat` — none of which are in this `pytest.ini`.
>
> It also claimed `--reuse-db`, which was **false when written and true now**:
> the flag was added later the same day, precisely because every run really did
> drop and recreate the test databases and a dev server holding a connection
> pool made the suite error out. Setting it then exposed a defect the rebuild
> had been hiding — see [`testing.md`](./testing.md#a-truncating-test-rolls-back-further-than-its-own-rows).

**MUST NOT** rely on a bare `pytest` from the root as evidence. Name the app
directories you touched; the root collects trees whose failures are not yours.

`make test` runs `check_editable --strict` and then the whole suite under
pytest — 2310 tests, the same set a direct invocation collects. It is the one
command that runs everything; it is also the one most likely to stop at its own
prerequisite, which is the point of that prerequisite.

> **Changed 2026-09-10.** It previously ran `manage.py test`, Django's own
> runner, which reads neither `pytest.ini` nor pytest-only constructs and
> collected almost none of this suite.

E2E lives in `e2e/` and is excluded from collection, not merely deselected:
those files drive a RUNNING server over HTTP through the generated Python
client, so they fail at import in a fresh checkout.

```bash
pytest e2e/                     # deliberately, against a live server
```

> **Corrected 2026-09-10.** This block listed `make e2e-referrals`,
> `e2e-marketplace`, `e2e-marketplace-recovery` and `e2e-marketplace-llm`.
> The Makefile defines none of them — they belong to a different service, as
> did the `pytest.ini` description above.

## `make commit`

Refuses to proceed on a detached HEAD, an in-progress rebase / merge /
cherry-pick / revert, unresolved conflicts, or a branch that is not `main`.
Each refusal prints the two commands that resolve it (continue, or abort).

It then adds, commits, fetches `origin/main`, rebases, and pushes.

**MUST NOT** work around a refusal by committing manually. Every one of those
states produces work that is lost or lands somewhere nobody looks.

## Definition of done

A change is done when the checks its blast radius implies have been **run by
you**, and their output read.

1. `make check` — and read the warnings, especially `rq.W001` if a queue is in
   scope.
2. `ruff check <the paths you touched>`, plus `--select F401` if you moved code.
3. Focused tests: `python -m pytest <the app dirs you touched>` — see
   [`testing.md`](./testing.md).
4. `make gen-dry` if a serializer, model, view or URL changed — see
   [`api-groups-and-generation.md`](./api-groups-and-generation.md).
5. For an app-code deploy: a **restart**, not a rebuild. For a dependency
   change: a rebuild.

**MUST**: say which of these you ran, and which you did not. "Checks pass" is
not a report; it is a claim about an unnamed set.

**MUST NOT** cite a gate you did not run, or cite one that skipped as though it
passed.

## Review checklist

- Which gates did you actually run, and did you read their output rather than
  their exit code?
- If a queue changed: was `manage.py check` run somewhere a worker is running?
- If django-cfg imports changed: has the framework been released first?
- Did a `check_editable` exit 0 mean "passed", or "skipped on a machine with no
  editable checkout"?
- Did you move code without a hand-run `ruff check --select F401`?
- Did you rely on a bare `pytest` from the root? It collects trees whose
  failures are not yours.
- Did the suite ERROR on the test database rather than fail an assertion? That
  is a connection holder, not your code — [`testing.md`](./testing.md).
- Did a test fail with `Portal.DoesNotExist` or another missing seed row? Run
  the file alone. Passing in isolation means collection order, not your logic —
  a `transaction=True` test truncated the migration-seeded rows.
- Did you change a migration and then reuse the test databases? `--reuse-db` is
  on by default; rebuild once with `--create-db` (which needs django-cfg
  ≥ 2.3.1 — see [`testing.md`](./testing.md#the-database-trap)).
- Was another agent or worktree running the suite while you measured? They share
  one set of test databases and truncate each other. That number is not
  evidence.
