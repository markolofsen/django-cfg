/**
 * @djangocfg/og-image
 *
 * Universal OG Image generation for Next.js applications
 *
 * Features:
 * - Edge runtime compatible
 * - Dynamic Google Fonts loading (no public/ directory needed)
 * - Customizable templates
 * - Type-safe configuration
 * - URL generation helpers
 *
 * @example
 * ```typescript
 * // app/api/og/route.tsx
 * import { createOgImageHandler, edgeRuntimeConfig } from '@djangocfg/og-image';
 * import { loadGoogleFonts } from '@djangocfg/og-image/utils';
 * import { DefaultTemplate } from '@djangocfg/og-image/components';
 *
 * export const runtime = edgeRuntimeConfig.runtime;
 *
 * export const GET = createOgImageHandler({
 *   template: DefaultTemplate,
 *   fonts: async () => loadGoogleFonts([
 *     { family: 'Manrope', weight: 700 }
 *   ]),
 * });
 * ```
 */

// Handler
export {
  createOgImageHandler,
  edgeRuntimeConfig,
  type OgImageHandlerConfig,
  type OgImageFont,
  type OgImageSize,
  type OgImageTemplateProps,
  type OgImageTemplate,
  type OgImageRequest,
} from './handler';

// Components
export { DefaultTemplate, LightTemplate } from './components';

// Utils
export {
  loadGoogleFont,
  loadGoogleFonts,
  createFontLoader,
  generateOgImageUrl,
  getAbsoluteOgImageUrl,
  createOgImageUrlBuilder,
  parseOgImageUrl,
  type FontConfig,
  type OgImageUrlParams,
} from './utils';
