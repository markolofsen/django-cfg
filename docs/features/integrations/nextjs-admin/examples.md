---
id: examples
title: Real-World Examples
description: Real-world examples and patterns for Next.js admin integration
sidebar_label: Examples
tags:
  - nextjs
  - admin
  - examples
---

# Real-World Examples

Practical examples and patterns for common use cases.

## Basic Examples

### Minimal Setup

The simplest possible configuration:

```python title="api/config.py"
from django_cfg import DjangoConfig, NextJsAdminConfig

config = DjangoConfig(
    project_name="Simple Blog",
    secret_key="your-secret-key",

    nextjs_admin=NextJsAdminConfig(
        project_path="../admin-frontend",
    ),
)
```

That's it! Everything else uses smart defaults.

### Custom Port for Development

If port 3001 is already in use:

```python title="api/config.py"
config = DjangoConfig(
    project_name="My App",

    nextjs_admin=NextJsAdminConfig(
        project_path="../admin-frontend",
        dev_url="http://localhost:3002",  # Custom dev port
    ),
)
```

Update Next.js dev command:

```json title="package.json"
{
  "scripts": {
    "dev": "next dev -p 3002"
  }
}
```

### Custom Production URL

For a branded admin URL:

```python title="api/config.py"
config = DjangoConfig(
    project_name="Analytics Platform",

    nextjs_admin=NextJsAdminConfig(
        project_path="../analytics-ui",
        static_url="/analytics/",
        tab_title="Analytics Dashboard",
    ),
)
```

Access at: `https://yourdomain.com/analytics/`

## Advanced Examples

### Multi-Environment Configuration

Different settings for dev, staging, and production:

```python title="api/config.py"
import os

ENV = os.getenv("ENV_MODE", "development")

# Base configuration
config = DjangoConfig(
    project_name="Multi-Env App",
    env_mode=ENV,
)

# Environment-specific Next.js config
if ENV == "development":
    config.nextjs_admin = NextJsAdminConfig(
        project_path="../admin-frontend",
        dev_url="http://localhost:3001",
    )
elif ENV == "staging":
    config.nextjs_admin = NextJsAdminConfig(
        project_path="/app/admin-frontend",
        static_url="/staging-admin/",
    )
else:  # production
    config.nextjs_admin = NextJsAdminConfig(
        project_path="/app/admin-frontend",
        static_url="/admin/",
    )
```

### Custom Next.js Structure

If your Next.js project doesn't follow the default structure:

```python title="api/config.py"
config = DjangoConfig(
    project_name="Custom Structure",

    nextjs_admin=NextJsAdminConfig(
        project_path="../my-admin-app",
        api_output_path="src/lib/api/generated",  # Custom API path
        static_output_path="dist",                # Custom build output
    ),
)
```

This assumes your Next.js project looks like:

```
my-admin-app/
├── src/
│   └── lib/
│       └── api/
│           └── generated/    # API clients here
├── dist/                     # Build output here
└── package.json
```

### API Authentication in Next.js

Using generated API clients with authentication:

```typescript title="src/lib/api-client.ts"
import { ProfilesClient } from '@/api/generated/profiles/client';
import { TradingClient } from '@/api/generated/trading/client';

// Get JWT token from localStorage (injected by Django)
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('auth_token');
}

// Create authenticated API client
export function createProfilesClient() {
  const token = getAuthToken();

  return new ProfilesClient({
    baseURL: '/api',
    headers: {
      'Authorization': token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json',
    },
  });
}

export function createTradingClient() {
  const token = getAuthToken();

  return new TradingClient({
    baseURL: '/api',
    headers: {
      'Authorization': token ? `Bearer ${token}` : '',
    },
  });
}
```

Usage in components:

```typescript title="src/components/Dashboard.tsx"
import { useEffect, useState } from 'react';
import { createProfilesClient } from '@/lib/api-client';
import { Profile } from '@/api/generated/profiles/types';

export default function Dashboard() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadProfile() {
      try {
        const client = createProfilesClient();
        const data = await client.getProfile();
        setProfile(data);
      } catch (error) {
        console.error('Failed to load profile:', error);
      } finally {
        setLoading(false);
      }
    }

    loadProfile();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (!profile) return <div>Failed to load profile</div>;

  return (
    <div>
      <h1>Welcome, {profile.name}</h1>
      <p>Email: {profile.email}</p>
    </div>
  );
}
```

