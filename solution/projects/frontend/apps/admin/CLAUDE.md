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

## CLI Search (Fast)

```bash
django-cfg search "database configuration"
django-cfg search "redis cache" --limit 3
```

## API

```bash
curl 'https://mcp.djangocfg.com/api/search?q=database&limit=5'
```

## TypeScript

```ts
import { search, getDocs } from '@djangocfg/nextjs/ai';

const results = await search('database configuration');
```
