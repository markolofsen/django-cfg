---
id: nextjs-admin-api-generation
title: API Client Generation
description: Generate and use TypeScript API clients for your Next.js admin
sidebar_label: API Generation
tags:
  - nextjs
  - admin
  - api
  - typescript
---

# API Client Generation

Automatically generate type-safe TypeScript clients from your Django APIs.

## Overview

Django-CFG can automatically generate TypeScript API clients from your Django REST Framework APIs, copy them to your Next.js project, and build your admin in one command:

```bash
python manage.py generate_clients --typescript
```

This generates:
- ✅ Type-safe TypeScript clients
- ✅ Request/response type definitions
- ✅ Authentication handling
- ✅ Error handling
- ✅ Auto-copied to Next.js project
- ✅ Next.js build triggered (if `auto_build=True`)

## Quick Start

### 1. Configure Next.js Admin

```python title="api/config.py"
from django_cfg import DjangoConfig, NextJsAdminConfig

config = DjangoConfig(
    project_name="My Project",

    nextjs_admin=NextJsAdminConfig(
        project_path="../django_admin",
        auto_copy_api=True,  # Auto-copy clients (default)
    ),
)
```

### 2. Generate Clients

```bash
python manage.py generate_clients --typescript
```

### 3. Use in Next.js

```typescript title="src/pages/dashboard.tsx"
import { ProfilesClient } from '@/api/generated/profiles/client';

export default function Dashboard() {
  const client = new ProfilesClient();
  const profile = await client.getProfile();

  return <div>Welcome, {profile.name}!</div>;
}
```

## Command Options

### Basic Usage

```bash
# Generate TypeScript clients
python manage.py generate_clients --typescript

# Generate Python clients
python manage.py generate_clients --python

# Generate both
python manage.py generate_clients --typescript --python

# Generate all supported languages
python manage.py generate_clients --all
```

### Advanced Options

```bash
# Skip building Next.js
python manage.py generate_clients --typescript --no-build

# Skip copying to Next.js project
python manage.py generate_clients --typescript --no-copy

# Verbose output
python manage.py generate_clients --typescript --verbose

# Dry run (show what would be generated)
python manage.py generate_clients --typescript --dry-run
```

## Generated Structure

### Output Directory

```
django_project/
├── openapi/
│   ├── schema.json              # OpenAPI 3.0 schema
│   └── clients/
│       ├── typescript/          # TypeScript clients
│       │   ├── profiles/
│       │   │   ├── client.ts    # API client
│       │   │   ├── types.ts     # Type definitions
│       │   │   └── http.ts      # HTTP utilities
│       │   └── trading/
│       │       └── ...
│       │
│       ├── python/              # Python clients
│       │   └── ...
│       │
│       └── go/                  # Go clients
│           └── ...
```

### Next.js Integration

If `NextJsAdminConfig` is configured:

```
django_admin/
└── apps/
    └── admin/
        └── src/
            └── api/
                └── generated/       # Auto-copied here
                    ├── profiles/
                    ├── trading/
                    └── ...
```

## TypeScript Client Usage

### Basic API Calls

```typescript title="src/lib/api.ts"
import { ProfilesClient } from '@/api/generated/profiles/client';
import { Profile } from '@/api/generated/profiles/types';

// Create client
const client = new ProfilesClient({
  baseURL: '/api',  // Django API base URL
});

// GET request
const profile: Profile = await client.getProfile();

// POST request
const newProfile = await client.createProfile({
  name: 'John Doe',
  email: 'john@example.com',
});

// PUT request
const updated = await client.updateProfile(profile.id, {
  name: 'Jane Doe',
});

// DELETE request
await client.deleteProfile(profile.id);
```

### With Authentication

