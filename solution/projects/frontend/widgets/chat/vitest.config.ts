import { defineConfig } from "vitest/config";

/**
 * Two projects, because two kinds of code live here.
 *
 * `chat`: no environment is declared. `core/**` is DOM-free by design, and the
 * `.tsx` tests assert on rendered strings rather than on a tree. Adding jsdom
 * would hide a regression that reached for the DOM from the reducer.
 *
 * `page`: jsdom. The page-snapshot capture engine and the highlight overlay ARE
 * DOM code — walking a document, computing accessible names, resolving a
 * locator — so their tests need a document. Kept to `src/page-tooling` so the
 * rest of the package stays headless.
 */
const PAGE = ["src/page-tooling"];

export default defineConfig({
  test: {
    projects: [
      {
        test: {
          name: "chat",
          include: ["src/**/*.test.ts", "src/**/*.test.tsx"],
          exclude: ["**/node_modules/**", ...PAGE.map((dir) => `${dir}/**`)],
        },
      },
      {
        test: {
          name: "page",
          globals: true,
          environment: "jsdom",
          include: PAGE.flatMap((dir) => [`${dir}/**/*.test.ts`, `${dir}/**/*.test.tsx`]),
          exclude: ["**/node_modules/**"],
        },
      },
    ],
  },
});
