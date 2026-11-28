import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';

// Storage keys are defined once, in the registry. A literal anywhere else is a bug.
const FORBIDDEN = [
  'user_profile_cache', 'auth_email', 'auth_redirect_url', 'fm_session_id', 'oauth_state',
  'oauth_provider', 'oauth_providers', 'cfg.access_token', 'cfg.refresh_token', 'cfg.api_key',
];

function walk(dir: string, out: string[] = []): string[] {
  for (const name of readdirSync(dir)) {
    const path = join(dir, name);
    if (statSync(path).isDirectory()) {
      if (name !== '__tests__' && name !== 'generated') walk(path, out);
    } else if (/\.tsx?$/.test(name)) out.push(path);
  }
  return out;
}

describe('no key literals outside the registry', () => {
  const files = walk(join(__dirname, '..'));
  it.each(FORBIDDEN)('"%s" is not spelled in source', (literal) => {
    const hits = files.filter((f) => readFileSync(f, 'utf8').includes(`'${literal}'`) || readFileSync(f, 'utf8').includes(`"${literal}"`));
    expect(hits).toEqual([]);
  });
});
