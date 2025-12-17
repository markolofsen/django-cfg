# API Client Code Generation

Type-safe API clients (Python, TypeScript, Go, Proto) from DRF endpoints via OpenAPI schema.

## Quick Start

```bash
python manage.py generate_client                    # All languages, all groups
python manage.py generate_client --typescript       # TypeScript only
python manage.py generate_client --groups profiles  # Specific group
python manage.py generate_client --no-build         # Skip Next.js build
```

## Pipeline

```
DRF ViewSets → drf-spectacular → OpenAPI Schema → IR Parser → Generators → Clients
                                                                    ↓
                                              Copy to Next.js → Build & Archive
```

## Configuration (api/config.py)

```python
openapi_client: OpenAPIClientConfig = OpenAPIClientConfig(
    enabled=True,                      # REQUIRED to enable
    groups=[                           # REQUIRED - at least one group
        OpenAPIGroupConfig(name="profiles", apps=["apps.profiles"]),
    ],
    # All other fields have sensible defaults
)

nextjs_admin: NextJsAdminConfig = NextJsAdminConfig(
    project_path="../frontend/apps/admin",  # REQUIRED - only this field
)
```

## OpenAPIClientConfig

| Field | Default | Description |
|-------|---------|-------------|
| `enabled` | `False` | **Must set True** |
| `groups` | `[]` | **Required when enabled** |
| `output_dir` | `"openapi"` | Output directory |
| `api_prefix` | `"api"` | URL prefix (/api/...) |
| `drf_title` | `"API"` | OpenAPI title |
| `drf_description` | `"RESTful API"` | OpenAPI description |
| `drf_version` | `"1.0.0"` | OpenAPI version |
| `drf_schema_path_prefix` | `None` → `/api/` | Schema path prefix |
| `drf_enable_browsable_api` | `True` | DRF browsable API |
| `drf_enable_throttling` | `False` | DRF throttling |
| `generate_python` | `True` | Python client |
| `generate_typescript` | `True` | TypeScript client |
| `generate_zod_schemas` | `False` | Zod validation (TS) |
| `generate_fetchers` | `False` | Typed fetchers (TS, needs Zod) |
| `generate_swr_hooks` | `False` | SWR hooks (TS, needs fetchers) |
| `generate_package_files` | `False` | package.json/pyproject.toml |
| `client_structure` | `"namespaced"` | `"namespaced"` or `"flat"` |
| `enable_archive` | `True` | Archive with versioning |
| `archive_retention_days` | `30` | Days to keep archives |

**TypeScript chain:** `zod_schemas` → `fetchers` → `swr_hooks`

## NextJsAdminConfig

| Field | Default | Description |
|-------|---------|-------------|
| `project_path` | — | **REQUIRED** - Path to Next.js project |
| `api_output_path` | `"apps/admin/app/_lib/api/generated"` | Where to copy TS clients |
| `static_output_path` | `"out"` | Next.js build output |
| `static_url` | `"/cfg/nextjs-admin/"` | URL prefix for static files |
| `dev_url` | `"http://localhost:3001"` | Dev server URL |
| `iframe_route` | `"/private"` | Route in iframe |
| `iframe_sandbox` | `"allow-same-origin allow-scripts..."` | Iframe sandbox attrs |
| `tab_title` | `"Next.js Admin"` | Admin tab title |

## Groups

Each group = separate OpenAPI schema + separate client package:

```python
groups=[
    OpenAPIGroupConfig(name="profiles", apps=["apps.profiles"], title="Profiles API"),
    OpenAPIGroupConfig(name="cfg", apps=["django_cfg.*"]),  # Wildcard
]
```

**Auto-discovery:** `cfg_*` groups for django_cfg.apps.*, `ext_*` for extensions.apps.*

## Command Flags

```bash
--python/--typescript/--go/--proto  # Language selection
--no-python/--no-typescript/...     # Skip language
--groups NAME [NAME...]             # Specific groups
--no-build                          # Skip Next.js build
--dry-run / --validate              # Check config
```

## Output

```
openapi/
├── schemas/{group}.yaml
└── clients/{python,typescript,go}/{group}/
```

## Usage

```typescript
// TypeScript
import { ProfilesClient } from '@/lib/api/generated/profiles';
const client = new ProfilesClient({ baseUrl, token });
await client.profiles.list({ page: 1 });

// SWR hooks (if generate_swr_hooks=True)
import { useProfilesList } from '@/lib/api/generated/profiles/hooks';
```

```python
# Python
from profiles.client import ProfilesClient
client = ProfilesClient(base_url="...", token="...")
await client.profiles.list(page=1)
```

## Troubleshooting

```bash
python manage.py validate_openapi --fix  # Fix missing type hints
python manage.py generate_client --validate
```
