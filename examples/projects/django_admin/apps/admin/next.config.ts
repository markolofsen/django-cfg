import type { NextConfig } from "next";
import path from "path";

const isStaticBuild = process.env.NEXT_PUBLIC_STATIC_BUILD === 'true';
const basePath = isStaticBuild ? '/cfg/nextjs-admin' : '';

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
    NEXT_PUBLIC_API_URL: isStaticBuild ? '' : 'http://localhost:8000',
  },

  // Disable features not supported in static export
  images: {
    unoptimized: true,
  },

  transpilePackages: [
    "@djangocfg/ui",
    "@djangocfg/layouts",
    "@djangocfg/markdown",
    "@djangocfg/api",
    "react-ts-tradingview-widgets"
  ],

  webpack: (config, { isServer }) => {
    // Force single React instance
    config.resolve.alias = {
      ...config.resolve.alias,
      react: path.resolve(__dirname, "node_modules/react"),
      "react-dom": path.resolve(__dirname, "node_modules/react-dom"),
    };

    return config;
  },
};

export default nextConfig;