### Token Refresh Hook

Automatically refresh expired JWT tokens:

```typescript title="src/hooks/useAuth.ts"
import { useEffect, useState } from 'react';

interface AuthTokens {
  access: string | null;
  refresh: string | null;
}

export function useAuth() {
  const [tokens, setTokens] = useState<AuthTokens>({
    access: null,
    refresh: null,
  });

  useEffect(() => {
    // Read tokens from localStorage
    const access = localStorage.getItem('auth_token');
    const refresh = localStorage.getItem('refresh_token');
    setTokens({ access, refresh });
  }, []);

  const refreshToken = async () => {
    if (!tokens.refresh) return false;

    try {
      const response = await fetch('/api/token/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: tokens.refresh }),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('auth_token', data.access);
        setTokens({ ...tokens, access: data.access });
        return true;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
    }

    return false;
  };

  return { tokens, refreshToken };
}
```

Usage:

```typescript title="src/lib/api-client.ts"
import { useAuth } from '@/hooks/useAuth';

export function useApiClient() {
  const { tokens, refreshToken } = useAuth();

  const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
    const headers = {
      ...options.headers,
      'Authorization': `Bearer ${tokens.access}`,
    };

    let response = await fetch(url, { ...options, headers });

    // If 401, try to refresh token
    if (response.status === 401) {
      const refreshed = await refreshToken();
      if (refreshed) {
        // Retry with new token
        headers.Authorization = `Bearer ${localStorage.getItem('auth_token')}`;
        response = await fetch(url, { ...options, headers });
      }
    }

    return response;
  };

  return { fetchWithAuth };
}
```

## Real-World Use Cases

### E-Commerce Analytics Dashboard

```python title="api/config.py"
config = DjangoConfig(
    project_name="E-Commerce Platform",

    nextjs_admin=NextJsAdminConfig(
        project_path="../analytics-dashboard",
        static_url="/analytics/",
        tab_title="Analytics",
        iframe_route="/dashboard",
    ),

    project_apps=[
        "apps.products",
        "apps.orders",
        "apps.analytics",
    ],
)
```

Next.js dashboard with real-time charts:

```typescript title="apps/analytics-dashboard/src/pages/dashboard/index.tsx"
import { useEffect, useState } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import { createAnalyticsClient } from '@/lib/api-client';

export default function AnalyticsDashboard() {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    const client = createAnalyticsClient();

    // Fetch initial data
    client.getDashboardMetrics().then(setMetrics);

    // Poll for updates every 30 seconds
    const interval = setInterval(() => {
      client.getDashboardMetrics().then(setMetrics);
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="grid grid-cols-2 gap-4">
      <div className="card">
        <h2>Sales Over Time</h2>
        <Line data={metrics?.salesData} />
      </div>
      <div className="card">
        <h2>Top Products</h2>
        <Bar data={metrics?.productsData} />
      </div>
    </div>
  );
}
```

### Multi-Tenant SaaS Admin

Different admin interfaces per tenant:

```python title="api/config.py"
config = DjangoConfig(
    project_name="Multi-Tenant SaaS",

    nextjs_admin=NextJsAdminConfig(
        project_path="../tenant-admin",
        static_url="/tenant-admin/",
        tab_title="Tenant Dashboard",
    ),
)
```

Next.js with tenant context:

```typescript title="src/contexts/TenantContext.tsx"
import { createContext, useContext, useEffect, useState } from 'react';

interface Tenant {
  id: string;
  name: string;
  subdomain: string;
}

const TenantContext = createContext<Tenant | null>(null);

export function TenantProvider({ children }) {
  const [tenant, setTenant] = useState<Tenant | null>(null);

  useEffect(() => {
    // Extract tenant from subdomain or API
    const subdomain = window.location.hostname.split('.')[0];

    fetch(`/api/tenants/?subdomain=${subdomain}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
      },
    })
      .then(res => res.json())
      .then(setTenant);
  }, []);

  return (
    <TenantContext.Provider value={tenant}>
      {children}
    </TenantContext.Provider>
  );
}

