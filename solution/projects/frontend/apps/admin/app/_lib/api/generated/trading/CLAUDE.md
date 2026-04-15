# Django CFG API - Typescript Client

Auto-generated. **Do not edit manually.**

```bash
python manage.py generate_client --groups trading --typescript
```

## Stats

| | |
|---|---|
| Version | 3.1.0 |
| Operations | 10 |
| Schemas | 9 |

## Resources

- **trading** (10 ops)

## Operations

**trading:**
- `POST` /apix/trading/orders/ → `trading_orders_create`
- `DELETE` /apix/trading/orders/{id}/ → `trading_orders_destroy`
- `GET` /apix/trading/orders/ → `trading_orders_list`
- `PATCH` /apix/trading/orders/{id}/ → `trading_orders_partial_update`
- `GET` /apix/trading/orders/{id}/ → `trading_orders_retrieve`
- `PUT` /apix/trading/orders/{id}/ → `trading_orders_update`
- `GET` /apix/trading/portfolios/ → `trading_portfolios_list`
- `GET` /apix/trading/portfolios/me/ → `trading_portfolios_me_retrieve`
- `GET` /apix/trading/portfolios/{id}/ → `trading_portfolios_retrieve`
- `GET` /apix/trading/portfolios/stats/ → `trading_portfolios_stats_retrieve`

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

@see https://djangocfg.com/docs/features/api-generation

