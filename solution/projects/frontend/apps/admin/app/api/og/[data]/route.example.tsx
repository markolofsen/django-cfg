/**
 * OG Image Route Handler with dynamic data parameter
 * 
 * See README.md in this directory for setup instructions.
 * 
 * Uses /api/og/[data] instead of /api/og?data=... to avoid Next.js
 * stripping query parameters in internal requests
 * 
 * Note: This route is automatically excluded from static export by createOgImageDynamicRoute
 */

import { createOgImageDynamicRoute } from '@djangocfg/nextjs/og-image';
import { DefaultTemplate } from '@djangocfg/nextjs/og-image/components';
import { settings } from '@core/settings';
import type { NextRequest } from 'next/server';

/**
 * OG Image Route Handler with dynamic data parameter
 * 
 * Uses /api/og/[data] instead of /api/og?data=... to avoid Next.js
 * stripping query parameters in internal requests
 * 
 * Note: This route is automatically excluded from static export by createOgImageDynamicRoute
 */

export const runtime = 'nodejs';
export const revalidate = false;

const { GET: handlerGET } = createOgImageDynamicRoute({
  template: DefaultTemplate,
  defaultProps: {
    siteName: settings.app.name,
    logo: settings.app.icons.logoVector,
    // Customize to match previous OgImageTemplate style
    backgroundType: 'gradient',
    gradientStart: '#0f172a',
    gradientEnd: '#334155',
    titleSize: 80, // Larger title like custom template
    titleWeight: 800,
    titleColor: 'white',
    descriptionSize: 36, // Larger description
    descriptionColor: 'rgba(226, 232, 240, 0.9)',
    siteNameSize: 32, // Larger site name
    siteNameColor: 'rgba(255, 255, 255, 0.95)',
    padding: 80,
    logoSize: 56, // Larger logo
  },
  fonts: [
    { family: 'Manrope', weight: 700 },
    { family: 'Manrope', weight: 500 },
  ],
  size: { width: 1200, height: 630 },
});

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ data: string }> }
) {
  return handlerGET(request, context);
}
