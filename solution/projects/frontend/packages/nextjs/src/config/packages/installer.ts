/**
 * Package Installer
 *
 * Provides auto-installation functionality with user confirmation and progress indication.
 */

import chalk from 'chalk';
import { execSync, spawn } from 'child_process';
import Conf from 'conf';
import consola from 'consola';
import { existsSync } from 'fs';
import { join } from 'path';
import { createInterface } from 'readline';

import { isCI } from '../utils/env';
import { getMissingPackages } from './checker';

import type { MissingPackage } from './checker';
type InstallerCacheShape = {
  autoInstall?: boolean;
  skipPackages?: string[];
  lastPrompt?: number;
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

function createInstallerCache(): CacheLike<InstallerCacheShape> {
  try {
    return new Conf<InstallerCacheShape>({
      projectName: 'djangocfg-nextjs-installer',
      projectVersion: '1.0.0',
    });
  } catch {
    // Fallback for corrupted conf file or invalid JSON in cache storage.
    return createMemoryCache<InstallerCacheShape>();
  }
}

// Installer preferences cache
const installerCache = createInstallerCache();

// Don't prompt more than once per hour
const PROMPT_COOLDOWN_MS = 60 * 60 * 1000;

// Spinner frames for progress
const SPINNER_FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];

export interface InstallOptions {
  /** Auto-install without prompting */
  autoInstall?: boolean;
  /** Skip specific packages */
  skipPackages?: string[];
  /** Force prompt even if recently prompted */
  force?: boolean;
}

export interface InstallProgress {
  current: number;
  total: number;
  package: string;
  status: 'pending' | 'installing' | 'done' | 'error';
}

/**
 * Detect package manager
 */
export function detectPackageManager(): 'pnpm' | 'yarn' | 'npm' {
  try {
    // Check for lockfiles
    const cwd = process.cwd();

    if (existsSync(join(cwd, 'pnpm-lock.yaml'))) return 'pnpm';
    if (existsSync(join(cwd, 'yarn.lock'))) return 'yarn';
    if (existsSync(join(cwd, 'package-lock.json'))) return 'npm';

    // Check for global package manager
    try {
      execSync('pnpm --version', { stdio: 'ignore' });
      return 'pnpm';
    } catch {
      try {
        execSync('yarn --version', { stdio: 'ignore' });
        return 'yarn';
      } catch {
        return 'npm';
      }
    }
  } catch {
    return 'npm';
  }
}

/**
 * Build install command for a single package
 */
export function buildSingleInstallCommand(
  packageName: string,
  isDev: boolean,
  pm: 'pnpm' | 'yarn' | 'npm'
): string {
  const devFlag = isDev ? '-D ' : '';
  switch (pm) {
    case 'pnpm':
      return `pnpm add ${devFlag}${packageName}`;
    case 'yarn':
      return `yarn add ${devFlag}${packageName}`;
    case 'npm':
      return `npm install ${devFlag}${packageName}`;
  }
}

/**
 * Build install command for multiple packages (for display)
 */
export function buildInstallCommand(packages: MissingPackage[], pm: 'pnpm' | 'yarn' | 'npm'): string {
  const devPackages = packages.filter(p => p.devDependency).map(p => p.name);
  const prodPackages = packages.filter(p => !p.devDependency).map(p => p.name);

  const commands: string[] = [];

  if (devPackages.length > 0) {
    switch (pm) {
      case 'pnpm':
        commands.push(`pnpm add -D ${devPackages.join(' ')}`);
        break;
      case 'yarn':
        commands.push(`yarn add -D ${devPackages.join(' ')}`);
        break;
      case 'npm':
        commands.push(`npm install -D ${devPackages.join(' ')}`);
        break;
    }
  }

  if (prodPackages.length > 0) {
    switch (pm) {
      case 'pnpm':
        commands.push(`pnpm add ${prodPackages.join(' ')}`);
        break;
      case 'yarn':
        commands.push(`yarn add ${prodPackages.join(' ')}`);
        break;
      case 'npm':
        commands.push(`npm install ${prodPackages.join(' ')}`);
        break;
    }
  }

  return commands.join(' && ');
}

/**
 * Ask user for confirmation via readline
 */
async function askConfirmation(question: string): Promise<boolean> {
  // Skip prompt in CI or non-TTY environments
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
      if (!process.stdout.isTTY) {
        console.log(`  ${newText}`);
      }
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
        process.stdout.write('\r\x1b[K'); // Clear line
      }
      return this;
    },
  };
}

/**
 * Install a single package with progress
 */
