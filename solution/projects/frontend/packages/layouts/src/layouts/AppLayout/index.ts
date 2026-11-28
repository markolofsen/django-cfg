/**
 * Provider stack exports.
 *
 * `BaseApp` is the canonical, framework-agnostic provider wrapper (theme, auth,
 * i18n, monitor, error tracking…). Mount it ONCE at the app root. In Next.js
 * apps, per-route shells are chosen by native route-group `layout.tsx` files
 * (each imports `PrivateLayout` / `PublicLayout` and passes its own config) —
 * there is no runtime layout-router component here anymore.
 */

export { BaseApp } from './BaseApp';
export { resolveDevtoolsBaseUrl } from './devtoolsBaseUrl';
export { resolveRealtimeApiUrl } from './realtime/realtimeApiUrl';
export type { BaseAppProps } from './BaseApp';
export { createAppQueryClient, shouldRetryQuery } from './query';
export type { QueryDevtoolsLoader } from './query';
export { REALTIME_META_KEY, topicsOfQuery } from './realtime/queryRealtime';

export type { I18nLayoutConfig } from '../types';

export { ProjectNameProvider, useProjectName } from '../../shared/ProjectContext';
export {
  LayoutI18nProvider,
  useLayoutI18n,
  useLayoutI18nOptional,
} from '../../shared/LayoutI18nProvider';
export type { LayoutI18nProviderProps } from '../../shared/LayoutI18nProvider';

// Re-export theme-override primitives so consumers can force a theme on a
// subtree (e.g. an always-dark marketing route) without depending on ui-core
// internals directly.
export {
  ThemeOverride,
  resolveForcedTheme,
  ForcedThemeProvider,
  useForcedTheme,
} from '@djangocfg/ui-core/theme';
export type {
  ThemeOverrideRule,
  ThemeOverrideProps,
  ForcedTheme,
} from '@djangocfg/ui-core/theme';
