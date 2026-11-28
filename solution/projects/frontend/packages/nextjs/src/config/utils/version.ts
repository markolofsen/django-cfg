/**
 * Version Checking Utilities
 */

import chalk from 'chalk';
import Conf from 'conf';
import consola from 'consola';
import { readFileSync } from 'fs';
import { createRequire } from 'module';
import semver from 'semver';

import { DJANGOCFG_PACKAGES, PACKAGE_NAME, VERSION_CACHE_TTL_MS } from '../constants';

type VersionCacheShape = {
  latestVersion?: string;
  lastCheck?: number;
};

interface CacheLike<T extends Record<string, unknown>> {
  get<K extends keyof T>(key: K): T[K] | undefined;
  set<K extends keyof T>(key: K, value: T[K]): void;
  clear(): void;
}

function createMemoryCache<T extends Record<string, unknown>>(): CacheLike<T> {
  const store = new Map<string, unknown>();
  return {
    get<K extends keyof T>(key: K): T[K] | undefined {
      return store.get(String(key)) as T[K] | undefined;
    },
    set<K extends keyof T>(key: K, value: T[K]): void {
      store.set(String(key), value);
    },
    clear(): void {
      store.clear();
    },
  };
}

function createVersionCache(): CacheLike<VersionCacheShape> {
  try {
    return new Conf<VersionCacheShape>({
      projectName: 'djangocfg-nextjs',
      projectVersion: '1.0.0',
    });
  } catch {
    // Fallback for corrupted conf file or invalid JSON in cache storage.
    return createMemoryCache<VersionCacheShape>();
  }
}

// Version cache using conf (stores in ~/.config/djangocfg-nextjs/)
const versionCache = createVersionCache();

/**
 * Get current package version from package.json
 */
export function getCurrentVersion(): string | null {
  try {
    // `createRequire(import.meta.url).resolve` rather than a bare `require`: the
    // published bundle is ESM, where `require` does not exist. Resolving is only
    // used to locate the file — the read itself goes through `fs`, so this does
    // not depend on JSON-module import support.
    const localRequire = createRequire(import.meta.url);
    const pkgPath = localRequire.resolve('../../../package.json');
    return JSON.parse(readFileSync(pkgPath, 'utf-8')).version || null;
  } catch {
    return null;
  }
}

/**
 * Fetch latest version from npm registry (with 1 hour caching via conf)
 */
export async function fetchLatestVersion(): Promise<string | null> {
  // Check cache first
  const lastCheck = versionCache.get('lastCheck') || 0;
  const cachedVersion = versionCache.get('latestVersion');

  if (cachedVersion && (Date.now() - lastCheck) < VERSION_CACHE_TTL_MS) {
    return cachedVersion;
  }

  // Fetch from npm registry
  try {
    const https = await import('https');
    return new Promise((resolve) => {
      const req = https.get(
        `https://registry.npmjs.org/${PACKAGE_NAME}/latest`,
        { timeout: 5000 },
        (res) => {
          let data = '';
          res.on('data', (chunk: string) => { data += chunk; });
          res.on('end', () => {
            try {
              const json = JSON.parse(data);
              const version = json.version || null;
              if (version) {
                versionCache.set('latestVersion', version);
                versionCache.set('lastCheck', Date.now());
              }
              resolve(version);
            } catch {
              resolve(cachedVersion || null);
            }
          });
        }
      );
      req.on('error', () => resolve(cachedVersion || null));
      req.on('timeout', () => { req.destroy(); resolve(cachedVersion || null); });
    });
  } catch {
    return cachedVersion || null;
  }
}

/**
 * Check if update is available
 */
export async function checkForUpdate(): Promise<{
  hasUpdate: boolean;
  currentVersion: string | null;
  latestVersion: string | null;
}> {
  const currentVersion = getCurrentVersion();
  if (!currentVersion) {
    return { hasUpdate: false, currentVersion: null, latestVersion: null };
  }

  const latestVersion = await fetchLatestVersion();
  const hasUpdate = !!(latestVersion && semver.gt(latestVersion, currentVersion));

  return { hasUpdate, currentVersion, latestVersion };
}

/**
 * Get update command for all djangocfg packages
 */
export function getUpdateCommand(): string {
  return `pnpm add ${DJANGOCFG_PACKAGES.map(p => `${p}@latest`).join(' ')}`;
}

/**
 * Print version info and update notification
 */
export async function printVersionInfo(): Promise<void> {
  const { hasUpdate, currentVersion, latestVersion } = await checkForUpdate();

  if (!currentVersion) return;

  // Print current version
  consola.box(`📦 @djangocfg/nextjs v${currentVersion}`);

  // Show update notification if available
  if (hasUpdate && latestVersion) {
    consola.warn(`Update Available! ${chalk.red(currentVersion)} → ${chalk.green(latestVersion)}`);
    consola.info(`Run: ${chalk.cyan(getUpdateCommand())}`);
    console.log('');
  }
}