async function installSinglePackage(
  pkg: MissingPackage,
  pm: 'pnpm' | 'yarn' | 'npm',
  index: number,
  total: number
): Promise<boolean> {
  const command = buildSingleInstallCommand(pkg.name, pkg.devDependency, pm);
  const progress = `[${index + 1}/${total}]`;
  const spinner = createSpinner(`${chalk.dim(progress)} Installing ${chalk.cyan(pkg.name)}...`);

  spinner.start();

  return new Promise((resolve) => {
    // `split` returns `string[]`, so `cmd` is `string | undefined` and no
    // `spawn` overload accepts that — which typed `proc` as `never` and made
    // every `proc.*` below an error. `buildSingleInstallCommand` never returns
    // an empty string; the fallback states that rather than asserting it.
    const [cmd = pm, ...args] = command.split(' ');
    const proc = spawn(cmd, args, {
      shell: true,
      cwd: process.cwd(),
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    let stderr = '';

    proc.stderr?.on('data', (data) => {
      stderr += data.toString();
    });

    proc.on('close', (code) => {
      if (code === 0) {
        spinner.succeed(`${chalk.dim(progress)} ${chalk.cyan(pkg.name)} ${chalk.green('installed')}`);
        resolve(true);
      } else {
        spinner.fail(`${chalk.dim(progress)} ${chalk.cyan(pkg.name)} ${chalk.red('failed')}`);
        if (stderr) {
          console.log(chalk.dim(`    ${stderr.split('\n')[0]}`));
        }
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
 * Install packages with progress indication
 */
export async function installPackagesWithProgress(packages: MissingPackage[]): Promise<boolean> {
  if (packages.length === 0) return true;

  const pm = detectPackageManager();
  const total = packages.length;

  console.log('');
  console.log(chalk.bold(`  Installing ${total} package${total > 1 ? 's' : ''}...`));
  console.log('');

  let successCount = 0;
  const failedPackages: string[] = [];

  for (const [i, pkg] of packages.entries()) {
    const success = await installSinglePackage(pkg, pm, i, total);
    if (success) {
      successCount++;
    } else {
      failedPackages.push(pkg.name);
    }
  }

  console.log('');

  if (failedPackages.length === 0) {
    consola.success(`All ${total} packages installed successfully!`);
    return true;
  } else if (successCount > 0) {
    consola.warn(`${successCount}/${total} packages installed. Failed: ${failedPackages.join(', ')}`);
    return false;
  } else {
    consola.error(`Failed to install packages: ${failedPackages.join(', ')}`);
    return false;
  }
}

/**
 * Install packages (simple version without per-package progress)
 */
export async function installPackages(packages: MissingPackage[]): Promise<boolean> {
  // Use progress version for multiple packages in TTY
  if (packages.length > 1 && process.stdout.isTTY) {
    return installPackagesWithProgress(packages);
  }

  // Simple installation for single package or non-TTY
  if (packages.length === 0) return true;

  const pm = detectPackageManager();
  const command = buildInstallCommand(packages, pm);

  consola.info(`Installing: ${chalk.cyan(packages.map(p => p.name).join(', '))}`);

  const spinner = createSpinner('Installing packages...');
  spinner.start();

  return new Promise((resolve) => {
    const proc = spawn(command, {
      shell: true,
      cwd: process.cwd(),
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    proc.on('close', (code) => {
      if (code === 0) {
        spinner.succeed('Packages installed successfully!');
        resolve(true);
      } else {
        spinner.fail('Failed to install packages');
        resolve(false);
      }
    });

    proc.on('error', () => {
      spinner.fail('Installation failed');
      resolve(false);
    });
  });
}

/**
 * Check and prompt for missing packages
 *
 * Returns true if all packages are available (either already installed or just installed)
 */
export async function checkAndInstallPackages(options: InstallOptions = {}): Promise<boolean> {
  const missing = getMissingPackages();

  // Filter out skipped packages
  const skipList = options.skipPackages || installerCache.get('skipPackages') || [];
  const toInstall = missing.filter(p => !skipList.includes(p.name));

  if (toInstall.length === 0) {
    return true;
  }

  // Check cooldown (don't prompt too often)
  const lastPrompt = installerCache.get('lastPrompt') || 0;
  if (!options.force && (Date.now() - lastPrompt) < PROMPT_COOLDOWN_MS) {
    // Show info but don't prompt
    printMissingPackagesInfo(toInstall);
    return false;
  }

  // Auto-install if configured
  if (options.autoInstall || installerCache.get('autoInstall')) {
    return installPackages(toInstall);
  }

  // Show missing packages
  console.log('');
  consola.box('📦 Missing Optional Packages');
  console.log('');

  for (const pkg of toInstall) {
    console.log(`  ${chalk.yellow('•')} ${chalk.bold(pkg.name)}`);
    console.log(`    ${chalk.dim(pkg.description)}`);
    console.log(`    ${chalk.dim(pkg.reason)}`);
    console.log('');
  }

  // Build install command for display
  const pm = detectPackageManager();
  const command = buildInstallCommand(toInstall, pm);

  console.log(`  ${chalk.cyan('Command:')} ${command}`);
  console.log('');

  // Ask for confirmation
  installerCache.set('lastPrompt', Date.now());

  const shouldInstall = await askConfirmation(
    `${chalk.green('?')} Install these packages now? ${chalk.dim('[Y/n]')} `
  );

  if (shouldInstall) {
    const success = await installPackages(toInstall);

    // Ask if user wants to enable auto-install for future
    if (success) {
      const enableAuto = await askConfirmation(
        `${chalk.green('?')} Enable auto-install for future? ${chalk.dim('[y/N]')} `
      );
      if (enableAuto) {
        installerCache.set('autoInstall', true);
        consola.info('Auto-install enabled. Run with --no-auto-install to disable.');
      }
    }

    return success;
  }

  // User declined, ask if they want to skip these packages permanently
  const skipPermanently = await askConfirmation(
    `${chalk.green('?')} Skip these packages in future prompts? ${chalk.dim('[y/N]')} `
  );

  if (skipPermanently) {
    const currentSkip = installerCache.get('skipPackages') || [];
    installerCache.set('skipPackages', [...currentSkip, ...toInstall.map(p => p.name)]);
    consola.info('Packages added to skip list.');
  }

  return false;
}

/**
 * Print info about missing packages without prompting
 */
function printMissingPackagesInfo(packages: MissingPackage[]): void {
  if (packages.length === 0) return;

  const pm = detectPackageManager();
  const command = buildInstallCommand(packages, pm);

  consola.warn(`Missing optional packages: ${packages.map(p => p.name).join(', ')}`);
  consola.info(`Install with: ${chalk.cyan(command)}`);
}

/**
 * Reset installer preferences
 */
export function resetInstallerPreferences(): void {
  installerCache.clear();
  consola.success('Installer preferences reset');
}
