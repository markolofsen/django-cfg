/**
 * OG Image Handler Factory
 *
 * Creates a Next.js Edge API handler for dynamic OG image generation
 */

import { ImageResponse } from '@vercel/og';
import type { NextRequest } from 'next/server';
import type {
  OgImageHandlerConfig,
  OgImageFont,
  OgImageTemplateProps,
} from './types';

/**
 * Edge runtime configuration for Next.js
 * Export this from your API route alongside the handler
 */
export const edgeRuntimeConfig = {
  runtime: 'edge' as const,
};

/**
 * Creates an OG image handler for Next.js API routes
 *
 * @param config - Handler configuration
 * @returns Handler function and runtime config
 *
 * @example
 * ```typescript
 * // app/api/og/route.tsx
 * import { createOgImageHandler, edgeRuntimeConfig } from '@djangocfg/og-image';
 * import { loadGoogleFonts } from '@djangocfg/og-image/fonts';
 *
 * export const runtime = edgeRuntimeConfig.runtime;
 *
 * export const GET = createOgImageHandler({
 *   template: ({ title, description }) => (
 *     <div style={{ fontSize: 60 }}>{title}</div>
 *   ),
 *   fonts: async () => loadGoogleFonts([
 *     { family: 'Manrope', weight: 700 }
 *   ]),
 *   size: { width: 1200, height: 630 },
 * });
 * ```
 */
export function createOgImageHandler(config: OgImageHandlerConfig) {
  const {
    template,
    fonts,
    size = { width: 1200, height: 630 },
    debug = false,
    defaults = {},
  } = config;

  // Pre-load fonts if provided as array
  let fontsPromise: Promise<OgImageFont[]> | undefined;
  if (fonts) {
    if (typeof fonts === 'function') {
      fontsPromise = fonts();
    } else {
      fontsPromise = Promise.resolve(fonts);
    }
  }

  return async function handler(req: NextRequest) {
    try {
      // Parse URL query parameters
      const { searchParams } = new URL(req.url);

      // Extract common parameters
      const title = searchParams.get('title') || defaults.title || 'Untitled';
      const description = searchParams.get('description') || defaults.description;
      const siteName = searchParams.get('siteName') || defaults.siteName;
      const logo = searchParams.get('logo') || defaults.logo;

      // Collect all query params for custom templates
      const customParams: Record<string, string> = {};
      searchParams.forEach((value, key) => {
        if (!['title', 'description', 'siteName', 'logo'].includes(key)) {
          customParams[key] = value;
        }
      });

      // Build template props
      const templateProps: OgImageTemplateProps = {
        title,
        description,
        siteName,
        logo,
        ...customParams,
      };

      if (debug) {
        console.log('[OG Image] Template props:', templateProps);
      }

      // Load fonts if configured
      const loadedFonts = fontsPromise ? await fontsPromise : undefined;

      if (debug && loadedFonts) {
        console.log('[OG Image] Loaded fonts:', loadedFonts.map(f => f.name));
      }

      // Render template
      const element = template(templateProps);

      // Generate image
      return new ImageResponse(element, {
        width: size.width,
        height: size.height,
        fonts: loadedFonts,
      });
    } catch (error) {
      console.error('[OG Image] Error generating image:', error);

      return new Response(
        `Failed to generate OG image: ${error instanceof Error ? error.message : 'Unknown error'}`,
        {
          status: 500,
        }
      );
    }
  };
}

/**
 * Export types for convenience
 */
export type {
  OgImageHandlerConfig,
  OgImageFont,
  OgImageSize,
  OgImageTemplateProps,
  OgImageTemplate,
  OgImageRequest,
} from './types';