```typescript title="src/lib/authenticated-client.ts"
import { ProfilesClient } from '@/api/generated/profiles/client';

function createAuthenticatedClient() {
  // Get token from localStorage (injected by Django)
  const token = localStorage.getItem('auth_token');

  return new ProfilesClient({
    baseURL: '/api',
    headers: {
      'Authorization': token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json',
    },
  });
}

// Usage
const client = createAuthenticatedClient();
const profile = await client.getProfile();
```

### Error Handling

```typescript title="src/lib/api-with-error-handling.ts"
import { ProfilesClient } from '@/api/generated/profiles/client';

async function safeApiCall<T>(
  apiCall: () => Promise<T>
): Promise<{ data: T | null; error: Error | null }> {
  try {
    const data = await apiCall();
    return { data, error: null };
  } catch (error) {
    console.error('API call failed:', error);
    return { data: null, error: error as Error };
  }
}

// Usage
const client = createAuthenticatedClient();
const { data, error } = await safeApiCall(() => client.getProfile());

if (error) {
  console.error('Failed to load profile:', error);
} else {
  console.log('Profile:', data);
}
```

### React Hook Pattern

```typescript title="src/hooks/useProfile.ts"
import { useEffect, useState } from 'react';
import { createAuthenticatedClient } from '@/lib/api';
import { Profile } from '@/api/generated/profiles/types';

export function useProfile() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const client = createAuthenticatedClient();

    client.getProfile()
      .then(setProfile)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  return { profile, loading, error };
}

// Usage in component
function Dashboard() {
  const { profile, loading, error } = useProfile();

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return <div>Welcome, {profile?.name}!</div>;
}
```

## Type Definitions

### Generated Types

```typescript title="Generated: profiles/types.ts"
// Automatically generated from Django models

export interface Profile {
  id: number;
  name: string;
  email: string;
  bio: string | null;
  avatar: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProfileCreate {
  name: string;
  email: string;
  bio?: string;
  avatar?: string;
}

export interface ProfileUpdate {
  name?: string;
  email?: string;
  bio?: string;
  avatar?: string;
}

export interface ProfileList {
  count: number;
  next: string | null;
  previous: string | null;
  results: Profile[];
}
```

### Using Types

```typescript title="src/components/ProfileCard.tsx"
import { Profile } from '@/api/generated/profiles/types';

interface ProfileCardProps {
  profile: Profile;  // Type-safe!
}

export function ProfileCard({ profile }: ProfileCardProps) {
  return (
    <div>
      <h2>{profile.name}</h2>
      <p>{profile.email}</p>
      {profile.bio && <p>{profile.bio}</p>}
    </div>
  );
}
```

## Advanced Patterns

### Request Interceptors

```typescript title="src/lib/api-client.ts"
import { ProfilesClient } from '@/api/generated/profiles/client';

class AuthenticatedProfilesClient extends ProfilesClient {
  constructor() {
    super({
      baseURL: '/api',
    });
  }

  // Override request method to add auth
  async request<T>(config: RequestConfig): Promise<T> {
    const token = localStorage.getItem('auth_token');

    return super.request({
      ...config,
      headers: {
        ...config.headers,
        'Authorization': token ? `Bearer ${token}` : '',
      },
    });
  }
}

const client = new AuthenticatedProfilesClient();
```

### Response Interceptors

```typescript title="src/lib/api-with-interceptors.ts"
import { ProfilesClient } from '@/api/generated/profiles/client';

class InterceptedClient extends ProfilesClient {
  async request<T>(config: RequestConfig): Promise<T> {
    try {
      const response = await super.request<T>(config);

      // Log successful requests
      console.log(`✅ ${config.method} ${config.url}`, response);

      return response;
    } catch (error) {
      // Handle errors globally
      console.error(`❌ ${config.method} ${config.url}`, error);

      // Refresh token if expired
      if (error.status === 401) {
        await this.refreshToken();
        // Retry request
        return super.request<T>(config);
      }

      throw error;
    }
  }

  private async refreshToken() {
    const refresh = localStorage.getItem('refresh_token');
    // ... refresh logic
  }
}
```

### Caching Layer

