/**
 * Compression Plugin Setup
 *
 * Adds Gzip and Brotli compression for static builds.
 */

import type { Configuration as WebpackConfig } from 'webpack';
import { createRequire } from 'module';

import { isPackageInstalled } from '../packages/checker';

// Optional peer dependencies are loaded synchronously at config time, which
// `import()` cannot do. `createRequire` is the ESM-safe equivalent of `require`.
const requirePeer = createRequire(import.meta.url);

export interface CompressionPluginOptions {
  /** Enable gzip compression */
  gzip?: boolean;
  /** Enable brotli compression */
  brotli?: boolean;
  /** Minimum file size to compress (default: 8192) */
  threshold?: number;
  /** Minimum compression ratio (default: 0.8) */
  minRatio?: number;
  /** Brotli compression level (default: 8) */
  brotliLevel?: number;
}

const DEFAULT_OPTIONS: Required<CompressionPluginOptions> = {
  gzip: true,
  brotli: true,
  threshold: 8192,
  minRatio: 0.8,
  brotliLevel: 8,
};

/**
 * Add compression plugins to webpack config
 *
 * Returns true if plugins were added, false if compression-webpack-plugin is not installed
 */
export function addCompressionPlugins(
  config: WebpackConfig,
  options: CompressionPluginOptions = {}
): boolean {
  // Check if compression-webpack-plugin is installed
  if (!isPackageInstalled('compression-webpack-plugin')) {
    return false;
  }

  const opts = { ...DEFAULT_OPTIONS, ...options };

  try {
    // Resolved at call time to avoid bundling it when it is not installed.
    const CompressionPlugin = requirePeer('compression-webpack-plugin');

    if (!config.plugins) {
      config.plugins = [];
    }

    // Gzip compression
    if (opts.gzip) {
      config.plugins.push(
        new CompressionPlugin({
          filename: '[path][base].gz',
          algorithm: 'gzip',
          test: /\.(js|css|html|svg|json)$/,
          threshold: opts.threshold,
          minRatio: opts.minRatio,
        })
      );
    }

    // Brotli compression
    if (opts.brotli) {
      config.plugins.push(
        new CompressionPlugin({
          filename: '[path][base].br',
          algorithm: 'brotliCompress',
          test: /\.(js|css|html|svg|json)$/,
          threshold: opts.threshold,
          minRatio: opts.minRatio,
          compressionOptions: {
            level: opts.brotliLevel,
          },
        })
      );
    }

    return true;
  } catch {
    // compression-webpack-plugin failed to load
    return false;
  }
}

/**
 * Check if compression is available
 */
export function isCompressionAvailable(): boolean {
  return isPackageInstalled('compression-webpack-plugin');
}
