/**
 * Universal Nextra-4 docs SEO toolkit — programmatic API.
 *
 * Brand-agnostic: all project specifics (base URL, name) come from a project
 * `seo.config.ts` resolved by `loadConfig` (see core/config.ts). Safe to copy
 * `scripts/seo/` verbatim into any Nextra app.
 */
export { loadConfig, DEFAULTS } from './core/config.js';
export { discoverRoutes, buildRouteIndex, fileToRoute } from './core/routes.js';
export { extractLinks, extractHeadings, extractExternalRefs, splitHref, isExternal, isHttp } from './core/extract.js';
export { checkLinks } from './commands/check.js';
export { checkExternal } from './commands/external.js';
export { fixLinks, printFixResult } from './commands/fix.js';
export { generateSitemap, generateSitemapXml, generateRobotsTxt } from './commands/sitemap.js';
export { printCheckReport, printExternalReport } from './reporters/report.js';
export type { RouteIndex } from './core/routes.js';
export type {
  NextraSeoConfig,
  RouteInfo,
  LinkRef,
  LinkKind,
  BrokenLink,
  BrokenReason,
  CheckResult,
  ExternalRef,
  ExternalCheck,
  ExternalResult,
} from './core/types.js';
export type { ExternalOptions } from './commands/external.js';
export type { FixChange, FixResult } from './commands/fix.js';
