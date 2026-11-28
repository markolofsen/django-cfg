import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    // Default to the fast Node environment. DOM-dependent suites opt in per-file
    // with a `// @vitest-environment jsdom` header comment, so the bulk of the
    // pure-logic tests never pay jsdom's ~500ms startup.
    environment: 'node',
    include: ['src/**/__tests__/**/*.test.{ts,tsx}'],
    exclude: ['node_modules/**', 'dist/**'],
  },
});
