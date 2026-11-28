/**
 * Package Updater
 *
 * Checks for outdated @djangocfg/* packages and offers to update them.
 */

import chalk from 'chalk';
import { spawn } from 'child_process';
import Conf from 'conf';
import consola from 'consola';
import { existsSync, readFileSync } from 'fs';
import { createRequire } from 'module';
import { join } from 'path';
import { createInterface } from 'readline';
import semver from 'semver';

import { DJANGOCFG_PACKAGES, PACKAGE_NAME } from '../constants';
import { isCI } from '../utils/env';
import { detectPackageManager } from './installer';

type UpdaterCacheShape = {
  autoUpdate?: boolean;
  lastCheck?: number;
  skippedVersions?: Record<string, string>;
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

function createUpdaterCache(): CacheLike<UpdaterCacheShape> {
  try {
    return new Conf<UpdaterCacheShape>({
      projectName: 'djangocfg-nextjs-updater',
      projectVersion: '1.0.0',
    });
  } catch {
    // Fallback for corrupted conf file or invalid JSON in cache storage.
    return createMemoryCache<UpdaterCacheShape>();
  }
}

// Updater preferences cache
const updaterCache = createUpdaterCache();

// Check for updates once per hour
const UPDATE_CHECK_COOLDOWN_MS = 60 * 60 * 1000;

// Spinner frames
const SPINNER_FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];

export interface PackageVersion {
  name: string;
  current: string | null;
  latest: string | null;
  hasUpdate: boolean;
}

export interface UpdateOptions {
  /** Auto-update without prompting */
  autoUpdate?: boolean;
  /** Force check even if recently checked (ignores cooldown) */
  force?: boolean;
  /** Force check even for workspace:* packages (for testing) */
  forceCheckWorkspace?: boolean;
}

/**
 * Check if package is a workspace dependency
 */
function isWorkspacePackage(packageName: string): boolean {
  try {
    const pkgJsonPath = join(process.cwd(), 'package.json');
    const pkgJson = JSON.parse(readFileSync(pkgJsonPath, 'utf-8'));

    const deps = { ...pkgJson.dependencies, ...pkgJson.devDependencies };
    const version = deps[packageName];

    return version?.startsWith('workspace:') || false;
  } catch {
    return false;
  }
}

/**
 * Get installed version of a package from consumer's project
 * Uses multiple fallback strategies for monorepo compatibility
 */
export function getInstalledVersion(packageName: string): string | null {
  const cwd = process.cwd();

  // Strategy 1: Direct read from node_modules (works with symlinks)
  try {
    const directPath = join(cwd, 'node_modules', packageName, 'package.json');
    if (existsSync(directPath)) {
      const pkg = JSON.parse(readFileSync(directPath, 'utf-8'));
      return pkg.version || null;
    }
  } catch {
    // Continue to next strategy
  }

  // Strategy 2: Resolve from the consumer's project root. `createRequire` is the
  // ESM-safe way to do this — a bare `require()` here does not exist once tsup
  // emits an .mjs bundle, and its shim throws rather than falling through to the
  // next strategy.
  try {
    const consumerRequire = createRequire(join(cwd, 'package.json'));
    const pkgPath = consumerRequire.resolve(`${packageName}/package.json`);
    return JSON.parse(readFileSync(pkgPath, 'utf-8')).version || null;
  } catch {
    // Continue to next strategy
  }

  // Strategy 3: Resolve relative to THIS module, for the hoisted/global case.
  try {
    const localRequire = createRequire(import.meta.url);
    const pkgPath = localRequire.resolve(`${packageName}/package.json`);
    return JSON.parse(readFileSync(pkgPath, 'utf-8')).version || null;
  } catch {
    return null;
  }
}

/**
 * Check if we should skip update checking for this package
 * (e.g., workspace packages shouldn't be checked against npm)
 */
export function shouldCheckUpdates(packageName: string): boolean {
  return !isWorkspacePackage(packageName);
}

/**
 * Fetch latest version from npm registry
 */
async function fetchLatestVersion(packageName: string): Promise<string | null> {
  try {
    const https = await import('https');
    return new Promise((resolve) => {
      const req = https.get(
        `https://registry.npmjs.org/${packageName}/latest`,
        { timeout: 5000 },
        (res) => {
          let data = '';
          res.on('data', (chunk: string) => { data += chunk; });
          res.on('end', () => {
            try {
              const json = JSON.parse(data);
              resolve(json.version || null);
            } catch {
              resolve(null);
            }
          });
        }
      );
      req.on('error', () => resolve(null));
      req.on('timeout', () => { req.destroy(); resolve(null); });
    });
  } catch {
    return null;
  }
}

