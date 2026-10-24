---
title: Domain Conventions
status: current
version: "1.0"
audience: backend, platform, agents
last_reviewed: 2026-09-01
---

# Domain Conventions

Patterns this tree has settled on that no page previously stated. Each is
derived by counting the code, not by preference — the command is given so you
can re-derive it.

The universal versions of these rules are in
[`../general/services-errors-and-integrations.md`](../general/services-errors-and-integrations.md)
and [`../general/security-and-tenancy.md`](../general/security-and-tenancy.md).
This page is what those look like *here*.

## `services/` as a package is the default

```bash
find apps modules -type d -name services | grep -v @archive   # 25
find apps modules -name 'service.py' -o -name 'services.py' | grep -v @archive   # 13
```

Counting `extensions/` as well raises the package count to 41 against 25 flat
files. Either way the package form is the majority and the default.

> **Retraction.** v1 called this "a discovery pattern, not a forced layout".
> That was accurate when written and is no longer the right guidance: the tree
> has converged, and a new flat `services.py` in a domain of any size now reads
> as an outlier rather than a choice.

**SHOULD**: create `services/` as a package for a new domain. One module per
cohesive concern, exported from `__init__.py`.

**MAY**: keep a flat `service.py` / `services.py` where the domain genuinely
has one service and is not growing.

> **Corrected 2026-09-06.** This paragraph used to name four flat files as the
> examples to follow — `apps/build/apps/tunnel/`, `apps/apikeys/`,
> `apps/marketplace/search/`, `apps/torrents/semantic/`. None exists here;
> they belong to the sibling service this page was adapted from.
>
> The state of this tree is stronger than the rule: **all eight domains with
> services use a `services/` package** — ai_photo, api_keys, calculators,
> catalog, inquiries, intelligence, normalizer, operations. There is not one
> flat top-level service module left. So the `MAY` above is a genuine
> allowance rather than a description of anything, and a new flat file would
> be the first.

**AVOID**: a flat `services.py` that has grown past a few hundred lines. Split
it into a directory rather than adding a section header comment. The general
rule that applies — decompose into a directory, not sideways into a sibling
module.

## There is no domain exception taxonomy in `apps/` — and that is an open question

```bash
find apps -name 'exceptions.py' -o -name 'errors.py' | grep -v @archive   # 0
find modules \( -name 'exceptions.py' -o -name 'errors.py' \)             # 6
```

> **Recounted 2026-09-06.** The old figures were the sibling service's:
> "zero in `apps/`, all six in `modules/`" including a `modules/skill_spy/`
> and an `extensions/apps/crm/` that do not exist here.

**Five in `modules/`**, all under `django_llm`: `core/errors.py`,
`routing/llm_router.py`, `features/image_edit/errors.py`,
`features/vision/image_fetcher.py`,
`features/translator/translators/text_translator.py`.

**Two in `apps/`**: `apps/operations/services/sync.py` and
`apps/normalizer/services/ingest/_orchestrator.py` — both at an ingestion
boundary, which is the same argument as a provider boundary.

The shape still holds. `modules/` is where provider boundaries live, and
a provider boundary is exactly where a typed error taxonomy earns its keep — an
LLM transport error is a different thing from a business rule refusal. The
product apps raise DRF and Django exceptions and translate at the view.

**This is flagged as an open question, not a mandate.** Two readings are
available and they lead to opposite work:

1. *The rule should be enforced.* Domain services in `apps/normalizer`,
   `apps/catalog` and `apps/intelligence` are large enough that a caller cannot
   distinguish "invalid input" from "provider unavailable" without reading the
   implementation — and for LLM ingestion that distinction decides whether a
   listing is retried or dropped. Adding taxonomies is real work across
   several apps.
2. *The expectation should be corrected.* The apps do not need one; the
   convention is "raise DRF exceptions in apps, typed errors at provider
   boundaries", and the handbook should say so plainly instead of implying a
   taxonomy that has never existed.

**MUST NOT** invent a mandate here by writing a new `exceptions.py` in one app
and citing this page. Whichever reading wins, it applies to all of `apps/` or
none of it — one app with a taxonomy and nineteen without is worse than either
end state.

