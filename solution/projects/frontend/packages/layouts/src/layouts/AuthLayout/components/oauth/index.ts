/**
 * Provider sign-in (GitHub, Google, ...). One folder, one job per subfolder:
 *
 *   providers/  what a provider is: registry (name, icon), icons, which ones to show
 *   buttons/    the buttons: one provider button, the list, the list wired to the hook
 *   notice/     the inline message after a failed round trip
 *   callback/   finishing the round trip on /auth?provider=<id>: URL parsing, the wait overlay
 *   errors/     failure code -> copy and next step, in one table
 *
 * `OAuthSection` is what `IdentifierStep` mounts: notice, buttons, "or".
 * Only `OAuthCallback` is part of the package's public API; the rest is internal.
 * To add a provider, edit `providers/registry.ts` only.
 */
export { OAuthSection, type OAuthSectionProps } from './OAuthSection';

export { OAuthCallback, type OAuthCallbackProps } from './callback/OAuthCallback';
export { OAuthCallbackOverlay, type OAuthCallbackOverlayProps } from './callback/OAuthCallbackOverlay';

export { OAuthButtons, type OAuthButtonsProps } from './buttons/OAuthButtons';
export { OAuthButtonList, type OAuthButtonListProps } from './buttons/OAuthButtonList';
export { OAuthProviderButton, type OAuthProviderButtonProps } from './buttons/OAuthProviderButton';

export { OAuthNotice, type OAuthNoticeProps } from './notice/OAuthNotice';
export { OAuthNoticeView, type OAuthNoticeViewProps } from './notice/OAuthNoticeView';

export { describeOAuthFailure, oauthErrorKey, type OAuthNoticeCopy } from './errors/errorCopy';
export { useOAuthErrorText } from './errors/useOAuthErrorText';

export { OAUTH_PROVIDERS, providerName, resolveOAuthProviders, type OAuthProviderEntry } from './providers';
