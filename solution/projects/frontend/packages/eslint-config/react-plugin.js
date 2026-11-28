import { fixupPluginRules } from "@eslint/compat";
import pluginReact from "eslint-plugin-react";

/**
 * eslint-plugin-react@7.37.5 (the latest release) still calls
 * `context.getFilename()`, `getSourceCode()` etc., which ESLint 10 removed, so
 * every `react/*` rule crashes with "contextOrFilename.getFilename is not a
 * function". `fixupPluginRules` puts those context methods back. Drop the shim
 * once eslint-plugin-react ships an ESLint 10 release (peer range is `^9.7`).
 */
export const reactPlugin = fixupPluginRules(pluginReact);

/** `plugin:react/recommended` as a flat config entry using the patched plugin. */
export const reactRecommended = {
  ...pluginReact.configs.flat.recommended,
  plugins: { react: reactPlugin },
};
