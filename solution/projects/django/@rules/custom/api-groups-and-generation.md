---
title: API Groups and Code Generation
status: current
version: "2.0"
audience: backend, frontend, platform, agents
last_reviewed: 2026-09-01
---

# API Groups and Code Generation

Generated code is a **compiled artifact** of backend contracts. Serializers,
views, URL routing, OpenAPI annotations, the websocket registry, models and
`generation.py` are its source. A generated file is never an independent source
of truth.

`django_cfg.modules.django_generator` can run three pipelines. **Two are used
here** — the framework also generates Centrifugo websocket bindings, which this
service does not configure:

```text
Django/DRF    → OpenAPI → sliced group specs → TypeScript / Python
Django models → ORM IR                       → async SQLModel surface
```

## Two configs, two owners

> **Retraction — the group config is no longer in `api/config.py`.** v1 said
> `api/config.py` owns the `OpenAPIGroupConfig` declarations. That file is
> gone.

| File | Owns |
|---|---|
| `api/settings/builders/openapi.py` | `OpenAPIGroupConfig` — group name, apps, tags, title, schema metadata. **9 groups** (`grep -c 'OpenAPIGroupConfig(' api/settings/builders/openapi.py`). |
| `generation.py` (repo root, 133 lines) | consumers — output path, language, target type, and which groups each consumer receives. |

**A group without `tags` never generates.** Only four of the nine declare one —
`public_catalog`, `public_concierge`, `public_calculators`, `operator`. The
other five are declared and inert. A group collects the operations of the apps
it names and then filters by tag; with no tag there is nothing to filter to, and
the generator reports success having produced nothing for it.

Changing one side is incomplete. Read the symptom:

- endpoint missing from a group → fix its tag or the group config;
- correct group absent from a client → fix that target's `groups`;
- **endpoint routed, tagged, in the schema, and still not in any client**
  → the group is not in the target's `groups` list. This is the one that
  wastes an afternoon: every backend check passes, so the search goes to
  the framework. The list is in `generation.py`, in this repository.
- retired consumer still receives code → remove its target;
- client shape wrong *everywhere* → fix the serializer, not every target.

**MUST NOT** infer a target from a directory name. `generation.py` carries
deliberate cross-repository paths and comments recording product-plane
decisions — several say why a group is *absent*.

## The real target list

> **Retraction.** Until 2026-09-10 this section described **cmdop**: ten
> targets, five sibling repositories, Centrifugo websocket bindings, Swift and
> Go clients, `torrents`. None of it exists here. It had been inherited
> wholesale and read as authoritative — and it cost a real afternoon, because a
> missing client was searched for in django-cfg's pipeline rather than in the
> `generation.py` sitting in this repository.

Read from `generation.py`. **Three targets: two OpenAPI, one ORM.** There is no
Centrifugo target and no Swift, Go or mobile consumer.

### OpenAPI (2)

| Lang / type | Output | Groups |
|---|---|---|
| Python / sdk | `parsers/libs/api/generated` | `normalizer`, `operations` |
| TS / web | `frontend/packages/api/src/generated` | `public_catalog`, `public_concierge`, `public_calculators`, `operator` |

The Python SDK is **one copy shared by every parser service**, and it lives
outside `fastapi/` because the Telegram daemon needs it too: a post reaches the
catalogue through the same `POST /apix/normalizer/normalize/` every HTTP parser
uses. The generator owns `libs/api/` and nothing else under `libs/` — a wider
clean-up there deletes hand-written code no schema can regenerate.

The TypeScript target is **one client for the whole monorepo**, in the workspace
package `@mls/api`. Both `apps/web` and `apps/web-bali` import the package's
public entry point, never the generated tree. Do not re-split it per app.

### ORM (1)

| Output | Apps |
|---|---|
| `parsers/fastapi/src/_shared/orm` | `catalog`, `inquiries`, `normalizer`, `operations`, `profiles` |

`ORMGenerator.FASTAPI`, `async_mode=True` — asyncpg + sqlmodel against
`mls_estate` directly.

**The Telegram daemon must NOT receive it.** It reaches the catalogue through
the normalizer, and a direct database handle would let it write around the LLM
pipeline that gives every listing its shape. That is a boundary, not a
packaging preference.

Targets land in **two** sibling trees: `parsers/` and `frontend/`.

### Group decisions that are deliberate absences

- **Five groups declare no tag and therefore generate nothing** — `profiles`,
  `operations`, `normalizer`, `intelligence`, `api_keys`. `operations` and
  `normalizer` still reach the Python SDK, because a target names groups by
  name; the other three reach no consumer at all. Declared is not generated.
- **`operator` is in the TypeScript target and is the only non-anonymous group
  there.** The staff drawer runs in the browser, so its client must exist. The
  tier is enforced by `IsAdminUser` on the endpoint — never by the client not
  knowing the URL. It stays its own group so a public page cannot reach a
  source name or a listing URL through the same import.
