#!/usr/bin/env node
/**
 * NPM Cleanup Script with Interactive Menu
 *
 * Removes old versions of @djangocfg packages from npm registry.
 * Similar to pypi-cleanup but for npm.
 *
 * Usage:
 *   node scripts/npm-cleanup.js
 *
 * Note: npm only allows unpublishing versions within 72 hours of publish.
 * For older versions, use deprecate mode.
 */

const { execSync } = require('child_process');
const readline = require('readline');

// ANSI colors
const colors = {
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  cyan: '\x1b[36m',
  dim: '\x1b[2m',
  bold: '\x1b[1m',
  reset: '\x1b[0m'
};

const log = {
  info: (msg) => console.log(`${colors.cyan}${msg}${colors.reset}`),
  success: (msg) => console.log(`${colors.green}✓ ${msg}${colors.reset}`),
  warn: (msg) => console.log(`${colors.yellow}⚠ ${msg}${colors.reset}`),
  error: (msg) => console.log(`${colors.red}✗ ${msg}${colors.reset}`),
  dim: (msg) => console.log(`${colors.dim}${msg}${colors.reset}`),
  bold: (msg) => console.log(`${colors.bold}${msg}${colors.reset}`)
};

// Every publishable member of packages/ and widgets/, as publish.config.mjs
// sees them — the same discovery the publisher uses, so this list cannot go
// stale the way a hand-written one did (it once named imgai/playground/ui).
const { readdirSync, readFileSync, existsSync } = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const ALL_PACKAGES = ['packages', 'widgets'].flatMap((dir) => {
  const base = path.join(ROOT, dir);
  if (!existsSync(base)) return [];
  return readdirSync(base, { withFileTypes: true })
    .filter((e) => e.isDirectory() && !e.name.startsWith('.') && !e.name.startsWith('@'))
    .map((e) => path.join(base, e.name, 'package.json'))
    .filter((f) => existsSync(f))
    .map((f) => JSON.parse(readFileSync(f, 'utf8')))
    .filter((pkg) => !pkg.private && pkg.name && pkg.name.startsWith('@djangocfg/'))
    .map((pkg) => pkg.name.replace('@djangocfg/', ''));
});

/**
 * Simple readline question helper
 */
