/**
 * Package Definitions
 *
 * Defines optional packages that can be auto-installed when needed.
 */

export interface PackageDefinition {
  /** npm package name */
  name: string;
  /** Human-readable description */
  description: string;
  /** When is this package needed? */
  condition: 'static-build' | 'dev' | 'always';
  /** Is this a dev dependency? */
  devDependency: boolean;
  /** Feature flag that enables this package */
  featureFlag?: string;
}

/**
 * Optional packages that can be auto-installed
 */
export const OPTIONAL_PACKAGES: PackageDefinition[] = [
  {
    name: 'compression-webpack-plugin',
    description: 'Gzip and Brotli compression for static builds',
    condition: 'static-build',
    devDependency: true,
  },
  {
    name: '@next/bundle-analyzer',
    description: 'Bundle analyzer for analyzing build output',
    condition: 'dev',
    devDependency: true,
    featureFlag: 'ANALYZE',
  },
];

/**
 * Required peer dependencies (should already be installed)
 */
export const PEER_DEPENDENCIES = [
  'next',
  'react',
  'react-dom',
] as const;

/**
 * Get packages needed for current build context
 */
export function getPackagesForContext(options: {
  isStaticBuild: boolean;
  isDev: boolean;
}): PackageDefinition[] {
  return OPTIONAL_PACKAGES.filter(pkg => {
    switch (pkg.condition) {
      case 'static-build':
        return options.isStaticBuild;
      case 'dev':
        return options.isDev;
      case 'always':
        return true;
      default:
        return false;
    }
  });
}
