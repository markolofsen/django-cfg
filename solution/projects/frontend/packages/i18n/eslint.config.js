/**
 * ESLint config for @djangocfg/i18n.
 *
 * Shipped `"lint": "eslint ."` with no config file, so every run exited
 * non-zero before reading a line — the same failing-open pattern recorded in
 * packages/@dev/decisions/a-gate-that-cannot-fail-is-not-a-gate.md.
 */
import { config } from '@djangocfg/eslint-config/react-internal';

export default [
  ...config,
  {
    ignores: ['dist/**', 'node_modules/**'],
  },
];
