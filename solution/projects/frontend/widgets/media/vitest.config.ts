import { defineConfig } from 'vitest/config';

/**
 * No environment is declared: the diagram renderer touches no DOM, and adding
 * jsdom for it would hide a regression that reintroduced one.
 */
export default defineConfig({
  test: {
    include: ['src/**/*.test.ts', 'src/**/*.test.tsx'],
    exclude: ['**/node_modules/**'],
  },
});
