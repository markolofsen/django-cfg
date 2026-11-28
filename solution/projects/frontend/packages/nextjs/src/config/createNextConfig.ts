/**
 * Base Next.js Configuration Factory
 *
 * Universal, reusable Next.js config for all DjangoCFG projects
 * Provides standard settings that can be extended per project
 *
 * @example
 * ```typescript
 * // In your project's next.config.ts
 * import { createBaseNextConfig } from '@djangocfg/nextjs/config';
 * import bundleAnalyzer from '@next/bundle-analyzer';
 *
 * const withBundleAnalyzer = bundleAnalyzer({
 *   enabled: process.env.ANALYZE === 'true',
 * });
 *
 * export default withBundleAnalyzer(createBaseNextConfig({
 *   // Your project-specific overrides
 *   transpilePackages: ['my-custom-package'],
 * }));
 * ```
 */

import type { NextConfig } from 'next';
import type { Configuration as WebpackConfig } from 'webpack';

import { type I18nPluginOptions, withI18n } from '../i18n/plugin';
import { type PWAPluginOptions, withPWA } from '../pwa/plugin';
import { DEFAULT_OPTIMIZE_PACKAGES, DEFAULT_TRANSPILE_PACKAGES } from './constants';
import { CSP_BASELINE_VENDORS, type CspVendor, resolveCspVendors } from './csp';
import { addCompressionPlugins } from './plugins/compression';
import { DevStartupPlugin } from './plugins/devStartup';
import { deepMerge } from './utils/deepMerge';
import {
  getApiUrl,
  getBasePath,
  getSiteUrl,
  isDev,
  isStaticBuild,
  warnIfApiUrlMissing,
} from './utils/env';

// ─────────────────────────────────────────────────────────────────────────
// Configuration Options
// ─────────────────────────────────────────────────────────────────────────

/**
 * Second argument Next.js passes to the `webpack` hook. Derived from Next's own
 * signature rather than re-declared, so it tracks upstream.
 */
type WebpackContext = Parameters<NonNullable<NextConfig['webpack']>>[1];

/**
 * DjangoCFG-specific options. Every other Next.js option passes through via the
 * `NextConfig` half of `BaseNextConfigOptions`; the keys redeclared here are
 * omitted from it because this package narrows or re-purposes them.
 */
