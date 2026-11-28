/**
 * Next.js Configuration for @djangocfg/demo
 *
 * Uses base configuration from @djangocfg/nextjs/config
 * with project-specific customizations.
 */

import createNextIntlPlugin from 'next-intl/plugin';

import { createBaseNextConfig, indexNowKeyRewrite } from '@djangocfg/nextjs/config';
import bundleAnalyzer from '@next/bundle-analyzer';

const withBundleAnalyzer = bundleAnalyzer({
  enabled: process.env.ANALYZE === 'true',
});

const withNextIntl = createNextIntlPlugin('./i18n/request.ts');

const API_URL = process.env.NEXT_PUBLIC_API_URL as string;

const config = createBaseNextConfig({
  checkUpdates: false,
  checkPackages: false,

  async rewrites() {
    if (!API_URL) return [];
    return {
      beforeFiles: [],
      afterFiles: [{ source: '/media/:path*', destination: `${API_URL}/media/:path*` }],
      // `/<key>.txt` → Django's IndexNow key (IndexNowConfig). Fallback, so
      // real files like robots.txt always win.
      fallback: [indexNowKeyRewrite(API_URL)],
    };
  },
});

export default withBundleAnalyzer(withNextIntl(config));
