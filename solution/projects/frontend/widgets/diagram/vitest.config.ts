import { defineConfig } from 'vitest/config';

/**
 * Node environment: a builder is a pure string function. The only React here
 * is the three theme hooks, which read `ui-core`'s palette and are exercised
 * through the values they feed the builders.
 */
export default defineConfig({
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts'],
    exclude: ['**/node_modules/**'],
  },
});
