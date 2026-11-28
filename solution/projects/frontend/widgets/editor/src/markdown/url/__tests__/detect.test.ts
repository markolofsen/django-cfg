import { describe, it, expect } from 'vitest';
import {
  findUrls,
  splitUrl,
  truncateUrlLabel,
  faviconUrl,
  normalizeHref,
} from '../detect';

describe('findUrls', () => {
  it('detects an https URL', () => {
    const matches = findUrls('see https://github.com/wailsapp/wails here');
    expect(matches).toHaveLength(1);
    expect(matches[0]!.href).toBe('https://github.com/wailsapp/wails');
  });

  it('detects an http URL', () => {
    const matches = findUrls('http://example.com/x');
    expect(matches[0]!.href).toBe('http://example.com/x');
  });

  it('prepends https to a bare www. host', () => {
    const matches = findUrls('visit www.djangocfg.com/docs now');
    expect(matches).toHaveLength(1);
    expect(matches[0]!.href).toBe('https://www.djangocfg.com/docs');
    expect(matches[0]!.raw).toBe('www.djangocfg.com/docs');
  });

  it('detects a mailto link', () => {
    const matches = findUrls('mail me@example.com? no — mailto:me@example.com please');
    expect(matches).toHaveLength(1);
    expect(matches[0]!.href).toBe('mailto:me@example.com');
  });

  it('trims trailing prose punctuation', () => {
    const matches = findUrls('go to https://djangocfg.com/docs.');
    expect(matches[0]!.href).toBe('https://djangocfg.com/docs');
    expect(matches[0]!.raw).toBe('https://djangocfg.com/docs');
  });

  it('does NOT match a bare file path', () => {
    expect(findUrls('/Users/me/dev/manifest.md')).toHaveLength(0);
  });

  it('does NOT match a dotted filename', () => {
    expect(findUrls('see manifest.md please')).toHaveLength(0);
  });

  it('does NOT match a URL glued onto a preceding non-space char', () => {
    // `xhttps://...` — not a real URL boundary.
    expect(findUrls('xhttps://evil.com')).toHaveLength(0);
  });

  it('offsets slice back to the matched raw text', () => {
    const text = 'prefix https://a.com/b suffix';
    const m = findUrls(text)[0]!;
    expect(text.slice(m.start, m.end)).toBe('https://a.com/b');
  });
});

describe('splitUrl', () => {
  it('splits domain (www. stripped) and rest', () => {
    const s = splitUrl('https://www.github.com/wailsapp/wails');
    expect(s.domain).toBe('github.com');
    expect(s.host).toBe('www.github.com');
    expect(s.rest).toBe('/wailsapp/wails');
  });

  it('yields empty rest for a bare host', () => {
    const s = splitUrl('https://github.com');
    expect(s.domain).toBe('github.com');
    expect(s.rest).toBe('');
  });

  it('splits a mailto address', () => {
    const s = splitUrl('mailto:me@example.com');
    expect(s.mail).toBe('me@example.com');
    expect(s.domain).toBe('example.com');
  });
});

describe('truncateUrlLabel', () => {
  it('keeps a short URL as domain + path', () => {
    expect(truncateUrlLabel('https://github.com/wailsapp/wails')).toBe(
      'github.com/wailsapp/wails',
    );
  });

  it('middle-ellipsises a long path, keeping domain + last segment', () => {
    const label = truncateUrlLabel(
      'https://github.com/wailsapp/wails/blob/main/v3/README.md',
    );
    expect(label).toContain('github.com');
    expect(label).toContain('README.md');
    expect(label).toContain('…');
    expect(label.length).toBeLessThanOrEqual(40);
  });

  it('renders a mailto as the bare address', () => {
    expect(truncateUrlLabel('mailto:me@example.com')).toBe('me@example.com');
  });
});

describe('normalizeHref', () => {
  it('prepends https to www.', () => {
    expect(normalizeHref('www.x.com')).toBe('https://www.x.com');
  });
  it('leaves an explicit scheme untouched', () => {
    expect(normalizeHref('http://x.com')).toBe('http://x.com');
  });
});

describe('faviconUrl', () => {
  it('builds a Google S2 favicon URL', () => {
    expect(faviconUrl('github.com')).toContain('s2/favicons');
    expect(faviconUrl('github.com')).toContain('domain=github.com');
  });
  it('returns empty for an empty host', () => {
    expect(faviconUrl('')).toBe('');
  });
});
