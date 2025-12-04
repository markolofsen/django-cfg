/**
 * Next.js Configuration
 *
 * Uses base configuration from @djangocfg/nextjs/config
 * with project-specific customizations
 */

import { createBaseNextConfig } from '@djangocfg/nextjs/config';
import bundleAnalyzer from '@next/bundle-analyzer';

const withBundleAnalyzer = bundleAnalyzer({
  enabled: process.env.ANALYZE === 'true',
});

// Create config with base settings
// Add project-specific overrides here if needed
const config = createBaseNextConfig({
  // Automatically open browser in development mode
  openBrowser: true,

  // Check for @djangocfg/* package updates on startup
  checkUpdates: true,

  // Check for missing optional packages
  checkPackages: true,
});

export default withBundleAnalyzer(config);
