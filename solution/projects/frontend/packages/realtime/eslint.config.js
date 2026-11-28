import { config } from '@djangocfg/eslint-config/react-internal';

export default [
  ...config,
  {
    ignores: ['dist/**', 'node_modules/**'],
  },
  {
    rules: {
      // A hook below an early return crashes in production (React #310).
      'react-hooks/rules-of-hooks': 'error',
    },
  },
];
