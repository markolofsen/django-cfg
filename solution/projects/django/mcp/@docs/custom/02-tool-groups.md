# 02 — The tool groups

Three groups, 15 tools. The general shape and its reasoning are
[`../general/03-package-shape.md`](../general/03-package-shape.md); this page
is what exists here.

```text
mcp/tools/
  catalog_tools.py    ← SHIM. Discovery sees this, not the package.
  catalog/
    __init__.py       TOOLS = [...]
    _bounds.py        MAX_ROWS, PUBLIC_MAX_ROWS, MAX_LIST_MEDIA, …
    _helpers.py       visible_assets, apply_public_filters, serialize_*
    search_properties.py  facets.py  get_property.py  market_summary.py
  leads_tools.py      ← SHIM
  leads/              list_leads, get_lead, stats, set_status, append_note
  operator_tools.py   ← SHIM
  operator/           search_assets, asset_detail, pipeline_health,
                      publish, unpublish, set_status
  _shared/            arguments.py  responses.py  identity.py  audit.py
  public.py  user.py  ← standalone tools, no group
```

**Never edit a shim to add a tool.** Add it to the package's `TOOLS`.

## Which group

| The tool… | Group |
|---|---|
| reads the published catalogue as a visitor would | `catalog` |
| reads or updates an inbound brief | `leads` |
| inspects or changes catalogue state as staff | `operator` |

`catalog` is the only group whose tools carry `public = True`. Adding a tool
there that a visitor may not see is the mistake this layout is arranged to
prevent: keep it out of the group, or leave the flag off deliberately and say
why.

## `catalog/_helpers.py` reuses the domain; it must not restate it

Three seams, each with exactly one implementation elsewhere:

| Helper | Delegates to |
|---|---|
| `visible_assets()` | `Asset.objects.public_catalog()` — the visibility gate |
| `apply_public_filters()` | `PublicAssetFilter` — the query-param contract |
| `serialize_assets()` | `AssetPublicSerializer` — the privacy allow-list |

The serializer is what withholds `latitude`, `longitude`, `address`,
`seller_name`, `seller_url` and `seller_phone`. A hand-written projection leaks
seller PII the first time someone adds a field to the model.

There is already one second source of truth in this codebase —
`apps/catalog/services/discovery.py:50` re-expresses the visibility gate with
hardcoded `"public"`/`"active"` literals, so a change to the gate must be made
twice. **Do not add a third.**

## What the list rows carry, and why

Set in `catalog/_bounds.py`, each with its reasoning in the file:

- `MAX_ROWS` 50, `PUBLIC_MAX_ROWS` 25 — the anonymous caller has no key to
  revoke, so the page is the only per-request cost lever.
- `MAX_LIST_MEDIA` 1 — a list row keeps the main photo and reports
  `media_count`. Full galleries are `catalog_get_property`'s job.
- `MAX_RESULT_CHARS` 40 000 — the whole-payload backstop. When it trips,
  `description` and `media` are dropped and `payload_trimmed` says so.
- `MAX_OFFSET` 10 000 — deep-paging guard.

Those last three exist because of a measured failure: five searches at 25 rows
returned 168k–490k characters each and none reached the model. The full account
is [`@dev/completed/mcp-agent-ergonomics/`](../../../@dev/completed/mcp-agent-ergonomics/PLAN.md).

## Tests

[`mcp/tests/`](../../tests/) — treat them as security and contract tests, not
happy-path protocol tests.

| File | Pins |
|---|---|
| `test_privacy_and_permissions.py` | the allow-list, and that public tools are public |
| `test_public_row_caps.py` | advertised ceiling == enforced ceiling, per profile; paging; sort |
| `test_public_payload_bounds.py` | the payload ceiling, at the transcript's real shape |
| `test_shared_helpers.py` | argument coercion and the empty shape |

`test_public_row_caps.py` asserts on the SQL slice rather than on the row count
in the payload. A count assertion needs inventory to mean anything: on a
catalogue holding fewer rows than the ceiling, every profile returns the same
number and the test passes while proving nothing.
