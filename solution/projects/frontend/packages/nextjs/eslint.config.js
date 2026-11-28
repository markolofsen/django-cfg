/**
 * ESLint config for @djangocfg/nextjs.
 *
 * Shipped `"lint": "eslint ."` with no config file, so every run exited
 * non-zero before reading a line — the same failing-open pattern recorded in
 * packages/@dev/decisions/a-gate-that-cannot-fail-is-not-a-gate.md.
 */
import { config } from '@djangocfg/eslint-config/react-internal';

export default [
  ...config,
  {
    // `@sources/**` matches the `@*` exclude in tsconfig.json: vendored copies
    // of upstream projects (serwist, vercel-og) kept for reference, absent from
    // `files`, unreachable from every `exports` entry. Linting them asks for
    // fixes to other people's code and buried this package's own warnings —
    // 40 `no-unknown-property` alone, all in vendored SVG markup.
    ignores: ['dist/**', 'node_modules/**', '@sources/**'],
  },
];
