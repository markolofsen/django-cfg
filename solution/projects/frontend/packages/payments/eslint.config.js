/**
 * ESLint config for @djangocfg/payments.
 *
 * The package shipped `"lint": "eslint . --max-warnings 0"` with no config
 * file, so every run failed open: ESLint exits non-zero before linting a single
 * line, and `--max-warnings 0` — the strictest-looking flag here — was checking
 * nothing at all.
 *
 * That is the same failure `@djangocfg/layouts` hit, where an unexecuted
 * `react-hooks/rules-of-hooks` let a hook below an early return reach
 * production and white-screen on a 401 (React #310). This package renders
 * checkout forms and payment state behind exactly that kind of guard.
 */
import { config } from '@djangocfg/eslint-config/react-internal';

export default [
  ...config,
  {
    ignores: ['dist/**', 'node_modules/**'],
  },
  {
    // `scripts/` runs under Node, not in the browser: the shared preset defines
    // only browser globals, so `process` reads as undefined there. Declaring
    // the environment is the fix — disabling `no-undef` for the file would
    // also stop it catching a real typo.
    files: ['scripts/**/*.mjs'],
    languageOptions: {
      globals: { process: 'readonly', console: 'readonly' },
    },
  },
  {
    rules: {
      // A hook after an early return is a guaranteed crash the moment the guard
      // flips, so `error` is what this rule is. The shared preset loads
      // `eslint-plugin-only-warn` and downgrades it anyway — stating the real
      // severity here means dropping that plugin makes it bite, instead of
      // leaving a `warn` nobody re-reads. This package does run
      // `--max-warnings 0`, so it fails either way.
      'react-hooks/rules-of-hooks': 'error',
    },
  },
];
