# @djangocfg/layouts

Internal package with layout system and components.

## What's Inside

- **AppLayout** - Universal layout system that auto-detects routes
- **Layout Components** - Public, Private, Auth layouts
- **Shared Components** - SEO, Navigation, Footer, Sidebar
- **Auth Hooks** - Authentication utilities

## Usage

### Basic Setup

```tsx
// _app.tsx
import { AppLayout } from '@djangocfg/layouts';
import { appLayoutConfig } from '@/core';

export default function App({ Component, pageProps }) {
  return (
    <AppLayout config={appLayoutConfig}>
      <Component {...pageProps} />
    </AppLayout>
  );
}
```

### Configuration

```tsx
// core/appLayoutConfig.ts
import type { AppLayoutConfig } from '@djangocfg/layouts';

export const appLayoutConfig: AppLayoutConfig = {
  app: {
    name: 'Your App',
    description: 'App description',
    logoPath: '/logo.svg',
    siteUrl: process.env.NEXT_PUBLIC_SITE_URL,
  },
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL,
  },
  routes: {
    // Route detection functions
  },
  publicLayout: {
    // Public layout config
  },
  privateLayout: {
    // Private layout config
  },
};
```

## Features

- **Auto Route Detection** - Automatically applies correct layout
- **SEO Component** - OG image generation, meta tags
- **Zero Prop Drilling** - All config via context
- **Type Safe** - Full TypeScript support

## Layouts

- **PublicLayout** - For public pages (landing, docs)
- **PrivateLayout** - For authenticated pages (dashboard)
- **AuthLayout** - For auth pages (login, signup)

## Components

- `Seo` - SEO meta tags with OG image
- `PageProgress` - Loading progress bar
- `Footer` - Configurable footer
- `Sidebar` - Dashboard sidebar
- `Navigation` - Header navigation
