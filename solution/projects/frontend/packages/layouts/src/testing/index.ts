// Storybook / test-only helpers. Public consumers should NOT import
// from this entrypoint in production code.

export {
  MockAuthFormProvider,
  type MockAuthFormProviderProps,
} from './MockAuthFormProvider';

export {
  MockAuthProvider,
  buildMockUser,
  type MockAuthProviderProps,
} from './MockAuthProvider';

// Auth step type, re-exported so storybook stories don't have to depend
// on @djangocfg/api/auth directly.
export type { AuthStep } from '@djangocfg/api/auth';

// Re-export auth internals so storybook can mount step components
// directly under MockAuthFormProvider without going through the full
// AuthLayout (which mounts its own real AuthFormProvider).
export { AuthShell } from '../layouts/AuthLayout/shells';
// Lets a story declare the same layout-level facts AuthLayout would (e.g. that
// the brand is already on the media half), instead of silently getting the
// context defaults.
export { AuthLayoutProvider, AuthSuccessScreen } from '../layouts/AuthLayout/AuthLayout';
// The layout's own default media-half content. Stories mount `AuthShell`
// directly, so they must supply this themselves to preview what an app that
// passes no `sidebar` actually gets.
export { AuthBrandPanel, AuthTopBar } from '../layouts/AuthLayout/components/shared';
export {
  IdentifierStep,
  OTPStep,
} from '../layouts/AuthLayout/components/steps';
// The provider round-trip card; reads `?provider=...` from the (mocked) router.
export { OAuthCallback } from '../layouts/AuthLayout/components/oauth';

// The 2FA challenge is its own surface; stories open it by beginning a challenge.
export { TwoFactorChallengeDialog, TwoFactorSetup } from '../snippets/TwoFactor';
export { beginTwoFactorChallenge, endTwoFactorChallenge } from '@djangocfg/api/auth';

// The one fake of the OAuth network for stories (providers, authorize, callback).
export {
  OAUTH_SERVER_ERROR_CODES,
  getOAuthApiMock,
  mockOAuthState,
  oauthApiMock,
  seedOAuthBrowser,
  type OAuthApiCall,
  type OAuthApiMock,
  type OAuthApiScript,
  type OAuthApiSeed,
  type OAuthServerErrorCode,
} from './mockOAuthApi';

// The whole layout, for stories that run a real round trip (callback to success screen).
export { AuthLayout } from '../layouts/AuthLayout/AuthLayout';
