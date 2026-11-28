/**
 * Next.js Configuration Utilities
 *
 * @example
 * ```typescript
 * import { createBaseNextConfig } from '@djangocfg/nextjs/config';
 *
 * export default createBaseNextConfig({
 *   checkPackages: true,
 *   checkUpdates: true,
 * });
 * ```
 */

// Main config factory
export { createBaseNextConfig, type BaseNextConfigOptions } from './createNextConfig';

// IndexNow key file → Django
export { indexNowKeyRewrite } from './indexnow';

// Constants
export {
  PACKAGE_NAME,
  DJANGOCFG_PACKAGES,
  DEFAULT_TRANSPILE_PACKAGES,
  DEFAULT_OPTIMIZE_PACKAGES,
  DJANGO_CFG_BANNER,
} from './constants';

// CSP vendor presets — declare third parties by name instead of by origin
export {
  CSP_VENDOR_PRESETS,
  CSP_BASELINE_VENDORS,
  resolveCspVendors,
  type CspVendor,
  type CspOrigins,
} from './csp';

// Re-export AI constants from ai module
export {
  MCP_BASE_URL,
  MCP_SERVER_URL,
  MCP_API_URL,
  AI_DOCS_HINT,
} from '../ai/constants';

// Utils
export { deepMerge } from './utils/deepMerge';
export {
  isStaticBuild,
  isDev,
  isProduction,
  isCI,
  getBasePath,
  getApiUrl,
  getSiteUrl,
} from './utils/env';
export {
  getCurrentVersion,
  fetchLatestVersion,
  checkForUpdate,
  getUpdateCommand,
  printVersionInfo,
} from './utils/version';

// Package management
export {
  OPTIONAL_PACKAGES,
  PEER_DEPENDENCIES,
  getPackagesForContext,
  type PackageDefinition,
} from './packages/definitions';
export {
  isPackageInstalled,
  getMissingPackages,
  checkPackages,
  type MissingPackage,
} from './packages/checker';
export {
  detectPackageManager,
  buildSingleInstallCommand,
  buildInstallCommand,
  installPackages,
  installPackagesWithProgress,
  checkAndInstallPackages,
  resetInstallerPreferences,
  type InstallOptions,
  type InstallProgress,
} from './packages/installer';
export {
  getInstalledVersion,
  checkForUpdates,
  getOutdatedPackages,
  updatePackagesWithProgress,
  checkAndUpdatePackages,
  resetUpdaterPreferences,
  type PackageVersion,
  type UpdateOptions,
} from './packages/updater';

// Plugins
export {
  DevStartupPlugin,
  resetDevStartupState,
  type DevStartupPluginOptions,
} from './plugins/devStartup';
export {
  addCompressionPlugins,
  isCompressionAvailable,
  type CompressionPluginOptions,
} from './plugins/compression';