```typescript title="src/lib/cached-client.ts"
import { ProfilesClient } from '@/api/generated/profiles/client';

const cache = new Map<string, { data: any; timestamp: number }>();

class CachedProfilesClient extends ProfilesClient {
  async getProfile(ttl: number = 60000): Promise<Profile> {
    const cacheKey = 'profile';
    const cached = cache.get(cacheKey);

    if (cached && Date.now() - cached.timestamp < ttl) {
      return cached.data;
    }

    const data = await super.getProfile();
    cache.set(cacheKey, { data, timestamp: Date.now() });

    return data;
  }
}
```

### Query Parameters

```typescript title="Usage with filters"
import { ProfilesClient } from '@/api/generated/profiles/client';

const client = new ProfilesClient();

// List with filters
const profiles = await client.listProfiles({
  page: 1,
  page_size: 10,
  search: 'john',
  ordering: '-created_at',
});

// Custom query params
const filtered = await client.listProfiles({
  status: 'active',
  created_after: '2024-01-01',
});
```

## Build Integration

### Automatic Build

When `auto_build=True` (default):

```bash
python manage.py generate_clients --typescript

# Automatically:
# 1. Generates TypeScript clients
# 2. Copies to Next.js project
# 3. Builds Next.js: cd ../django_admin && pnpm build
# 4. Creates ZIP: static/nextjs_admin.zip
```

### Manual Build

```bash
# Generate without building
python manage.py generate_clients --typescript --no-build

# Build manually later
cd ../django_admin/apps/admin
pnpm build
```

### Custom Build Command

```python title="api/config.py"
config = DjangoConfig(
    nextjs_admin=NextJsAdminConfig(
        project_path="../django_admin",
        build_command="pnpm build:prod",  # Custom command
    ),
)
```

## Customization

### Custom Output Path

```python title="api/config.py"
config = DjangoConfig(
    nextjs_admin=NextJsAdminConfig(
        project_path="../django_admin",
        api_output_path="src/lib/api",  # Custom path
    ),
)
```

### Skip Auto-Copy

```python title="api/config.py"
config = DjangoConfig(
    nextjs_admin=NextJsAdminConfig(
        project_path="../django_admin",
        auto_copy_api=False,  # Don't auto-copy
    ),
)
```

Then manually copy when needed:

```bash
cp -r openapi/clients/typescript/* ../django_admin/apps/admin/src/api/generated/
```

## Regeneration

### When to Regenerate

Regenerate clients when:
- Django models change
- API endpoints added/removed
- Request/response schemas change
- API permissions change

```bash
# After model changes
python manage.py makemigrations
python manage.py migrate

# Regenerate clients
python manage.py generate_clients --typescript
```

### CI/CD Integration

```yaml title=".github/workflows/generate-api.yml"
name: Generate API Clients

on:
  push:
    paths:
      - 'api/**'
      - 'apps/*/models.py'

jobs:
  generate:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Generate API clients
        run: python manage.py generate_clients --typescript

      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add openapi/ django_admin/
          git commit -m "chore: regenerate API clients" || exit 0
          git push
```

## Troubleshooting

### Clients Not Generated

**Check**: OpenAPI schema generation

```bash
# Generate schema only
python manage.py spectacular --file openapi/schema.json

# Check schema
cat openapi/schema.json | jq '.paths'
```

### Type Errors

**Solution**: Regenerate clients

```bash
rm -rf openapi/clients/typescript/
python manage.py generate_clients --typescript
```

### Import Errors

**Check**: Path alias in `tsconfig.json`

```json title="tsconfig.json"
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

## Next Steps

- [Configuration Reference](./configuration) - All config options
- [Examples](./examples) - Real-world usage examples
- [How It Works](./how-it-works) - Architecture deep dive
- [Troubleshooting](./troubleshooting) - Common issues

:::tip Best Practice
Regenerate clients after every API change to ensure type safety across your stack.
:::
