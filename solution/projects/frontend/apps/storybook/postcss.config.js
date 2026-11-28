/**
 * Storybook PostCSS config.
 *
 * Tailwind v4 wiring — must be CommonJS .js (not .mjs) and use the object
 * plugin form. See @plans/plan1-storybook/reports/04-tailwind-v4-storybook.md
 * — issue storybookjs/storybook#31373.
 *
 * No `autoprefixer` here: Tailwind v4 ships its own prefixing pipeline, and
 * the rest of the monorepo (apps/playground/postcss.config.js etc.) does not
 * use it either.
 */
module.exports = {
  plugins: {
    '@tailwindcss/postcss': {},
  },
};
