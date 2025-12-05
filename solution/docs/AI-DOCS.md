# AI Documentation (MCP Server)

Django-CFG is the **first Django framework with AI-native documentation**. Your AI coding assistant can access documentation instantly via MCP (Model Context Protocol).

## MCP Server Setup

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "djangocfg-docs": {
      "url": "https://mcp.djangocfg.com/mcp"
    }
  }
}
```

### Cursor IDE

Add to Cursor settings (MCP configuration):

```json
{
  "mcpServers": {
    "djangocfg-docs": {
      "url": "https://mcp.djangocfg.com/mcp"
    }
  }
}
```

### Other MCP Clients

Use the server URL: `https://mcp.djangocfg.com/mcp`

## CLI Commands

Search documentation from terminal:

```bash
# Search for topics
poetry run python manage.py ai_docs search "database configuration"
poetry run python manage.py ai_docs search "redis cache" --limit 5

# Get MCP server info
poetry run python manage.py ai_docs mcp

# Show AI hint for your project
poetry run python manage.py ai_docs hint

# JSON output for scripts
poetry run python manage.py ai_docs search "email" --json
```

## Python API

Use programmatically in your code:

```python
from django_cfg.modules.django_ai import search, get_docs

# Search documentation
results = search("How to configure PostgreSQL?")
for result in results:
    print(f"{result.title}: {result.url}")

# Get formatted documentation
docs = get_docs("database configuration")
print(docs)
```

## REST API

Access via HTTP:

```bash
# Search
curl 'https://mcp.djangocfg.com/api/search?q=database&limit=5'

# Get specific topic
curl 'https://mcp.djangocfg.com/api/docs?topic=DatabaseConfig'
```

## CLAUDE.md File

Your project includes a `CLAUDE.md` file that AI assistants automatically detect:

```
projects/django/CLAUDE.md
```

This file contains:
- MCP server configuration
- Common CLI commands
- Quick reference for AI assistants

## What AI Can Help With

Ask your AI assistant about:

- **Configuration**: "How do I configure PostgreSQL in django-cfg?"
- **Features**: "How do I enable email notifications?"
- **Models**: "Show me DatabaseConfig options"
- **Commands**: "What management commands are available?"
- **Deployment**: "How do I deploy with Docker?"

## Example Prompts

```
"Search django-cfg docs for Redis cache configuration"
"How do I set up JWT authentication in django-cfg?"
"What are the options for DjangoRQConfig?"
"Show me how to configure Centrifugo WebSockets"
```

## Benefits

- No copy-pasting documentation into prompts
- Always up-to-date information
- Works with Claude, Cursor, GPT, and any MCP client
- CLI and API access for automation

## More Information

- MCP Test Page: https://djangocfg.com/mcp
- Full Documentation: https://djangocfg.com/docs/ai-agents/documentation-access
