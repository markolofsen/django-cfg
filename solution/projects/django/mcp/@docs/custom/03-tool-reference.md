# 03 — Tool reference

What each tool answers, and what its result means. The authoritative text is
each tool's own `description` — this page adds what a reader needs *around*
that.

## catalog — the published catalogue (4, public)

The only group an anonymous caller reaches. Every tool reads
`Asset.objects.public_catalog()`: published + public + active + a canonical
slug + a non-member cluster role. **A property absent here may still exist** —
folded into a duplicate cluster, or unpublished — which is why
`catalog_get_property` says so rather than returning a bare miss.

| Tool | Answers |
|---|---|
| `catalog_search_properties` | filtered, sorted, paged listings |
| `catalog_get_property` | one property in full, by slug or UUID |
| `catalog_facets` | the valid filter values, with counts |
| `catalog_market_summary` | per-market inventory and price ranges |

**Read `search_mode` before concluding anything from an empty search.**
`literal_only` means `q` was substring-matched against the title, so a query in
another language or one describing a feature finds nothing *even when such
properties exist*. `hybrid` means the semantic lane also ran. The two produce
identical shapes, and an agent that cannot tell them apart reads "no semantic
match" as "no such inventory".

**A list row is a decision, not a card.** One photo plus `media_count`, a
shortened description, and — once backfilled — a one-sentence `summary`. Call
`catalog_get_property` for the gallery and the full text. If `payload_trimmed`
is set, `description` and `media` were dropped wholesale to fit the ceiling.

**`price_per_sqm` is only meaningful with `price_per_sqm_basis: "building"`.**
Where ingestion could not separate floor area from plot, both size fields hold
one number; the derivation refuses and leaves the field null. Sorting by
`price_per_sqm_asc` puts those rows last rather than first — which is what they
would otherwise be, since they read as the cheapest per m² in the catalogue.
Measured 2026-09-03: **727 rows** carry a figure from the pre-fix rule.

**`catalog_facets` does not describe the whole catalogue.** Measured
2026-09-03: **9 793 of 14 290 published properties (68.5%) match no market** —
Dominican Republic 3 085, United States 1 152, Costa Rica 1 079, Curaçao 839,
and a long tail. They are reachable by `country`, never by `region`, and no
market count includes them. The tool reports the total under `unmarketed`;
without that an agent concludes the catalogue is five markets.

## leads — inbound briefs (5, operator)

| Tool | Answers |
|---|---|
| `leads_list` | inbound leads, newest first |
| `leads_get` | one lead in full |
| `leads_stats` | counts by status, recent arrivals, untouched |
| `leads_set_status` | move one lead's status |
| `leads_append_note` | add a note without overwriting |

**Run `leads_stats` before concluding the queue is empty.** A filtered
`leads_list` returns nothing while work waits under a different status — the
distinction an empty list cannot make.

`leads_append_note` appends; it never rewrites the existing note. That is the
difference between a record and a whiteboard.

## operator — the catalogue as a control surface (6, operator)

| Tool | Answers |
|---|---|
| `operator_search_assets` | staff-side search, ignores the public gate |
| `operator_asset_detail` | one asset with internal state |
| `operator_pipeline_health` | what is held back, and by which clause |
| `operator_publish` | publish by explicit id list |
| `operator_unpublish` | withdraw by explicit id list |
| `operator_set_asset_status` | set status by explicit id list |

**The three mutations take an explicit id list, never a filter.** A filter
means the model chose the set; a list means an operator saw it. They also
require a **staff-bound** access key — `service_username` in the config — so a
key without one gets a refusal rather than a partial success.

**Every mutation is audited** to `core.MCPAuditEntry`. This project had no
audit substrate before it: `simple_history` registers no models here, and
`.update()` bypasses `admin.LogEntry` entirely, so this record is the only
account of who changed what. Attribution is to the service account, which is
why that account must be purpose-made rather than a human's.

`operator_pipeline_health` is the first call for "what needs attention" — it
names *which clause of the public gate* holds each asset back, which is
otherwise a dozen searches.

## django-cfg built-ins (operator only)

`query_model`, `get_model_schema`, `aggregate_model`, `list_apps`, `list_urls`,
`get_user_info` and friends come from the framework, over the models listed in
[01](01-configuration-and-profiles.md).

They are **capabilities, not approval**: generic and unscoped by nature, which
is exactly why the public profile has none of them and why introspection can
never reach it.
