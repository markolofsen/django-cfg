import type { OAuthFailureCode } from '@djangocfg/api/auth';

/** Translation keys of the visitor-facing sentences, one per kind of failure. */
export const OAUTH_ERROR_KEYS = {
  invalid_state: 'layouts.auth.oauth.error.invalid_state',
  oauth_exchange_failed: 'layouts.auth.oauth.error.oauth_exchange_failed',
  invalid_id_token: 'layouts.auth.oauth.error.invalid_id_token',
  email_missing: 'layouts.auth.oauth.error.email_missing',
  email_not_verified: 'layouts.auth.oauth.error.email_not_verified',
  hosted_domain_not_allowed: 'layouts.auth.oauth.error.hosted_domain_not_allowed',
  account_inactive: 'layouts.auth.oauth.error.account_inactive',
  link_not_allowed: 'layouts.auth.oauth.error.link_not_allowed',
  rate_limited: 'layouts.auth.oauth.error.rate_limited',
  provider_unavailable: 'layouts.auth.oauth.error.provider_unavailable',
  not_configured: 'layouts.auth.oauth.error.not_configured',
  cancelled: 'layouts.auth.oauth.error.cancelled',
  generic: 'layouts.auth.oauth.error.generic',
} as const;

export type OAuthErrorKey = (typeof OAUTH_ERROR_KEYS)[keyof typeof OAUTH_ERROR_KEYS];

/** The next step a notice points at: the email field below (no button; focus moves there), a retry button, or nothing the visitor can do. */
export type OAuthNoticeAction = 'email' | 'retry' | 'none';

interface Rule {
  /** Which sentence the visitor reads. */
  copy: keyof typeof OAUTH_ERROR_KEYS;
  /** What they can do about it. A retry is only offered where trying again can change the outcome. */
  action: OAuthNoticeAction;
  /** Site misconfiguration: a developer line is shown under the sentence. */
  developerHint?: boolean;
}

const retry = (copy: Rule['copy']): Rule => ({ copy, action: 'retry' });
const email = (copy: Rule['copy']): Rule => ({ copy, action: 'email' });
const nothing = (copy: Rule['copy']): Rule => ({ copy, action: 'none' });

/**
 * Every failure code, once: what is said and what is offered.
 *
 * Exhaustive on purpose: a code the backend adds fails typecheck here until
 * someone decides what to tell the visitor. Faults only a developer can fix
 * (`origin_not_allowed`, a missing redirect) read as "not available on this
 * site" and point at email.
 */
const RULES: Record<OAuthFailureCode, Rule> = {
  invalid_state: retry('invalid_state'),
  oauth_exchange_failed: retry('oauth_exchange_failed'),
  invalid_id_token: retry('invalid_id_token'),
  email_missing: email('email_missing'),
  email_not_verified: email('email_not_verified'),
  hosted_domain_not_allowed: email('hosted_domain_not_allowed'),
  account_inactive: nothing('account_inactive'),
  link_not_allowed: email('link_not_allowed'),
  rate_limited: nothing('rate_limited'),
  provider_unavailable: retry('provider_unavailable'),
  cancelled: nothing('cancelled'),
  oauth_disabled: email('not_configured'),
  github_oauth_disabled: email('not_configured'),
  origin_not_allowed: { copy: 'not_configured', action: 'email', developerHint: true },
  missing_redirect_uri: email('not_configured'),
  server_error: retry('generic'),
  not_found: retry('generic'),
  unknown_provider: retry('generic'),
};

/** The sentence for a code; the generic one when the cause is unknown. */
export const oauthErrorKey = (code?: OAuthFailureCode | null): OAuthErrorKey =>
  OAUTH_ERROR_KEYS[code ? RULES[code].copy : 'generic'];

export interface OAuthNoticeCopy {
  /** Only the code that needs a heading has one; the rest are a single sentence. */
  titleKey?: 'layouts.auth.oauth.notice.linkNotAllowedTitle';
  bodyKey: OAuthErrorKey;
  action: OAuthNoticeAction;
  /** Present when the page's own configuration is at fault: a line for whoever deploys it. */
  developerHintKey?: 'layouts.auth.oauth.notice.originNotAllowedHint';
}

/**
 * What the sign-in form tells a visitor whose provider round trip failed.
 *
 * `null` means "say nothing": the visitor cancelled on the provider's page and
 * is back at the form they started from. An absent code is the unknown case.
 */
export const describeOAuthFailure = (code?: OAuthFailureCode | null): OAuthNoticeCopy | null => {
  const rule: Rule = code ? RULES[code] : retry('generic');
  if (rule.copy === 'cancelled') return null;
  return {
    titleKey: rule.copy === 'link_not_allowed' ? 'layouts.auth.oauth.notice.linkNotAllowedTitle' : undefined,
    bodyKey: OAUTH_ERROR_KEYS[rule.copy],
    action: rule.action,
    developerHintKey: rule.developerHint ? 'layouts.auth.oauth.notice.originNotAllowedHint' : undefined,
  };
};
