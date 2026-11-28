import { defineConfig } from 'tsup';

export default defineConfig({
  entry: {
    index: 'src/index.ts',
    'sitemap/index': 'src/sitemap/index.ts',
    'health/index': 'src/health/index.ts',
    'human-check/index': 'src/human-check/index.ts',
    'og-image/index': 'src/og-image/index.ts',
    // App icons: the pure element (also usable in a client bundle) and the `next/og` route factory, separate chunks.
    'app-icon/index': 'src/app-icon/index.ts',
    'app-icon/next': 'src/app-icon/next.ts',
    'navigation/index': 'src/navigation/index.ts',
    'config/index': 'src/config/index.ts',
    'auth/index': 'src/auth/index.ts',
    // Edge middleware (imports next/server only; keep it apart from `auth`, which reads next/headers).
    'auth/middleware': 'src/auth/middleware.ts',
    'ai/index': 'src/ai/index.ts',
    'ai/cli': 'src/ai/cli.ts',
    'pwa/index': 'src/pwa/index.ts',
    // Manifest generator shipped as its OWN chunk so a Next `app/manifest.ts`
    // route can import `createManifest` without pulling in `plugin.ts`, which
    // references `@serwist/next` via `createRequire`. Turbopack statically
    // traces that reference and chokes on serwist's `new URL(".", import.meta.url)`,
    // failing the whole build. Keeping manifest serwist-free sidesteps it.
    'pwa/manifest': 'src/pwa/manifest.ts',
    'pwa/worker/index': 'src/pwa/worker/index.ts',
    // monitor module
    'monitor/index': 'src/monitor/index.ts',
    // i18n module
    'i18n/index': 'src/i18n/index.ts',
    'i18n/server': 'src/i18n/server.ts',
    'i18n/client': 'src/i18n/client.ts',
    'i18n/proxy': 'src/i18n/proxy.ts',
    'i18n/navigation': 'src/i18n/navigation.ts',
    'i18n/routing': 'src/i18n/routing.ts',
    'i18n/request': 'src/i18n/request.ts',
    'i18n/plugin': 'src/i18n/plugin.ts',
    'i18n/provider': 'src/i18n/provider.tsx',
    'i18n/components': 'src/i18n/components/index.ts',
  },
  format: ['esm'],
  dts: true,
  splitting: false,
  sourcemap: true,
  clean: true,
  external: [
    'react',
    'react-dom',
    'next',
    'next/navigation',
    'next/server',
    'next/og',
    'next-intl',
    'next-intl/server',
    'next-intl/routing',
    'next-intl/navigation',
    'next-intl/plugin',
    'next-intl/middleware',
    '@djangocfg/api',
    '@djangocfg/i18n',
    '@djangocfg/layouts',
    '@djangocfg/devtools',
    '@djangocfg/devtools/server',
    '@djangocfg/ui-core',
    '@djangocfg/ui-core/components',
    'lucide-react',
    '@core/settings',
  ],
  esbuildOptions(options) {
      // Don't inline process.env.NODE_ENV — let consumer (Next.js) handle it
      options.define = { ...options.define, 'process.env.NODE_ENV': 'process.env.NODE_ENV' };
    options.jsx = 'automatic';
    options.jsxDev = false;
  },
});

