# MCP Integration Architecture

This document describes how MCP tools from external servers are discovered and executed via the SDKRouter agent system.

## The Flow

The SDKRouter does **not** proxy MCP requests. Instead, it orchestrates the agent to call the remote MCP server directly.

```text
User / CmdOp Agent
   │
   ▼ 1. POST /chat/{slug}/sessions/...
SDKRouter (FastAPI)
   │
   ▼ 2. Get Project from DB
   │   KnowledgeBaseProject.objects.get(slug="cmdop-public")
   │
   ▼ 3. Read MCP Config from Project
   │   - mcp_enabled = true
   │   - mcp_server_url = "http://cmdop-django/cfg/mcp/"
   │   - mcp_access_key = "..."
   │
   ▼ 4. Pass config to Agent Runner
Agent Runner (Python)
   │
   ▼ 5. Discover Tools
   │   GET {mcp_server_url}/info/
   │   → Returns 17 tools (e.g., get_cmdop_skills)
   │
   ▼ 6. Execute Tool
   │   POST {mcp_server_url}/
   │   Headers: X-MCP-Access-Key: {mcp_access_key}
   │   Body: { "jsonrpc": "2.0", "method": "tools/call", ... }
   │
   ▼ 7. Return Result
Remote MCP Server (Django)
```

## Configuration Source

The MCP server address and credentials are stored in the **KnowledgeBaseProject** database model.

| Field | Description |
|-------|-------------|
| `mcp_enabled` | `bool` — Whether to enable MCP for this project. |
| `mcp_server_url` | `str` — Base URL of the remote MCP server (e.g., Django-CFG). |
| `mcp_access_key` | `str` — Authentication key passed in `X-MCP-Access-Key` header. |
| `mcp_server_name` | `str` — Friendly name for logging/UI. |

## Agent Logic

The agent logic is located in `agent/runner.py` (Python) and `tools/mcpclient/mcpclient.go` (Go).

### Python (Agent Runner)
```python
# Resolve project to get MCP settings
project = await _resolve_project(deps)

if project and project.mcp_enabled:
    # Discover tools via the fast /info/ endpoint
    tools = await discover_remote_tools(
        server_url=project.mcp_server_url,
        access_key=project.mcp_access_key
    )
    # Attach tools to the agent's toolset
    for tool in tools:
        agent.tools.append(tool)
```

### Go (CmdOp / SDKRouter SDK)
```go
// Get project config from DB
project := sdkrouter.Knowbase.GetProject(ctx, "cmdop-public")

if project.McpEnabled {
    // Discover tools
    tools, err := client.MCPClient.DiscoverTools(
        ctx,
        project.McpServerURL,
        project.McpAccessKey,
    )
    // Execute tool
    result, err := client.MCPClient.CallTool(
        ctx,
        project.McpServerURL,
        project.McpAccessKey,
        "get_cmdop_skills",
        args,
    )
}
```

## Caching

To avoid hitting the MCP server for every single message, tool discovery is cached:
- **TTL**: 5 minutes.
- **Key**: Hash of `(server_url + access_key)`.
- **Invalidation**: If a tool call fails with "tool not found", the cache is cleared and discovery is retried once.

## Security

- **No Proxy**: The user's request is not proxied through the SDKRouter to the MCP server. The Agent (server-side) makes the call.
- **Authentication**: The `X-MCP-Access-Key` header is required for all MCP endpoints.
- **Isolation**: Only tools explicitly enabled in the remote MCP server are available.
