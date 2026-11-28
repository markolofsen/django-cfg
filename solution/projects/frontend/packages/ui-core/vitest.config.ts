import { defineConfig } from 'vitest/config';

/** Node environment: component tests render to a string, so no DOM is needed. */
export default defineConfig({
  test: {
    include: ['src/**/*.test.{ts,tsx}'],
    exclude: ['**/node_modules/**'],
  },
});
