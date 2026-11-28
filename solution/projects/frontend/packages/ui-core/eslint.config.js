/**
 * ESLint config for @djangocfg/ui-core.
 *
 * The package shipped `"lint": "eslint ."` with no config file, so every run
 * failed open — ESLint exits before linting a line, and a script that always
 * fails reads as "lint is broken here" rather than as a finding.
 *
 * It matters most in this package. The token-hygiene rule in the shared base
 * preset (no raw Tailwind colour scales — semantic tokens only) exists to keep
 * components theme-correct, and ui-core is where those components live. The
 * rule has never executed over any of them.
 *
 * See `@djangocfg/layouts`'s config for what the same silence cost there: an
 * unexecuted `react-hooks/rules-of-hooks` let a hook below an early return
 * reach production and white-screen on a 401 (React #310).
 */
import { config } from '@djangocfg/eslint-config/react-internal';

export default [
  ...config,
  {
    ignores: ['dist/**', 'node_modules/**'],
  },
  {
    rules: {
      // Stated as `error` deliberately, though the shared preset loads
      // `eslint-plugin-only-warn` and downgrades it: the severity here records
      // what this rule IS, so removing that plugin makes it bite rather than
      // leaving it a warning nobody re-reads.
      'react-hooks/rules-of-hooks': 'error',
    },
  },
];
