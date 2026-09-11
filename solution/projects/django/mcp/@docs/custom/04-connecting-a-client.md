# 04 — Connecting a client

Two audiences, two routes. Pick by whether the caller needs a key.

## Public — no key, nothing to install

The anonymous profile is a plain HTTP MCP endpoint:

```
https://mcp.caribbeanrealestatemls.com/mcp/
```

Four `catalog_*` tools, 20 requests/minute, no credential. For Claude Code it
is also packaged as a plugin — [`mcp/plugin/`](../../plugin/README.md), whose
`.mcp.json` names that URL and nothing else.

That URL serves the **public** profile only. `/cfg/mcp/` on the API host is the
operator one, and `/mcp/agent/` does not exist anonymously — an anonymous
caller must not be able to spend the deployment's LLM budget.

## Operator — `manage.py mcp_install`

Registers this server with Claude Code and Codex. It writes only the *client*
side; Django already serves the endpoint.

```bash
python manage.py mcp_install --local              # http://127.0.0.1:8000/cfg/mcp/
python manage.py mcp_install --prod               # the deployment's APP__API_URL
python manage.py mcp_install --local --dry-run    # show the changes, write nothing
python manage.py mcp_install --local --uninstall

python manage.py mcp_doctor                       # is any of this actually wired?
```

Useful flags: `--agent claude|codex`, `--url` (with `--name`), `--key`,
`--scope`, and `--key-env-var` (Codex only — reads the key from an environment
variable at request time instead of writing it into the config file).

**It is a management command, not a script, because the endpoint and the key
already live in the Django config.** Anything external has to be told them
again, and a second copy of a credential goes stale silently. The machinery is
`django_cfg.modules.django_mcp.install`; this project only declares its targets
in [`../../api/settings/mcp_config.py`](../../../api/settings/mcp_config.py),
beside the key itself.

## Local and prod are two registrations, not one setting

They are separate entries under separate names, and this is the trap worth
naming: **both ends serve the same tools over the same protocol**, and this
project deliberately shares one access key across them (commit `36b060a`).

So a client aimed at the wrong one **does not fail**. It connects, lists every
tool, and answers from the other environment's database. The two registrations
differ by URL alone — which is exactly why the names must not be mixed up, and
why `--prod` reads the deployment's own dotenv rather than the config loaded on
your laptop.

## Verifying

`curl` is not a verification — see
[`../general/05-verifying-a-tool.md`](../general/05-verifying-a-tool.md). It
sends whatever JSON you type, while a real client negotiates a session and
reads the response the way the protocol specifies. Two bugs in this project's
history passed a full `curl` pass and failed every real client.

Finish with the assistant you intend people to use, and call a tool rather than
listing them.
