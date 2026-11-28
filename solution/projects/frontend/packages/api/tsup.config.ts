import { defineConfig } from 'tsup';

// `pnpm build` empties dist/ before tsup and runs scripts/check-dist.mjs after
// it. Do not use `clean: true` here instead: tsup builds these configs at the
// same time into one outDir, so each config's clean would delete files another
// config has just written.
//
// Each config bundles its entry alone, so `index`, `auth`, `clients` and
// `hooks` each inline their own copy of src/runtime. Sharing one copy through
// `splitting` would need them in one config, where the "use client" banner
// lands on every output, shared chunks included, and would turn the
// server-safe root entry's runtime into a client module. One auth store per
// page has to come from the runtime itself (a `globalThis` slot), not from
// bundling.
export default defineConfig([
  // Main entry - server-safe (fetchers, schemas, types - NO hooks)
  {
    entry: ['src/index.ts'],
    format: ['esm', 'cjs'],
    outDir: 'dist',
    target: 'node18',
    platform: 'neutral',
    sourcemap: true,
    dts: true,
    external: [
      'react',
      'react-dom',
      'next',
      '@tanstack/react-query',
      'zod',
      'consola',
    ],
    esbuildOptions(options) {
      // Don't inline process.env.NODE_ENV — let consumer (Next.js) handle it
      options.define = { ...options.define, 'process.env.NODE_ENV': 'process.env.NODE_ENV' };
      options.keepNames = true;
      options.preserveSymlinks = true;
    },
    outExtension({ format }) {
      return format === 'esm' ? { js: '.mjs' } : { js: '.cjs' };
    },
  },
  // MSW entry - generated handlers and Faker response factories
  {
    entry: { mocks: 'src/_api/mocks.ts' },
    format: ['esm', 'cjs'],
    outDir: 'dist',
    target: 'node18',
    platform: 'neutral',
    sourcemap: true,
    dts: true,
    external: ['msw', '@faker-js/faker', 'zod'],
    esbuildOptions(options) {
      options.keepNames = true;
      options.preserveSymlinks = true;
    },
    outExtension({ format }) {
      return format === 'esm' ? { js: '.mjs' } : { js: '.cjs' };
    },
  },
  // Auth entry - client-only (contexts, hooks, utils)
  {
    entry: { auth: 'src/auth/index.ts' },
    format: ['esm', 'cjs'],
    outDir: 'dist',
    target: 'node18',
    platform: 'neutral',
    sourcemap: true,
    dts: true,
    external: [
      'react',
      'react-dom',
      'next',
      '@tanstack/react-query',
      'zod',
      'consola',
    ],
    esbuildOptions(options) {
      // Don't inline process.env.NODE_ENV — let consumer (Next.js) handle it
      options.define = { ...options.define, 'process.env.NODE_ENV': 'process.env.NODE_ENV' };
      options.keepNames = true;
      options.preserveSymlinks = true;
      options.banner = { js: '"use client";' };
    },
    outExtension({ format }) {
      return format === 'esm' ? { js: '.mjs' } : { js: '.cjs' };
    },
  },
  // Storage entry - the key registry alone (no client, no dependencies)
  {
    entry: { storage: 'src/storage.ts' },
    format: ['esm', 'cjs'],
    outDir: 'dist',
    target: 'node18',
    platform: 'neutral',
    sourcemap: true,
    dts: true,
    esbuildOptions(options) {
      options.keepNames = true;
      options.preserveSymlinks = true;
    },
    outExtension({ format }) {
      return format === 'esm' ? { js: '.mjs' } : { js: '.cjs' };
    },
  },
  // Auth server entry - server-safe (middlewares only)
  {
    entry: { 'auth-server': 'src/auth/server.ts' },
    format: ['esm', 'cjs'],
    outDir: 'dist',
    target: 'node18',
    platform: 'neutral',
    sourcemap: true,
    dts: true,
    external: [
      'react',
      'react-dom',
      'next',
      '@tanstack/react-query',
      'zod',
      'consola',
    ],
    esbuildOptions(options) {
      // Don't inline process.env.NODE_ENV — let consumer (Next.js) handle it
      options.define = { ...options.define, 'process.env.NODE_ENV': 'process.env.NODE_ENV' };
      options.keepNames = true;
      options.preserveSymlinks = true;
    },
    outExtension({ format }) {
      return format === 'esm' ? { js: '.mjs' } : { js: '.cjs' };
    },
  },
  // Clients entry - pre-configured API instances with hooks and fetchers
  {
    entry: { clients: 'src/clients.ts' },
    format: ['esm', 'cjs'],
    outDir: 'dist',
    target: 'node18',
    platform: 'neutral',
    sourcemap: true,
    dts: true,
    external: [
      'react',
      'react-dom',
      'next',
      '@tanstack/react-query',
      'zod',
      'consola',
    ],
    esbuildOptions(options) {
      // Don't inline process.env.NODE_ENV — let consumer (Next.js) handle it
      options.define = { ...options.define, 'process.env.NODE_ENV': 'process.env.NODE_ENV' };
      options.keepNames = true;
      options.preserveSymlinks = true;
      options.banner = { js: '"use client";' };
    },
    outExtension({ format }) {
      return format === 'esm' ? { js: '.mjs' } : { js: '.cjs' };
    },
  },
  // Hooks entry - client-only convenience hooks wrapping generated React Query
  {
    entry: { hooks: 'src/hooks/index.ts' },
    format: ['esm', 'cjs'],
    outDir: 'dist',
    target: 'node18',
    platform: 'neutral',
    sourcemap: true,
    dts: true,
    external: [
      'react',
      'react-dom',
      'next',
      '@tanstack/react-query',
      'zod',
      'consola',
    ],
    esbuildOptions(options) {
      options.define = { ...options.define, 'process.env.NODE_ENV': 'process.env.NODE_ENV' };
      options.keepNames = true;
      options.preserveSymlinks = true;
      options.banner = { js: '"use client";' };
    },
    outExtension({ format }) {
      return format === 'esm' ? { js: '.mjs' } : { js: '.cjs' };
    },
  },
]);
