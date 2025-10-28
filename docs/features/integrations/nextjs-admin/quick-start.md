---
id: nextjs-admin-quick-start
title: Quick Start
description: Get started with Next.js admin integration in 5 minutes
sidebar_label: Quick Start
tags:
  - nextjs
  - admin
  - quickstart
---

# Quick Start

Get your Next.js admin dashboard running in just 5 minutes.

## Prerequisites

Before you begin, ensure you have:

- Django-CFG installed and configured
- Node.js 18+ and pnpm/npm/yarn installed
- A Next.js project (or use our starter template)

:::tip Need a Next.js Project?
If you don't have a Next.js project yet, you can clone our starter template:
```bash
git clone https://github.com/django-cfg/nextjs-admin-template
```
:::

## Step 1: Configure Django

Add Next.js admin configuration to your Django config:

```python title="api/config.py"
from django_cfg import DjangoConfig, NextJsAdminConfig

config = DjangoConfig(
    project_name="My Project",
    secret_key="your-secret-key",

    # Add Next.js admin integration
    nextjs_admin=NextJsAdminConfig(
        project_path="../django_admin",  # Path to your Next.js project
    ),

    # ... rest of your configuration
)
```

:::info Smart Defaults
With just `project_path`, django-cfg automatically configures:
- API output path: `apps/admin/src/api/generated`
- Static output: `out/`
- Dev server: `http://localhost:3001`
- Production URL: `/cfg/admin/`
:::

## Step 2: Generate API Clients

Generate TypeScript clients from your Django APIs:

```bash
python manage.py generate_clients --typescript
```

This command will:

1. ✅ Generate TypeScript client code from your Django APIs
2. ✅ Copy generated clients to your Next.js project
3. ✅ Build Next.js static export (if `auto_build=True`)
4. ✅ Create ZIP archive for production deployment

<details>
  <summary>Output Example</summary>

```bash
$ python manage.py generate_clients --typescript

Generating API clients...
✅ Generated TypeScript clients
   → openapi/clients/typescript/

Copying to Next.js project...
✅ Copied to ../django_admin/apps/admin/src/api/generated/

Building Next.js...
✅ Next.js build complete
   → out/ (5.2MB)

Creating ZIP archive...
✅ Created static/nextjs_admin.zip (7.2MB)

Done! Your Next.js admin is ready.
```

</details>

## Step 3: Run Development Servers

### Option A: Development Mode (Recommended for Development)

Run both Django and Next.js dev servers:

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs groupId="terminal-setup">
  <TabItem value="split" label="Split Terminal" default>

```bash
# Terminal 1: Django
python manage.py runserver

# Terminal 2: Next.js (with hot reload)
cd ../django_admin/apps/admin && pnpm dev
```

  </TabItem>
  <TabItem value="tmux" label="Using tmux">

```bash
# Create tmux session
tmux new -s django-admin

# Split window
Ctrl+B %

# Terminal 1: Django
python manage.py runserver

# Switch pane
Ctrl+B →

# Terminal 2: Next.js
cd ../django_admin/apps/admin && pnpm dev
```

  </TabItem>
  <TabItem value="makefile" label="Using Makefile">

```makefile title="Makefile"
.PHONY: dev

dev:
	@echo "Starting Django and Next.js..."
	python manage.py runserver & \
	cd ../django_admin/apps/admin && pnpm dev
```

```bash
make dev
```

  </TabItem>
</Tabs>

### Option B: Production Mode (Test Production Build Locally)

Build and serve the static Next.js build:

```bash
# 1. Build Next.js
cd ../django_admin/apps/admin
pnpm build

# 2. Run Django (serves static build)
cd ../../..
python manage.py runserver
```

## Step 4: Access Your Admin

Open your browser and navigate to:

```
http://localhost:8000/admin/
```

You should see:

1. **Tab 1: Built-in Dashboard** - Django-CFG's default admin
2. **Tab 2: Next.js Admin** - Your custom Next.js dashboard

:::tip First Load
On the first request in production mode, django-cfg automatically extracts the ZIP archive. This may take ~100ms. Subsequent requests are instant.
:::

## Verify Everything Works

### Check Authentication

The Next.js admin should automatically receive JWT tokens:

```javascript title="In Next.js app - src/utils/auth.ts"
// Tokens are automatically injected by Django
const token = localStorage.getItem('auth_token');
const refreshToken = localStorage.getItem('refresh_token');

console.log('Token available:', !!token); // Should be true
```

### Check API Connectivity

Test that your Next.js app can call Django APIs:

```typescript title="src/components/Dashboard.tsx"
import { ProfilesClient } from '@/api/generated/profiles/client';

export default function Dashboard() {
  const client = new ProfilesClient();

  // This should work out of the box
  const data = await client.getProfile();

  return <div>{data.name}</div>;
}
```

## Next Steps

<div className="row margin-top--lg">
  <div className="col col--6">

### 🎨 Customize Configuration

Learn about all configuration options:

```python
nextjs_admin=NextJsAdminConfig(
    project_path="../django_admin",
    dev_url="http://localhost:3002",  # Custom port
    iframe_route="/dashboard",         # Custom route
    tab_title="My Admin",              # Custom title
)
```

[Configuration Reference →](./configuration)

  </div>
  <div className="col col--6">

### 🚀 Deploy to Production

Deploy your admin with Docker:

```dockerfile
# Copy ZIP archive
COPY static/nextjs_admin.zip /app/static/

# Auto-extracts on first request
```

[Deployment Guide →](./deployment)

  </div>
</div>

## Troubleshooting

### Next.js Admin Tab Not Showing

**Problem**: Only the built-in dashboard tab appears.

**Solution**: Ensure `NextJsAdminConfig` is configured:

```python
# Make sure this is set
nextjs_admin=NextJsAdminConfig(
    project_path="../django_admin",
)
```

### iframe Not Loading

**Problem**: iframe shows blank page or errors.

<Tabs>
  <TabItem value="dev" label="Development Mode">

**Check**: Is Next.js dev server running?

```bash
cd ../django_admin/apps/admin && pnpm dev
```

**Check**: Is dev server on correct port?

```bash
# Should show: Local: http://localhost:3001
```

  </TabItem>
  <TabItem value="prod" label="Production Mode">

**Check**: Does ZIP archive exist?

```bash
ls -lh static/nextjs_admin.zip
# Should show file ~5-10MB
```

**Check**: Logs for extraction errors:

```bash
# Should show: "Successfully extracted nextjs_admin.zip"
python manage.py runserver
```

  </TabItem>
</Tabs>

### API Calls Failing

**Problem**: Next.js app can't call Django APIs.

**Solution**: Check CORS settings:

```python title="api/config.py"
config = DjangoConfig(
    # ... other settings

    # Allow localhost for development
    cors_allowed_origins=[
        "http://localhost:3001",  # Next.js dev server
        "http://127.0.0.1:3001",
    ],
)
```

## Common Commands Reference

```bash
# Generate TypeScript clients
python manage.py generate_clients --typescript

# Run Django server
python manage.py runserver

# Run Next.js dev server
cd ../django_admin/apps/admin && pnpm dev

# Build Next.js for production
cd ../django_admin/apps/admin && pnpm build

# Check ZIP archive was created
ls -lh static/nextjs_admin.zip
```

## Need Help?

- [Configuration Guide](./configuration)
- [How It Works](./how-it-works)
- [Troubleshooting Guide](./troubleshooting)
- [Examples](./examples)

:::tip Join the Community
Have questions? Join our Discord or open an issue on GitHub.
:::
