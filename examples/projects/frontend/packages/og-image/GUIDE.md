# @djangocfg/og-image

Universal OG (Open Graph) Image generation for Next.js applications with Edge Runtime support.

## Features

- 🚀 **Edge Runtime Compatible** - Fast, globally distributed image generation
- 🎨 **Customizable Templates** - Use default templates or create your own
- 🔤 **Dynamic Font Loading** - Load Google Fonts without storing in `public/` directory
- 📦 **Type-Safe** - Full TypeScript support with comprehensive types
- 🔗 **URL Helpers** - Utilities for generating OG image URLs
- ⚡ **Zero Config** - Works out of the box with sensible defaults

## Installation

```bash
pnpm add @djangocfg/og-image
```

## Quick Start

### 1. Create an API Route

Create a new file at `app/api/og/route.tsx`:

```typescript
import { createOgImageHandler, edgeRuntimeConfig } from '@djangocfg/og-image';
import { DefaultTemplate } from '@djangocfg/og-image/components';
import { loadGoogleFonts } from '@djangocfg/og-image/utils';

// Enable Edge Runtime
export const runtime = edgeRuntimeConfig.runtime;

// Create handler with default template and Google Fonts
export const GET = createOgImageHandler({
  template: DefaultTemplate,
  fonts: async () => loadGoogleFonts([
    { family: 'Manrope', weight: 700 },
    { family: 'Inter', weight: 400 }
  ]),
  size: { width: 1200, height: 630 },
  defaults: {
    siteName: 'My Site',
  }
});
```

### 2. Generate OG Image URLs

```typescript
import { generateOgImageUrl } from '@djangocfg/og-image/utils';

const ogImageUrl = generateOgImageUrl('/api/og', {
  title: 'My Page Title',
  description: 'Page description here',
});

// Use in meta tags
<meta property="og:image" content={ogImageUrl} />
```

### 3. Use in SEO Component

```typescript
import { generateOgImageUrl, getAbsoluteOgImageUrl } from '@djangocfg/og-image/utils';

export function Seo({ title, description }: SeoProps) {
  const relativeUrl = generateOgImageUrl('/api/og', { title, description });
  const absoluteUrl = getAbsoluteOgImageUrl(relativeUrl, 'https://example.com');

  return (
    <Head>
      <meta property="og:image" content={absoluteUrl} />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />
    </Head>
  );
}
```

## Custom Templates

Create your own template component:

```typescript
import type { OgImageTemplateProps } from '@djangocfg/og-image';

export function CustomTemplate({ title, description }: OgImageTemplateProps) {
  return (
    <div
      style={{
        height: '100%',
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(to bottom, #000, #111)',
        fontSize: 60,
        fontWeight: 700,
        color: 'white',
      }}
    >
      <div>{title}</div>
      {description && <div style={{ fontSize: 30 }}>{description}</div>}
    </div>
  );
}

// Use in handler
export const GET = createOgImageHandler({
  template: CustomTemplate,
});
```

## Font Loading

### Google Fonts (Recommended)

Load fonts dynamically from Google Fonts API:

```typescript
import { loadGoogleFonts } from '@djangocfg/og-image/utils';

const fonts = await loadGoogleFonts([
  { family: 'Manrope', weight: 700 },
  { family: 'Inter', weight: 400, style: 'normal' }
]);
```

### With Caching

Use font loader with caching for better performance:

```typescript
import { createFontLoader } from '@djangocfg/og-image/utils';

const fontLoader = createFontLoader();

export const GET = createOgImageHandler({
  fonts: async () => [
    {
      name: 'Manrope',
      data: await fontLoader.load('Manrope', 700),
      weight: 700,
      style: 'normal',
    }
  ]
});
```

## API Reference

### `createOgImageHandler(config)`

Creates a Next.js Edge API handler for OG image generation.

**Parameters:**

- `config.template` - Template component or render function
- `config.fonts` - Array of fonts or async function that returns fonts
- `config.size` - Image dimensions (default: 1200x630)
- `config.debug` - Enable debug logging
- `config.defaults` - Default values for template props

**Returns:** Handler function for Next.js API routes

### `generateOgImageUrl(baseUrl, params)`

Generate OG image URL with query parameters.

**Parameters:**

- `baseUrl` - Base URL of the OG image API route
- `params` - URL parameters (title, description, etc.)

**Returns:** Complete URL with encoded query parameters

### `loadGoogleFonts(fonts)`

Load multiple Google Fonts dynamically.

**Parameters:**

- `fonts` - Array of font configurations

**Returns:** Promise of font data ready for ImageResponse

## Templates

### Default Templates

- `DefaultTemplate` - Modern gradient-based template
- `LightTemplate` - Clean light-themed template

Both support:
- `title` - Page title (required)
- `description` - Page description (optional)
- `siteName` - Site name for header (optional)
- `logo` - Logo URL or data URI (optional)

## Examples

### With URL Builder

```typescript
import { createOgImageUrlBuilder } from '@djangocfg/og-image/utils';

const buildOgUrl = createOgImageUrlBuilder('/api/og', {
  siteName: 'My Site',
  logo: '/logo.png'
});

const url1 = buildOgUrl({ title: 'Page 1' });
const url2 = buildOgUrl({ title: 'Page 2', description: 'Custom desc' });
```

### Custom Query Parameters

```typescript
// In your template
export function CustomTemplate({ title, theme, category }: OgImageTemplateProps) {
  return <div>Title: {title}, Theme: {theme}, Category: {category}</div>;
}

// Generate URL with custom params
const url = generateOgImageUrl('/api/og', {
  title: 'My Post',
  theme: 'dark',
  category: 'tech'
});
```

## Edge Runtime Compatibility

This package is designed for Next.js Edge Runtime. Make sure to export the runtime configuration:

```typescript
export const runtime = 'edge';
```

Or use the provided config:

```typescript
import { edgeRuntimeConfig } from '@djangocfg/og-image';

export const runtime = edgeRuntimeConfig.runtime;
```

## Troubleshooting

### Fonts not loading

Make sure you're using the Edge Runtime and fonts are loaded asynchronously:

```typescript
fonts: async () => loadGoogleFonts([...])
```

### Image size too large

Edge functions have a 1-2MB limit. Reduce the number of fonts or use font subsetting:

```typescript
await loadGoogleFont('Manrope', 'Text to optimize for', 700);
```

## License

MIT
