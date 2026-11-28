/**
 * Base Layout Types
 *
 * Core layout configuration that combines all provider configs
 */

import type { ReactNode } from 'react';
import type { AuthConfig } from '@djangocfg/api/auth';

// Import provider configs from their modules
import type { AnalyticsConfig } from '../../snippets/Analytics/types';
import type { ErrorBoundaryConfig, ErrorTrackingConfig } from '../../components/errors/types';

/**
 * Opaque alias for the `routing` object returned by `defineRouting()` from
 * `next-intl/routing`. Typed as `unknown` so consumer apps can pass shared
 * (no `pathnames`) or localized routing without fighting next-intl's
 * conditional generics. The bridge inside `BaseApp` casts it back when it
 * calls `createNavigation(routing)`.
 */
export type NextIntlRouting = object & { __nextIntlRouting?: never };

// Import local provider configs
import type { ThemeConfig } from './providers.types';
import type { QueryClient } from '@tanstack/react-query';
import type { QueryDevtoolsLoader } from '../AppLayout/query/AppQueryProvider';
import type { DevtoolsProps } from '@djangocfg/devtools';
import type { RealtimeConfig } from '@djangocfg/realtime/react';

// ============================================================================
// Base Layout Props
// ============================================================================

/**
 * Base Layout Props
 *
 * Core configuration for BaseApp component.
 * All provider configs are imported from their respective modules.
 */
/** Tuning for the top loading bar, see `BaseLayoutProps.progressBar`. */
export interface RouteProgressOptions {
  color?: string;
  height?: number;
  shouldShow?: (from: URL, to: URL) => boolean;
}

export interface BaseLayoutProps {
  children: ReactNode;

  /** Project name — used as default for devtools.project */
  project?: string;

  /** Theme configuration */
  theme?: ThemeConfig;

  /** Auth configuration. Pass `false` to disable AuthProvider entirely (public apps). */
  auth?: AuthConfig | false;

  /**
   * django-cfg API origin for apps with `auth={false}` (public apps): used as the
   * devtools ingest `baseUrl`, so one value is enough. With auth configured the
   * origin comes from `auth.apiUrl`. An explicit `devtools={{ baseUrl }}` wins.
   */
  apiUrl?: string;

  /** Analytics configuration (from snippets/Analytics) */
  analytics?: AnalyticsConfig;

  /** Error tracking configuration (from components/errors) */
  errorTracking?: ErrorTrackingConfig;

  /**
   * The app's own React Query client. Without it `BaseApp` reuses a QueryClient provided above it, else creates one
   * per mount with django-cfg's defaults (`createAppQueryClient`: no retry on 4xx, up to 2 on a network error or a
   * 5xx, `throwOnError: false`, `staleTime` 30 s, refetch on focus, mutations not retried). A client passed here
   * is used as it is: its defaults are not merged.
   */
  queryClient?: QueryClient;

  /**
   * React Query Devtools, development builds only, loaded on demand:
   * `queryDevtools={() => import('@tanstack/react-query-devtools')}` (the app installs the package).
   */
  queryDevtools?: QueryDevtoolsLoader;

  /** Error boundary configuration (from components/errors, enabled by default) */
  errorBoundary?: ErrorBoundaryConfig;

  /**
   * Devtools configuration (`@djangocfg/devtools`): error/console capture with
   * backend ingest + the floating debug panel. Capture is on by default;
   * `devtools={{ button: false }}` hides the panel button, `ingest: false`
   * keeps events local.
   */
  devtools?: DevtoolsConfig;

  /**
   * Realtime (`@djangocfg/realtime`): one lazy WebSocket per tab for `useTopic`. On by default and free until a
   * component subscribes. The URL defaults to the API origin (`realtime.apiUrl`, `apiUrl`, `auth.apiUrl`, then
   * `NEXT_PUBLIC_API_URL`) plus `/ws`, `wss:` for `https:`. A mounted query tagged with a topic
   * (`invalidated_by` on its view) is invalidated on each message and gap of that topic; `onGap` replaces the
   * default for `useTopic` subscriptions. `false` turns it off.
   */
  realtime?: RealtimeConfig | false;

  /**
   * Locale-switching plumbing. Mounted into a `LayoutI18nProvider` inside
   * `BaseApp` — every locale-aware component (footer, navbar, sidebar,
   * UserMenu, LocaleSwitcher) reads from there via `useLayoutI18n()`.
   */
  i18n?: I18nLayoutConfig;

  /**
   * Installed-app meta tags (`viewport-fit=cover`, `apple-mobile-web-app-capable`, `mobile-web-app-capable`,
   * translucent status bar), added to `<head>` when the app's own `viewport`/`metadata` lack them. On by default;
   * pass `false` to opt out.
   */
  pwaMeta?: boolean;

