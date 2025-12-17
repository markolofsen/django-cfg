# Django CFG API - Typescript Client

Auto-generated. **Do not edit manually.**

```bash
python manage.py generate_client --groups profiles --typescript
```

## Stats

| | |
|---|---|
| Version | 3.0.3 |
| Operations | 10 |
| Schemas | 8 |

## Resources

- **Profiles** (10 ops)

## Operations

**Profiles:**
- `POST` /api/profiles/profiles/ → `profiles_profiles_create`
- `DELETE` /api/profiles/profiles/{id}/ → `profiles_profiles_destroy`
- `GET` /api/profiles/profiles/ → `profiles_profiles_list`
- `PATCH` /api/profiles/profiles/me/ → `profiles_profiles_me_partial_update`
- `GET` /api/profiles/profiles/me/ → `profiles_profiles_me_retrieve`
- `PUT` /api/profiles/profiles/me/ → `profiles_profiles_me_update`
- `PATCH` /api/profiles/profiles/{id}/ → `profiles_profiles_partial_update`
- `GET` /api/profiles/profiles/{id}/ → `profiles_profiles_retrieve`
- `GET` /api/profiles/profiles/stats/ → `profiles_profiles_stats_retrieve`
- `PUT` /api/profiles/profiles/{id}/ → `profiles_profiles_update`

## Usage

```typescript
import { APIClient } from './';

const client = new APIClient({ baseUrl, token });

await client.profiles.list();
await client.profiles.retrieve({ id: 1 });
await client.profiles.create({ ... });
```

**SWR Hooks:**
```typescript
import { useProfilesList } from './hooks';
const { data, isLoading } = useProfilesList();
```

## How It Works

```
DRF ViewSets → drf-spectacular → OpenAPI → IR Parser → Generator → This Client
```

**Configuration** (`api/config.py`):
```python
openapi_client = OpenAPIClientConfig(
    enabled=True,
    groups=[OpenAPIGroupConfig(name="profiles", apps=["..."])],
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
