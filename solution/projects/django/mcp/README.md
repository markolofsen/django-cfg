# MCP Server — MLS Django

Exposes this Django project to AI agents over the Model Context Protocol.

- **Config:** [`../api/settings/mcp_config.py`](../api/settings/mcp_config.py) —
  the *only* place access is declared. It moved out of `__init__.py` on
  2026-09-02; see that file's docstring for why. Tools in [`tools/`](tools/) are
  still auto-discovered at startup.
- **Endpoints:** `POST /cfg/mcp/` (operator, `X-MCP-Access-Key`) and `/mcp/`
  (public, keyless, the four `catalog_*` tools) — also served at
  `https://mcp.caribbeanrealestatemls.com/mcp/`.
- **Documentation:** [`@docs/`](@docs/README.md) —
  [`general/`](@docs/general/README.md) for how to build an MCP surface,
  [`custom/`](@docs/custom/README.md) for this one's profiles, groups and tools.
- **Delivery tracks:**
  [operator surface](../@dev/completed/mcp-operator-surface/PLAN.md) (leads +
  catalogue control) ·
  [public endpoint](../@dev/active/public-mcp-discovery/PLAN.md) (read-only,
  keyless, discoverable) ·
  [agent ergonomics](../@dev/completed/mcp-agent-ergonomics/PLAN.md) (payload
  ceilings and what an agent actually hit).

## Know this before touching anything

**The key lives in the environment, and an empty one OPENS the endpoint.**
`MCP__ACCESS_KEY` — never a literal in this repository, where it was until
2026-09-02 and is therefore burnt in git history. The trap is that the framework
reads `_access_key_required()` as `bool(access_key)`: no key configured means no
key *required*, which is right for a laptop and catastrophic in production,
where every probe answers 200 instead of 401 and nothing looks wrong. So
`mcp_config.py` raises in production rather than starting unauthenticated, and
falls back locally to `dev-only-insecure-mcp-key` — deliberately not
secret-shaped, so nobody can paste it into a production `.env` and have it work.

**There is exactly one declaration, and there used to be two.** This package
built its own `mcp_config` until 2026-09-02, and `MCPConfig.ready()` replaced the
settings-declared object with it. The one that actually served requests was
therefore the one holding the committed key — measured, not theorised: the live
`access_key` read `propapis-dev-key-2025` at runtime. Do **not** reintroduce an
`mcp_config` name in `mcp/__init__.py`; the auto-loader looks for exactly that.

**A key has an identity, and by default it is nobody.** A valid key
authenticates as `AnonymousUser`, so tools gated on `user.is_staff` refuse — and
to an agent a refusal reads almost exactly like an empty result, which is how
half a working surface looks like missing data. `MCP__SERVICE_USERNAME` binds
the key to a real account. It takes a `USERNAME_FIELD` value, **which here is an
email**; a bare name matches no row and rejects *every* request rather than
degrading to anonymous. It is that account's password by another name — point it
at a purpose-made, minimally privileged staff user, never a human's.

**Authorization is per-profile, not per-tool.** A *profile* binds an access
rule, a tool set and a mount path, and one process serves several. This service
serves two:

| Profile | Path | Access | Tools |
|---|---|---|---|
| `operator` | `/cfg/mcp/` | key | all 31 |
| `public` | `/mcp/` | anonymous | the 4 `catalog_*` |

The profile is resolved from the **URL**, never a header — a header would let
the caller pick their own surface. `tools/list` is filtered by profile and
`tools/call` re-checks, so an `operator_*` name posted at `/mcp/` answers *not
found*: filtering the listing alone would be cosmetic, since a caller who
learned the name elsewhere could still invoke it, and a permission error would
confirm the tool exists.

The public set is not listed anywhere in this project. It is whatever declares
`public = True` on its tool class — a list in the config would be a second
source that drifts the day someone adds a tool.

The public profile is also cheaper to serve: 20 requests/minute per IP against
the operator's 100, and 25 rows per search against 50 (`_bounds.py`). Anonymous
callers have no key to revoke, so the page and the rate are the only units of
cost there is any control over.

**A tool that varies by profile must vary its schema too.** `catalog_search_properties`
overrides `schema_for(profile)` so the anonymous listing advertises the ceiling
it will actually enforce. Clamping only in `execute` would advertise 1-50 and
return 25 — which an agent reads as a broken server rather than as a policy.

> Until 2026-09-03 this said the two lanes could not share a process, because
> `_access_key_required()` was one boolean for the whole endpoint. That was
> true, and django-cfg 2.2.158 removed the constraint rather than working
> around it.

**`GET /cfg/mcp/info/` needs the key.** It used to list every tool with its full
input schema to anyone — never a data leak, since execution always needed the
key, but the names and argument shapes mapped the service for whoever asked.
The anonymous `/mcp/info/` still answers without one, listing only its own four
tools, because that is what an anonymous profile is for.

A working `/info/` is still **not** evidence that your key is right: it
distinguishes 401 from 200, not a correct key from a wrong one. Verify with an
actual `tools/call`.

