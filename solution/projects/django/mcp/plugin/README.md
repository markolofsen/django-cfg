# Claude Code plugin — source

These four files are the **source** of a Claude Code plugin marketplace. They
are not used by this Django service; they are here because this is where the
MCP server they describe is defined, and a copy that lives beside the server
cannot drift from it.

To publish, copy this directory to the root of a **public GitHub repository**.
Claude Code fetches marketplaces from GitHub by `owner/repo`, so it cannot read
this project's GitLab origin.

```
<repo-root>/
  .claude-plugin/marketplace.json
  plugins/caribbean-mls/.claude-plugin/plugin.json
  plugins/caribbean-mls/.mcp.json
```

A visitor then runs two commands:

```bash
claude plugin marketplace add <owner>/<repo>
claude plugin install caribbean-mls@caribbean-mls
```

## Why this exists alongside the copy-paste command

`claude mcp add --transport http …` already works and is one line, so the
plugin is not a replacement — it is the version that can carry more later.
A plugin can ship skills, subagents and slash commands beside the server, and
it updates when the marketplace does; a pasted command is frozen at the moment
it was pasted.

## The `.mcp.json` shape is not what the docs say

The reference documentation wraps servers in an `mcpServers` object. The
plugin loader does not: the file is a bare map of name to definition, which is
what Sentry's published plugin ships and what `claude plugin validate` accepts.
Follow the shape here, not the prose.

```json
{ "caribbean-mls": { "type": "http", "url": "https://mcp.caribbeanrealestatemls.com/mcp/" } }
```

## Keep the URL in step

The endpoint appears here and in `NEXT_PUBLIC_MCP_URL` on the frontend. This
file cannot read that variable — it is static JSON fetched by a client that
has never seen our deployment — so a change to the public endpoint has to be
made in both. That duplication is the cost of being installable at all.

Validate after any edit:

```bash
claude plugin validate .
```
