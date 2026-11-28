export { validateEmail } from './validation';
export {
  formatAuthError,
  logAuthFailure,
  resolveAuthError,
  AUTH_ERROR_KEYS,
  type AuthErrorCopy,
  type AuthErrorKey,
} from './errors';
export {
  readOAuthFailure,
  type OAuthClientErrorCode,
  type OAuthErrorCode,
  type OAuthFailure,
  type OAuthFailureCode,
  type OAuthProviderId,
} from './oauthErrors';
export {
  resolveGuardIsLoading,
  shouldRedirectToAuth,
  resolveGuardIsAuthenticated,
  isForbidden,
  type GuardInput,
} from './guard';
export { normalizePath, isAllowedAuthPath } from './path';
export {
  safeNext,
  resolveSso,
  buildSsoLoginUrl,
  registrableDomain,
  deriveAuthHost,
  parseSsoHost,
  getSsoState,
  type SsoConfig,
  type SsoState,
  type SsoOffReason,
} from './sso';
export { resolveAuthStatus, type AuthStatus, type AuthStateInput } from './authState';
export { logger, authLogger } from './logger';
export {
  Analytics,
  AnalyticsEvent,
  AnalyticsCategory,
  // Lets @djangocfg/analytics inject the real implementation without api having
  // to depend on it (which would be a cycle — analytics reads auth state).
  setAnalyticsSink,
  type AnalyticsSink,
  type AnalyticsEventType,
  type AnalyticsCategoryType,
} from './analytics';
