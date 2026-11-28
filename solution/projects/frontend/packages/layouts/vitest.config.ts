import { defineConfig } from 'vitest/config';

/**
 * Node by default: most tests cover pure parsers. A component test opts into a DOM per file with a
 * `// @vitest-environment jsdom` header. `*.test-d.ts` are type tests (`expectTypeOf`, `@ts-expect-error`): tsc runs them.
 */
export default defineConfig({
  test: {
    include: ['src/**/*.test.{ts,tsx}'],
    exclude: ['**/node_modules/**'],
    typecheck: { enabled: true, include: ['src/**/*.test-d.ts'] },
  },
});