**SHOULD**: raise the question with the owner when a change makes it concrete,
and record the answer here.

## Machine authentication: one permission class

> **Recounted 2026-09-06.** This section listed six classes across
> `apps/build/`, `apps/apikeys/` and `modules/parser_auth/`, with a warning
> about `HasValidApiKey` being defined three times. None of that is this
> service — it was the sibling product's, carried over wholesale.

| Class | Defined at | Reach for it when |
|---|---|---|
| `HasApiKey` | `apps/api_keys/api/permissions.py` | any machine caller; pairs with `APIKeyAuthentication`, which sets `request.auth` |

That is the whole surface. `HasApiKey` accepts **any** tier including demo, so
it answers "is this a known caller", not "may this caller do this" — a tier
check is the view's job, not the permission's.

Browser-session routes use `IsAuthenticated` (2 files) and `AllowAny` (16).

> **Known defect, tracked.** Keys are issued with a `car_` prefix — another
> product's — and the `Bearer` path checks it while `X-API-Key` does not, so
> the two headers accept different sets of keys. See
> [`@dev/planned/api-keys-carry-a-neighbours-prefix`](../../@dev/planned/api-keys-carry-a-neighbours-prefix/PLAN.md).

**MUST**: use the endpoint's intended mechanism. An API-key route and an
internal-secret route each need their own authentication *and* permission
classes; inheriting the browser session's classes silently widens who can call
them.

**MUST NOT** add a sixth class for a case an existing one covers. Six is
already at the edge of what a reviewer can hold; each addition makes "which one
does this route use" harder to answer.

## Money: Decimal in the database, micro-USD on the wire

> **Correction, 2026-09-06 — `MoneyField` *is* the catalogue's money type.**
> A previous retraction here said `grep -rn MoneyField apps modules` returned
> zero matches. It returns **26**, including `Asset.price` and `Listing.price`
> (`django_cfg.modules.django_currency`). The retraction was written against
> the payments claim it was correcting and overshot.

What actually exists:

**`MoneyField` on the two catalogue price columns**, and plain `DecimalField`
elsewhere (`apps.intelligence` valuations state this explicitly in their own
docstring). `MoneyField` stores the amount in the source's currency and adds
accessors that convert through `CurrencyRate`:

| Accessor | Is |
|---|---|
| `price` / `price_currency` | what the source asks, untouched |
| `price_target` / `price_target_rounded` | the same money in USD |
| `price_display` / `price_target_display` | formatted, for a template |

**Publish both, never one.** The catalogue holds USD, IDR and EUR, and a number
without its unit is not a price: a Bali villa asking 5,190,000,000 IDR rendered
as **$5.2B** on the site until 73 rows were relabelled on 2026-09-06. The
public serializer carries `price`, `price_currency` *and* `price_usd` for that
reason — the rate lives here, so a client cannot derive it.

> **This service has no billing domain.** A previous version of this page
> documented a `MICRO_PER_USD` integer wire layer, `Plan.daily_allowance_cents`
> and `apps/billing/tests/test_inference_usage.py`. None of that exists here —
> there is no `apps/billing`, no `modules/payments`, no micro-USD layer. It
> described the CarAPIs codebase. Removed 2026-09-02.

The rules that do carry over, because they are about money rather than about
that service:

**MUST**: quantize with `ROUND_HALF_UP` explicitly when converting money.
Python's default is banker's rounding — defensible for statistics, indefensible
for a price shown to a customer.

**MUST NOT** turn `None` into `0`. `None` means "not measured"; `0` means
"measured, and it was zero". A fabricated `$0.00` states a fact we do not have,
in the unit a reader trusts most. This matters directly in the catalogue: a
listing with no published price must not normalize to zero — see
[`../../@docs`](../../@docs/README.md) on `Asset` price handling and
`@rules/parsers.md` §5 on the ingestion side, which for the same reason leaves
`price=None` when a source quotes only a local currency.

**Marker values in numeric fields are a trap** generally: check a field's
docstring before comparing against zero, since `0` may encode "no limit"
rather than a quantity.

**MUST NOT** re-add a money-denominated field to a customer-facing serializer
without an explicit decision. The test will stop you; the point is that you
should not have to be stopped.

