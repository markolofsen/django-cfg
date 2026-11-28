import { defineConfig } from 'vitest/config';

/**
 * Node environment: what is tested here is the pure half — URL and file-path
 * detection, the paste rule, the mention presets. The editors themselves need
 * a ProseMirror document a unit test cannot usefully stand up.
 */
export default defineConfig({
  test: {
    environment: 'node',
    include: ['src/**/__tests__/**/*.test.{ts,tsx}', 'src/**/*.test.{ts,tsx}'],
    exclude: ['**/node_modules/**'],
  },
});
