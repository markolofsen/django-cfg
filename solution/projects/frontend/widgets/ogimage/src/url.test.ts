import { describe, expect, it } from 'vitest';

import { domainFromEnv, resolvePublicUrl, siteUrlFromEnv, withoutOgImages } from './url';

describe('resolvePublicUrl', () => {
  it('prefers the env value, trims the trailing slash', () => {
    expect(resolvePublicUrl('https://a.test/', 'https://b.test')).toBe('https://a.test');
  });

  it('falls back when the env value is empty', () => {
    expect(resolvePublicUrl('', 'https://b.test')).toBe('https://b.test');
    expect(resolvePublicUrl(undefined, 'https://b.test/sub/')).toBe('https://b.test/sub');
  });

  it('throws when neither is given', () => {
    expect(() => resolvePublicUrl(undefined)).toThrow(/public URL/u);
  });
});

describe('siteUrlFromEnv / domainFromEnv', () => {
  it('reads NEXT_PUBLIC_SITE_URL from the injected env', () => {
    const env = { NEXT_PUBLIC_SITE_URL: 'https://site.test:8443/' };
    expect(siteUrlFromEnv({ env })).toBe('https://site.test:8443');
    expect(domainFromEnv({ env })).toBe('site.test:8443');
  });

  it('uses the fallback when the env is bare', () => {
    expect(domainFromEnv({ env: {}, fallback: 'https://fallback.test' })).toBe('fallback.test');
  });
});

describe('withoutOgImages', () => {
  it('removes images from both openGraph and twitter, keeping everything else', () => {
    const out = withoutOgImages({
      title: 'T',
      openGraph: { title: 'T', images: [{ url: '/x.png' }] },
      twitter: { card: 'summary_large_image', images: ['/x.png'] },
    });
    expect(out.title).toBe('T');
    expect(out.openGraph).toEqual({ title: 'T' });
    expect(out.twitter).toEqual({ card: 'summary_large_image' });
  });

  it('leaves absent blocks absent', () => {
    expect(withoutOgImages({ title: 'T' })).toEqual({ title: 'T', openGraph: undefined, twitter: undefined });
  });
});
