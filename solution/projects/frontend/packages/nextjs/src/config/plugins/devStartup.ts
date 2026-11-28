/**
 * Dev Startup Webpack Plugin
 *
 * Handles banner display, version checking, and package updates.
 */

import type { Compiler } from 'webpack';
import chalk from 'chalk';
import { existsSync } from 'fs';
import { join } from 'path';

import { AI_DOCS_HINT } from '../../ai/constants';
import { DJANGO_CFG_BANNER } from '../constants';
import { checkAndInstallPackages } from '../packages/installer';
import { checkAndUpdatePackages } from '../packages/updater';
import { getCurrentVersion } from '../utils/version';

// Track if startup tasks were already run (persists across HMR)
let startupDone = false;

export interface DevStartupPluginOptions {
  /** Check for missing optional packages (default: true) */
  checkPackages?: boolean;
  /** Auto-install missing packages without prompting */
  autoInstall?: boolean;
  /** Check for @djangocfg/* package updates (default: true) */
  checkUpdates?: boolean;
  /** Auto-update packages without prompting */
  autoUpdate?: boolean;
  /** Force check workspace:* packages (for testing in monorepo) */
  forceCheckWorkspace?: boolean;
}

/**
 * Webpack plugin for dev startup tasks
 */
export class DevStartupPlugin {
  private options: DevStartupPluginOptions;

  constructor(options: DevStartupPluginOptions = {}) {
    this.options = options;
  }

  apply(compiler: Compiler): void {
    // Use tapPromise for proper async handling
    compiler.hooks.done.tapPromise('DevStartupPlugin', async () => {
      // Run startup tasks only once
      if (!startupDone) {
        startupDone = true;
        await this.runStartupTasks();
      }
    });
  }

  private async runStartupTasks(): Promise<void> {
    // 1. Print banner
    console.log('\n' + chalk.yellowBright.bold(DJANGO_CFG_BANNER));

    // 2. Print current version
    const version = getCurrentVersion();
    if (version) {
      console.log(chalk.dim(`  📦 @djangocfg/nextjs v${version}`));
    }

    // 3. Check PWA setup
    this.checkPWASetup();

    // 4. Print AI docs hint
    console.log(chalk.magenta(`  ${AI_DOCS_HINT}\n`));

    // 5. Check for package updates
    if (this.options.checkUpdates !== false) {
      try {
        await checkAndUpdatePackages({
          autoUpdate: this.options.autoUpdate,
          forceCheckWorkspace: this.options.forceCheckWorkspace,
          force: true, // Force check ignoring cooldown
        });
      } catch (err) {
        console.log(chalk.red('  Update check failed:'), err);
      }
    }

    // 6. Check for missing optional packages
    if (this.options.checkPackages !== false) {
      await checkAndInstallPackages({
        autoInstall: this.options.autoInstall,
      });
    }
  }

  private checkPWASetup(): void {
    const cwd = process.cwd();
    const swPath = join(cwd, 'app', 'sw.ts');
    const manifestPath = join(cwd, 'app', 'manifest.ts');

    const hasSW = existsSync(swPath);
    const hasManifest = existsSync(manifestPath);

    if (hasSW || hasManifest) {
      console.log(chalk.cyan('  📱 PWA Configuration:'));

      if (hasSW) {
        console.log(chalk.green('     ✓ Service Worker: app/sw.ts'));
      } else {
        console.log(chalk.yellow('     ⚠ Service Worker: not found'));
      }

      if (hasManifest) {
        console.log(chalk.green('     ✓ Manifest: app/manifest.ts'));
      } else {
        console.log(chalk.yellow('     ⚠ Manifest: not found'));
      }

      console.log(chalk.dim('     → Check: DevTools → Application → Service Workers'));
      console.log(chalk.dim('     → Test push: import from @djangocfg/nextjs/pwa'));
    }
  }
}

/**
 * Reset plugin state (useful for tests)
 */
export function resetDevStartupState(): void {
  startupDone = false;
}
