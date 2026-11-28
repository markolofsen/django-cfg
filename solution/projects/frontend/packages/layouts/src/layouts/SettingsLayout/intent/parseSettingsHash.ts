/**
 * The fragment grammar of the Settings dialog: `settings/<section>?<params>`.
 *
 * The query is a one-shot arrival intent (an assistant's consent request, a pre-filled form). It rides in the
 * fragment so it never reaches a server log, a CDN log or a `Referer`; the dialog reads it once and strips it.
 */

/** Hard caps: the fragment is attacker-reachable input, and the store keeps what it parses. */
const MAX_PARAMS = 8;
const MAX_VALUE_LENGTH = 4096;

export interface ParsedSettingsHash {
  open: boolean;
  section: string | null;
  /** Flat and length-capped; empty when the fragment carried no query. */
  params: Record<string, string>;
}

const CLOSED: ParsedSettingsHash = { open: false, section: null, params: {} };

/** Parse a bare fragment (no leading '#'): `"settings/mcp?request=abc"` → `{ open, section: 'mcp', params: { request: 'abc' } }`. */
export function parseSettingsHash(fragment: string, urlKey: string): ParsedSettingsHash {
  if (!fragment) return CLOSED;

  const queryAt = fragment.indexOf('?');
  const path = queryAt === -1 ? fragment : fragment.slice(0, queryAt);
  const query = queryAt === -1 ? '' : fragment.slice(queryAt + 1);

  const [key, ...rest] = path.split('/');
  if (key !== urlKey) return CLOSED;

  const params: Record<string, string> = {};
  for (const [name, value] of new URLSearchParams(query)) {
    if (Object.keys(params).length >= MAX_PARAMS) break;
    if (value.length > MAX_VALUE_LENGTH) continue;
    params[name] = value;
  }
  return { open: true, section: rest.join('/') || null, params };
}

/** Build the bare fragment `"settings/usage"` (or `"settings"` when no section). Never carries params: an intent is not written back. */
export function buildSettingsHash(urlKey: string, section: string | null): string {
  return section ? `${urlKey}/${section}` : urlKey;
}

/**
 * The section to open for a parsed fragment. `resolved` is the host's check against the sections it knows *right now*;
 * it is null both for a typo and for a section that has not registered yet (a host adds its MCP section once a
 * backend answer arrives, after the dialog has already read a deep link on a cold load). Dropping the id in the
 * second case made the dialog write `#settings` over the link and open on the first section, so the id is kept: an
 * unknown one only shows the fallback section, a late one is picked up as soon as it registers.
 */
export function sectionToOpen(requested: string | null, resolved: string | null): string | null {
  return resolved ?? requested;
}

/** True when the fragment is a Settings deep link that carries an arrival intent (`#settings/mcp?request=…`). */
export function carriesIntent(fragment: string, urlKey: string): boolean {
  const parsed = parseSettingsHash(fragment, urlKey);
  return parsed.open && Object.keys(parsed.params).length > 0;
}
