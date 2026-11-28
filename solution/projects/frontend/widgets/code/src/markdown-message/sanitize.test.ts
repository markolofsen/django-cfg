import { describe, expect, it } from 'vitest';

import { buildSchema, buildUrlTransform, HTML_SCHEMA_BASE } from './sanitize';

/**
 * This module is the XSS boundary for every markdown message the product
 * renders — chat replies, OpenAPI descriptions, anything user- or model-authored.
 * A regression here does not look like a broken layout: it looks like a working
 * page that happens to execute someone else's `javascript:` href.
 *
 * The half that is just as load-bearing is the NEGATIVE space. `buildUrlTransform`
 * runs BEFORE rehype-sanitize and returns `''` for anything it does not recognise,
 * so if its allow-branch narrows, every ordinary link in the app silently loses its
 * href and nothing throws.
 */

describe('HTML_SCHEMA_BASE', () => {
  it('keeps the default schema\'s tags rather than replacing them', () => {
    // The tag list is spread from rehype-sanitize's default. If a refactor
    // stopped spreading it, `<p>`/`<a>` would be stripped and every message
    // would render as a wall of unstyled text.
    const tags = HTML_SCHEMA_BASE.tagNames;
    expect(Array.isArray(tags)).toBe(true);
    expect(tags).toContain('p');
    expect(tags).toContain('a');
  });

  it('adds the presentational tags OpenAPI descriptions use', () => {
    const tags = HTML_SCHEMA_BASE.tagNames;
    for (const tag of ['br', 'b', 'i', 'u', 's', 'sub', 'sup', 'small', 'mark', 'kbd', 'code', 'pre', 'details', 'summary']) {
      expect(tags).toContain(tag);
    }
  });

  it('does not allow script or style', () => {
    const tags = HTML_SCHEMA_BASE.tagNames;
    expect(tags).not.toContain('script');
    expect(tags).not.toContain('style');
    expect(tags).not.toContain('iframe');
  });
});

describe('buildSchema', () => {
  it('returns the base schema unchanged when no extra protocols are asked for', () => {
    // Identity, not a copy — the caller memoizes on it, and a fresh object
    // each call would re-run the whole sanitize pipeline on every render.
    expect(buildSchema(undefined)).toBe(HTML_SCHEMA_BASE);
    expect(buildSchema([])).toBe(HTML_SCHEMA_BASE);
  });

  it('appends the opted-in scheme to the href protocols, keeping the safe defaults', () => {
    const schema = buildSchema(['cmdop']);
    const protocols = schema.protocols;
    expect(protocols).toBeTypeOf('object');
    const href = (protocols as { href?: string[] }).href;
    expect(href).toContain('cmdop');
    expect(href).toContain('http');
    expect(href).toContain('https');
    expect(href).toContain('mailto');
  });

  it('does not mutate the shared base schema', () => {
    // Both callers share HTML_SCHEMA_BASE; a mutating build would leak one
    // app's custom scheme into every other consumer in the same bundle.
    const before = JSON.stringify(HTML_SCHEMA_BASE.protocols ?? null);
    buildSchema(['obsidian']);
    expect(JSON.stringify(HTML_SCHEMA_BASE.protocols ?? null)).toBe(before);
  });

  it('leaves protocol lists other than href alone', () => {
    const schema = buildSchema(['cmdop']);
    const protocols = schema.protocols as Record<string, string[]>;
    const src = protocols.src;
    if (src !== undefined) {
      expect(src).not.toContain('cmdop');
    }
  });
});

describe('buildUrlTransform', () => {
  it('is undefined when nothing is opted in, so react-markdown keeps its own default', () => {
    expect(buildUrlTransform(undefined)).toBeUndefined();
    expect(buildUrlTransform([])).toBeUndefined();
  });

  const transform = buildUrlTransform(['cmdop']);

  it('passes an opted-in scheme through VERBATIM', () => {
    // Verbatim matters: the host parses the URL back, so a lowercased or
    // re-encoded href resolves to the wrong machine.
    expect(transform?.('cmdop://machine/My%20Box')).toBe('cmdop://machine/My%20Box');
    expect(transform?.('CMDOP://Machine/X')).toBe('CMDOP://Machine/X');
  });

  it('keeps ordinary http(s) links', () => {
    expect(transform?.('https://example.com/a?b=c')).toBe('https://example.com/a?b=c');
    expect(transform?.('http://example.com')).toBe('http://example.com');
  });

  it('keeps the other safe schemes react-markdown allows', () => {
    expect(transform?.('mailto:a@b.com')).toBe('mailto:a@b.com');
    expect(transform?.('tel:+15551234')).toBe('tel:+15551234');
    expect(transform?.('xmpp:a@b')).toBe('xmpp:a@b');
    expect(transform?.('irc://a')).toBe('irc://a');
    expect(transform?.('ircs://a')).toBe('ircs://a');
  });

  it('keeps relative and in-page links', () => {
    expect(transform?.('#anchor')).toBe('#anchor');
    expect(transform?.('/docs/intro')).toBe('/docs/intro');
    expect(transform?.('./sibling')).toBe('./sibling');
    expect(transform?.('../parent')).toBe('../parent');
    expect(transform?.('?q=1')).toBe('?q=1');
  });

  it('keeps a bare relative filename', () => {
    expect(transform?.('intro.md')).toBe('intro.md');
  });

  it('drops data:, which is the bypass the fallback regex does catch', () => {
    // `/` is not in the "bare relative path" character class, so the base64
    // payload fails to match and the href is dropped.
    expect(transform?.('data:text/html;base64,PHNjcmlwdD4=')).toBe('');
  });

  it('drops javascript:', () => {
    // Regression. The bare-name fallback used to be
    //   /^[a-z0-9._~!$&'()*+,;=:@%-]+$/i
    // — a class holding both `:` and `(` `)`, so `javascript:alert(1)` matched
    // it in full and was returned verbatim, which is the one string the
    // function's own comment says it drops as an "XSS guard".
    //
    // It was never exploitable end to end: rehype-sanitize runs afterwards and
    // its `protocols.href` allow-list still stripped the href. A layer of
    // defence-in-depth that does not defend is broken anyway — anyone reusing
    // this function alone, or widening the sanitize schema, inherited a real
    // hole.
    expect(transform?.('javascript:alert(1)')).toBe('');
  });

  it('drops vbscript:', () => {
    expect(transform?.('vbscript:msgbox(1)')).toBe('');
  });

  it('still passes a bare relative filename, which the class exists for', () => {
    // The reason the fallback exists at all — removing `:` must not cost this.
    expect(transform?.('intro.md')).toBe('intro.md');
    expect(transform?.('a_file-name.v2.md')).toBe('a_file-name.v2.md');
  });

  it('drops a scheme that was not opted in', () => {
    expect(transform?.('obsidian://open?vault=x')).toBe('');
  });

  it('is not fooled by a tab or newline inside the scheme', () => {
    // `java\tscript:` is a classic filter bypass: browsers strip the control
    // character before resolving, so the href executes if it slips through.
    expect(transform?.('java\tscript:alert(1)')).toBe('');
    expect(transform?.('java\nscript:alert(1)')).toBe('');
  });

  it('opts in each scheme in a multi-scheme list independently', () => {
    const multi = buildUrlTransform(['cmdop', 'obsidian']);
    expect(multi?.('cmdop://a')).toBe('cmdop://a');
    expect(multi?.('obsidian://a')).toBe('obsidian://a');
    expect(multi?.('slack://a')).toBe('');
  });
});
