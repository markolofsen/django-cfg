import { defineConfig } from 'vitest/config';

/**
 * Node by default: the core runs with no DOM. A React test opts into jsdom per
 * file with a `// @vitest-environment jsdom` header.
 */
export default defineConfig({
  test: {
    include: ['src/**/*.test.{ts,tsx}'],
    exclude: ['**/node_modules/**'],
  },
});
