import { describe, expect, it } from 'vitest';

import { resolveOAuthProviders } from './resolveProviders';

describe('resolveOAuthProviders', () => {
  it('shows everything the server lists, in the server order', () => {
    expect(resolveOAuthProviders(['github', 'google'])).toEqual(['github', 'google']);
  });

  it('narrows to the requested ids', () => {
    expect(resolveOAuthProviders(['github', 'google'], ['google'])).toEqual(['google']);
  });

  it('orders by the request', () => {
    expect(resolveOAuthProviders(['github', 'google'], ['google', 'github'])).toEqual(['google', 'github']);
  });

  it('never shows a provider the server did not list', () => {
    expect(resolveOAuthProviders(['github'], ['google', 'github'])).toEqual(['github']);
    expect(resolveOAuthProviders([], ['google'])).toEqual([]);
  });

  it('shows nothing for an empty request and drops duplicates', () => {
    expect(resolveOAuthProviders(['github', 'google'], [])).toEqual([]);
    expect(resolveOAuthProviders(['github', 'google'], ['google', 'google'])).toEqual(['google']);
  });
});
