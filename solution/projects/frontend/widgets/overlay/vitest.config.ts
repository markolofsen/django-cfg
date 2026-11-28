import { defineConfig } from 'vitest/config';

/**
 * Node environment, and `passWithNoTests` — the one widget where that is a
 * statement rather than a silence.
 *
 * Vitest 4 fails an empty run where 3 passed, which is how four widgets turned
 * out to have no tests at all. Three of them (`charts`, `code`, `visual`) had
 * real logic hiding in them and now have suites, including three genuine bugs
 * the first assertions found. This one does not: all 33 files are React
 * components, context providers and barrels, and its only `.ts` files are type
 * declarations — 140 lines of interfaces with no runtime value among them.
 * Every exported symbol is a component or a `useContext` hook.
 *
 * What is worth testing here is behaviour under a DOM — focus handling, scroll
 * position, Escape — which needs jsdom and `@testing-library/react`, and that
 * is a real suite to write, not a config flag. The stories cover these four
 * surfaces in the meantime.
 *
 * So: `true` because there is nothing pure to assert, NOT because an empty run
 * is convenient. Delete this line the moment a `.test.ts` lands.
 */
export default defineConfig({
  test: {
    environment: 'node',
    passWithNoTests: true,
    include: ['src/**/*.test.{ts,tsx}'],
    exclude: ['**/node_modules/**'],
  },
});
