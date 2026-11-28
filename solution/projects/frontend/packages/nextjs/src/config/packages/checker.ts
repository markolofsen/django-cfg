/**
 * Package Checker
 *
 * Checks which optional packages are missing and need to be installed.
 */

import { createRequire } from 'module';
import { join } from 'path';

import { isDev, isStaticBuild } from '../utils/env';
import { getPackagesForContext, OPTIONAL_PACKAGES } from './definitions';

import type { PackageDefinition } from './definitions';
export interface MissingPackage extends PackageDefinition {
  /** Why is this package needed? */
  reason: string;
}

/**
 * Check if a package is installed in the consumer's project
 * Uses process.cwd() to check from the consumer's context, not the library's
 */
export function isPackageInstalled(packageName: string): boolean {
  try {
    // Create require from consumer's cwd to check their node_modules
    const consumerRequire = createRequire(join(process.cwd(), 'package.json'));
    consumerRequire.resolve(packageName);
    return true;
  } catch {
    // Fallback: try regular require (for packages hoisted to root)
    try {
      require.resolve(packageName);
      return true;
    } catch {
      return false;
    }
  }
}

/**
 * Get all missing packages for current context
 */
export function getMissingPackages(): MissingPackage[] {
  const neededPackages = getPackagesForContext({ isStaticBuild, isDev });
  const missing: MissingPackage[] = [];

  for (const pkg of neededPackages) {
    if (!isPackageInstalled(pkg.name)) {
      missing.push({
        ...pkg,
        reason: getReasonText(pkg),
      });
    }
  }

  return missing;
}

/**
 * Check specific packages
 */
export function checkPackages(packageNames: string[]): MissingPackage[] {
  const missing: MissingPackage[] = [];

  for (const name of packageNames) {
    if (!isPackageInstalled(name)) {
      const definition = OPTIONAL_PACKAGES.find(p => p.name === name);
      missing.push({
        name,
        description: definition?.description || 'Optional package',
        condition: definition?.condition || 'always',
        devDependency: definition?.devDependency ?? true,
        reason: definition ? getReasonText(definition) : 'Requested by configuration',
      });
    }
  }

  return missing;
}

/**
 * Get human-readable reason for package requirement
 */
function getReasonText(pkg: PackageDefinition): string {
  switch (pkg.condition) {
    case 'static-build':
      return 'Required for static build (NEXT_PUBLIC_STATIC_BUILD=true)';
    case 'dev':
      return 'Required for development mode';
    case 'always':
      return 'Required for all builds';
    default:
      return 'Optional feature';
  }
}