- **`public_catalog` names `apps.intelligence` as well as `apps.catalog`.** The
  picks endpoint is a section of the catalogue rail and belongs in the namespace
  the rail already reads. The tag alone is not enough: a group collects the
  operations of the apps it *names*, so an unlisted app's endpoint lands in
  whichever group does name it.
- **`public_concierge` claims two tags**, its own and `public_newsletter`. Both
  are anonymous, rate-limited inbound-lead endpoints from one app, so they share
  a group rather than each needing one.

### The newsletter precedent

The newsletter viewset was registered and tagged, and **no group claimed its
tag**. So it never entered the schema, never generated, and the frontend
compensated with a hand-written URL in its proxy route:
`${baseUrl}/apix/inquiries/newsletter/`.

That is exactly the drift a generated client exists to prevent — a path string
in the app that nothing checks against the backend. When the route moves,
nothing fails until a visitor does.

**The generator's failure mode is silence.** An endpoint whose tag no group
claims, or whose group no target lists, is simply absent; the run reports
success. **MUST NOT** answer a missing client by writing the URL by hand — fix
the group or the target's `groups`, whichever the symptom list above names.

**MUST**: when adding a group to a target, write *why* in the comment, as every
existing entry does. The comments are the only record of these decisions.

## Enum pinning — the highest-value section

**This service pins none today** — there is no `enum_name_overrides` key in
`api/settings/builders/openapi.py`. The section stays because the failure it
describes is one edit away, and because the diagnostics below are how you find
out you need it. (v1 claimed "25 pinned enums at lines 39-84"; that was the
sibling service.)

Generic nested names (`Status`, `Kind`, `Role`, `Reason`) collide in
drf-spectacular, which then invents a hash-suffixed name like `Status181Enum`.
That name changes on unrelated backend edits and produces a diff in every
downstream client.

The grammar: **`<Domain><Field>Enum` → dotted path to the `TextChoices`
subclass.** The mapping is intentionally inverted — key is the *desired schema
name*, value is the *source class*.

```python
# Illustrative shape — key is the desired schema name, value the source class:
'AssetStatusEnum': 'apps.catalog.models.asset.Asset.Status',
```

**SHOULD**: prefer a globally specific `TextChoices` class name at the source.
Pin only when renaming is not available.

Two pins carry reasoning that transfers to any similar case:

**`BillingCycleEnum` — value-identical enums dedupe into one component.**
`Subscription.Cycle` and `Order.BillingPeriod` are both `monthly`/`annual`.
drf-spectacular dedupes them into **one** enum, so they must share a **single**
name. Giving them two names is a duplication error, not two components.

**`GrantReasonEnum` — a bare literal list stole a class-backed field's
component.** `Grant.Reason` is exposed as `EntitlementsGrantSerializer.source`,
while the demotion serializer declares its own `reason` as a bare literal list.
Spectacular named the *literal* one `ReasonEnum` and then matched the grant
field to it — so `source` shipped
`payment_incomplete|payment_failed|lapsed`. The generated client **rejected
every real grant and blanked the plan panel**. Pinning gives the class-backed
one its own component; the literal list has no class to point at, so it keeps
the invented name.

The lesson generalises: **a bare literal list in a serializer competes for a
component name with every class-backed field of the same name.** Prefer a
`TextChoices` class over an inline literal list wherever the value is a domain
vocabulary.

Diagnostics:

```bash
.venv/bin/python manage.py suggest_enum_overrides
DJANGO_CFG_ENUM_COLLISION_POLICY=error make gen-dry
```

## Running generation

`generation.py` is **configuration, not a script**. It is loaded inside an
initialized Django by the `gen` management command.

```bash
# correct
make gen-dry
.venv/bin/python manage.py gen --dry-run

# wrong — can fail before django-cfg initializes, and skips the command's
# filters and reporting
.venv/bin/python generation.py
```

```bash
make gen-list   # configured OpenAPI targets
make gen-dry    # plan without writing
make gen-ts | gen-go | gen-py | gen-sdk | gen-web
make gen        # everything
```

Underlying flags: `--groups <a> <b>`, `--target web`, `--config <path>`,
`--verbose`. (`--swift` exists in the framework and does nothing here — there is
no Swift target.)

**Flags filter configured work; they do not create a missing target.** A
successful no-op is not proof the client you wanted exists. Inspect the config
and diff the output.

**`--list-targets` prints OpenAPI targets only** at the current django-cfg
version — it does not enumerate the ORM target. Read both sections of
`generation.py` before declaring the map complete.

**`gen --check` does not exist.** The framework README mentions it in some
revisions; the management command does not expose it. Trust `manage.py gen
--help` and the local command source over a stale example.

## Cache

The generator caches rendered specs and per-target output, and **generator
source is not always part of the fingerprint** — a warm run can skip external
tools after framework generator code changed.