export const useTenant = () => useContext(TenantContext);
```

### IoT Device Management

Real-time device monitoring dashboard:

```python title="api/config.py"
config = DjangoConfig(
    project_name="IoT Platform",

    nextjs_admin=NextJsAdminConfig(
        project_path="../device-dashboard",
        static_url="/devices/",
        tab_title="Device Monitor",
    ),

    # Enable Centrifugo for WebSocket
    centrifugo=DjangoCfgCentrifugoConfig(
        enabled=True,
        api_url="http://centrifugo:8000",
    ),
)
```

Next.js with real-time updates via Centrifugo:

```typescript title="src/hooks/useDeviceStatus.ts"
import { useEffect, useState } from 'react';
import Centrifuge from 'centrifuge';

interface Device {
  id: string;
  name: string;
  status: 'online' | 'offline';
  lastSeen: string;
}

export function useDeviceStatus(deviceId: string) {
  const [device, setDevice] = useState<Device | null>(null);
  const [centrifuge, setCentrifuge] = useState<Centrifuge | null>(null);

  useEffect(() => {
    // Connect to Centrifugo
    const token = localStorage.getItem('auth_token');
    const client = new Centrifuge('ws://localhost:8000/connection/websocket', {
      token,
    });

    // Subscribe to device channel
    const sub = client.subscribe(`device:${deviceId}`, (ctx) => {
      setDevice(ctx.data);
    });

    client.connect();
    setCentrifuge(client);

    return () => {
      sub.unsubscribe();
      client.disconnect();
    };
  }, [deviceId]);

  return { device, centrifuge };
}
```

### Financial Trading Dashboard

Complex data visualization with real-time updates:

```python title="api/config.py"
config = DjangoConfig(
    project_name="Trading Platform",

    nextjs_admin=NextJsAdminConfig(
        project_path="../trading-dashboard",
        static_url="/trading/",
        tab_title="Trading Desk",
        iframe_route="/desk",
    ),
)
```

Next.js with TradingView charts:

```typescript title="src/components/TradingChart.tsx"
import { useEffect, useRef } from 'react';
import { createTradingClient } from '@/lib/api-client';

export default function TradingChart({ symbol }: { symbol: string }) {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const client = createTradingClient();

    // Fetch historical data
    client.getHistoricalData(symbol).then((data) => {
      // Initialize TradingView chart
      const chart = new TradingView.widget({
        container: chartRef.current!,
        symbol,
        interval: '1',
        datafeed: {
          // Custom datafeed using Django API
          getBars: async (symbolInfo, resolution, from, to) => {
            const bars = await client.getBars(symbol, from, to);
            return bars;
          },
        },
      });
    });
  }, [symbol]);

  return <div ref={chartRef} className="h-full w-full" />;
}
```

## Integration Patterns

### API Response Caching

Cache API responses for better performance:

```typescript title="src/lib/cache.ts"
const cache = new Map<string, { data: any; timestamp: number }>();

export async function cachedFetch<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttl: number = 60000  // 1 minute default
): Promise<T> {
  const now = Date.now();
  const cached = cache.get(key);

  if (cached && (now - cached.timestamp) < ttl) {
    return cached.data;
  }

  const data = await fetcher();
  cache.set(key, { data, timestamp: now });
  return data;
}
```

Usage:

```typescript
import { cachedFetch } from '@/lib/cache';
import { createProfilesClient } from '@/lib/api-client';

const profile = await cachedFetch(
  'profile',
  () => createProfilesClient().getProfile(),
  300000  // Cache for 5 minutes
);
```

### Optimistic Updates

Update UI immediately, sync with server later:

```typescript title="src/hooks/useOptimisticUpdate.ts"
import { useState } from 'react';

export function useOptimisticUpdate<T>(
  initialData: T,
  updateFn: (data: T) => Promise<T>
) {
  const [data, setData] = useState<T>(initialData);
  const [isUpdating, setIsUpdating] = useState(false);

  const update = async (newData: Partial<T>) => {
    // Optimistic update
    setData((prev) => ({ ...prev, ...newData }));
    setIsUpdating(true);

    try {
      // Sync with server
      const updated = await updateFn({ ...data, ...newData });
      setData(updated);
    } catch (error) {
      // Rollback on error
      setData(initialData);
      throw error;
    } finally {
      setIsUpdating(false);
    }
  };

  return { data, update, isUpdating };
}
```

## Next Steps

- [Configuration Reference](./configuration) - All config options
- [API Generation](./api-generation) - Generate TypeScript clients
- [Troubleshooting](./troubleshooting) - Common issues
- [Deployment](./deployment) - Deploy to production

:::tip Need More Examples?
Check out our [example repository](https://github.com/django-cfg/nextjs-admin-examples) for complete working examples.
:::
