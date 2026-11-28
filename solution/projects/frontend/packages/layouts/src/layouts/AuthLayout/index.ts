/**
 * Auth Layout exports
 */

// Main layout
export { AuthLayout, AuthSuccessScreen, useAuthLayoutContext } from './AuthLayout';
export type { AuthSuccessScreenProps } from './AuthLayout';

// Context and hooks
export { AuthFormProvider, useAuthFormContext } from './context';

// Shells
export {
  AuthShell,
  AuthShellProvider,
  useAuthShell,
  useAuthShellOptional,
} from './shells';

// Step components
export {
  IdentifierStep,
  OTPStep,
  OAuthCallback,
  type OAuthCallbackProps,
} from './components';

// Shared UI components
export * from './components/shared';

// Types — all from single source: ./types
export type {
  // Auth logic (re-exported from @djangocfg/api/auth)
  AuthStep,
  AuthFormState,
  AuthFormReturn,
  UseAuthFormOptions,
  // Layout UI types (owned by this package)
  AuthLayoutConfig,
  AuthFormContextType,
  OAuthFailure,
  AuthLayoutProps,
  AuthHelpProps,
  // Shell types
  AuthShellVariant,
  AuthBackgroundConfig,
  AuthShellContextValue,
} from './types';
