/**
 * Shared Constants for DjangoCFG Next.js Configuration
 */

// Package name for version checks
export const PACKAGE_NAME = '@djangocfg/nextjs';

// Version cache TTL (1 hour)
export const VERSION_CACHE_TTL_MS = 60 * 60 * 1000;

// ASCII Art Banner for Django CFG
export const DJANGO_CFG_BANNER = `
██████╗      ██╗ █████╗ ███╗   ██╗ ██████╗  ██████╗      ██████╗███████╗ ██████╗
██╔══██╗     ██║██╔══██╗████╗  ██║██╔════╝ ██╔═══██╗    ██╔════╝██╔════╝██╔════╝
██║  ██║     ██║███████║██╔██╗ ██║██║  ███╗██║   ██║    ██║     █████╗  ██║  ███╗
██║  ██║██   ██║██╔══██║██║╚██╗██║██║   ██║██║   ██║    ██║     ██╔══╝  ██║   ██║
██████╔╝╚█████╔╝██║  ██║██║ ╚████║╚██████╔╝╚██████╔╝    ╚██████╗██║     ╚██████╔╝
╚═════╝  ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝      ╚═════╝╚═╝      ╚═════╝
`;

// All @djangocfg packages that can be updated together
export const DJANGOCFG_PACKAGES = [
  '@djangocfg/ui-core',
  '@djangocfg/layouts',
  '@djangocfg/nextjs',
  '@djangocfg/api',
  '@djangocfg/eslint-config',
  '@djangocfg/typescript-config',
] as const;

// Default packages to transpile
// Required for proper RSC (React Server Components) handling.
//
// Every widget is here because widgets ship SOURCE — `main` points at
// `./src/index.ts`, there is no build step, and an untranspiled `.ts` in
// node_modules is a syntax error at the app's first import, not a warning.
export const DEFAULT_TRANSPILE_PACKAGES = [
  '@djangocfg/i18n',
  '@djangocfg/ui-core',
  '@djangocfg/layouts',
  '@djangocfg/api',
  '@djangocfg/analytics',
  '@djangocfg/devtools',
  '@djangocfg/payments',
  '@djangocfg/widget-avatar',
  '@djangocfg/widget-charts',
  '@djangocfg/widget-chat',
  '@djangocfg/widget-chat-dev',
  '@djangocfg/widget-code',
  '@djangocfg/widget-data',
  '@djangocfg/widget-diagram',
  '@djangocfg/widget-editor',
  '@djangocfg/widget-forms',
  '@djangocfg/widget-kit',
  '@djangocfg/widget-map',
  '@djangocfg/widget-mcp',
  '@djangocfg/widget-media',
  '@djangocfg/widget-ogimage',
  '@djangocfg/widget-overlay',
  '@djangocfg/widget-player',
  '@djangocfg/widget-visual',
] as const;

// Default packages to optimize imports
export const DEFAULT_OPTIMIZE_PACKAGES = [
  '@djangocfg/ui-core',
  '@djangocfg/layouts',
  'lucide-react',
  'recharts',
] as const;