interface DjangoCfgNextOptions {
  /** Additional transpile packages (merged with defaults) */
  transpilePackages?: string[];
  /** Additional optimize package imports (merged with defaults) */
  optimizePackageImports?: string[];
  /** Check for @djangocfg/* package updates on startup (default: true) */
  checkUpdates?: boolean;
  /** Auto-update outdated packages without prompting (default: false) */
  autoUpdate?: boolean;
  /** Force check workspace:* packages for updates (for testing in monorepo) */
  forceCheckWorkspace?: boolean;
  /** Check for missing optional packages on startup (default: true) */
  checkPackages?: boolean;
  /** Auto-install missing packages without prompting (default: false) */
  autoInstall?: boolean;
  /**
   * Allow embedding this app in iframe from specified origins
   * Set to ['*'] to allow all origins, or specify domains like ['https://djangocfg.com']
   */
  allowIframeFrom?: string[];
  /**
   * Loosen the baseline CSP just enough for Stripe.js / Stripe Checkout &
   * Elements to work. When true, the required Stripe origins are added to
   * `script-src` (js.stripe.com — loads the SDK), `frame-src`
   * (js.stripe.com + checkout.stripe.com — Elements/Checkout mount iframes)
   * and `connect-src` (api.stripe.com — tokenization/confirm XHR). Without
   * this, the browser blocks Stripe.js and the payment form never renders.
   * Enable ONLY on apps that actually mount Stripe (e.g. the billing
   * dashboard), so every other app keeps the tighter default. Default: false.
   */
  stripe?: boolean;
  /**
   * Content-Security-Policy control.
   *
   * - `false` — do not emit the `Content-Security-Policy` header at all.
   *   Use this on apps with no user auth/payment surface and unpredictable
   *   third-party embeds (a pitch deck, a marketing microsite) where
   *   naming every future embed's origin is not worth the maintenance —
   *   `X-Content-Type-Options`/`Referrer-Policy`/`X-Frame-Options` below
   *   still apply.
   * - object — keep the baseline CSP but additively loosen it. Prefer
   *   `vendors` (declare WHAT you use by name; the package owns which origins
   *   that implies) over hand-listing origins per directive. Every array is
   *   additive; omit a key to leave that directive untouched.
   * - omitted — tightest default (`frame-src 'self'`, etc.), same as today.
   *
   * **Scripts nothing in this file can see are already handled.** Cloudflare
   * Web Analytics (injected at the edge) and Google Analytics (injected at
   * runtime by `BaseApp analytics={{ googleTrackingId }}`) are both switched on
   * outside `next.config.ts`, so their origins are in the baseline and you do
   * NOT need to list them — see `CSP_BASELINE_VENDORS`. Turn them off with
   * `baseline: false`.
   *
   * @example
   * ```ts
   * // Declare the third parties this app actually uses — origins come from
   * // the shared registry, so a vendor host change is fixed in one place.
   * // (Cloudflare + GA are already in the baseline; no need to list them.)
   * createBaseNextConfig({ csp: { vendors: ['stripe'] } })
   *
   * // Escape hatch for something not in the registry yet
   * createBaseNextConfig({ csp: { frameSrc: ['https://www.youtube-nocookie.com'] } })
   *
   * // No CSP at all — simplest option for a low-risk app with ad hoc embeds
   * createBaseNextConfig({ csp: false })
   * ```
   */
  csp?:
    | false
    | {
        /**
         * Named third-party vendors this app uses (`'stripe'`, `'cloudflare'`,
         * `'google-analytics'`, …). Each expands to the exact origins that
         * vendor needs across the relevant directives. See `CSP_VENDOR_PRESETS`
         * for the full list. Unknown names warn at build time, never throw.
         */
        vendors?: (CspVendor | (string & {}))[];
        /**
         * Drop the baseline vendors (see `CSP_BASELINE_VENDORS`: Cloudflare Web
         * Analytics + Google Analytics). They are on by default because each is
         * switched on somewhere `next.config.ts` cannot read — the Cloudflare
         * beacon is injected at the edge, and gtag.js is injected at runtime by
         * `BaseApp analytics={{ googleTrackingId }}` — so an opt-in flag would
         * only ever be discovered as a production console error.
         *
         * Set `false` for an app you know mounts neither, to get back the
         * tightest `script-src`.
         * @default true
         */
        baseline?: boolean;
        /** Extra `frame-src` origins (iframes this app embeds). */
        frameSrc?: string[];
        /** Extra `script-src` origins (third-party SDK scripts). */
        scriptSrc?: string[];
        /** Extra `connect-src` origins (XHR/fetch/WebSocket to a third party). */
        connectSrc?: string[];
        /** Extra `img-src` origins (hotlinked third-party images). */
        imgSrc?: string[];
        /** Extra `font-src` origins (third-party web fonts). */
        fontSrc?: string[];
      };
  /**
   * PWA configuration options
   * Set to false to disable PWA, or provide custom options
   * @default { enabled: true (in production), disable: true (in development) }
   */
  pwa?: PWAPluginOptions | false;
  /**
   * i18n configuration options for internationalization
   * Enables URL-based locale routing (e.g., /en/about, /ru/about)
   *
   * @example
   * ```ts
   * i18n: {
   *   locales: ['en', 'ru', 'ko'],
   *   defaultLocale: 'en',
   * }
   * ```
   */
  i18n?: I18nPluginOptions;
  /** Turbopack configuration (Next.js 16+ default bundler) */
  turbopack?: NextConfig['turbopack'];
  /** Custom webpack configuration function (called after base webpack logic) */
  webpack?: (
    config: WebpackConfig,
    options: WebpackContext
  ) => WebpackConfig | void;
  /** Custom experimental options (merged with defaults) */
  experimental?: NextConfig['experimental'];
  /** Custom env variables (merged with defaults) */
  env?: Record<string, string | undefined>;
  /** Additional redirects (merged with base URL normalization redirects) */
  redirects?: NextConfig['redirects'];
  /** Additional headers (merged with base CORS/security headers) */
  headers?: NextConfig['headers'];
  /** Additional rewrites */
  rewrites?: NextConfig['rewrites'];
}