function question(prompt) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  return new Promise((resolve) => {
    rl.question(prompt, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

/**
 * Check if user is logged in to npm
 */
function checkNpmLogin() {
  try {
    const result = execSync('npm whoami', { encoding: 'utf-8' }).trim();
    log.success(`Logged in as: ${result}`);
    return true;
  } catch (error) {
    log.error('Not logged in to npm. Run: npm login');
    return false;
  }
}

/**
 * Get all versions of a package from npm registry
 */
function getPackageVersions(packageName) {
  const fullName = `@djangocfg/${packageName}`;

  try {
    const result = execSync(`npm view ${fullName} versions --json`, {
      encoding: 'utf-8',
      stdio: ['pipe', 'pipe', 'pipe']
    });

    const versions = JSON.parse(result);
    return Array.isArray(versions) ? versions : [versions];
  } catch (error) {
    return [];
  }
}

/**
 * Get publish time for each version
 */
function getVersionTimes(packageName) {
  const fullName = `@djangocfg/${packageName}`;

  try {
    const result = execSync(`npm view ${fullName} time --json`, {
      encoding: 'utf-8',
      stdio: ['pipe', 'pipe', 'pipe']
    });

    return JSON.parse(result);
  } catch (error) {
    return {};
  }
}

/**
 * Compare semantic versions
 */
function compareVersions(a, b) {
  const partsA = a.split('.').map(x => parseInt(x.replace(/[^0-9]/g, '')) || 0);
  const partsB = b.split('.').map(x => parseInt(x.replace(/[^0-9]/g, '')) || 0);

  for (let i = 0; i < Math.max(partsA.length, partsB.length); i++) {
    const numA = partsA[i] || 0;
    const numB = partsB[i] || 0;
    if (numA !== numB) return numA - numB;
  }
  return 0;
}

/**
 * Unpublish a specific version
 */
function unpublishVersion(packageName, version) {
  const fullName = `@djangocfg/${packageName}@${version}`;

  try {
    execSync(`npm unpublish ${fullName}`, {
      encoding: 'utf-8',
      stdio: ['pipe', 'pipe', 'pipe']
    });
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * Deprecate a specific version
 */
function deprecateVersion(packageName, version, message) {
  const fullName = `@djangocfg/${packageName}@${version}`;
  const deprecationMessage = message || 'This version is deprecated. Please upgrade to the latest version.';

  try {
    execSync(`npm deprecate "${fullName}" "${deprecationMessage}"`, {
      encoding: 'utf-8',
      stdio: ['pipe', 'pipe', 'pipe']
    });
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * Check if version can be unpublished (within 72 hours)
 */
function canUnpublish(publishTime) {
  const publishDate = new Date(publishTime);
  const now = new Date();
  const hoursSincePublish = (now - publishDate) / (1000 * 60 * 60);
  return hoursSincePublish < 72;
}

/**
 * Fetch and display package info
 */
async function fetchPackageInfo(keepLatest) {
  console.log('');
  log.info('📋 Fetching package versions from npm...');
  console.log('');

  const packageData = [];
  let totalVersions = 0;
  let totalToDelete = 0;

  for (const pkg of ALL_PACKAGES) {
    const fullName = `@djangocfg/${pkg}`;
    const versions = getPackageVersions(pkg);

    if (versions.length === 0) {
      log.warn(`${fullName}: No versions found on npm`);
      continue;
    }

    versions.sort(compareVersions);

    const versionsToKeep = versions.slice(-keepLatest);
    const versionsToDelete = versions.slice(0, -keepLatest);

    totalVersions += versions.length;
    totalToDelete += versionsToDelete.length;

    packageData.push({
      name: pkg,
      fullName,
      versions,
      versionsToKeep,
      versionsToDelete
    });

    console.log(`${colors.cyan}${fullName}${colors.reset}`);
    console.log(`  Total: ${versions.length} | ${colors.green}Keep: ${versionsToKeep.join(', ')}${colors.reset}`);

    if (versionsToDelete.length > 0) {
      console.log(`  ${colors.red}Delete: ${versionsToDelete.length} versions${colors.reset}`);
    }
  }

  console.log('');
  console.log('─'.repeat(50));
  console.log(`${colors.bold}Summary:${colors.reset} ${totalVersions} total, ${colors.red}${totalToDelete} to delete${colors.reset}`);
  console.log('');

  return { packageData, totalVersions, totalToDelete };
}

/**
 * Execute cleanup
 */
async function executeCleanup(packageData, useDeprecate) {
  const summary = { deleted: 0, failed: 0, skipped: 0 };

  // Get version times for unpublish check
  const versionTimes = {};
  for (const pkg of packageData) {
    versionTimes[pkg.name] = getVersionTimes(pkg.name);
  }

  for (const pkg of packageData) {
    for (const version of pkg.versionsToDelete) {
      const fullName = `@djangocfg/${pkg.name}@${version}`;
      const publishTime = versionTimes[pkg.name]?.[version];

      if (useDeprecate) {
        process.stdout.write(`  Deprecating ${fullName}... `);
        const result = deprecateVersion(pkg.name, version);
        if (result.success) {
          console.log(`${colors.green}done${colors.reset}`);
          summary.deleted++;
        } else {
          console.log(`${colors.red}failed${colors.reset}`);
          summary.failed++;
        }
      } else {
        if (publishTime && !canUnpublish(publishTime)) {
          console.log(`  ${colors.yellow}Skip ${fullName} (>72h old)${colors.reset}`);
          summary.skipped++;
          continue;
        }

        process.stdout.write(`  Unpublishing ${fullName}... `);
        const result = unpublishVersion(pkg.name, version);
        if (result.success) {
          console.log(`${colors.green}done${colors.reset}`);
          summary.deleted++;
        } else {
          console.log(`${colors.red}failed${colors.reset}`);
          summary.failed++;
        }
      }
    }
  }

  return summary;
}

/**
 * Interactive menu
 */
async function interactiveMenu() {
  console.log('');
  log.bold('🧹 NPM Cleanup for @djangocfg packages');
  console.log('');

  // Check npm login
  if (!checkNpmLogin()) {
    process.exit(1);
  }

  // Menu
  console.log('');
  console.log(`${colors.yellow}Select action:${colors.reset}`);
  console.log('  1. Preview cleanup (dry-run)');
  console.log('  2. Unpublish old versions (< 72h only)');
  console.log('  3. Deprecate old versions (all ages)');
  console.log('  4. Exit');
  console.log('');

  const choice = await question('Enter choice [1-4]: ');

  if (choice === '4' || choice.toLowerCase() === 'q') {
    console.log('Bye!');
    process.exit(0);
  }

  // Ask how many versions to keep
  const keepInput = await question('How many latest versions to keep? [1]: ');
  const keepLatest = parseInt(keepInput) || 1;

  // Fetch package info
  const { packageData, totalToDelete } = await fetchPackageInfo(keepLatest);

  if (totalToDelete === 0) {
    log.success('Nothing to clean up!');
    process.exit(0);
  }

  if (choice === '1') {
    log.warn('DRY RUN - no changes made');
    console.log('');

    // Ask if user wants to proceed
    const proceed = await question('Proceed with actual cleanup? (y/n): ');
    if (proceed.toLowerCase() !== 'y') {
      console.log('Cancelled.');
      process.exit(0);
    }

    // Re-ask for mode
    console.log('');
    console.log(`${colors.yellow}Select cleanup mode:${colors.reset}`);
    console.log('  1. Unpublish (< 72h old versions only)');
    console.log('  2. Deprecate (all versions)');
    const mode = await question('Enter choice [1-2]: ');

    const useDeprecate = mode === '2';

    console.log('');
    console.log(`${colors.bold}${colors.red}⚠️  DESTRUCTIVE OPERATION${colors.reset}`);
    const confirm = await question('Type "yes" to confirm: ');

    if (confirm.toLowerCase() !== 'yes') {
      log.warn('Aborted');
      process.exit(0);
    }

    console.log('');
    log.info('Starting cleanup...');
    const summary = await executeCleanup(packageData, useDeprecate);

    console.log('');
    console.log('─'.repeat(50));
    log.bold('Complete!');
    console.log(`  ${colors.green}Processed: ${summary.deleted}${colors.reset}`);
    if (summary.failed > 0) console.log(`  ${colors.red}Failed: ${summary.failed}${colors.reset}`);
    if (summary.skipped > 0) console.log(`  ${colors.yellow}Skipped: ${summary.skipped}${colors.reset}`);

  } else if (choice === '2' || choice === '3') {
    const useDeprecate = choice === '3';

    console.log('');
    console.log(`${colors.bold}${colors.red}⚠️  DESTRUCTIVE OPERATION${colors.reset}`);
    if (useDeprecate) {
      console.log('This will deprecate all old versions.');
    } else {
      console.log('This will unpublish versions < 72h old.');
      console.log(`${colors.yellow}Older versions will be skipped. Use deprecate mode for them.${colors.reset}`);
    }

    const confirm = await question('Type "yes" to confirm: ');

    if (confirm.toLowerCase() !== 'yes') {
      log.warn('Aborted');
      process.exit(0);
    }

    console.log('');
    log.info('Starting cleanup...');
    const summary = await executeCleanup(packageData, useDeprecate);

    console.log('');
    console.log('─'.repeat(50));
    log.bold('Complete!');
    console.log(`  ${colors.green}Processed: ${summary.deleted}${colors.reset}`);
    if (summary.failed > 0) console.log(`  ${colors.red}Failed: ${summary.failed}${colors.reset}`);
    if (summary.skipped > 0) console.log(`  ${colors.yellow}Skipped: ${summary.skipped}${colors.reset}`);

  } else {
    log.error('Invalid choice');
    process.exit(1);
  }
}

// Run
interactiveMenu().catch(error => {
  log.error(`Fatal error: ${error.message}`);
  process.exit(1);
});
