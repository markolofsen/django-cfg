# Django MCP Module — Model Context Protocol

Transform any Django-CFG project into an MCP server for AI agents.

## What it does

- 🤖 **11 built-in tools** — introspection, ORM queries, aggregations, time-series, user lookup
- 🔒 **Secure by default** — deny-by-default, field redaction, row limits, command sandboxing
- 🔌 **Auto-discovery** — drop `mcp/__init__.py` and `mcp/tools/*.py` in your project root
- 🧠 **LLM agent** — `/cfg/mcp/agent/` endpoint, uses `django_llm` (OpenRouter)
- 📡 **Full MCP protocol** — JSON-RPC 2.0 on `/cfg/mcp/`

## Quick Start

### 1. Create `mcp/__init__.py` in project root

```python
from django_cfg import MCPConfigBuilder

mcp = MCPConfigBuilder()

# Expose models
mcp.expose("profiles.UserProfile", read_only=True, max_results=50)
mcp.expose("accounts.User", hidden_fields=["password", "secret_key"])

# Allow commands
mcp.allow_command("clearsessions")

# Enable introspection
mcp.enable_introspection(expose_urls=True)

# Set access key (required)
mcp.set_access_key("your-secret-key")

# Custom tools
@mcp.tool(name="get_stats", description="Get system stats")
def get_stats(ctx) -> str:
    import psutil
    return f"CPU: {psutil.cpu_percent()}%"

mcp_config = mcp.build()
```

### 2. Use the agent

```bash
# Chat with the agent
curl -X POST http://localhost:8000/cfg/mcp/agent/ \
  -H "Content-Type: application/json" \
  -H "X-MCP-Access-Key: your-secret-key" \
  -d '{"message": "How many active users?"}'
```

```json
{
  "response": "You have 1,234 active users.",
  "tool_calls": 1,
  "session_id": "agent-session"
}
```

## Endpoints

| Endpoint | Protocol | Use |
|----------|----------|-----|
| `POST /cfg/mcp/` | JSON-RPC 2.0 | MCP protocol (tools/list, tools/call) |
| `POST /cfg/mcp/agent/` | REST | Chat-style agent interface |

## Built-in Tools (11)

| Category | Tools |
|----------|-------|
| **Introspection** | `list_apps`, `get_model_schema`, `list_urls` |
| **User Info** | `get_user_info` — lookup by ID, email, or username |
| **Data Access** | `query_model`, `get_object` — ORM with filters |
| **Commands** | `execute_command` — whitelisted management commands |
| **Analytics** | `aggregate_model`, `time_series`, `top_values`, `distribution` |
| **Project** | Auto-discovered from `mcp/tools/*.py`, on top of the 11 |

## Security

| Layer | Mechanism |
|-------|-----------|
| **Auth** | `X-MCP-Access-Key`, enforced with `401` — **only when `access_key` is set**; unset means open |
| **Models** | Deny-by-default — only exposed models accessible |
| **Fields** | Automatic PII redaction (emails, phones, keys) |
| **Queries** | Max rows, cost estimation, read-only by default |
| **Commands** | Whitelist only, 30s timeout, stdout captured |

`GET /cfg/mcp/info/` is public by design and lists every tool with its schema.
Not a data leak, but it is reconnaissance — block it at the proxy on a public
host.

> **Check a deployed server before trusting its auth.** Until 2026-08-04 the
> access key was compared and then ignored, so tools ran for unauthenticated
> callers while `tools/list` kept answering `200`. A request with no key must
> return `401`:
>
> ```bash
> curl -s -o /dev/null -w '%{http_code}\n' -X POST <url> \
>   -H 'Content-Type: application/json' \
>   -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
> ```

## LLM

- **Default model**: `openai/gpt-4.1-nano` via OpenRouter
- **Configuration**: Uses your project's `django_llm` setup — no separate keys
- **Override**: `mcp.set_llm_model("anthropic/claude-3.5-haiku")`

## Project Structure

```
project_root/
├── mcp/
│   ├── __init__.py          # MCPConfigBuilder config
│   └── tools/               # Custom tools (auto-discovered)
│       ├── __init__.py
│       └── orders.py        # Your custom tools
├── manage.py
└── api/
    └── config.py            # Django-CFG config
```

## Files

| File | Purpose |
|------|---------|
| `__cfg__.py` | Pydantic config model |
| `config_builder.py` | `MCPConfigBuilder` API |
| `apps.py` | Django AppConfig + auto-discovery |
| `views.py` | MCP JSON-RPC endpoint |
| `auto_loader.py` | Discovers `mcp/` from project root |
| `tools/` | Built-in tools (introspection, queries) |
| `agent/` | Agent runner, ORM tools, context |
| `sql/` | AST validator, cost estimator |
| `services/` | Redaction, context management |

## Docs

Public guide: [AI MCP Guide](https://djangocfg.com/guides/ai-mcp)

Module-level detail lives in [`@docs/`](./@docs/README.md):

| Page | Read it when |
|------|--------------|
| [architecture.md](./@docs/architecture.md) | You are changing the request path — it states the auth and statelessness invariants and why both once broke. |
| [tools.md](./@docs/tools.md) | You are writing a tool. |
| [configuration.md](./@docs/configuration.md) | You need a config field's exact effect. |
| [agent-chat.md](./@docs/agent-chat.md) | You are touching the admin SSE chat. |
| [redis.md](./@docs/redis.md) | Cache, budget, or chat history. |
| [remote-consumption.md](./@docs/remote-consumption.md) | You are *calling* a remote MCP server rather than serving one. |
