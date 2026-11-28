import { defineConfig } from 'vitest/config';

/**
 * Node environment: the tests are the pure half of speech recognition — the
 * reducer, the transcript assembly, language search and id generation. The
 * engine itself is a browser API no test environment provides.
 */
export default defineConfig({
  test: {
    environment: 'node',
    include: ['src/**/__tests__/**/*.test.{ts,tsx}', 'src/**/*.test.{ts,tsx}'],
    exclude: ['**/node_modules/**'],
  },
});