/**
 * Check all @djangocfg packages for updates
 * All packages are aligned to the version of @djangocfg/nextjs (master package)
 * Skips workspace:* packages unless forceCheckWorkspace is true
 */
export async function checkForUpdates(options: { forceCheckWorkspace?: boolean } = {}): Promise<PackageVersion[]> {
  const results: PackageVersion[] = [];

  // First, get the latest version of master package (@djangocfg/nextjs)
  // All other packages should align to this version
  const masterLatest = await fetchLatestVersion(PACKAGE_NAME);
  if (!masterLatest) {
    // Can't determine target version, skip update check
    return results;
  }

  // Check packages against master version
  const checks = DJANGOCFG_PACKAGES.map(async (name) => {
    // Skip workspace packages unless force mode
    const isWorkspace = !shouldCheckUpdates(name);
    if (!options.forceCheckWorkspace && isWorkspace) {
      return null;
    }

    const current = getInstalledVersion(name);
    if (!current) {
      return null;
    }

    // All packages should update to master package version
    const hasUpdate = !!(masterLatest && current && semver.gt(masterLatest, current));

    return { name, current, latest: masterLatest, hasUpdate };
  });

  const checkResults = await Promise.all(checks);

  for (const result of checkResults) {
    if (result) {
      results.push(result);
    }
  }

  return results;
}

/**
 * Get packages that need updating
 */
export async function getOutdatedPackages(options: { forceCheckWorkspace?: boolean } = {}): Promise<PackageVersion[]> {
  const all = await checkForUpdates(options);
  const skipped = updaterCache.get('skippedVersions') || {};

  return all.filter(pkg => {
    if (!pkg.hasUpdate) return false;
    // Skip if user chose to skip this specific version
    if (skipped[pkg.name] === pkg.latest) return false;
    return true;
  });
}

/**
 * Create a simple spinner
 */
function createSpinner(text: string) {
  let frameIndex = 0;
  let interval: NodeJS.Timeout | null = null;
  let currentText = text;

  const render = () => {
    const frame = SPINNER_FRAMES[frameIndex];
    process.stdout.write(`\r${chalk.cyan(frame)} ${currentText}`);
    frameIndex = (frameIndex + 1) % SPINNER_FRAMES.length;
  };

  return {
    start() {
      if (process.stdout.isTTY) {
        interval = setInterval(render, 80);
        render();
      } else {
        console.log(`  ${currentText}`);
      }
      return this;
    },
    text(newText: string) {
      currentText = newText;
      return this;
    },
    succeed(text?: string) {
      if (interval) clearInterval(interval);
      if (process.stdout.isTTY) {
        process.stdout.write(`\r${chalk.green('✓')} ${text || currentText}\n`);
      } else {
        console.log(`  ${chalk.green('✓')} ${text || currentText}`);
      }
      return this;
    },
    fail(text?: string) {
      if (interval) clearInterval(interval);
      if (process.stdout.isTTY) {
        process.stdout.write(`\r${chalk.red('✗')} ${text || currentText}\n`);
      } else {
        console.log(`  ${chalk.red('✗')} ${text || currentText}`);
      }
      return this;
    },
    stop() {
      if (interval) clearInterval(interval);
      if (process.stdout.isTTY) {
        process.stdout.write('\r\x1b[K');
      }
      return this;
    },
  };
}

/**
 * Ask user for confirmation
 */
async function askConfirmation(question: string): Promise<boolean> {
  if (isCI || !process.stdin.isTTY) {
    return false;
  }

  return new Promise((resolve) => {
    const rl = createInterface({
      input: process.stdin,
      output: process.stdout,
    });

    rl.question(question, (answer) => {
      rl.close();
      const normalized = answer.toLowerCase().trim();
      resolve(normalized === '' || normalized === 'y' || normalized === 'yes');
    });
  });
}

/**
 * Update a single package with progress
 */
