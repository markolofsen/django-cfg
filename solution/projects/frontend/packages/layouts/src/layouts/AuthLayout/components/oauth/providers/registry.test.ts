import { describe, expect, it } from 'vitest';

import { OAUTH_PROVIDERS, providerName } from './registry';

describe('providerName', () => {
  it('returns the brand name of a known provider', () => {
    expect(providerName('github')).toBe('GitHub');
    expect(providerName('google')).toBe('Google');
  });

  it('shows an unknown id as it came, never an inherited property', () => {
    expect(providerName('gitlab')).toBe('gitlab');
    expect(providerName('constructor')).toBe('constructor');
    expect(providerName('')).toBe('');
  });

  it('gives every provider an icon and a name', () => {
    for (const entry of Object.values(OAUTH_PROVIDERS)) {
      expect(entry.name).not.toBe('');
      expect(typeof entry.Icon).toBe('function');
    }
  });
});
