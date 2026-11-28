import { describe, expect, it } from 'vitest';

import { clickDestination, type ClickLike } from './linkClick';

const BASE = 'http://site.test/board?tab=1';

/** A stand-in for an anchor; `closest` finds itself, like a click on the link's own box. */
function anchor(attrs: Record<string, string>) {
  const a = {
    href: new URL(attrs.href ?? '', BASE).href,
    target: attrs.target ?? '',
    hasAttribute: (n: string) => n in attrs,
    closest: (_s: string) => a,
  };
  return a;
}

const click = (target: ClickLike['target'], over: Partial<ClickLike> = {}): ClickLike => ({
  button: 0,
  metaKey: false,
  ctrlKey: false,
  shiftKey: false,
  altKey: false,
  target,
  ...over,
});

describe('clickDestination', () => {
  it('a plain left click on a same-origin link gives its URL', () => {
    expect(clickDestination(click(anchor({ href: '/other?x=1' })), BASE)?.pathname).toBe('/other');
  });

  it('finds the anchor from a child element', () => {
    const a = anchor({ href: '/other' });
    expect(clickDestination(click({ closest: () => a }), BASE)).not.toBeNull();
  });

  it.each([
    ['middle button', { button: 1 }],
    ['meta', { metaKey: true }],
    ['ctrl', { ctrlKey: true }],
    ['shift', { shiftKey: true }],
    ['alt', { altKey: true }],
  ])('ignores %s', (_n, over) => {
    expect(clickDestination(click(anchor({ href: '/other' }), over), BASE)).toBeNull();
  });

  it.each([
    ['target=_blank', { href: '/o', target: '_blank' }],
    ['download', { href: '/o', download: '' }],
    ['opt-out attribute', { href: '/o', 'data-no-route-progress': '' }],
    ['another origin', { href: 'https://other.test/o' }],
    ['mailto', { href: 'mailto:a@b.c' }],
  ])('ignores %s', (_n, attrs) => {
    expect(clickDestination(click(anchor(attrs)), BASE)).toBeNull();
  });

  it('target=_self still counts', () => {
    expect(clickDestination(click(anchor({ href: '/o', target: '_self' })), BASE)).not.toBeNull();
  });

  it('a click outside any link gives null', () => {
    expect(clickDestination(click({ closest: () => null }), BASE)).toBeNull();
    expect(clickDestination(click(null), BASE)).toBeNull();
  });
});