async function updateSinglePackage(
  pkg: PackageVersion,
  pm: 'pnpm' | 'yarn' | 'npm',
  index: number,
  total: number
): Promise<boolean> {
  const progress = `[${index + 1}/${total}]`;
  const versionInfo = `${chalk.red(pkg.current)} → ${chalk.green(pkg.latest)}`;
  const spinner = createSpinner(
    `${chalk.dim(progress)} Updating ${chalk.cyan(pkg.name)} ${versionInfo}`
  );

  spinner.start();

  // Always install with @latest to keep package.json consistent
  const command = pm === 'pnpm'
    ? `pnpm add ${pkg.name}@latest`
    : pm === 'yarn'
    ? `yarn add ${pkg.name}@latest`
    : `npm install ${pkg.name}@latest`;

  return new Promise((resolve) => {
    const proc = spawn(command, {
      shell: true,
      cwd: process.cwd(),
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    proc.on('close', (code) => {
      if (code === 0) {
        spinner.succeed(
          `${chalk.dim(progress)} ${chalk.cyan(pkg.name)} ${chalk.green(pkg.latest!)}`
        );
        resolve(true);
      } else {
        spinner.fail(
          `${chalk.dim(progress)} ${chalk.cyan(pkg.name)} ${chalk.red('failed')}`
        );
        resolve(false);
      }
    });

    proc.on('error', () => {
      spinner.fail(`${chalk.dim(progress)} ${chalk.cyan(pkg.name)} ${chalk.red('failed')}`);
      resolve(false);
    });
  });
}

/**
 * Update packages with progress
 */
export async function updatePackagesWithProgress(packages: PackageVersion[]): Promise<boolean> {
  if (packages.length === 0) return true;

  const pm = detectPackageManager();
  const total = packages.length;

  console.log('');
  console.log(chalk.bold(`  Updating ${total} package${total > 1 ? 's' : ''}...`));
  console.log('');

  let successCount = 0;
  const failedPackages: string[] = [];

  for (const [i, pkg] of packages.entries()) {
    const success = await updateSinglePackage(pkg, pm, i, total);
    if (success) {
      successCount++;
    } else {
      failedPackages.push(pkg.name);
    }
  }

  console.log('');

  if (failedPackages.length === 0) {
    consola.success(`All ${total} packages updated successfully!`);
    return true;
  } else if (successCount > 0) {
    consola.warn(`${successCount}/${total} packages updated. Failed: ${failedPackages.join(', ')}`);
    return false;
  } else {
    consola.error(`Failed to update packages: ${failedPackages.join(', ')}`);
    return false;
  }
}

/**
 * Check and prompt for package updates
 */
export async function checkAndUpdatePackages(options: UpdateOptions = {}): Promise<boolean> {
  // Check cooldown
  const lastCheck = updaterCache.get('lastCheck') || 0;
  if (!options.force && (Date.now() - lastCheck) < UPDATE_CHECK_COOLDOWN_MS) {
    return true;
  }

  updaterCache.set('lastCheck', Date.now());

  // Check for updates
  const spinner = createSpinner('Checking for updates...');
  spinner.start();

  const outdated = await getOutdatedPackages({
    forceCheckWorkspace: options.forceCheckWorkspace,
  });

  spinner.stop();

  console.log(chalk.dim(`  Found ${outdated.length} outdated package(s)`));

  if (outdated.length === 0) {
    console.log(chalk.green('  ✓ All packages are up to date'));
    return true;
  }

  // Auto-update if configured
  if (options.autoUpdate || updaterCache.get('autoUpdate')) {
    return updatePackagesWithProgress(outdated);
  }

  // Show outdated packages
  console.log('');
  consola.box('📦 Updates Available');
  console.log('');

  for (const pkg of outdated) {
    console.log(
      `  ${chalk.yellow('•')} ${chalk.bold(pkg.name)}  ` +
      `${chalk.red(pkg.current)} → ${chalk.green(pkg.latest)}`
    );
  }
  console.log('');

  // Ask for confirmation
  const shouldUpdate = await askConfirmation(
    `${chalk.green('?')} Update these packages now? ${chalk.dim('[Y/n]')} `
  );

  if (shouldUpdate) {
    const success = await updatePackagesWithProgress(outdated);

    if (success) {
      const enableAuto = await askConfirmation(
        `${chalk.green('?')} Enable auto-update for future? ${chalk.dim('[y/N]')} `
      );
      if (enableAuto) {
        updaterCache.set('autoUpdate', true);
        consola.info('Auto-update enabled.');
      }
    }

    return success;
  }

  // User declined, ask if they want to skip these versions
  const skipVersions = await askConfirmation(
    `${chalk.green('?')} Skip these versions in future? ${chalk.dim('[y/N]')} `
  );

  if (skipVersions) {
    const skipped = updaterCache.get('skippedVersions') || {};
    for (const pkg of outdated) {
      if (pkg.latest) {
        skipped[pkg.name] = pkg.latest;
      }
    }
    updaterCache.set('skippedVersions', skipped);
    consola.info('Versions skipped. Will prompt again for newer versions.');
  }

  return false;
}

/**
 * Reset updater preferences
 */
export function resetUpdaterPreferences(): void {
  updaterCache.clear();
  consola.success('Updater preferences reset');
}
