import { defineConfig } from 'vitest/config';

/** No tests yet: the viewers are composition over `ui-core`, and what is worth asserting about them is what a story shows. */
export default defineConfig({
  test: { include: ['src/**/*.test.{ts,tsx}'], exclude: ['**/node_modules/**'], passWithNoTests: true },
});
