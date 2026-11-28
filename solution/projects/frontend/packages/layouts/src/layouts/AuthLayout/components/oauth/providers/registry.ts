import type React from 'react';

import type { OAuthProviderId } from '@djangocfg/api/auth';

import { GithubIcon } from './icons/GithubIcon';
import { GoogleIcon } from './icons/GoogleIcon';

export interface OAuthProviderEntry {
  /** Brand name. Never translated: it fills `{provider}` in the button and message copy. */
  name: string;
  /** The provider's mark, an svg component. */
  Icon: React.FC;
}

/**
 * The one place that knows what a provider looks like.
 *
 * Keyed by the API package's id type, so a provider the backend adds fails
 * typecheck here until it has a name and an icon. Nothing else changes: the
 * button list, labels, notices and error copy all read this table.
 *
 * To add a provider: draw `icons/<Name>Icon.tsx`, add one line below.
 */
export const OAUTH_PROVIDERS: Record<OAuthProviderId, OAuthProviderEntry> = {
  github: { name: 'GitHub', Icon: GithubIcon },
  google: { name: 'Google', Icon: GoogleIcon },
};

const isKnown = (id: string): id is OAuthProviderId => Object.prototype.hasOwnProperty.call(OAUTH_PROVIDERS, id);

/** Brand name for an id; an id this client does not know is shown as it came. */
export const providerName = (id: string): string => (isKnown(id) ? OAUTH_PROVIDERS[id].name : id);
