/**
 * ESLint config for @djangocfg/analytics.
 *
 * The package shipped `"lint": "eslint ."` with no config file, so every run
 * exited non-zero before reading a line — identical output whether the code was
 * clean or broken, which reads as "lint is broken here" rather than as a
 * finding. The fifth instance of that pattern found in this workspace; see
 * packages/@dev/decisions/a-gate-that-cannot-fail-is-not-a-gate.md.
 */
import { config } from '@djangocfg/eslint-config/react-internal';

export default [
  ...config,
  {
    ignores: ['dist/**', 'node_modules/**'],
  },
  {
    rules: {
      // ERROR, not warn, for the reason recorded in @djangocfg/layouts' config:
      // a hook below an early return is a guaranteed production crash (React
      // #310), not a style nit.
      'react-hooks/rules-of-hooks': 'error',
    },
  },
];
