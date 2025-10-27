import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  transpilePackages: [
    "@djangocfg/ui",
    "@djangocfg/layouts",
    "@djangocfg/markdown",
    "@djangocfg/api"
  ],
  // Use standalone only in production build
  ...(process.env.NODE_ENV === "production" && { output: "standalone" }),

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
