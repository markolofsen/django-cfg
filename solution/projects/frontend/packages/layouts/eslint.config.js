/**
 * ESLint config for @djangocfg/layouts.
 *
 * This package shipped `"lint": "eslint ."` with NO config file, so every lint
 * run failed open — `react-hooks/rules-of-hooks` had never actually executed
 * here. That is how a hook below an early return reached production and
 * white-screened my.cmdop.com/private/ with React #310 on a 401 (the guard is
 * statically dead in dev, so nothing caught it locally either).
 *
 * The shared react-internal preset already enables the react-hooks plugin;
 * this file just points the package at it.
 */
import { config } from '@djangocfg/eslint-config/react-internal';

export default [
  ...config,
  {
    // `@archive/**` matches the `@*` exclude in tsconfig.json: retired code kept
    // for reference, outside `src`, unreachable from every `exports` entry and
    // absent from `files`. Linting it asks for fixes to code that never runs and
    // hides the warnings that do matter among them.
    ignores: ['dist/**', 'node_modules/**', '@archive/**'],
  },
  {
    rules: {
      // ERROR, not warn: a hook after an early return is not a style nit — it
      // is a guaranteed production crash the moment the guard flips (React
      // #310), and it can be invisible in dev when the guard depends on
      // NODE_ENV. A warning would not fail CI, which is how this shipped.
      'react-hooks/rules-of-hooks': 'error',
    },
  },
];
