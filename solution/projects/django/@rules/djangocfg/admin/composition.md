---
title: Django Admin Composition and Decomposition
status: current
version: "2.0"
audience: backend, product, operations, agents
last_reviewed: 2026-09-01
---

# Django Admin Composition and Decomposition

Design an admin around **operator decisions**, not around the database schema.
A good screen answers, in order: what happened, whether intervention is needed,
what evidence supports it, and which safe action is available.

Schema-shaped admins fail on the second question. Every field is present and
nothing tells the operator whether to act.

## Module boundaries

**MAY**: keep a single `admin.py` while an app has a few small screens.
**SHOULD**: promote it to an `admin/` package when any of these becomes true:

- the file mixes multiple operator workflows;
- actions, filters, forms or display helpers need independent tests;
- a model has a diagnostic view with substantial query or presentation logic;
- the file is hard to review without jumping between unrelated models.

Prefer this package shape:

```text
admin/
├── __init__.py       # imports registration modules only
├── model_admin.py    # AdminConfig and ModelAdmin for one workflow
├── actions.py        # thin adapters into domain services
├── filters.py        # reusable, tested filters
├── forms.py          # validation and deliberate operator input
└── inlines.py        # bounded child summaries
```

**MUST**: registration belongs at the edge (`__init__.py`), business
transitions belong in services. **MUST NOT** let display and query helpers
become a second domain layer — that is the failure mode this layout exists to
prevent, and it arrives one convenience helper at a time.

## Information architecture

**The changelist is a triage surface.** Show a stable identifier, human
identity, state, owner or tenant, and the most relevant time. Add filters for
finite states and searchable external identifiers.

**AVOID** JSON blobs, verbose prose and expensive aggregates in the default
list.

**The detail page is progressive disclosure**, in this order:

1. identity and current state;
2. editable operator-owned inputs;
3. safe lifecycle actions;
4. collapsed provider metadata and diagnostics;
5. bounded related evidence, or links to dedicated history screens.

**MUST NOT**: make colour the only state signal — it is redundant
reinforcement. Use explicit labels, human dates with exact timestamps
available, and action names that state their outcome. A dangerous action needs
confirmation and a visible success or failure result.

## Data and query boundaries

- **MUST**: configure `select_related` for single-valued relations shown in a
  list.
- **SHOULD**: use `prefetch_related` only when the bounded result is actually
  rendered.
- **MUST NOT**: inline an unbounded event, delivery, observation or transition
  stream. Prefer a dedicated read-only changelist reached by a filtered
  relation.
- **MUST NOT**: call providers, LLMs or queues while rendering a page. A page
  render is not a place to hold a network dependency.
- **SHOULD**: enqueue slow work after commit and expose its durable status
  separately.

Admin search operates on production data. **MUST**: choose indexed identifiers,
and measure the generated SQL before adding broad relation traversal.

## Mutation boundaries

**MUST**: classify each screen explicitly. The classification decides what the
permissions and readonly configuration must say.

| Kind | Allowed behaviour |
|---|---|
| Reference / configuration | validated edits; deletion only when lifecycle permits |
| Lifecycle aggregate | limited fields plus service-backed actions |
| Evidence / event | no add, change or delete by default |
| Secret / credential | metadata only; never reveal stored secret material |
| External projection | read-only, or reconciled through an explicit service |

**MUST**: a bulk action iterates through the domain service unless that service
provides a safe bulk primitive. **MUST**: report partial failures — do not
silently claim the whole selection succeeded. An action that reports success
for a partially failed batch is worse than one that fails loudly, because the
operator stops looking.

## Migration policy

Migration to django-cfg has **two independently reviewable steps**:

1. change the standalone base to `PydanticAdmin`, preserving behaviour;
2. redesign with `AdminConfig`, display fields, fieldsets and documentation.

**MUST NOT** combine step two with a business-lifecycle rewrite. Three changes
in one diff means a behaviour regression cannot be attributed to any of them.

**MUST**: snapshot permissions, readonly fields, actions, URLs and query
loading before conversion, and compare after.

Native Django inlines **MAY** remain as they are. **SHOULD**: replace one only
when django-cfg exposes a documented compatible primitive with a concrete UX
benefit — confirm it in the current exports, per
[`./reference.md`](./reference.md).

## Review checklist

- Can an operator identify the tenant and the state without opening each row?
- Is source-of-truth ownership obvious for every editable field?
- Are secrets, raw credentials and unnecessary personal data absent?
- Do actions use domain services, permissions, confirmation and audit trails?
- Are evidence records immutable through every admin path, and is related
  history bounded or moved to its own screen?
- Are empty, loading, failure and partial-success states understandable, and
  has changelist query behaviour been checked at realistic row counts?
