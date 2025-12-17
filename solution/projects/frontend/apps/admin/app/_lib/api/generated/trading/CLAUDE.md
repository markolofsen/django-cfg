# Django CFG API - Typescript Client

Auto-generated. **Do not edit manually.**

```bash
python manage.py generate_client --groups trading --typescript
```

## Stats

| | |
|---|---|
| Version | 3.0.3 |
| Operations | 10 |
| Schemas | 9 |

## Resources

- **trading** (10 ops)

## Operations

**trading:**
- `POST` /api/trading/orders/ → `trading_orders_create`
- `DELETE` /api/trading/orders/{id}/ → `trading_orders_destroy`
- `GET` /api/trading/orders/ → `trading_orders_list`
- `PATCH` /api/trading/orders/{id}/ → `trading_orders_partial_update`
- `GET` /api/trading/orders/{id}/ → `trading_orders_retrieve`
- `PUT` /api/trading/orders/{id}/ → `trading_orders_update`
- `GET` /api/trading/portfolios/ → `trading_portfolios_list`
- `GET` /api/trading/portfolios/me/ → `trading_portfolios_me_retrieve`
- `GET` /api/trading/portfolios/{id}/ → `trading_portfolios_retrieve`
- `GET` /api/trading/portfolios/stats/ → `trading_portfolios_stats_retrieve`

## Usage

```typescript
import { APIClient } from './';

const client = new APIClient({ baseUrl, token });

await client.trading.list();
await client.trading.retrieve({ id: 1 });
await client.trading.create({ ... });
```

**SWR Hooks:**
```typescript
import { useTradingList } from './hooks';
const { data, isLoading } = useTradingList();
```

## How It Works

```
DRF ViewSets → drf-spectacular → OpenAPI → IR Parser → Generator → This Client
```

**Configuration** (`api/config.py`):
```python
openapi_client = OpenAPIClientConfig(
    enabled=True,
    groups=[OpenAPIGroupConfig(name="trading", apps=["..."])],
    generate_zod_schemas=True,  # → schemas.ts
    generate_fetchers=True,     # → fetchers.ts
    generate_swr_hooks=True,    # → hooks.ts
)
```

**Copy to Next.js** (if `nextjs_admin` configured):
```python
nextjs_admin = NextJsAdminConfig(
    project_path="../frontend/apps/...",
    api_output_path="app/_lib/api/generated",
)
```

@see https://djangocfg.com/docs/features/api-generation
