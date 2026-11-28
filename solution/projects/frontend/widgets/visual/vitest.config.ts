import { defineConfig } from 'vitest/config';

/**
 * Node environment. The group arrived from ui-tools with no tests; this config
 * makes adding one a one-file change rather than a decision.
 */
export default defineConfig({
  test: {
    environment: 'node',
    include: ['src/**/*.test.{ts,tsx}'],
    exclude: ['**/node_modules/**'],
  },
});
