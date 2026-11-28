/**
 * Auth Layout Types
 *
 * - Pure auth logic types re-exported from @djangocfg/api/auth
 * - UI/layout types defined here — api package has no business knowing about them
 */

import type React from 'react';

export type {
  AuthStep,
  AuthFormState,
  AuthFormStateHandlers,
  AuthFormSubmitHandlers,
  AuthFormValidation,
  AuthFormAutoSubmit,
  AuthFormReturn,
  UseAuthFormOptions,
} from '@djangocfg/api/auth';

import type { AuthFormReturn, OAuthFailureCode, OAuthProviderId } from '@djangocfg/api/auth';

import type { AuthBackgroundConfig, AuthShellVariant } from './shells';

// Re-export shell types so consumers can import everything from ./types
export type { AuthBackgroundConfig, AuthShellVariant, AuthShellContextValue } from './shells';

// ─────────────────────────────────────────────────────────────────────────────
// Layout Config — UI-specific configuration for AuthLayout
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Marketing-consent checkbox on the identifier step.
 *
 * The label copy comes from the consuming app (its own i18n) — the shared
 * packages ship no product-specific wording.
 */
export interface AuthMarketingConsentConfig {
  /** Render the checkbox and send consent fields with the OTP request. */
  enabled: boolean;
  /** Version tag of the disclosure copy, sent as `consent_disclosure_version`. */
  disclosureVersion: string;
  /** Checkbox label — arrives from the app, not from @djangocfg/i18n. */
  label: React.ReactNode;
  /**
   * Explicit default checked-state (e.g. server-decided from the consent
   * policy endpoint). Wins over the built-in timezone heuristic, which
   * remains the fallback while this is undefined (policy loading/failed).
   */
  defaultChecked?: boolean;
}

export interface AuthLayoutConfig {
  /** Support page URL */
  supportUrl?: string;
  /** Terms of service URL */
  termsUrl?: string;
  /** Privacy policy URL */
  privacyUrl?: string;
  /** Source URL for tracking */
  sourceUrl: string;
  /**
   * Narrow or reorder the provider buttons. Leave it out: the sign-in page
   * shows every provider the server has configured, in the server's order.
   * Ids the server did not list are never shown.
   */
  oauthProviders?: OAuthProviderId[];
  /** @deprecated The server decides which providers appear. Remove the prop; it has no effect and goes in the next minor. */
  enableGithubAuth?: boolean;
  /** Logo node rendered above the form and on the success screen. Pass any
   * React node — an inline-SVG brand component, an `<img>`, etc. */
  logo?: React.ReactNode;
  /** URL to redirect after successful auth (default: /private) */
  redirectUrl?: string;
  /** Optional marketing-consent checkbox on the identifier step. Absent ⇒ no checkbox, OTP body unchanged. */
  marketingConsent?: AuthMarketingConsentConfig;
}

// ─────────────────────────────────────────────────────────────────────────────
// Context — form state + layout config merged for step components
// ─────────────────────────────────────────────────────────────────────────────

// `marketingConsent` is omitted from the config side of the merge: the name is
// taken by the checkbox *state* (boolean | null) from AuthFormReturn, so the
// prop object is re-exposed as `marketingConsentConfig`.
export interface AuthFormContextType
  extends AuthFormReturn,
    Omit<AuthLayoutConfig, 'marketingConsent' | 'oauthProviders' | 'enableGithubAuth'> {
  marketingConsentConfig?: AuthMarketingConsentConfig;
  /** The provider buttons to show: the server's list after the `oauthProviders` prop is applied. */
  oauth: {
    providers: OAuthProviderId[];
    /** False only while the server's list is first loading. */
    isReady: boolean;
  };
  /** The failed provider round trip the form should explain, until the visitor dismisses it. */
  oauthNotice: OAuthFailure | null;
  setOAuthNotice: (failure: OAuthFailure | null) => void;
}

/** A provider sign-in that did not finish. `code` is absent when the cause is unknown. */
export interface OAuthFailure {
  provider: string;
  code?: OAuthFailureCode;
}

// ─────────────────────────────────────────────────────────────────────────────
// Component Props
// ─────────────────────────────────────────────────────────────────────────────

export interface AuthLayoutProps extends AuthLayoutConfig {
  children?: React.ReactNode;
  className?: string;
  /** Shell variant — controls the overall layout shape. @default 'fullsplit' */
  variant?: AuthShellVariant;
  /**
   * Which side the media (image) half sits on in the `fullsplit` variant.
   * Ignored by other variants. @default 'left'
   */
  mediaSide?: 'left' | 'right';
  /** Background configuration (image, gradient, overlay, blur). */
  background?: AuthBackgroundConfig;
  /** Slot for the right column in split variant (testimonial, branding, etc.). */
  sidebar?: React.ReactNode;
  /** Callback when identifier step succeeds */
  onIdentifierSuccess?: (identifier: string) => void;
  /** Callback when OTP verification succeeds */
  onOTPSuccess?: () => void;
  /**
   * Callback when OAuth succeeds. `user` is the provider callback's user
   * payload, untyped upstream — narrow it before reading fields.
   */
  onOAuthSuccess?: (user: unknown, isNewUser: boolean, provider: string) => void;
  /** Callback on any error */
  onError?: (message: string) => void;
}

export interface AuthHelpProps {
  className?: string;
  variant?: 'default' | 'compact';
}
