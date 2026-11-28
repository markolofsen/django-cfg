/**
 * Config loading — brand-agnostic.
 *
 * The engine ships with NO project specifics. Each project supplies a
 * `seo.config.{ts,mjs,js,json}` in its app root (cwd), e.g.:
 *
 *   // apps/docs/seo.config.ts
 *   import type { NextraSeoConfig } from './scripts/seo';
 *   const config: Partial<NextraSeoConfig> = {
 *     baseUrl: 'https://docs.example.com',
 *     name: 'example-docs-seo',
 *   };
 *   export default config;
 *
 * Resolution order (first match wins): an explicit --config path, then
 * `seo.config.{ts,mjs,js,json}` in cwd. Anything the project omits falls back
 * to DEFAULTS. `--base-url` etc. on the CLI still override the loaded config.
 */
import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import type { NextraSeoConfig } from './types.js';

export const DEFAULTS: NextraSeoConfig = {
  /** Display name for the CLI + outbound user-agent. Override per project. */
  name: 'nextra-docs-seo',
  /** Generate public/llms.txt during `sitemap` (default on; off = hand-curated). */
  llms: true,
  contentDir: 'content',
  /** No sensible default — set per project in seo.config; required for sitemap. */
  baseUrl: 'http://localhost:3000',
  outputDir: 'public',
  publicDir: 'public',
  ignore: [],
  /** No basePath by default (root-served app). Set per project (e.g. '/docs'). */
  basePath: '',
  /** Component/app sources scanned for raw `<a href>` when basePath is set. */
  appGlobs: ['app/**/*.{tsx,jsx}'],
};

const CONFIG_CANDIDATES = [
  'seo.config.ts',
  'seo.config.mjs',
  'seo.config.js',
  'seo.config.json',
];

export async function loadConfig(configPath?: string): Promise<NextraSeoConfig> {
  let user: Partial<NextraSeoConfig> = {};

  const candidates = configPath ? [configPath] : CONFIG_CANDIDATES;

  for (const c of candidates) {
    const full = resolve(process.cwd(), c);
    if (!existsSync(full)) continue;
    if (full.endsWith('.json')) {
      user = JSON.parse(readFileSync(full, 'utf8')) as Partial<NextraSeoConfig>;
    } else {
      // .ts is resolved by the tsx runtime the CLI is launched with.
      const mod = await import(pathToFileURL(full).href);
      user = (mod.default ?? mod) as Partial<NextraSeoConfig>;
    }
    break;
  }

  return { ...DEFAULTS, ...user };
}
