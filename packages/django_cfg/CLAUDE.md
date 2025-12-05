# DjangoCFG - AI Documentation

DjangoCFG documentation is available via MCP server.

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

## API

```bash
curl 'https://mcp.djangocfg.com/api/search?q=database+configuration&limit=5'
```

## Python

```python
from django_cfg.modules.django_ai import search, get_docs

# Search and get results
results = search("How to configure database?")
for r in results:
    print(r.title, r.url)

# Get formatted documentation
print(get_docs("database configuration"))
```

## Django Command

```bash
poetry run python manage.py ai_docs search "database configuration"
poetry run python manage.py ai_docs search "redis cache" --limit 3
poetry run python manage.py ai_docs search "email smtp" --json
poetry run python manage.py ai_docs info DatabaseConfig
poetry run python manage.py ai_docs mcp
poetry run python manage.py ai_docs hint
```

## Common Topics

- DatabaseConfig - PostgreSQL, MySQL, SQLite
- CacheConfig - Redis, Memcached
- EmailConfig - SMTP, SendGrid
- LoggingConfig - Logging setup
- SecurityConfig - CORS, CSRF
- DRFConfig - Django REST Framework
- NgrokConfig - Ngrok tunnels
