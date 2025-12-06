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
# In this project
pnpm ai-docs search "database configuration"
pnpm ai-docs mcp

# Or globally (after: npm install -g @djangocfg/nextjs)
djangocfg-docs search "database configuration"
djangocfg-docs mcp
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