## Deep imports from django-cfg

```bash
grep -rn "from django_cfg\." apps modules api extensions mcp | wc -l   # 311
```

The general rule prefers a small adapter over a deep import into a dependency.
Reality here, by module:

| Import root | Sites | Reading |
|---|---:|---|
| `django_cfg.modules.django_admin.base` | 74 | arguably an intended extension point the framework has not promoted to a top-level export |
| `django_cfg.modules.django_admin` | 70 | the promoted surface |
| `django_cfg.modules.django_mcp.tools.base` | 37 | same shape as `django_admin.base` |
| `django_cfg.core.*` (state, decorators, config, backends.suppression, utils.url_helpers) | 17 | **genuinely concerning** — `core` is the framework's internals |
| `django_cfg.modules.django_llm.llm.*` | 4 | **breaks this project's own shim rule** |

Two findings worth acting on:

**`django_cfg.core.*` is internal.** Seventeen sites reach into the framework's
own core — `state`, `decorators`, `config`, `backends.suppression`,
`utils.url_helpers`. Each is a refactor upstream away from breaking here, and
none is a documented extension point.

**The `django_llm` imports break a local rule.** `modules/llm_router.py` is the
required door for LLM routing in this project. Four `from
django_cfg.modules.django_llm.llm.*` imports bypass it.

**MUST**: route LLM calls through `modules/llm_router.py`. A shim with four
holes in it is not a boundary.

**SHOULD**: when you need something from `django_cfg.core.*`, ask whether the
framework should export it — that question belongs in
[`../djangocfg/working-with-the-framework.md`](../djangocfg/working-with-the-framework.md),
because the fix may be upstream.

**MUST NOT** patch `site-packages` to work around a missing export. A local
editable fix is not shipped until the package is versioned and published.

## `Media` holds every kind, so select by type — never by "all media"

`catalog.Media` is one table discriminated by `media_type`: images, and since
2026-09-04 video. A second table was considered and rejected — it would make
"what media does this property have" a two-query question and put cross-media
ordering out of reach of SQL.

The cost of that choice lands on **every reader**:

```python
asset.media.images()   # photographs — what image code almost always means
asset.media.visible()  # not operator-hidden; says nothing about type
asset.media.all()      # everything, including video
```

**A bare `.all()` or `.visible()` in image code is a defect**, and the
dangerous version does not raise. Three callers had it when video was added:
two would have rendered an `.mp4` inside an `<img>`, and the third —
`dedup/representatives.py` — counted media to score photographic coverage, so
a video would silently have changed which listing wins as cluster
representative. Nothing would have errored; the catalogue would just have been
subtly wrong.

Rules for a new media kind:

- **Add it to `MediaType`, not to a new model**, until it needs fields images
  cannot share. Then it is a satellite table with a `OneToOne` to `Media`, and
  nothing already written moves.
- **`grep` for `\.media\.` before shipping it.** Every hit is either already
  type-filtered or a decision you are now making.
- **Provider ids live in `metadata`, addresses do not.** A signed CDN URL
  expires; store what lets you re-resolve it. `original_url` is the source
  page, never the signed link.
- **Anything over a few MB is fetched by a job, not in the request.** Attach
  records the intent with an empty `file`; that state is legible, not broken.

## Review checklist

- Is a new domain's service layer a `services/` package rather than a flat
  module?
- Did you add an `exceptions.py` to one app while nineteen have none?
- Which `HasValidApiKey` did you import — and is it the one you meant?
- Is money persisted as `Decimal`, with explicit `ROUND_HALF_UP` on any
  conversion? (There is no micro-USD wire layer here — that was CarAPIs.)
- Does a published price carry its currency *and* its USD figure, or does it
  leave a client to guess the unit?
- Does any code path turn a `None` amount into `0`?
- Did you add a money-denominated field to a customer-facing serializer?
- Does a new `django_cfg` import reach into `core.*` or bypass
  `modules/llm_router.py`?
- Does image code select `.media.images()`, or did it take `.all()` and quietly
  inherit whatever media kinds exist now?
- Did a large download land in a request rather than a job?
