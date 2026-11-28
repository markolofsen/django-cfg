/**
 * AuthLayout configurator types
 */

export type AuthShellVariant = 'centered' | 'split';
export type PresetKind = 'centered' | 'split' | 'custom';

export interface AuthBackgroundConfig {
  enabled: boolean;
  imageUrl: string;
  gradient: string;
  overlay: string;
  blur: string;
}

export interface AuthSidebarConfig {
  enabled: boolean;
  showQuote: boolean;
  showAuthor: boolean;
}

export interface AuthFormConfig {
  showLogo: boolean;
  showTerms: boolean;
  showGithub: boolean;
  showGoogle: boolean;
  showSupport: boolean;
}

/** Full config used by the playground and embed page. */
export interface AuthPlaygroundConfig {
  variant: AuthShellVariant;
  background: AuthBackgroundConfig;
  sidebar: AuthSidebarConfig;
  form: AuthFormConfig;
}

/** Centered-only subset (no sidebar). */
export interface AuthCenteredConfig {
  background: AuthBackgroundConfig;
  form: AuthFormConfig;
}

/** Split-only subset (always has sidebar + background). */
export interface AuthSplitConfig {
  background: AuthBackgroundConfig;
  sidebar: AuthSidebarConfig;
  form: AuthFormConfig;
}
