/**
 * Product-event catalog.
 *
 * This is the single TypeScript source of truth for framework event names and
 * their properties. Products extend `AnalyticsEventMap` by declaration merging
 * instead of maintaining a second enum, transport, or browser global.
 */

/**
 * Event Categories
 */
export const AnalyticsCategory = {
  AUTH: 'auth',
  ERROR: 'error',
  NAVIGATION: 'navigation',
  ENGAGEMENT: 'engagement',
  USER: 'user',
} as const;

/**
 * Predefined Event Names
 */
export const AnalyticsEvent = {
  // Auth Events
  AUTH_OTP_REQUEST: 'auth_otp_request',
  AUTH_OTP_VERIFY_SUCCESS: 'auth_otp_verify_success',
  AUTH_OTP_VERIFY_FAIL: 'auth_otp_verify_fail',
  AUTH_LOGIN_SUCCESS: 'auth_login_success',
  AUTH_LOGOUT: 'auth_logout',
  AUTH_SESSION_EXPIRED: 'auth_session_expired',
  AUTH_TOKEN_REFRESH: 'auth_token_refresh',
  AUTH_TOKEN_REFRESH_FAIL: 'auth_token_refresh_fail',

  // OAuth Events
  AUTH_OAUTH_START: 'auth_oauth_start',
  AUTH_OAUTH_SUCCESS: 'auth_oauth_success',
  AUTH_OAUTH_FAIL: 'auth_oauth_fail',

  // Error Events
  ERROR_BOUNDARY: 'error_boundary',
  ERROR_API: 'error_api',
  ERROR_VALIDATION: 'error_validation',
  ERROR_NETWORK: 'error_network',

  // Navigation Events
  NAV_ADMIN_ENTER: 'nav_admin_enter',
  NAV_DASHBOARD_ENTER: 'nav_dashboard_enter',
  NAV_PAGE_VIEW: 'nav_page_view',

  // Engagement Events
  THEME_CHANGE: 'theme_change',
  SIDEBAR_TOGGLE: 'sidebar_toggle',
  MOBILE_MENU_OPEN: 'mobile_menu_open',

  // User Events
  USER_PROFILE_VIEW: 'user_profile_view',
  USER_PROFILE_UPDATE: 'user_profile_update',
} as const;

export type AnalyticsCategoryType = typeof AnalyticsCategory[keyof typeof AnalyticsCategory];
export type AnalyticsEventType = typeof AnalyticsEvent[keyof typeof AnalyticsEvent];

export type AnalyticsPropertyValue = string | number | boolean | null;

/**
 * `| undefined` in the value: an optional dimension the caller did not supply
 * arrives as an explicit `undefined`, and every transport already drops it
 * (JSON.stringify omits it, GA4 ignores it). Without it, the identical sink
 * contract in `@djangocfg/api` — the auth events' only route into this package
 * — does not type-check against it.
 */
export type AnalyticsEventProperties = Record<
  string,
  AnalyticsPropertyValue | undefined
>;

/**
 * Framework event names with their valid payloads.
 *
 * Apps can extend this interface:
 *
 * ```ts
 * declare module '@djangocfg/analytics' {
 *   interface AnalyticsEventMap {
 *     'billing.checkout_started': { plan: 'pro' | 'team' }
 *   }
 * }
 * ```
 */
export interface AnalyticsEventMap {
  auth_otp_request: { method?: 'email' | 'phone' };
  auth_login_success: { provider?: 'email' | 'github'; is_new_user?: boolean };
  auth_otp_verify_fail: { reason?: string };
  auth_session_expired: Record<string, never>;
  auth_token_refresh: Record<string, never>;
  auth_token_refresh_fail: { reason?: string };
  auth_logout: Record<string, never>;
  auth_oauth_start: { provider: 'github' };
  auth_oauth_fail: { provider?: 'github'; reason?: string };
  error_boundary: { boundary?: string };
  error_api: { status?: number; operation?: string };
  error_validation: { field?: string };
  error_network: { operation?: string };
  nav_admin_enter: Record<string, never>;
  nav_dashboard_enter: Record<string, never>;
  nav_page_view: Record<string, never>;
  theme_change: { theme?: string };
  sidebar_toggle: { open?: boolean };
  mobile_menu_open: Record<string, never>;
  user_profile_view: Record<string, never>;
  user_profile_update: Record<string, never>;
  'layouts.auth.step_viewed': { step: 'identifier' | 'otp' | '2fa' | '2fa-setup' | 'success' };
}

/** A catalog event is fully typed; arbitrary product events remain supported. */
export type AnalyticsEventName = keyof AnalyticsEventMap | (string & {});

export type AnalyticsEventProps<Name extends AnalyticsEventName> =
  Name extends keyof AnalyticsEventMap
    ? AnalyticsEventMap[Name]
    : AnalyticsEventProperties;
