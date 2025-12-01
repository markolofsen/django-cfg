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
  
  // Example: Add custom transpile packages if needed
  // transpilePackages: ['my-custom-package'],

  // Example: Add custom webpack rules (will be called AFTER base webpack logic)
  // webpack: (config, options) => {
  //   // Your custom webpack configuration
  //   return config;
  // },
});

export default withBundleAnalyzer(config);
