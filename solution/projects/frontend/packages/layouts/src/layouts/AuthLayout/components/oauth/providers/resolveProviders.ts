import type { OAuthProviderId } from '@djangocfg/api/auth';

/**
 * The providers to show: the server's list, narrowed and ordered by the app's
 * `oauthProviders` prop when it gives one.
 *
 * The server owns availability, so the prop can only remove or reorder; an id
 * the server did not list is never shown, whatever the prop says.
 */
export const resolveOAuthProviders = (
  server: readonly OAuthProviderId[],
  requested?: readonly OAuthProviderId[],
): OAuthProviderId[] => {
  if (!requested) return [...server];
  const enabled = new Set(server);
  return [...new Set(requested)].filter((id) => enabled.has(id));
};
