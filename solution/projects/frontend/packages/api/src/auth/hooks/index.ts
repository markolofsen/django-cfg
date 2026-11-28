'use client';

// Session (reactive snapshot from the generated auth store)
export { useSession, type SessionSnapshot, type SessionStatus } from './useSession';

// Time zone preference (X-Timezone override)
export { useTimezone, type UseTimezoneReturn } from './useTimezone';

// Router hooks
export { useCfgRouter } from './useCfgRouter';
export { useQueryParams } from './useQueryParams';

// Core form hooks (decomposed)
export { useAuthFormState, type UseAuthFormStateReturn } from './useAuthFormState';
export { useAuthValidation, validateIdentifier } from './useAuthValidation';

// Complete form hook (composes the above)
export { useAuthForm, type AuthFormReturn, type UseAuthFormOptions } from './useAuthForm';

// Auto-auth from URL
export { useAutoAuth, type UseAutoAuthOptions } from './useAutoAuth';

// OAuth — one hook for every provider, plus the server's provider list
export {
  useOAuthLogin,
  isOAuthProviderId,
  clearOAuthAttempt,
  OAUTH_PROVIDER_IDS,
  type OAuthUser,
  type UseOAuthLoginOptions,
  type UseOAuthLoginReturn,
} from './useOAuthLogin';
export { useOAuthProviders, type UseOAuthProvidersReturn } from './useOAuthProviders';
/** @deprecated Use `useOAuthLogin`. Removed in the next minor. */
export { useGithubAuth, type UseGithubAuthOptions, type UseGithubAuthReturn } from './useGithubAuth';

// 2FA — one consolidated hook (verify / setup / status namespaces),
// plus the underlying sub-hooks for single-concern consumers.
export {
  useTwoFactor,
  useTwoFactorVerify,
  useTwoFactorSetup,
  useTwoFactorStatus,
  type UseTwoFactorOptions,
  type UseTwoFactorReturn,
  type UseTwoFactorVerifyOptions,
  type UseTwoFactorVerifyReturn,
  type UseTwoFactorSetupOptions,
  type UseTwoFactorSetupReturn,
  type UseTwoFactorStatusReturn,
  type TwoFactorSetupData,
  type TwoFactorDevice,
} from './useTwoFactor';

// 2FA challenge handoff between the sign-in step and the challenge dialog
export {
  beginTwoFactorChallenge,
  endTwoFactorChallenge,
  useTwoFactorChallenge,
  type TwoFactorChallenge,
} from './useTwoFactorChallenge';

// Auth guards and redirects
export {
  consumeSavedRedirect,
  peekSavedRedirect,
  useAuthRedirectManager,
} from './useAuthRedirect';

// Storage hook (through the key registry)
export { useCfgStored } from './useCfgStored';
export { useBase64, encodeBase64, decodeBase64 } from './useBase64';

// Profile cache
export {
  getCachedProfile,
  setCachedProfile,
  clearProfileCache,
  hasValidCache,
  getCacheMetadata,
  type ProfileCacheOptions,
} from './useProfileCache';

// Account deletion
export {
  useDeleteAccount,
  type UseDeleteAccountReturn,
  type DeleteAccountResult,
} from './useDeleteAccount';
