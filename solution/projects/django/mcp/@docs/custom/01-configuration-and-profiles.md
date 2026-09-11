# 01 — Configuration and profiles

Everything on this page is
[`api/settings/mcp_config.py`](../../../api/settings/mcp_config.py). Read it
alongside; this explains the decisions, it does not restate the file.

## Why the config is not in `mcp/`

It was `mcp/__init__.py` until 2026-08-18. Two config objects declared the same
thing, `auto_loader` picked one, and the loser was the file people were
editing. The surviving declaration held a **committed access key**, so the
endpoint served real data under a value anyone with repository read access
could look up.

Any key that predates 2026-08-18 is in git history and must be treated as
public.

## The two profiles

The operator profile is everything the builder declares. The public profile is
added beside it by `enable_public_profile(path=PUBLIC_PATH, ...)` and serves
whatever declares `public = True` on its tool class.

| | operator | public |
|---|---|---|
| Path | `/cfg/mcp/` | `/mcp/` (`PUBLIC_PATH`) |
| Auth | `X-MCP-Access-Key` | none |
| Rate | 100/minute | 20/minute (`PUBLIC_RATE_LIMIT`) |
| Introspection | yes | never |
| Row ceiling | `MAX_ROWS` | `PUBLIC_MAX_ROWS` |

**The tool list is deliberately not restated in settings.** It is derived from
the `public` flag, because a copy in the config file drifts the day someone
adds a tool and forgets to edit it.

**Introspection can never reach the public profile.** django-cfg refuses to
build an anonymous profile with it enabled — introspection describes internal
URLs and schemas to whoever asks. Two live defects were found here on
2026-09-03: `/cfg/mcp/info/` had been listing all 30 tools *with full input
schemas* to anonymous callers, and `rate_limit` was validated, stored and
enforced nowhere.

**The guard is `hasattr(mcp, "enable_public_profile")`.** This project runs
against published django-cfg, unpinned, and profiles landed after 2.2.157. An
unconditional call would raise at settings import on an older release — a total
outage, not a missing feature.

## The access key

`MCP__ACCESS_KEY`, from the environment, never a literal.

**An empty key opens the endpoint.** django-cfg reads
`_access_key_required()` as `bool(access_key)`, so an unset key makes the
endpoint answer 200 to every anonymous probe instead of 401, and nothing in the
logs looks wrong. Right for a laptop, catastrophic in production — so
production refuses to start, and local falls back to
`dev-only-insecure-mcp-key`.

`service_username` binds the key to a Django account, which is what makes
staff-gated tools answer rather than refuse. **It is that account's password by
another name**: point it at a purpose-made, minimally privileged staff user,
never a human's. Mutations are attributed to it — see
[03](03-tool-reference.md).

## Exposed models

Read-only, all of them:

| Model | Cap | Note |
|---|---|---|
| `profiles.UserProfile` | 50 | hides `user_id` |
| `api_keys.APIKey` | 50 | hides `plain_key`, `hashed_key` |
| `catalog.Source` | 100 | |
| `catalog.PropertyType` | 100 | also public |
| `catalog.Developer` | 200 | also public |
| `catalog.Project` | 200 | |

`plain_key` is the credential itself — this model stores it in clear text, so
it must never reach an agent.

The public profile exposes only `catalog.PropertyType` and `catalog.Developer`.
`profiles.UserProfile` and `api_keys.APIKey` have no business on an anonymous
endpoint, read-only or not.

## `env` is imported inside the function

Not at module scope. A module-level `from api.environment import env` binds the
object once, so a test patching `api.environment.env` changes something the
function never reads — and the production-refuses-to-start guard would be
tested against production's own values.

## Targets

`mcp.add_target("local")` and `add_target("prod", "../docker/.env.prod")` are
what give `manage.py mcp_install --local` / `--prod`.

`prod` reads the deployment's own dotenv because the command runs on a laptop,
where the loaded config holds the *development* URL and would otherwise
register a local endpoint under the name "prod".

**This project shares one key across both** (commit `36b060a`), so the two
registrations differ by URL alone. A client aimed at the wrong one does not
fail — it connects, lists everything, and answers from the other environment's
database.
