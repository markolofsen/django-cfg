import js from "@eslint/js";
import eslintConfigPrettier from "eslint-config-prettier";
import turboPlugin from "eslint-plugin-turbo";
import tseslint from "typescript-eslint";

/**
 * A shared ESLint configuration for the repository.
 *
 * `eslint-plugin-only-warn` used to sit at the bottom of this array, rewriting
 * every rule's severity to "warn". Combined with only 1 of the 25 members that
 * lint passing `--max-warnings 0`, it meant no lint run in this workspace could
 * fail — including `rules-of-hooks`, which `layouts` and `api` deliberately
 * raise to "error" because a hook below an early return is React #310 in
 * production. Removed 2026-09-09; the severities below are now the real ones.
 *
 * @type {import("eslint").Linter.Config[]}
 * */
export const config = [
  js.configs.recommended,
  eslintConfigPrettier,
  ...tseslint.configs.recommended,
  {
    plugins: {
      turbo: turboPlugin,
    },
    rules: {
      // "error": an env var outside the cache key means turbo can hand back a
      // build made with a different value — a wrong artifact that looks cached
      // and correct. `NEXT_PUBLIC_*` is inlined at build time, so this is not
      // hypothetical.
      "turbo/no-undeclared-env-vars": "error",
    },
  },
  {
    rules: {
      // "error", because this is not style: it found a `startTime` in `nextjs`'s
      // health route that was captured and never reported, dropping the duration
      // the endpoint was meant to return.
      //
      // The ignore patterns encode how this repo already writes "deliberately
      // unused" — an interface method that must keep its signature, a caught
      // error nobody inspects. Without them the convention itself reports as a
      // finding, making the intended spelling the failing one.
      "@typescript-eslint/no-unused-vars": [
        "error",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
          caughtErrorsIgnorePattern: "^_",
          destructuredArrayIgnorePattern: "^_",
        },
      ],
    },
  },
  {
    // Design-system token hygiene: forbid raw Tailwind color-scale classes
    // (bg-amber-500, text-emerald-600, border-red-500/40, …) in className /
    // class strings. The styles guide mandates SEMANTIC tokens — success /
    // warning / destructive / info, muted / foreground / border / primary,
    // and the chart palette (chart-1..5) for categorical data — so colors
    // adapt across themes + presets. Raw scales break that silently.
    //
    // Enforced via no-restricted-syntax on string + template literals. The
    // regex deliberately EXCLUDES the semantic families and the chart
    // palette; if you hit a genuine exception (a brand hex in an SVG logo,
    // a decorative non-status color with no token), disable on that line
    // with a reason.
    files: ["**/*.{ts,tsx,js,jsx}"],
    rules: {
      // "error": a raw color scale does not adapt to theme or preset, and the
      // failure is invisible — the component just renders the wrong color in
      // dark mode. Genuine exceptions disable on the line with a reason.
      "no-restricted-syntax": [
        "error",
        {
          selector:
            "Literal[value=/(bg|text|border|ring|fill|stroke|from|to|via|divide|outline|decoration|accent|caret|shadow)-(red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose|slate|gray|zinc|neutral|stone)-[0-9]/]",
          message:
            "Raw Tailwind color scale — use a semantic token (success/warning/destructive/info, muted/foreground/border/primary, chart-1..5). See ui-core styles README. Disable on this line with a reason only for a genuine exception (brand hex / decorative no-token color).",
        },
        {
          selector:
            "TemplateElement[value.raw=/(bg|text|border|ring|fill|stroke|from|to|via|divide|outline|decoration|accent|caret|shadow)-(red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose|slate|gray|zinc|neutral|stone)-[0-9]/]",
          message:
            "Raw Tailwind color scale — use a semantic token (success/warning/destructive/info, muted/foreground/border/primary, chart-1..5). See ui-core styles README.",
        },
      ],
    },
  },
  {
    ignores: ["dist/**"],
  },
];
