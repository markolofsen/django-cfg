import { defineConfig } from 'vitest/config';

/**
 * Node environment on purpose: `next/og` renders through satori + resvg
 * (wasm), which needs no DOM, and a jsdom would only hide a regression that
 * reintroduced one.
 */
export default defineConfig({
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts', 'src/**/*.test.tsx'],
    exclude: ['**/node_modules/**'],
  },
});
