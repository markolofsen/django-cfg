import { defineConfig } from 'vitest/config';

/**
 * Node by default: most of what is tested here is pure — selection, rename,
 * clipboard and keyboard reducers. The one DOM test declares its own
 * environment with `// @vitest-environment jsdom`, so a jsdom default would
 * only slow the rest down and hide a regression that reached for the DOM from
 * a reducer.
 */
export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['src/**/__tests__/**/*.test.{ts,tsx}', 'src/**/*.test.{ts,tsx}'],
    exclude: ['**/node_modules/**'],
  },
});
