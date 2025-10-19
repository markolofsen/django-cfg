# @djangocfg/og-image Changelog

## [1.0.0] - 2025-10-11

### Added

- ✨ **Universal OG Image Generation Package**
  - Edge Runtime compatible handler factory
  - Dynamic Google Fonts loading (no public/ directory needed)
  - Customizable templates (DefaultTemplate, LightTemplate)
  - Type-safe configuration with TypeScript
  - URL generation helpers

- 📦 **Package Structure**
  ```
  @djangocfg/og-image/
  ├── handler         - createOgImageHandler(), edgeRuntimeConfig
  ├── components      - DefaultTemplate, LightTemplate
  └── utils           - loadGoogleFonts(), generateOgImageUrl()
  ```

- 🎨 **Default Templates**
  - `DefaultTemplate` - Modern gradient-based design
  - `LightTemplate` - Clean light-themed design
  - Both support: title, description, siteName, logo

- 🔧 **Font Utilities**
  - `loadGoogleFont()` - Load single font from Google Fonts API
  - `loadGoogleFonts()` - Load multiple fonts
  - `createFontLoader()` - Font loader with caching

- 🔗 **URL Helpers**
  - `generateOgImageUrl()` - Generate OG image URLs with params
  - `getAbsoluteOgImageUrl()` - Convert to absolute URLs
  - `createOgImageUrlBuilder()` - URL builder with presets
  - `parseOgImageUrl()` - Parse URL parameters

### Changed

- 🔄 **Updated cloud app API route** (`apps/cloud/src/api/og/route.tsx`)
  - Now uses `@djangocfg/og-image` package
  - Loads Manrope font from Google Fonts (not from public/)
  - Supports legacy base64 data parameter for backward compatibility
  - Uses custom `OgImageTemplate` with Unrealon branding

- 🔄 **Updated Seo.tsx component** (`packages/layouts/.../Seo.tsx`)
  - Uses `generateOgImageUrl()` instead of manual base64 encoding
  - Added proper OG meta tags (width, height, type)
  - Supports absolute URL generation via `siteUrl` prop
  - Cleaner and more maintainable code

### Environment Configuration

- 📝 **Updated `.env.example`** - Added comprehensive documentation
- 📝 **Updated `docker/.env`** - Added NEXT_PUBLIC_SITE_URL
- 📝 **Updated `docker/.env.dev`** - Added frontend configuration
- 📝 **Updated `docker/.env.production.example`** - Added production URLs
- 🐳 **Updated docker-compose files** - Pass NEXT_PUBLIC_SITE_URL to containers

### Documentation

- 📚 **Package README** - Comprehensive usage guide with examples
- 📚 **ENV_CONFIGURATION.md** - Environment variables setup guide
- 📚 **CHANGELOG.md** - This file

## Migration Guide

### From old implementation to @djangocfg/og-image

#### Before (old implementation):

```typescript
// route.tsx
import { ImageResponse } from '@vercel/og';

export default async function handler(req: Request) {
  const fontData = await fetch(`${settings.url}/static/fonts/Manrope/Manrope-Bold.ttf`)
    .then((res) => res.arrayBuffer());

  return new ImageResponse(<OgImage />, {
    fonts: [{ name: 'Manrope', data: fontData }]
  });
}
```

#### After (new implementation):

```typescript
// route.tsx
import { createOgImageHandler, edgeRuntimeConfig } from '@djangocfg/og-image';
import { loadGoogleFonts } from '@djangocfg/og-image/utils';

export const runtime = edgeRuntimeConfig.runtime;

export const GET = createOgImageHandler({
  template: OgImageTemplate,
  fonts: async () => loadGoogleFonts([
    { family: 'Manrope', weight: 700 }
  ])
});
```

### Benefits

- ✅ No fonts in public/ directory
- ✅ Reusable across projects
- ✅ Type-safe configuration
- ✅ Built-in URL helpers
- ✅ Edge Runtime optimized
- ✅ Easier to test and maintain

## Breaking Changes

None - First release

## Dependencies

- `@vercel/og` ^0.8.5
- `next` >=13.0.0 (peer)
- `react` >=18.0.0 (peer)

## Browser Support

Works in all modern browsers. OG images are generated server-side on Edge Runtime.

## License

MIT

## Contributors

- Claude Code (Reforms AI) - Initial implementation
- Mark (Инопланетянин) - Project architect

## Links

- [Package README](./README.md)
- [Environment Configuration Guide](../../../docker/ENV_CONFIGURATION.md)
- [Next.js App Router Documentation](https://nextjs.org/docs/app)
- [@vercel/og Documentation](https://vercel.com/docs/functions/edge-functions/og-image-generation)
