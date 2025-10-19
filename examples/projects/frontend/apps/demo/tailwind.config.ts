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
    '../../packages/ui/src/**/*.{js,ts,jsx,tsx,mdx}',
    '../../packages/layouts/src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
} satisfies Config
