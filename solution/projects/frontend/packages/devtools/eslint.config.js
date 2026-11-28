/**
 * ESLint config for @djangocfg/devtools.
 *
 * The package shipped `"lint": "eslint ."` with no config file, so every run
 * failed open — ESLint exits non-zero before linting anything, and a script
 * that always fails is read as "lint is broken here" rather than as a finding.
 *
 * See `@djangocfg/layouts`'s config for what the unexecuted
 * `react-hooks/rules-of-hooks` cost the last time this state went unnoticed.
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
