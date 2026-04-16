/**
 * OG Image Route Handler Example
 *
 * This is an example of a custom OG image route. The current implementation
 * uses Django's built-in og-image renderer via @djangocfg/nextjs/og-image.
 *
 * For dynamic OG images, configure the Django backend og-image endpoint
 * and use buildOgUrl / withOgImage from @djangocfg/nextjs/og-image in metadata.
 *
 * See app/_core/metadata.ts for usage.
 *
 * Note: This route is automatically excluded from static export by Next.js
 * when using output: 'export' mode — route handlers are not statically exported.
 */

import { buildOgUrl, createOgMetadata } from '@djangocfg/nextjs/og-image';

// Example: building an OG image URL for a specific page
export const exampleOgUrl = buildOgUrl({
  title: 'Django CFG Admin',
  description: 'Modern Django framework with type-safe Pydantic v2 configuration',
  preset: 'DARK_BLUE',
});

// Example: generating metadata with OG image for a page
export const exampleMetadata = createOgMetadata({
  title: 'Django CFG Admin',
  description: 'Modern Django framework with type-safe Pydantic v2 configuration',
  preset: 'DARK_BLUE',
});
