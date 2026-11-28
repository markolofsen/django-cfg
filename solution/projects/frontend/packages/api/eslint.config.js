/**
 * ESLint config for @djangocfg/api.
 *
 * This package had neither a config file nor a `lint` script, so it was absent
 * from `turbo lint` entirely — not failing, not passing, just not there. That
 * is quieter than the three packages whose lint failed open, and worse: a
 * package that never appears in the output never prompts the question.
 *
 * The react-internal preset applies because this package ships hooks
 * (`useGithubAuth`, `useTwoFactorVerify`, the storage hooks); its
 * `react-hooks/*` rules are the ones that matter here.
 */
import { config } from '@djangocfg/eslint-config/react-internal';

export default [
  ...config,
  {
    /*
     * `_api/generated/**` is written by `make gen` (openapi_processor / ts.tool)
     * and every file in it says DO NOT EDIT. Linting it asks for fixes that the
     * next generator run deletes, and its ~13 `any` would bury the same number
     * of hand-written ones in the noise. If those matter, the fix belongs in the
     * generator, not here.
     *
     * The rest of `src/` is hand-written and is linted normally — including the
     * hooks that consume the generated client.
     */
    ignores: ['dist/**', 'node_modules/**', 'src/_api/generated/**'],
  },
  {
    rules: {
      // ERROR, not warn, for the reason recorded in @djangocfg/layouts' config:
      // a hook below an early return is a guaranteed production crash (React
      // #310), not a style nit. Auth hooks are exactly where an early return
      // guards on a token and flips in production but not in dev.
      'react-hooks/rules-of-hooks': 'error',
    },
  },
];
