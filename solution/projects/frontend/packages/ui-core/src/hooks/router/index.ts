// ============================================================================
// Router hooks — framework-agnostic navigation primitives.
// See ./README.md for design rationale and Next.js adapter example.
// ============================================================================

'use client';

// Adapter (context + provider + default + types)
export {
  RouterAdapterContext,
  RouterAdapterProvider,
  defaultAdapter,
  useRouterAdapter,
} from './adapter';
export type {
  RouterAdapter,
  RouterNavigateOptions,
  RouterAdapterProviderProps,
  RouterLocation,
} from './adapter';

// useLocation (+ per-property subscription)
export {
  useLocation,
  useLocationProperty,
  patchHistoryOnce,
  NAVIGATE_EVENT,
  PUSH_STATE_EVENT,
  REPLACE_STATE_EVENT,
} from './useLocation';
export type { LocationSnapshot } from './useLocation';

// Per-page switches for the scroll jump and the loading bar live in ../../route-progress
export { useNavigationBehavior } from '../../route-progress';
export type { NavigationBehavior } from '../../route-progress';

// useScrollToTop (fills the gaps in Next's own scroll restoration)
export { useScrollToTop } from './useScrollToTop';
export type { UseScrollToTopOptions } from './useScrollToTop';

// usePathnameChange (a callback when the PATH changes; query and hash do not count)
export { usePathnameChange, watchPathname } from './usePathnameChange';
export type { PathnameChangeHandler, UsePathnameChangeOptions } from './usePathnameChange';

// useNavigate
export { useNavigate } from './useNavigate';
export type { NavigateOptions, UseNavigateReturn } from './useNavigate';

// useQueryParams
export { useQueryParams } from './useQueryParams';
export type {
  QueryParamsSnapshot,
  QueryParamValue,
  QueryParamUpdates,
  SetQueryParamsOptions,
  UseQueryParamsReturn,
} from './useQueryParams';

// useBackOrFallback
export { useBackOrFallback } from './useBackOrFallback';
export type { UseBackOrFallbackReturn } from './useBackOrFallback';

// useUrlBuilder (+ pure helpers)
export { useUrlBuilder, buildUrl, buildQueryString } from './useUrlBuilder';
export type {
  QueryValue,
  QueryParamsInput,
  UseUrlBuilderReturn,
} from './useUrlBuilder';

// useSmartLink
export { useSmartLink } from './useSmartLink';
export type {
  UseSmartLinkOptions,
  SmartLinkHandlers,
} from './useSmartLink';

// useIsActive
export { useIsActive } from './useIsActive';
export type { UseIsActiveOptions } from './useIsActive';

// useQueryState (typed single-key URL state, nuqs-style)
export { useQueryState } from './useQueryState';
export type {
  UseQueryStateOptions,
  QueryStateUpdater,
} from './useQueryState';

// useHashState (useState-style binding to the URL fragment; bypasses the
// adapter so `#hash` writes are absolute — avoids Next.js hash doubling)
export { useHashState } from './useHashState';
export type {
  UseHashStateOptions,
  HashStateUpdater,
} from './useHashState';

// Parsers (typed marshalling between URL strings and JS values)
export {
  parseAsString,
  parseAsInteger,
  parseAsFloat,
  parseAsBoolean,
  parseAsIsoDate,
  parseAsStringEnum,
  parseAsArrayOf,
  parseAsJson,
} from './parsers';
export type { QueryParser, QueryParserBuilder } from './parsers';

// useRouter (composite facade)
export { useRouter } from './useRouter';
export type { UseRouterReturn } from './useRouter';
