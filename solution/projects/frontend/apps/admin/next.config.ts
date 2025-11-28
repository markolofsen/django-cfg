import type { NextConfig } from "next";
import path from "path";
import bundleAnalyzer from "@next/bundle-analyzer";
import CompressionPlugin from "compression-webpack-plugin";

const isStaticBuild = process.env.NEXT_PUBLIC_STATIC_BUILD === 'true';
const basePath = isStaticBuild ? '/cfg/nextjs-admin' : '';

const withBundleAnalyzer = bundleAnalyzer({
  enabled: process.env.ANALYZE === 'true',
});

const nextConfig: NextConfig = {
  reactStrictMode: true,
  trailingSlash: true,

  // Static export configuration - only for production builds
  ...(isStaticBuild && {
    output: "export",
    distDir: "out",
    basePath,  // Django serves from /cfg/nextjs-admin/
    assetPrefix: basePath,  // All assets prefixed with /cfg/nextjs-admin
  }),

  // Standalone output for Docker deployment
  ...(!isStaticBuild && {
    output: "standalone",
  }),

  // Environment variables
  env: {
    NEXT_PUBLIC_BASE_PATH: basePath,
    // API URL based on build mode:
    // - Static build: '' (empty string) for relative paths to same domain
    // - Dev server: 'http://localhost:8000' for local development
    NEXT_PUBLIC_API_URL: isStaticBuild ? '' : process.env.NEXT_PUBLIC_API_URL,
  },

  // Disable features not supported in static export
  images: {
    unoptimized: true,
  },

  // Optimize package imports for better code splitting
  experimental: {
    optimizePackageImports: [
      "@djangocfg/ui",
      "@djangocfg/layouts",
      "lucide-react",
      "recharts"
    ],
  },

  transpilePackages: [
    "@djangocfg/ui",
    "@djangocfg/layouts",
    "@djangocfg/markdown",
    "@djangocfg/api",
    "@djangocfg/centrifugo"
  ],

  webpack: (config, { isServer }) => {
    // Force single React instance
    config.resolve.alias = {
      ...config.resolve.alias,
      react: path.resolve(__dirname, "node_modules/react"),
      "react-dom": path.resolve(__dirname, "node_modules/react-dom"),
    };

    // Add compression plugins for static build
    if (!isServer && isStaticBuild) {
      // Gzip compression
      config.plugins.push(
        new CompressionPlugin({
          filename: '[path][base].gz',
          algorithm: 'gzip',
          test: /\.(js|css|html|svg|json)$/,
          threshold: 8192, // Only compress files > 8KB
          minRatio: 0.8,   // Only compress if size reduction > 20%
        })
      );

      // Brotli compression (better than gzip, supported by modern browsers)
      config.plugins.push(
        new CompressionPlugin({
          filename: '[path][base].br',
          algorithm: 'brotliCompress',
          test: /\.(js|css|html|svg|json)$/,
          threshold: 8192,
          minRatio: 0.8,
          compressionOptions: {
            level: 11, // Maximum compression
          },
        })
      );
    }

    return config;
  },
};

export default withBundleAnalyzer(nextConfig);
