# Django-CFG Frontend

Modern Next.js admin panel with automatic Django integration.

## Quick Start

### 1. Generate API Clients

```bash
make generate-api
```

This generates TypeScript clients from Django OpenAPI schema.

### 2. Build Static Export

```bash
make build-admin
```

This builds Next.js and copies static files to `django_cfg/frontend/admin/`.

### 3. Use in Django Project

**Automatic setup (2 lines):**

```python
# settings.py
from django_cfg.apps.frontend import setup_frontend_serving

frontend_config = setup_frontend_serving()
INSTALLED_APPS += frontend_config['INSTALLED_APPS']
```

```python
# urls.py
from django_cfg.apps.frontend import get_frontend_urls

urlpatterns += get_frontend_urls()
```

**Run:**

```bash
python manage.py runserver
# Admin: http://localhost:8000/admin/
```

## Project Structure

```
@frontend/
├── apps/
│   └── admin/              # Next.js Admin App
│       ├── src/
│       ├── package.json
│       └── next.config.ts
│
├── packages/
│   ├── api/                # Generated API clients
│   ├── ui/                 # UI components
│   └── layouts/            # Layout components
│
├── Makefile                # Build commands
└── README.md               # This file
```

## Available Commands

### Development

```bash
cd apps/admin
pnpm dev                    # Start Next.js dev server (port 3000)
```

### API Generation

```bash
make generate-api           # Generate TypeScript API clients
```

This:
1. Runs `python manage.py generate_clients --typescript`
2. Copies generated clients to `packages/api/src/cfg/generated/`
3. Builds `@djangocfg/api` package

### Static Build

```bash
make build-admin            # Build Next.js static export
```

This:
1. Runs `next build` in `apps/admin`
2. Creates static build in `apps/admin/out/`
3. **Copies to `../django_cfg/frontend/admin/`**
4. Builds `packages/api`

Output locations:
- `apps/admin/out/` - Next.js build
- `../django_cfg/frontend/admin/` - Django package

## Workflow

### Frontend Development

```bash
# Start dev server
cd apps/admin
pnpm dev

# Open http://localhost:3000
# Backend API: http://localhost:8000/api/
```

### API Changes

When Django models change:

```bash
make generate-api
```

### Production Build

```bash
# Build static files
make build-admin

# Check build
python manage.py check_frontend

# Test in Django
python manage.py runserver
# Open http://localhost:8000/admin/
```

## Next.js Configuration

Static export is configured in `apps/admin/next.config.ts`:

```typescript
const nextConfig = {
  output: "export",           // Static export
  distDir: "out",            // Output directory
  images: {
    unoptimized: true        // Required for static export
  },
}
```

## API Client Usage

Generated clients are available in `@djangocfg/api`:

```typescript
import { api } from '@djangocfg/api';

// Type-safe API calls
const tasks = await api.cfg_tasks.list();
const user = await api.cfg_accounts_user_profile.retrieve(1);
```

SWR hooks for React:

```typescript
import { useTasksApiTasksStatsRetrieve } from '@djangocfg/api';

function TasksStats() {
  const { data, error, isLoading } = useTasksApiTasksStatsRetrieve(api);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return <div>Running tasks: {data?.running_count}</div>;
}
```

## Package Scripts

```json
{
  "dev": "next dev",
  "build": "pnpm check && next build",
  "build:static": "next build",
  "check": "tsc --noEmit"
}
```

## Django Integration

The built static files are automatically served by Django when you install `django-cfg`:

```python
# Minimal setup
from django_cfg.apps.frontend import setup_frontend_serving, get_frontend_urls

# Settings
INSTALLED_APPS += setup_frontend_serving()['INSTALLED_APPS']

# URLs
urlpatterns += get_frontend_urls()
```

Features:
- ✅ Automatic URL routing
- ✅ Static file serving
- ✅ Next.js client-side routing support
- ✅ Security (directory traversal protection)
- ✅ Caching (1 hour)
- ✅ Content-type detection

## Publishing

```bash
# 1. Build frontend
make build-admin

# 2. Build Python package
poetry build

# 3. Publish
poetry publish
```

## Management Commands

```bash
# Check frontend build status
python manage.py check_frontend

# Output:
# 🔍 Checking frontend builds...
# ✅ Admin: Built
#    Path: /path/to/django_cfg/frontend/admin
#    Size: 234.5 KB
```

## Troubleshooting

### Build not found

```bash
# Make sure you built the frontend
cd @frontend
make build-admin

# Check if files exist
ls -la ../django_cfg/frontend/admin/
```

### API types outdated

```bash
# Regenerate API clients
make generate-api
```

### Dev server issues

```bash
# Kill existing dev server
pnpm kill-port

# Restart
pnpm dev
```

## Environment Variables

Create `.env.local` in `apps/admin/`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Documentation

- **`BUILD.md`** - Build process details
- **`../django_cfg/apps/frontend/README.md`** - Django app documentation
- **`../django_cfg/apps/frontend/EXAMPLE.md`** - Usage examples
- **`../django_cfg/frontend/INTEGRATION.md`** - Integration guide

## Tech Stack

- **Next.js** 15.5.4 - React framework
- **React** 19.2.0 - UI library
- **TypeScript** 5.9 - Type safety
- **Tailwind CSS** 4.1 - Styling
- **SWR** 2.3 - Data fetching
- **Zod** 4.1 - Schema validation

## Architecture

```
Development                Production
┌──────────────┐          ┌──────────────┐
│ Next.js      │          │ Static Files │
│ Dev Server   │   →      │ (HTML/JS)    │
│ :3000        │  build   │              │
└──────────────┘          └──────────────┘
       ↓                         ↓
┌──────────────┐          ┌──────────────┐
│ Django API   │          │ Django       │
│ :8000/api/   │          │ Serves Both  │
└──────────────┘          └──────────────┘
```

## Examples

### Minimal Django Project

```python
# settings.py
from django_cfg.apps.frontend import setup_frontend_serving

INSTALLED_APPS = [
    'django.contrib.staticfiles',
]

INSTALLED_APPS += setup_frontend_serving()['INSTALLED_APPS']
```

```python
# urls.py
from django_cfg.apps.frontend import get_frontend_urls

urlpatterns = get_frontend_urls()
```

### With Django REST Framework

```python
# urls.py
from django.urls import path, include
from django_cfg.apps.frontend import get_frontend_urls

urlpatterns = [
    path('api/', include('myapp.urls')),
]

urlpatterns += get_frontend_urls()
```

### Custom Admin Path

```python
# urls.py
from django.urls import re_path
from django_cfg.apps.frontend.views import AdminView

urlpatterns = [
    re_path(r'^dashboard/(?P<path>.*)$', AdminView.as_view()),
]

# Admin now at: http://localhost:8000/dashboard/
```

## Contributing

1. Make changes in `apps/admin/`
2. Test with `pnpm dev`
3. Build with `make build-admin`
4. Test in Django with `python manage.py runserver`
5. Commit changes

## License

Part of django-cfg package.
