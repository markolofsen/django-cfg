import { defineConfig } from 'vitest/config';

/**
 * Node environment on purpose: everything here is pure or renders to a string.
 * A jsdom would only hide a regression that reached for the DOM from a
 * formatter. The one behaviour that needs a document, the copy click, is
 * pinned where a host mounts the block (`widget-chat`'s `code-copy.test.tsx`).
 */
export default defineConfig({
  test: {
    environment: 'node',
    include: ['src/**/*.test.{ts,tsx}'],
    exclude: ['**/node_modules/**'],
  },
});
