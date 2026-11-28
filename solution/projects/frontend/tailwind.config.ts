import type { Config } from 'tailwindcss'

/**
 * Tailwind CSS v4 Configuration
 *
 * IMPORTANT: This config ONLY defines content paths for monorepo.
 * Theme, colors, plugins are defined in CSS files (not here).
 *
 * Tailwind v4 uses CSS-first configuration:
 * - Theme: defined in packages/ui/src/styles/theme.css via CSS variables
 * - Plugins: not needed (animations in CSS)
 * - Content: defined here to scan monorepo packages
 */
export default {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    '@djangocfg/ui-core/src/**/*.{js,ts,jsx,tsx,mdx}',
    '@djangocfg/ui-nextjs/src/**/*.{js,ts,jsx,tsx,mdx}',
    '@djangocfg/layouts/src/**/*.{js,ts,jsx,tsx,mdx}',
    // Widgets ship source, so their classes are only in `src/`. One glob
    // rather than sixteen entries: a new widget is picked up without a config
    // change, and a missed one is a class silently absent at runtime.
    './widgets/*/src/**/*.{js,ts,jsx,tsx,mdx}',
    './apps/storybook/stories/**/*.{ts,tsx,mdx}',
    './apps/storybook/.storybook/**/*.{ts,tsx}',
  ],
} satisfies Config
