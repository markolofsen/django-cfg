// ============================================================================
// Hooks - Reusable React Hooks (No Next.js/Browser Storage dependencies)
// For use in Electron, Vite, CRA apps
//
// Hooks are grouped by domain (see ./<group>/index.ts). This top-level barrel
// re-exports everything for convenience: `from '@djangocfg/ui-core/hooks'`.
// For tree-shaking or clarity, import the group directly:
//   `from '@djangocfg/ui-core/hooks/dom'`, etc.
// ============================================================================

'use client';

export * from './dom';
export * from './state';
export * from './storage';
export * from './media';
export * from './device';
export * from './feedback';
export * from './theme';
export * from './time';
export * from './events';
export * from './hotkey';
export * from './audio';
export * from './debug';
export * from './tabs';

// ----------------------------------------------------------------------------
// Router — framework-agnostic navigation primitives.
// See ./router/README.md for design notes and the Next.js adapter example.
// ----------------------------------------------------------------------------
export {
  // Adapter
  RouterAdapterContext,
  RouterAdapterProvider,
  defaultAdapter,
  useRouterAdapter,
  // useLocation
  useLocation,
  useLocationProperty,
  NAVIGATE_EVENT,
  // useNavigate
  useNavigate,
  // useQueryParams
  useQueryParams,
  // useBackOrFallback
  useBackOrFallback,
  // useUrlBuilder
  useUrlBuilder,
  buildUrl,
  buildQueryString,
  // useSmartLink
  useSmartLink,
  // useIsActive
  useIsActive,
  // useQueryState (typed single-key URL state)
  useQueryState,
  // useHashState (useState-style URL fragment binding; adapter-bypassing)
  useHashState,
  // Parsers
  parseAsString,
  parseAsInteger,
  parseAsFloat,
  parseAsBoolean,
  parseAsIsoDate,
  parseAsStringEnum,
  parseAsArrayOf,
  parseAsJson,
  // useRouter (composite facade)
  useRouter,
  // usePathnameChange (a callback when the path changes, not the query)
  usePathnameChange,
  watchPathname,
  // useScrollToTop (covers the routes Next's own scroll handler skips)
  useScrollToTop,
  // Per-page switches for the scroll jump and the loading bar
  useNavigationBehavior,
} from './router';
export type {
  RouterAdapter,
  RouterNavigateOptions,
  NavigationBehavior,
  RouterAdapterProviderProps,
  RouterLocation,
  LocationSnapshot,
  NavigateOptions,
  UseNavigateReturn,
  QueryParamsSnapshot,
  QueryParamValue,
  QueryParamUpdates,
  SetQueryParamsOptions,
  UseQueryParamsReturn,
  UseBackOrFallbackReturn,
  QueryValue,
  QueryParamsInput,
  UseUrlBuilderReturn,
  UseSmartLinkOptions,
  SmartLinkHandlers,
  UseIsActiveOptions,
  UseQueryStateOptions,
  QueryStateUpdater,
  UseHashStateOptions,
  HashStateUpdater,
  QueryParser,
  QueryParserBuilder,
  UseRouterReturn,
  UseScrollToTopOptions,
  PathnameChangeHandler,
  UsePathnameChangeOptions,
} from './router';