  /**
   * The top loading bar shown while moving between pages (`@djangocfg/ui-core/route-progress`). On by default;
   * `false` removes it for the whole app. An object tunes it: `color`, `height` (px) and `shouldShow(from, to)`,
   * the app's route rule (default: the pathname changes, so `?tab=2` and `#hash` never show it). A page or
   * section can silence the bar, and the jump to the top, while it is mounted:
   * `useNavigationBehavior({ progress: false, scroll: false })`.
   */
  progressBar?: boolean | RouteProgressOptions;
  /**
   * Show the viewport diagnostic dot (a 24px dot in a corner; tap it to open the HUD) even where there is no Settings dialog,
   * e.g. a video-call page. Default false. The HUD state is per origin (`localStorage`).
   */
  debug?: boolean;
}

/** Devtools config for BaseApp — the `<Devtools>` props minus children. */
export type DevtoolsConfig = Omit<DevtoolsProps, 'children'>;

/**
 * Brand block surfaced inside the locale-switcher dialog. Shared via
 * `I18nLayoutConfig.brand` so footer / navbar / sidebar all open the same
 * dialog with the same identity.
 */
export interface I18nBrandConfig {
  /** Logo node — img / svg / lucide icon. Sized ~36×36 in the dialog header. */
  logo?: ReactNode;
  /** Project name shown beside the logo. */
  name?: string;
}

/** UI strings for the locale-switcher dialog (also passed via i18n). */
export interface I18nDialogLabels {
  dialogTitle?: string;
  dialogSubtitle?: string;
  searchPlaceholder?: string;
  emptyResults?: string;
  closeLabel?: string;
  triggerLabel?: string;
}

/**
 * i18n configuration consumed by layouts, navbars, footer controls, and the
 * UserMenu locale row. Same shape as `@djangocfg/nextjs`'s `useLocaleSwitcher`,
 * with optional `brand` / `dialogLabels` so every locale-switcher mount
 * (footer, navbar, sidebar) opens the same fullscreen dialog with a
 * consistent identity.
 */
export interface I18nLayoutConfig {
  /** Current locale (e.g. `"en"`, `"ru"`, `"pt-BR"`). */
  locale: string;
  /** Available locales. */
  locales: string[];
  /** Called when the user picks a new locale. */
  onLocaleChange: (locale: string) => void;
  /** Brand surfaced in the locale-switcher dialog header. */
  brand?: I18nBrandConfig;
  /** Custom UI strings for the locale-switcher dialog. */
  dialogLabels?: I18nDialogLabels;
  /**
   * Optional `routing` object from `next-intl`'s `defineRouting()`. When
   * passed, `BaseApp` builds a locale-aware Link adapter from it and mounts
   * a `LinkProvider` so every `<Link>` rendered inside layouts keeps the
   * active locale prefix on click. Without it, non-default-locale users get
   * sent back to the default locale on every navbar / footer click.
   */
  routing?: NextIntlRouting;
  /**
   * The "this page is available in <your language>" hint shown when the browser's language is a site locale other than
   * the current one. On by default when `locales.length > 1` (nothing renders for a one-language site); `false` turns it
   * off for the app. An object tunes it.
   */
  suggestion?: false | LocaleSuggestionOptions;
}

/** Tuning for the locale hint (`I18nLayoutConfig.suggestion`). */
export interface LocaleSuggestionOptions {
  /** Pathname prefixes or patterns where the language is fixed by meaning (legal text, a translated landing); never shown there. */
  exclude?: (string | RegExp)[];
  /** Quiet time after the page settles before the hint appears. Default 1500 ms. */
  delayMs?: number;
  /** How long a dismissal for one language pair is remembered. Default 180 days. */
  ttlDays?: number;
}

// ============================================================================
// Layout Visual Variant
// ============================================================================

/**
 * Visual style of the private/app shell.
 * - `full-bleed` (default) — flat, Claude-style: content fills the page next to
 *   the sidebar, divided by a single 1px border.
 * - `boxed` — content lives in a rounded card inset from the viewport edges on a
 *   sidebar-coloured canvas. Mobile (<md) falls back to `full-bleed` automatically.
 */
export type LayoutVisualVariant = 'full-bleed' | 'boxed';

/** Border radius preset for the boxed container. */
export type LayoutBoxedRadius = 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl';

/** Background token used for the area *behind* the boxed container. */
export type LayoutBoxedBackground = 'sidebar' | 'muted' | 'card' | 'background';

/**
 * Visual config for the private layout shell.
 * All `boxed`-only options are ignored when `variant === 'full-bleed'`.
 */
export interface LayoutVisualConfig {
  /** Visual variant. Default: `'full-bleed'`. */
  variant?: LayoutVisualVariant;
  /**
   * Inset (px) between the boxed container and the viewport edges on desktop.
   * Either a single value (applied to all sides next to the sidebar) or per-axis.
   * Default: `12`.
   */
  inset?: number | { x?: number; y?: number };
  /** Border radius preset of the boxed container. Default: `'2xl'`. */
  radius?: LayoutBoxedRadius;
  /** Background colour token shown *behind* the boxed container. Default: `'sidebar'`. */
  background?: LayoutBoxedBackground;
  /** Whether to render a 1px border on the boxed container. Default: `true`. */
  border?: boolean;
  /**
   * Optional max width for the inner scrollable area (Tailwind size token).
   * Default: `'none'` (fills available width minus inset).
   */
  maxWidth?: 'none' | 'screen-xl' | 'screen-2xl' | '7xl';
}

