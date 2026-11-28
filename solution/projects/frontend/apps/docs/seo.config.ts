/**
 * Project SEO config for the shared `@nextra/seo-engine` toolkit.
 *
 * The engine (packages/seo-engine) is brand-agnostic and shared across all the
 * Nextra apps. This file is the ONLY per-project piece — keep all project
 * specifics (base URL, name) here, not inside the engine.
 */
import type { NextraSeoConfig } from '@nextra/seo-engine';

const config: Partial<NextraSeoConfig> = {
  name: 'djangocfg-docs-seo',
  baseUrl: 'https://djangocfg.com',
  // contentDir / publicDir / outputDir default to content/ + public/ — fine here.
};

export default config;
