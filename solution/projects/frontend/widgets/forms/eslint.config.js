/**
 * ESLint config for the `forms` widget.
 *
 * Widgets shipped no config and no `lint` script, so `turbo lint` skipped this
 * package entirely — a clean run that had never read a line of it.
 */
import { config } from '@djangocfg/eslint-config/react-internal';

export default [
  ...config,
  {
    ignores: ['dist/**', 'node_modules/**'],
  },
  {
    rules: {
      // ERROR, not warn: a hook called outside a component's render — below an
      // early return, or inside a plain callback — is a production crash
      // (React #310), not a style nit.
      'react-hooks/rules-of-hooks': 'error',
    },
  },
];
