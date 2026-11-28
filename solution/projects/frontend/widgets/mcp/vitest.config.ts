import { defineConfig } from 'vitest/config';

/** No DOM: the tests cover the pure install builders and the dictionaries. */
export default defineConfig({
  test: {
    include: ['src/**/*.test.ts', 'src/**/*.test.tsx'],
    exclude: ['**/node_modules/**'],
  },
});
