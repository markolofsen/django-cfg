import { defineConfig } from 'vitest/config';

/**
 * Node environment. Nothing here has tests yet — the group arrived from
 * ui-tools with none — so this config exists to make adding one a one-file
 * change rather than a decision.
 */
export default defineConfig({
  test: {
    environment: 'node',
    include: ['src/**/*.test.{ts,tsx}'],
    exclude: ['**/node_modules/**'],
  },
});
