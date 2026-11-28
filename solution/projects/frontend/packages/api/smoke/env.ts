/**
 * The build-time environment the smoke suite's "bundle" is built with.
 *
 * `vitest.smoke.config.ts` writes these values into the literal `process.env.NEXT_PUBLIC_*` reads of `src/`, as
 * Next.js does when it builds a page. Every other `NEXT_PUBLIC_*` name becomes `undefined`. The process
 * environment itself holds none of them while a case runs (`harness.resetPage`), so a runtime that reads the
 * environment any other way sees nothing, just as it would in a browser.
 */
export const SMOKE_BUILD_ENV = {
  NEXT_PUBLIC_API_URL: 'https://api.env.test',
} as const;
