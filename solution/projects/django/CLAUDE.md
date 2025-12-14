# DjangoCFG AI Documentation

## MCP Server

```json
{
    "mcpServers": {
        "djangocfg-docs": {
            "url": "https://mcp.djangocfg.com/mcp"
        }
    }
}
```

## CLI

```bash
django-cfg search "database configuration"
django-cfg mcp
django-cfg hint
```

## API

```bash
curl 'https://mcp.djangocfg.com/api/search?q=database&limit=5'
```

## Python

```python
from django_cfg.modules.django_ai import search, get_docs

results = search("database configuration")
docs = get_docs("How to configure PostgreSQL?")
```