**Registering is not working.** A tool can import cleanly, register, and appear
in `tools/list` for its entire life while raising on every call. Finish by
invoking the tool, not by counting the registry. `curl` also does not verify the
protocol — two bugs in the sibling service passed a full `curl` pass and failed
every real MCP client.

## Tools (31)

| Group | Tools | Notes |
|---|---|---|
| **Catalogue** (4) | `catalog_search_properties` · `catalog_get_property` · `catalog_facets` · `catalog_market_summary` | Public-safe by construction: every read goes through `Asset.objects.public_catalog()` and `AssetPublicSerializer`, so nothing here is disclosed that the website does not already serve anonymously. **`q` is a literal substring match on the title** — a query in another language, or one naming a feature, finds nothing even when matching properties exist. Every description says so. |
| **Operator** (6) | `operator_search_assets` · `operator_asset_detail` · `operator_pipeline_health` · `operator_publish` · `operator_unpublish` · `operator_set_asset_status` | **Staff-bound; never expose publicly.** Reads return seller contact details, coordinates and valuation. Writes go through `apps/catalog/services/publish.py` — the same transition the admin uses — take explicit id lists, and are audited. `operator_asset_detail` answers *why* a property is not live, clause by clause. |
| **Leads** (5) | `leads_list` · `leads_get` · `leads_stats` · `leads_set_status` · `leads_append_note` | Contact details come from `leads_get` on **one** id, never from the list. Writes are staff-bound, run on the `estate` connection under `select_for_update`, and are audited. |
| **Reference** (3) | `get_data_sources` · `get_property_types` · `get_developers` | Predate the groups above. |
| **User** (2) | `get_user_profile` · `get_user_api_keys` | Need an identity; refuse an unbound key. |
| **django-cfg built-ins** (11) | `list_apps` · `get_model_schema` · `list_urls` · `get_user_info` · `query_model` · `get_object` · `aggregate_model` · `time_series` · `top_values` · `distribution` · `execute_command` | `execute_command` is registered unconditionally by the framework but **zero commands are whitelisted**, so every call refuses. |

### The two rules the groups are built on

**A mutation calls a domain service, never a raw ORM write** — so the admin, a
command and this surface cannot diverge.

**An empty answer is loud.** Every result with nothing in it carries
`filters_applied`, `empty_reason` and `hint`, because an agent cannot ask a
follow-up: a bare `[]` reads as "nothing is wrong, there is none of this" even
when the real cause was a rejected filter. Refusals are shaped differently again
(`error` + `hint`) — "you may not" and "there is none" must not look alike.

## Audit

Every state-changing call writes `core.MCPAuditEntry` — tool, actor, target ids,
outcome, duration. Refusals are recorded too, so attempted privileged calls are
visible.

This is the **only** record of who changed what: `simple_history` is enabled
with no model registered, and the publish services use `.update()`, which
bypasses `post_save` and `admin.LogEntry` alike. Free text is stored as its
length, never its content.

## Configuration

```bash
# api/environment/.env.secrets — never committed
MCP__ACCESS_KEY=...                     # required in production; empty = open endpoint
MCP__SERVICE_USERNAME=ops@example.com   # a USERNAME_FIELD value: an EMAIL here
```

Locally both may be omitted; the key falls back to `dev-only-insecure-mcp-key`
and tools needing staff identity will refuse.

## Testing

```bash
KEY="${MCP__ACCESS_KEY:-dev-only-insecure-mcp-key}"

# 1. List tools
curl -s -X POST http://localhost:8000/cfg/mcp/ \
  -H "Content-Type: application/json" -H "X-MCP-Access-Key: $KEY" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python3 -m json.tool

# 2. Call one
curl -s -X POST http://localhost:8000/cfg/mcp/ \
  -H "Content-Type: application/json" -H "X-MCP-Access-Key: $KEY" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_data_sources","arguments":{}},"id":2}' \
  | python3 -m json.tool

# 3. Confirm the endpoint is not open — this MUST print 401, never 200
curl -s -o /dev/null -w '%{http_code}\n' -X POST http://localhost:8000/cfg/mcp/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

## Adding a tool

Discovery globs `tools/*.py` — **flat and non-recursive**, so a package
registers nothing on its own and needs a `<group>_tools.py` shim importing its
`TOOLS` list. Sub-modules import absolutely (`from mcp.tools.catalog._helpers
import …`); relative imports fail, because a discovered module is loaded by path
rather than as a package member. Files starting with `_` are skipped, which is
why shared code lives in `_shared/`.

New groups follow the package layout
[`@rules/custom/mcp-tools.md`](../@rules/custom/mcp-tools.md) requires: ceilings
in the group's own `_bounds.py`, arguments clamped rather than raised, and every
empty result returned through `empty()` with `filters_applied` / `empty_reason`
/ `hint`.

Verify it registered — then **call it**:

```bash
PYTHONPATH=. .venv/bin/python -c "
import os, django; os.environ['DJANGO_SETTINGS_MODULE'] = 'api.settings.base'; django.setup()
from django_cfg.modules.django_mcp.tools.base import tool_registry
print(len(tool_registry._tools), sorted(tool_registry._tools))"
```

## See also

- Module docs: `django_cfg/modules/django_mcp/@docs/` — `architecture.md` for
  the request lifecycle and the 401 invariant.
