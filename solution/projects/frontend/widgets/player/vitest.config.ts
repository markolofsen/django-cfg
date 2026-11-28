import { defineConfig } from "vitest/config";

/**
 * `@sources/` holds four reference repositories, each with its own test suite
 * and dependency tree. Vitest's default include would collect them and report
 * failures that say nothing about our code.
 */
export default defineConfig({
  test: {
    include: ["src/**/*.test.ts", "src/**/*.test.tsx"],
    exclude: ["**/node_modules/**", "@sources/**"],
  },
});
