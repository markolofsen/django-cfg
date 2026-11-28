import type { OAuthFailureCode, OAuthProviderId } from '@djangocfg/api/auth';

/** Query parameters a provider round trip leaves on the callback URL. */
export const OAUTH_CALLBACK_PARAMS = [
  'provider',
  'code',
  'state',
  'scope',
  'authuser',
  'prompt',
  'hd',
  'iss',
  'error',
  'error_description',
  'error_uri',
] as const;

/** What the callback URL asks the page to do. */
export type OAuthCallbackIntent =
  | { kind: 'none' }
  | { kind: 'exchange'; provider: OAuthProviderId; code: string; state: string }
  /** The provider returned without a code. `code` is set when we know the cause (Cancel). */
  | { kind: 'failure'; provider: string; code?: OAuthFailureCode; description?: string };

/**
 * Decide what a callback URL means. Pure: no storage, no network.
 *
 * `provider` is the only trigger, so a normal visit to the sign-in page is
 * `none`. A provider `error` wins over a `code`: it is a refusal, whatever
 * else rides along.
 */
export const readOAuthCallback = (
  params: URLSearchParams,
  isOAuthProviderId: (value: string) => value is OAuthProviderId,
): OAuthCallbackIntent => {
  const provider = params.get('provider');
  if (!provider) return { kind: 'none' };

  if (!isOAuthProviderId(provider)) {
    return { kind: 'failure', provider, code: 'unknown_provider' };
  }

  const providerError = params.get('error');
  if (providerError) {
    return {
      kind: 'failure',
      provider,
      // Google answers Cancel with `access_denied`; every other provider error is not ours to explain.
      code: providerError === 'access_denied' ? 'cancelled' : undefined,
      description: params.get('error_description') || providerError,
    };
  }

  const code = params.get('code');
  const state = params.get('state');
  if (!code || !state) return { kind: 'failure', provider, code: 'invalid_state' };

  return { kind: 'exchange', provider, code, state };
};

/**
 * The same URL without the callback parameters. The code and state are single
 * use and must not stay in the address bar, history or a shared link; every
 * other parameter and the hash are kept.
 */
export const stripOAuthCallbackParams = (href: string): string => {
  const url = new URL(href);
  for (const key of OAUTH_CALLBACK_PARAMS) url.searchParams.delete(key);
  return `${url.pathname}${url.search}${url.hash}`;
};
