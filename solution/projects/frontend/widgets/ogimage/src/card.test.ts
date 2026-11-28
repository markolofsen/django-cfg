import { describe, expect, it } from 'vitest';

import { createOgCards, fitDescription, ogFooter, ogImageUrl } from './card';

const PNG_SIGNATURE = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

async function expectPng(response: Response) {
  expect(response.headers.get('content-type')).toBe('image/png');
  const bytes = new Uint8Array(await response.arrayBuffer());
  expect(Array.from(bytes.subarray(0, 8))).toEqual(PNG_SIGNATURE);
  return bytes;
}

describe('fitDescription', () => {
  it('drops empty and whitespace-only text', () => {
    expect(fitDescription('Title', undefined)).toBeUndefined();
    expect(fitDescription('Title', null)).toBeUndefined();
    expect(fitDescription('Title', '   ')).toBeUndefined();
  });

  it('keeps a short description under a short title untouched', () => {
    expect(fitDescription('Short', 'A description.')).toBe('A description.');
  });

  it('gives a three-line title the card to itself', () => {
    expect(fitDescription('x'.repeat(45), 'Anything at all')).toBeUndefined();
  });

  it('shrinks the budget as the title grows, cutting at a word boundary', () => {
    const description = 'word '.repeat(40).trim(); // 199 chars
    const short = fitDescription('Short', description)!;
    const medium = fitDescription('x'.repeat(40), description)!;
    expect(short.length).toBeLessThanOrEqual(151);
    expect(medium.length).toBeLessThanOrEqual(93);
    expect(short.endsWith('…')).toBe(true);
    expect(short).not.toMatch(/\s…$/u);
  });

  it('strips trailing punctuation before the ellipsis', () => {
    const description = `${'a'.repeat(140)}, ${'b'.repeat(20)}`;
    expect(fitDescription('Short', description)).toBe(`${'a'.repeat(140)}…`);
  });
});

describe('ogFooter', () => {
  it('joins present facts and drops absent ones', () => {
    expect(ogFooter('$1.2M', null, undefined, '', 3, 'Bahamas')).toBe('$1.2M  ·  3  ·  Bahamas');
  });

  it('is undefined when nothing is present', () => {
    expect(ogFooter(null, undefined, '  ')).toBeUndefined();
  });
});

describe('ogImageUrl', () => {
  const site = 'https://example.com';

  it('passes absolute http(s) URLs and data URIs through', () => {
    expect(ogImageUrl('https://cdn.example.com/a.jpg', site)).toBe('https://cdn.example.com/a.jpg');
    expect(ogImageUrl('data:image/png;base64,AAAA', site)).toBe('data:image/png;base64,AAAA');
  });

  it('resolves a root-relative path against the site', () => {
    expect(ogImageUrl('/media/a.jpg', site)).toBe('https://example.com/media/a.jpg');
  });

  it('degrades anything unusable to undefined', () => {
    expect(ogImageUrl(undefined, site)).toBeUndefined();
    expect(ogImageUrl('', site)).toBeUndefined();
    expect(ogImageUrl('ftp://example.com/a.jpg', site)).toBeUndefined();
    expect(ogImageUrl('/media/a.jpg', 'not a url')).toBeUndefined();
  });
});

describe('createOgCards', () => {
  const cards = createOgCards({
    name: 'Acme',
    description: 'Things, made.',
    tagline: 'Since 1999',
    domain: 'acme.test',
    siteUrl: 'https://acme.test',
    accentColor: '#A78BFA',
  });

  it('exposes the route contract', () => {
    expect(cards.size).toEqual({ width: 1200, height: 630 });
    expect(cards.contentType).toBe('image/png');
  });

  it('renders the brand card as a PNG', async () => {
    await expectPng(await cards.brandCard('Skills & MCP servers', 'Browse and install.'));
  }, 30_000);

  it('renders a content card as a PNG', async () => {
    await expectPng(
      await cards.contentCard({
        title: 'A fairly long skill title that wraps onto two lines',
        eyebrow: 'Skill',
        description: 'A description that should be trimmed to the budget the title leaves.',
        footer: 'Acme · Skills',
      }),
    );
  }, 30_000);

  it('falls back to the brand card when the title is empty', async () => {
    const [brand, fallback] = await Promise.all([cards.brandCard(), cards.contentCard({ title: '  ', eyebrow: 'Skill' })]);
    const a = await expectPng(brand);
    const b = await expectPng(fallback);
    expect(Buffer.from(a).equals(Buffer.from(b))).toBe(true);
  }, 30_000);
});