/**
 * DjangoCFG options plus every remaining Next.js config option.
 */
export type BaseNextConfigOptions = DjangoCfgNextOptions &
  Omit<NextConfig, keyof DjangoCfgNextOptions>;

// ─────────────────────────────────────────────────────────────────────────
// Base Configuration Factory
// ─────────────────────────────────────────────────────────────────────────

/**
 * Create base Next.js configuration with standard DjangoCFG settings
 *
 * @param options - Custom configuration options to merge with base config
 * @returns Next.js configuration function
 */
export function createBaseNextConfig(
  options: BaseNextConfigOptions = {}
): NextConfig {

  const basePath = getBasePath();
  warnIfApiUrlMissing();
  const apiUrl = getApiUrl();
  const siteUrl = getSiteUrl();

  // Base configuration
  const baseConfig: NextConfig = {
    reactStrictMode: true,
    trailingSlash: true,

    // Dev indicator position — set explicitly so it's managed from one place
    // across every @djangocfg app. Apps can override via `devIndicators` in
    // their options (deep-merged over this). Kept bottom-left for now.
    devIndicators: { position: 'bottom-left' },

    // Static export configuration
    ...(isStaticBuild && {
      output: 'export' as const,
      distDir: 'out',
      basePath: basePath,
      // Fix for Next.js 15.5.4: prevent 500.html generation issue
      generateBuildId: async () => {
        return 'static-build';
      },
    }),

    // Standalone output for Docker (only in production, not dev)
    ...(!isStaticBuild && !isDev && {
      output: 'standalone' as const,
    }),

    // Environment variables
    env: {
      NEXT_PUBLIC_BASE_PATH: basePath,
      NEXT_PUBLIC_API_URL: apiUrl,
      NEXT_PUBLIC_SITE_URL: siteUrl,
      // Disable Next.js telemetry (Next.js 15+ uses env var instead of config option)
      NEXT_TELEMETRY_DISABLED: '1',
      ...options.env,
    },

    // Images configuration
    images: {
      unoptimized: true,
    },

    // CORS headers for static files and iframe embedding
    async headers() {
      const headers: { source: string; headers: { key: string; value: string }[] }[] = [
        {
          source: '/static/:path*',
          headers: [
            { key: 'Access-Control-Allow-Origin', value: '*' },
            { key: 'Access-Control-Allow-Methods', value: 'GET, OPTIONS' },
            { key: 'Access-Control-Allow-Headers', value: 'Origin, Content-Type, Accept' },
          ],
        },
      ];

      // ── Baseline security headers on every route ──────────────────────────
      // First line of defence against XSS/clickjacking/sniffing. The CSP here is
      // a PRAGMATIC baseline: it kills the high-value injection vectors
      // (plugins/objects, <base> hijacking, form-action exfiltration, iframe
      // embedding) while still allowing the inline/eval scripts a Next.js app
      // needs in dev. A fully strict nonce-based `script-src` is a follow-up
      // (needs middleware + per-request nonce wiring) — tracked in the
      // auth-hardening plan. `allowIframeFrom` (below) overrides frame-ancestors.
      const hasIframeAllowlist =
        !!options.allowIframeFrom && options.allowIframeFrom.length > 0;
      const frameAncestors = hasIframeAllowlist
        ? (options.allowIframeFrom!.includes('*')
            ? '*'
            : `'self' ${options.allowIframeFrom!.join(' ')}`)
        : "'none'";

      // `csp: false` opts an app out of the CSP header entirely (see the
      // option's doc comment) — the other baseline headers still apply.
      const cspDisabled = options.csp === false;
      const cspExtra = typeof options.csp === 'object' ? options.csp : undefined;

      // In dev the backend (Django) is plain http/ws on localhost,
      // so connect/img must allow http:/ws:. Production stays strict (https/wss
      // only) to forbid downgrade/cleartext exfiltration.
      //
      // Third-party origins come from the shared vendor registry (./csp), so
      // "which hosts does Stripe need" is answered in exactly one place. The
      // legacy `stripe: true` flag is just sugar for `vendors: ['stripe']` and
      // resolves through that same registry — no second copy of the origins.
      // Baseline vendors apply unless explicitly opted out. They are baseline
      // rather than per-app because each is enabled somewhere this file cannot
      // read — Cloudflare's beacon is injected by the edge after this header is
      // emitted, and gtag.js is injected at runtime by `BaseApp analytics={{
      // googleTrackingId }}` from the app's settings.ts. Leaving either opt-in
      // guarantees a silent production breakage in every app that forgets it
      // (which was all of them). See CSP_BASELINE_VENDORS for the full rule.
      const vendorNames = [
        ...(cspExtra?.baseline === false ? [] : CSP_BASELINE_VENDORS),
        ...(options.stripe ? ['stripe'] : []),
        ...(cspExtra?.vendors ?? []),
      ];
      const vendor = resolveCspVendors(vendorNames);

      // Vendor-derived origins and the per-directive escape hatch are equivalent
      // and additive; a host named by both is emitted once.
      const join = (...groups: (string[] | undefined)[]) => {
        const all = [...new Set(groups.flatMap((g) => g ?? []))];
        return all.length ? ' ' + all.join(' ') : '';
      };

      const extraScript = join(vendor.scriptSrc, cspExtra?.scriptSrc);
      const extraConnect = join(vendor.connectSrc, cspExtra?.connectSrc);
      const extraFrame = join(vendor.frameSrc, cspExtra?.frameSrc);
      const extraImg = join(vendor.imgSrc, cspExtra?.imgSrc);
      const extraFont = join(vendor.fontSrc, cspExtra?.fontSrc);

      const connectSrc = isDev
        ? `connect-src 'self' http: https: ws: wss:${extraConnect}`
        : `connect-src 'self' https: wss:${extraConnect}`;
      const imgSrc = isDev
        ? `img-src 'self' data: blob: http: https:${extraImg}`
        : `img-src 'self' data: blob: https:${extraImg}`;

      if (!cspDisabled) {
        const cspDirectives = [
          "default-src 'self'",
          // Next.js requires inline + eval for its runtime/HMR. Tighten to nonces later.
          `script-src 'self' 'unsafe-inline' 'unsafe-eval'${extraScript}`,
          "style-src 'self' 'unsafe-inline'",
          imgSrc,
          `font-src 'self' data:${extraFont}`,
          // API calls go cross-origin to Django.
          connectSrc,
          // Declared vendors (Stripe Elements/Checkout, video embeds…) and any
          // app-declared trusted origins mount iframes; add their hosts here.
          `frame-src 'self'${extraFrame}`,
          "object-src 'none'",
          "base-uri 'self'",
          "form-action 'self'",
          `frame-ancestors ${frameAncestors}`,
        ];

        headers.push({
          source: '/:path*',
          headers: [
            { key: 'X-Content-Type-Options', value: 'nosniff' },
            { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
            { key: 'Content-Security-Policy', value: cspDirectives.join('; ') },
            // X-Frame-Options for older browsers. Omitted when a wildcard iframe
            // allowlist is set (browsers then rely on CSP frame-ancestors).
            ...(hasIframeAllowlist && options.allowIframeFrom!.includes('*')
              ? []
              : [{ key: 'X-Frame-Options', value: hasIframeAllowlist ? 'SAMEORIGIN' : 'DENY' }]),
          ],
        });
      } else {
        // Still ship the non-CSP baseline headers even with CSP disabled.
        headers.push({
          source: '/:path*',
          headers: [
            { key: 'X-Content-Type-Options', value: 'nosniff' },
            { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
            ...(hasIframeAllowlist && options.allowIframeFrom!.includes('*')
              ? []
              : [{ key: 'X-Frame-Options', value: hasIframeAllowlist ? 'SAMEORIGIN' : 'DENY' }]),
          ],
        });
      }

      // Merge with user-provided headers
      const userHeaders = options.headers ? await options.headers() : [];
      return [...headers, ...userHeaders];
    },

    // Rewrites (user-provided only)
    ...(options.rewrites && {
      rewrites: options.rewrites,
    }),

    // Redirects for URL normalization
    // Fixes "Failed to construct 'URL': Invalid URL" error with double slashes
    async redirects() {
      const baseRedirects = [
        // Normalize double slashes in URL path (e.g., /foo//bar -> /foo/bar)
        {
          source: '/:path*(//)/:rest*',
          destination: '/:path*/:rest*',
          permanent: true,
        },
        // Handle root double slash (e.g., // -> /)
        {
          source: '//',
          destination: '/',
          permanent: true,
        },
      ];

      // Merge with user-provided redirects
      const userRedirects = options.redirects ? await options.redirects() : [];
      return [...baseRedirects, ...userRedirects];
    },

    // Transpile packages (merge with user-provided)
    transpilePackages: [
      ...DEFAULT_TRANSPILE_PACKAGES,
      ...(options.transpilePackages || []),
    ],

    // Turbopack configuration (Next.js 16+ default bundler)
    // Always set turbopack config to silence Next.js 16 warning about webpack config
    turbopack: options.turbopack || {},

    // Experimental features
    experimental: {
      // Optimize package imports (only in production)
      ...(!isDev && {
        optimizePackageImports: [
          ...DEFAULT_OPTIMIZE_PACKAGES,
          ...(options.optimizePackageImports || []),
        ],
      }),
      // Dev mode optimizations
      ...(isDev && {
        optimizeCss: false,
      }),
      // User experimental options applied last (can override base settings)
      ...options.experimental,
    },

    // Webpack configuration
    webpack: (config: WebpackConfig, webpackOptions: WebpackContext) => {
      const { isServer, dev } = webpackOptions;

      // Add dev startup plugin (client-side only in dev)
      if (dev && !isServer) {
        if (!config.plugins) {
          config.plugins = [];
        }
        config.plugins.push(
          new DevStartupPlugin({
            checkUpdates: options.checkUpdates,
            autoUpdate: options.autoUpdate,
            forceCheckWorkspace: options.forceCheckWorkspace,
            checkPackages: options.checkPackages,
            autoInstall: options.autoInstall,
          })
        );
      }

      // Dev mode optimizations
      if (dev) {
        config.optimization = {
          ...config.optimization,
          removeAvailableModules: false,
          removeEmptyChunks: false,
          splitChunks: false, // Disable code splitting in dev for faster compilation
        };
      }

      // Filesystem cache (dev and production)
      config.cache = {
        type: 'filesystem',
        buildDependencies: {},
      };

      // Compression plugins (only for static build in production, client-side)
      if (!isServer && isStaticBuild && !dev) {
        addCompressionPlugins(config);
      }

      // Call user's webpack function if provided
      if (options.webpack) {
        return options.webpack(config, webpackOptions);
      }

      return config;
    },
  };

  const { i18n: i18nOptions, pwa: pwaOptions } = options;

  // Keys already consumed above; they must not reach deepMerge, either because
  // Next.js does not understand them or because baseConfig already derived the
  // real value. `transpilePackages` is the load-bearing case: baseConfig merged
  // it with DEFAULT_TRANSPILE_PACKAGES, and leaving it here made deepMerge
  // REPLACE that merged array with the user's bare list (dropping the defaults,
  // so every @djangocfg source package stopped transpiling).
  const DJANGOCFG_ONLY_KEYS = [
    'i18n',
    'pwa',
    'transpilePackages',
    'optimizePackageImports',
    'checkUpdates',
    'autoUpdate',
    'forceCheckWorkspace',
    'checkPackages',
    'autoInstall',
    'allowIframeFrom',
    'stripe',
    'csp',
  ] as const satisfies readonly (keyof BaseNextConfigOptions)[];

  const nextConfigOptions = Object.fromEntries(
    Object.entries(options).filter(
      ([key]) => !(DJANGOCFG_ONLY_KEYS as readonly string[]).includes(key)
    )
  ) as Partial<NextConfig>;

  // Deep merge only valid Next.js options with base config
  let finalConfig = deepMerge(baseConfig, nextConfigOptions);

  // Apply PWA wrapper only if explicitly configured (opt-in)
  // PWA requires sw.ts file in the app, so apps must explicitly enable it
  if (pwaOptions) {
    finalConfig = withPWA(finalConfig, pwaOptions);
  }

  // Apply i18n wrapper if configured
  // Enables next-intl for locale routing and translations
  if (i18nOptions) {
    finalConfig = withI18n(finalConfig, i18nOptions);
  }

  return finalConfig;
}
