---
title: Authorization Tiers
status: current
version: "1.0"
audience: backend, frontend, qa, agents
last_reviewed: 2026-09-10
---

# Authorization Tiers

Who may call what, and where that decision is written. The portable half of
this — scope is derived, never accepted; do not leak existence — is
[`../general/security-and-tenancy.md`](../general/security-and-tenancy.md).
This page names the tiers **this** service actually has.

## There are three, and no more

| Tier | Mechanism | Serves |
|---|---|---|
| Anonymous | none | the published catalogue, concierge and newsletter intake, calculators |
| Service | `X-API-Key` (`apps.api_keys`) | the deployed frontends and internal callers |
| Operator | `permissions.IsAdminUser` — Django's `is_staff` | everything that publishes provenance or mutates the catalogue |

**MUST NOT** add a fourth tier without a second endpoint that needs it. A role
axis with one use is a concept the whole codebase then has to carry: every
future endpoint must decide where it sits on it, every test must construct a
user for it, and the frontend must learn to ask. `is_staff` is the catalogue's
existing operator boundary — `ListingViewSet`, `SourceViewSet` and
`OperatorAssetViewSet` all use it — and a new staff-only endpoint joins that
tier rather than inventing one.

Where a genuinely different capability appears, prefer a **per-object or
per-capability check inside the operator tier** over a new global tier.

## The public projection withholds provenance

The rule that generates most of the day-to-day decisions here:

> **A source's identity and a listing's URL are withheld from anonymous
> callers. Together they are a route around the MLS.**

So `source_code`, `source_name` and `listing_url` are operator-tier fields.
`test_asset_public_contract.py` asserts their absence, and that test is the
contract — not a nicety.

**A `kind` is not identity.** Which *sort* of place a listing came from — a
channel, a marketplace, a portal, direct — names neither a site nor an address,
so it is public and renders as a caveat beside the listing. The distinction to
apply when a new provenance field appears: *does this let a visitor reach the
seller without us?* If yes it is operator-tier; if it only changes how to read
the listing, it may be public.

**Trust resolves fail-closed.** An asset is a dedup cluster of listings, so it
has no single source. Where several disagree, the **least-vouched** kind wins —
the same direction `requires_review` resolves. Never surface the best of a set
of sources as though it described the asset.

## Staff endpoints see the unpublished rows

An operator endpoint **MUST NOT** apply `public_catalog()`. The unpublished
rows are the work: an operator asking why something is invisible needs the
invisible row itself. Gating the operator surface by the public gate produces a
404 for exactly the asset the operator opened the page to inspect.

The corollary is that these endpoints publish state the public gate exists to
hide, which is why the tier boundary above is tested per endpoint rather than
assumed from the router.

## Every staff endpoint carries three access tests

Not one. The tier is the feature on these endpoints, so it gets the coverage a
feature gets:

1. **Anonymous is refused** — `401` or `403`.
2. **A signed-in non-staff user is refused** — `403`. `is_staff`, not
   `is_authenticated`; an account is not an operator. This is the test that
   actually catches the mistake, because a `permission_classes` left at the
   project default passes test 1 and fails test 2.
3. **The withheld fields are absent from the public endpoint's body** — asserted
   against the rendered response, not the serializer's field list, so a field
   reaching the client through a nested serializer or a `to_representation`
   override is still caught.

## A staff endpoint needs its own OpenAPI group

A group is a **client namespace**, and the operator operations must not be
reachable through the same import as the public ones — otherwise the generated
client offers a public page a method that returns a source URL, and only a
reviewer stands between that and a bundle.

Registration mechanics, and the trap where an endpoint whose tag no group
claims silently never generates, are in
[`api-groups-and-generation.md`](./api-groups-and-generation.md).

## Review checklist

- Does this endpoint sit in one of the three tiers, or is it inventing a fourth?
- If it is staff-only: does it have all three access tests?
- Does it publish a source identity or a listing URL to anyone anonymous?
- Does an operator read deliberately skip `public_catalog()`?
- Does a new provenance field let a visitor reach the seller without us?
