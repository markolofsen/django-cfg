/**
 * OG Image Generation API Route (Pages Router)
 *
 * Generates dynamic Open Graph images for social media sharing
 * Uses @djangocfg/og-image package with Google Fonts
 */

import { ImageResponse } from 'next/og';
import type { NextRequest } from 'next/server';
import { loadGoogleFonts } from '@djangocfg/og-image/utils';
import { OgImageTemplate } from '@/components/app/OgImageTemplate';
import { settings } from '@/core/settings';

// Enable Edge Runtime
export const config = {
  runtime: 'edge',
};

/**
 * OG Image Handler with base64 support
 */
export default async function handler(req: NextRequest): Promise<Response> {
  const { searchParams } = new URL(req.url);

  let title = searchParams.get('title') || settings.app.name;
  let subtitle = searchParams.get('subtitle') || settings.app.description || '';
  let description = searchParams.get('description') || subtitle;

  // Check for legacy base64 data parameter (safe encoding)
  const dataParam = searchParams.get('data');
  if (dataParam) {
    try {
      // Decode base64 and parse JSON
      const decodedData = JSON.parse(
        Buffer.from(dataParam, 'base64').toString('utf-8')
      );

      if (decodedData.title) title = decodedData.title;
      if (decodedData.subtitle) subtitle = decodedData.subtitle;
      if (decodedData.description) description = decodedData.description;
    } catch (error) {
      console.error('[OG Image] Error decoding base64 data:', error);
      // Continue with query params
    }
  }

  // Load Manrope fonts from Google Fonts
  const fonts = await loadGoogleFonts([
    { family: 'Manrope', weight: 700 },
    { family: 'Manrope', weight: 500 },
  ]);

  // Prepare template props
  const templateProps = {
    title,
    subtitle,
    description,
    siteName: settings.app.name,
    logo: `${process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'}${settings.app.icons.logoVector}`,
  };

  return new ImageResponse(
    <OgImageTemplate {...templateProps} />,
    {
      width: 1200,
      height: 630,
      fonts,
      debug: process.env.NODE_ENV === 'development',
    }
  );
}
