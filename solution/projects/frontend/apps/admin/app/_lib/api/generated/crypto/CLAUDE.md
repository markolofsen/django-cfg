# Django CFG API - Typescript Client

Auto-generated. **Do not edit manually.**

```bash
python manage.py generate_client --groups crypto --typescript
```

## Stats

| | |
|---|---|
| Version | 3.0.3 |
| Operations | 7 |
| Schemas | 8 |

## Resources

- **crypto** (7 ops)

## Operations

**crypto:**
- `GET` /api/crypto/coins/ → `crypto_coins_list`
- `GET` /api/crypto/coins/{id}/ → `crypto_coins_retrieve`
- `GET` /api/crypto/coins/stats/ → `crypto_coins_stats_retrieve`
- `GET` /api/crypto/exchanges/ → `crypto_exchanges_list`
- `GET` /api/crypto/exchanges/{slug}/ → `crypto_exchanges_retrieve`
- `GET` /api/crypto/wallets/ → `crypto_wallets_list`
- `GET` /api/crypto/wallets/{id}/ → `crypto_wallets_retrieve`

## Usage

```typescript
import { APIClient } from './';

const client = new APIClient({ baseUrl, token });

await client.crypto.list();
await client.crypto.retrieve({ id: 1 });
```

**SWR Hooks:**
```typescript
import { useCryptoList } from './hooks';
const { data, isLoading } = useCryptoList();
```

## How It Works

```
DRF ViewSets → drf-spectacular → OpenAPI → IR Parser → Generator → This Client
```

**Configuration** (`api/config.py`):
```python
openapi_client = OpenAPIClientConfig(
    enabled=True,
    groups=[OpenAPIGroupConfig(name="crypto", apps=["..."])],
    generate_zod_schemas=True,  # → schemas.ts
    generate_fetchers=True,     # → fetchers.ts
    generate_swr_hooks=True,    # → hooks.ts
)
```

@see https://djangocfg.com/docs/features/api-generation

