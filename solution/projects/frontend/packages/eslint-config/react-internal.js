import js from "@eslint/js";
import eslintConfigPrettier from "eslint-config-prettier";
import tseslint from "typescript-eslint";
import pluginReactHooks from "eslint-plugin-react-hooks";
import { reactRecommended } from "./react-plugin.js";
import globals from "globals";
import { config as baseConfig } from "./base.js";

/**
 * A custom ESLint configuration for libraries that use React.
 *
 * @type {import("eslint").Linter.Config[]} */
export const config = [
  ...baseConfig,
  js.configs.recommended,
  eslintConfigPrettier,
  ...tseslint.configs.recommended,
  reactRecommended,
  {
    languageOptions: {
      ...reactRecommended.languageOptions,
      globals: {
        ...globals.serviceworker,
        ...globals.browser,
      },
    },
  },
  {
    plugins: {
      "react-hooks": pluginReactHooks,
    },
    settings: { react: { version: "detect" } },
    rules: {
      // Only the two classic rules. react-hooks 7's `recommended` also turns on
      // the React Compiler rules (set-state-in-effect, refs, immutability...),
      // which flag existing, working code as errors; adopting them is a
      // separate cleanup, not part of the eslint 10 upgrade.
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn",
      // React scope no longer necessary with new JSX transform.
      "react/react-in-jsx-scope": "off",
      // Same reasoning, for TypeScript: `react/prop-types` checks for a runtime
      // `propTypes` declaration, which is what a props TYPE already is here —
      // statically, and more completely. Left on, it reports every typed
      // component in the workspace as unvalidated, which trains readers to
      // scroll past the lint output rather than read it.
      "react/prop-types": "off",
    },
  },
];
