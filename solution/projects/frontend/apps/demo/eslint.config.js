/**
 * ESLint config for the demo app.
 *
 * `next lint` was removed in Next 16 (this app is on 16.2.10), and the script
 * still called it — so `pnpm lint` here failed with "Invalid project directory
 * provided, no such directory: .../apps/demo/lint": Next was reading `lint` as
 * a path argument. Identical output whether the code was clean or broken, which
 * is the failing-open pattern recorded in
 * packages/@dev/decisions/a-gate-that-cannot-fail-is-not-a-gate.md.
 *
 * A second config, `eslint.config.mjs`, sat beside this one until 2026-09-09
 * turning `no-explicit-any`, `no-unused-vars` and `exhaustive-deps` off. ESLint
 * prefers `.js`, so it had been dead since this file appeared — but reading it
 * gave the opposite impression of what the app actually enforces. Deleted.
 */
import { nextJsConfig } from '@djangocfg/eslint-config/next-js';

export default [
  ...nextJsConfig,
  {
    /*
     * `app/_lib/api/generated/**` is written by `make api` and says DO NOT EDIT.
     * Same call as `packages/api`: fixes here are deleted by the next generator
     * run, and its 27 warnings would bury the 3 hand-written ones. If they
     * matter, the fix belongs in the generator.
     */
    ignores: [
      '.next/**',
      'node_modules/**',
      'next-env.d.ts',
      'app/_lib/api/generated/**',
    ],
  },
  {
    /*
     * PostCSS loads its config through Node's CJS require, so `module.exports`
     * is correct there — the app has no `"type": "module"`. Without this, the
     * shared config parses it as ESM and reports `'module' is not defined`.
     */
    files: ['postcss.config.js'],
    languageOptions: {
      globals: { module: 'writable' },
      sourceType: 'commonjs',
    },
  },
];