```bash
DJANGO_CFG_GEN_NO_CACHE=1 make gen-dry
DJANGO_CFG_GEN_PARALLELISM=1 make gen   # serial, easier to diagnose
```

**MUST NOT** delete a consumer directory to fix a cache issue. Force the cache
off, reproduce one target or group, and read the sliced schema and the tool
error.

## Schema quality

Generated quality cannot exceed schema quality. Every client-consumed endpoint
needs a stable operation ID where automatic naming is ambiguous, named request
and response serializers, accurate status-specific responses, intentional
pagination (`pagination_class = None` for a single object), a stable tag
matching its group, explicit auth and error contracts, and schema-safe queryset
behaviour.

**AVOID** anonymous inline object schemas. The TypeScript extras cannot
reliably produce reusable Zod schemas and hooks from an inline response. Use a
named wrapper serializer.

```python
def get_queryset(self):
    if getattr(self, "swagger_fake_view", False):
        return Model.objects.none()
    return Model.objects.for_user(self.request.user)
```

**MUST NOT** execute provider calls, tenant resolution, expensive queries or
side effects while rendering a schema.

## Groups and tags

Group names are contract partitions, not UI decoration. Use stable lowercase
snake_case tags for new domain groups. **Renaming a tag — including changing its
case — renames generated operations and types, and is a client migration.**

A group may claim several tags (`public_concierge` claims its own and
`public_newsletter`), which is how sibling endpoints from one app share a
namespace. Pin the tags explicitly rather than letting a group absorb every
operation of the apps it names.

Before adding a group, decide which URL module owns the endpoint, whether the
group is a runtime mount or a schema slice or both, which consumers genuinely
need it, and **whether including it exposes writes or secret-bearing
serializers to a consumer that only needs public reads**. Generation is not
authorization, but least-surface generation reduces accidental misuse.

## ORM generation is a security boundary

The ORM target exposes `mls_estate` directly to the FastAPI dashboard and proxy
store: `catalog`, `inquiries`, `normalizer`, `operations`, `profiles`. Adding an
app or model exposes columns and enables direct-database behaviour outside
Django's services.

Before adding one, review: does the consumer truly need direct ownership; secret
and personal-data columns; soft-delete and publication semantics; indexes and
uniqueness the generated queries assume; migration and deploy ordering between
the two services; and whether an HTTP contract is safer than shared-database
coupling.

**Generated ORM code does not transfer lifecycle ownership.** The consumer
reads; Django writes. The Telegram daemon is the worked example: it is denied
the ORM entirely and goes through the normalizer, because a direct handle would
let it write around the pipeline that gives every listing its shape.

## Writing into sibling trees

`make gen` writes into **two** sibling trees, `parsers/` and `frontend/`, both
inside this same repository — so a generated diff shows up in the working tree
of whoever is running it, alongside their own uncommitted work. Before a real
run:

1. `git status` in Django **and** every affected consumer;
2. coordinate with parallel work in generated directories;
3. `make gen-dry`, or a narrow group/language target;
4. generate only the consumers the contract change affects;
5. review generated and hand-written diffs **separately**;
6. run each consumer's own formatter, typecheck and tests.

**MUST NOT** overwrite or reformat unrelated changes in a target tree. If a
target contains unexplained edits, stop and find the owner.

Mechanical deletions and renames in the output are **API compatibility
signals**, not noise.

## Generated versus hand-written

**MUST NOT** patch a generated type, client, serializer, Zod schema, hook or
ORM model to hide a backend mismatch. Fix the source and regenerate.

Hand-written adapters live **outside** generated roots and provide friendly
facade names, base URL and auth injection, error normalization and intentional
compatibility shims — never duplicated schema declarations.

## Contract change workflow

1. Change serializer / view / model, and its tests.
2. `manage.py check` and focused API tests.
3. Inspect schema errors and endpoint registration.
4. `make gen-dry` with the correct local django-cfg.
5. Narrow generation, then full generation if shared components changed.
6. Review both target trees.
7. Run the consumers' own checks.
8. Ship source and generated consumers as one coordinated delivery, or stage a
   backward-compatible rollout.

For a breaking change, deploy additively: introduce the new shape, release
consumers, observe adoption, then remove the old contract. **A successful local
generation does not make an incompatible deployment safe.**

## Review checklist

- Is the endpoint present exactly once in the runtime URL tree, and does its
  tag place it in the intended group?
- Did you change **both** `builders/openapi.py` and `generation.py` where the
  change spans group and consumer?
- Are new enum components class-backed, or pinned — and does a bare literal
  list anywhere compete for the same name?
- Is the group assigned only to consumers that need it, with a comment saying
  why?
- Are secrets and internal fields absent from generated public types?
- Did `gen-dry` report only explainable diffs, in the trees you expected?
