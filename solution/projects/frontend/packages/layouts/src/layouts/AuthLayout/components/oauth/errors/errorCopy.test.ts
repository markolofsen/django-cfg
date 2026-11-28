import { describe, expect, it } from 'vitest';

import { describeOAuthFailure, oauthErrorKey } from './errorCopy';

describe('describeOAuthFailure', () => {
  it('says nothing when the visitor cancelled', () => {
    expect(describeOAuthFailure('cancelled')).toBeNull();
  });

  it('points a staff account at the email code, with a heading', () => {
    expect(describeOAuthFailure('link_not_allowed')).toEqual({
      titleKey: 'layouts.auth.oauth.notice.linkNotAllowedTitle',
      bodyKey: 'layouts.auth.oauth.error.link_not_allowed',
      action: 'email',
      developerHintKey: undefined,
    });
  });

  it('offers a retry where trying again can help', () => {
    for (const code of ['invalid_state', 'oauth_exchange_failed', 'provider_unavailable', 'server_error'] as const) {
      expect(describeOAuthFailure(code)?.action).toBe('retry');
    }
  });

  it('offers nothing the visitor cannot act on', () => {
    expect(describeOAuthFailure('account_inactive')?.action).toBe('none');
    expect(describeOAuthFailure('rate_limited')?.action).toBe('none');
  });

  it('treats a missing code as the generic failure', () => {
    expect(describeOAuthFailure(undefined)).toEqual({
      titleKey: undefined,
      bodyKey: 'layouts.auth.oauth.error.generic',
      action: 'retry',
      developerHintKey: undefined,
    });
  });

  it('says the site is not set up, with a developer hint, when the origin is refused', () => {
    expect(describeOAuthFailure('origin_not_allowed')).toEqual({
      titleKey: undefined,
      bodyKey: 'layouts.auth.oauth.error.not_configured',
      action: 'email',
      developerHintKey: 'layouts.auth.oauth.notice.originNotAllowedHint',
    });
  });

  it('gives the other configuration faults the same sentence without the hint', () => {
    for (const code of ['oauth_disabled', 'github_oauth_disabled', 'missing_redirect_uri'] as const) {
      const copy = describeOAuthFailure(code);
      expect(copy?.bodyKey).toBe('layouts.auth.oauth.error.not_configured');
      expect(copy?.developerHintKey).toBeUndefined();
    }
  });
});

describe('oauthErrorKey', () => {
  it('maps a code to its sentence and an unknown cause to the generic one', () => {
    expect(oauthErrorKey('rate_limited')).toBe('layouts.auth.oauth.error.rate_limited');
    expect(oauthErrorKey('server_error')).toBe('layouts.auth.oauth.error.generic');
    expect(oauthErrorKey(undefined)).toBe('layouts.auth.oauth.error.generic');
  });
});
