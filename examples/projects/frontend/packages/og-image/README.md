# @djangocfg/og-image

OG (Open Graph) image generation utilities for social media sharing.

## What's Inside

- Edge Runtime compatible image handler
- Google Fonts loader (no fonts in public/ needed)
- URL generation with base64 encoding
- Default and custom templates
- Type-safe configuration

## Usage

### In Pages Router API Route

```tsx
// pages/api/og.tsx
import { ImageResponse } from 'next/og';
import { loadGoogleFonts } from '@djangocfg/og-image/utils';

export const config = { runtime: 'edge' };

export default async function handler(req) {
  const fonts = await loadGoogleFonts([
    { family: 'Manrope', weight: 700 }
  ]);

  return new ImageResponse(
    <YourTemplate />,
    { width: 1200, height: 630, fonts }
  );
}
```

### Generate OG Image URLs

```tsx
import { generateOgImageUrl } from '@djangocfg/og-image/utils';

// Base64 encoding (safe, default)
const url = generateOgImageUrl('/api/og', {
  title: 'Page Title',
  subtitle: 'Description'
});
// Result: /api/og?data=eyJ0aXRsZSI6IlBhZ2UgVGl0bGUiLCJzdWJ0aXRsZSI6IkRlc2NyaXB0aW9uIn0=

// Or query params (legacy)
const url = generateOgImageUrl('/api/og', {
  title: 'Page Title'
}, false);
// Result: /api/og?title=Page+Title
```

### Use in SEO Meta Tags

```tsx
<meta property="og:image" content={ogImageUrl} />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
```

## Features

- **Edge Runtime** - Fast, global deployment
- **Dynamic Fonts** - Load from Google Fonts API
- **Base64 Safe URLs** - Avoid encoding issues
- **Type Safe** - Full TypeScript support
- **Template System** - Create custom templates

## API

### `loadGoogleFonts(fonts)`

Load fonts from Google Fonts API.

```tsx
const fonts = await loadGoogleFonts([
  { family: 'Manrope', weight: 700 },
  { family: 'Inter', weight: 400 }
]);
```

### `generateOgImageUrl(baseUrl, params, useBase64?)`

Generate OG image URL with params.

```tsx
const url = generateOgImageUrl('/api/og', {
  title: 'Hello',
  description: 'World'
}, true); // base64 encoding (default)
```

### `getAbsoluteOgImageUrl(relativePath, siteUrl)`

Convert relative to absolute URL.

```tsx
const absolute = getAbsoluteOgImageUrl(
  '/api/og?data=...',
  'https://example.com'
);
```

## Environment Variables

```bash
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

Used for generating absolute URLs for social media meta tags.
