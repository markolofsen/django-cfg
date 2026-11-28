import { defineConfig } from 'vitest/config';

/**
 * Node environment on purpose: the seed rules are pure and `use-avatar-svg`
 * is asserted through its returned markup, not through a rendered tree. A
 * jsdom would only hide a regression that reintroduced a DOM dependency.
 */
export default defineConfig({
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts', 'src/**/*.test.tsx'],
    exclude: ['**/node_modules/**'],
  },
});
