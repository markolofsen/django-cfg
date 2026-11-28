import { defineConfig } from 'vitest/config';

/**
 * Node environment: the tested surface is the pure half — geometry helpers,
 * layer factories, the geocode resolver. The MapLibre components are not
 * unit-testable without a WebGL context, and a jsdom would only make a test
 * that reached for one fail somewhere less obvious.
 */
export default defineConfig({
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts'],
    exclude: ['**/node_modules/**'],
  },
});
